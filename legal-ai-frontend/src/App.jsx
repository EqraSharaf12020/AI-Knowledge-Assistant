import React, { useRef, useState } from 'react';
import axios from 'axios';
import { Download, FileSearch, Home, Shield, Sparkles, Zap } from 'lucide-react';
import PDFViewer from './components/PDFViewer';
import RiskSidebar from './components/RiskSidebar';
import FileUpload from './components/FileUpload';
import ChatWindow from './components/ChatWindow';

const RISK_WEIGHTS = {
  High: 35,
  Medium: 18,
  Low: 8,
};

function deriveRiskSummary(analysisData) {
  const risks = analysisData?.risks || [];
  const highCount = risks.filter((item) => item.type === 'High').length;
  const mediumCount = risks.filter((item) => item.type === 'Medium').length;
  const lowCount = risks.filter((item) => item.type === 'Low').length;

  const score = Math.min(
    100,
    highCount * RISK_WEIGHTS.High +
      mediumCount * RISK_WEIGHTS.Medium +
      lowCount * RISK_WEIGHTS.Low
  );

  let label = 'Low';
  if (score >= 70) {
    label = 'Critical';
  } else if (score >= 45) {
    label = 'Elevated';
  } else if (score >= 20) {
    label = 'Guarded';
  }

  return {
    score,
    label,
    counts: {
      high: highCount,
      medium: mediumCount,
      low: lowCount,
      total: risks.length,
    },
  };
}

function sanitizePdfText(value) {
  return String(value || '')
    .replace(/\\/g, '\\\\')
    .replace(/\(/g, '\\(')
    .replace(/\)/g, '\\)')
    .replace(/\r?\n/g, ' ');
}

function buildPdfDocument(lines) {
  const pageWidth = 612;
  const pageHeight = 792;
  const left = 50;
  const top = 742;
  const lineHeight = 18;
  const linesPerPage = 36;
  const pages = [];

  for (let index = 0; index < lines.length; index += linesPerPage) {
    pages.push(lines.slice(index, index + linesPerPage));
  }

  const objects = [];
  const fontObjectNumber = 3 + pages.length * 2;

  objects.push('1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n');

  const pageObjectNumbers = pages.map((_, index) => 3 + index * 2);
  objects.push(
    `2 0 obj\n<< /Type /Pages /Kids [${pageObjectNumbers
      .map((number) => `${number} 0 R`)
      .join(' ')}] /Count ${pages.length} >>\nendobj\n`
  );

  pages.forEach((pageLines, index) => {
    const pageObjectNumber = 3 + index * 2;
    const contentObjectNumber = pageObjectNumber + 1;
    const content = [
      'BT',
      '/F1 11 Tf',
      '0.2 0.2 0.2 rg',
      `${left} ${top} Td`,
    ];

    pageLines.forEach((line, lineIndex) => {
      const safeLine = sanitizePdfText(line);
      if (lineIndex === 0) {
        content.push(`(${safeLine}) Tj`);
      } else {
        content.push(`0 -${lineHeight} Td`);
        content.push(`(${safeLine}) Tj`);
      }
    });

    content.push('ET');
    const contentStream = `${content.join('\n')}\n`;

    objects.push(
      `${pageObjectNumber} 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${pageWidth} ${pageHeight}] /Resources << /Font << /F1 ${fontObjectNumber} 0 R >> >> /Contents ${contentObjectNumber} 0 R >>\nendobj\n`
    );
    objects.push(
      `${contentObjectNumber} 0 obj\n<< /Length ${contentStream.length} >>\nstream\n${contentStream}endstream\nendobj\n`
    );
  });

  objects.push(`${fontObjectNumber} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n`);

  let pdf = '%PDF-1.4\n';
  const offsets = [0];
  const encoder = new TextEncoder();

  objects.forEach((object) => {
    offsets.push(encoder.encode(pdf).length);
    pdf += object;
  });

  const xrefOffset = encoder.encode(pdf).length;
  pdf += `xref\n0 ${objects.length + 1}\n`;
  pdf += '0000000000 65535 f \n';
  offsets.slice(1).forEach((offset) => {
    pdf += `${String(offset).padStart(10, '0')} 00000 n \n`;
  });
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF`;

  return new Blob([pdf], { type: 'application/pdf' });
}

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);
  const [uploadHistory, setUploadHistory] = useState([]);
  const hiddenFileInput = useRef(null);

  const featureItems = [
    {
      icon: FileSearch,
      title: 'Clause Intelligence',
      description:
        'Surface hidden obligations, missing protections, and ambiguous wording in seconds.',
    },
    {
      icon: Shield,
      title: 'Risk Prioritization',
      description:
        'Highlight what matters most before the contract reaches signature or review.',
    },
    {
      icon: Sparkles,
      title: 'AI Guidance',
      description:
        'Turn legal complexity into direct, actionable suggestions for the next draft.',
    },
  ];

  const handleUpload = async (uploadedFile) => {
    const entryId = `${uploadedFile.name}-${Date.now()}`;
    const newHistoryItem = {
      id: entryId,
      name: uploadedFile.name,
      file: uploadedFile,
      uploadedAt: new Date().toLocaleString(),
      analysis: null,
    };

    setFile(uploadedFile);
    setUploadHistory((prev) => [newHistoryItem, ...prev]);
    setLoading(true);
    setAnalysisData(null);

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      const response = await axios.post('http://localhost:8000/analyze/', formData);
      setAnalysisData(response.data.analysis);
      setUploadHistory((prev) =>
        prev.map((item) =>
          item.id === entryId ? { ...item, analysis: response.data.analysis } : item
        )
      );
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Backend connection failed. Is the server running?');
    } finally {
      setLoading(false);
    }
  };

  const handleHistorySelect = (historyItem) => {
    setFile(historyItem.file);
    setAnalysisData(historyItem.analysis);
  };

  const handleHistoryUploadClick = () => {
    hiddenFileInput.current?.click();
  };

  const handleGoHome = () => {
    setFile(null);
    setLoading(false);
    setAnalysisData(null);
  };

  const handleExportAnalysis = () => {
    if (!analysisData) {
      return;
    }

    const riskSummary = deriveRiskSummary(analysisData);
    const fileName = (file?.name || 'contract-analysis').replace(/\.pdf$/i, '');
    const lines = [
      'LexGuard AI Analysis Report',
      `Document: ${file?.name || 'Uploaded Document'}`,
      `Generated: ${new Date().toLocaleString()}`,
      `Overall Risk Score: ${riskSummary.score}/100 (${riskSummary.label})`,
      `Risk Counts: High ${riskSummary.counts.high}, Medium ${riskSummary.counts.medium}, Low ${riskSummary.counts.low}`,
      '',
    ];

    if (analysisData.risks && analysisData.risks.length > 0) {
      analysisData.risks.forEach((item, index) => {
        lines.push(`Clause ${index + 1}: ${item.type || 'Risk'} - ${item.risk || 'Risk'}`);
        lines.push(`Clause Text: ${item.clause || 'N/A'}`);
        lines.push(`Suggestion: ${item.suggestion || 'N/A'}`);
        lines.push('');
      });
    } else {
      lines.push(`Summary: ${analysisData.raw || 'No structured risks found for this document.'}`);
    }

    const blob = buildPdfDocument(lines);
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');

    link.href = downloadUrl;
    link.download = `${fileName}-risk-report.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);
  };

  const riskSummary = deriveRiskSummary(analysisData);

  return (
    <div className={`app-shell ${file ? 'app-shell-document' : 'app-shell-landing'}`}>
      <header className="app-header">
        <button type="button" className="brand-block brand-button" onClick={handleGoHome}>
          <div className="brand-icon">
            <Shield size={22} />
          </div>
          <div className="brand-copy">
            <h1>
              LexGuard <span>AI</span>
            </h1>
            <div className="brand-subline">
              {file ? (
                <span className="brand-home-chip">
                  <span className="header-home-icon">
                    <Home size={14} />
                  </span>
                  <span>Home</span>
                </span>
              ) : (
                <p>Contract review assistant for faster legal screening</p>
              )}
            </div>
          </div>
        </button>
      </header>
      <input
        ref={hiddenFileInput}
        type="file"
        accept=".pdf"
        style={{ display: 'none' }}
        onChange={(event) => {
          const uploadedFile = event.target.files?.[0];
          if (uploadedFile) {
            handleUpload(uploadedFile);
          }
        }}
      />

      <main className={`app-main ${file ? 'app-main-document' : 'app-main-landing'}`}>
        {file ? (
          <div className="workspace-layout">
            <aside className="history-stage">
              <div className="panel-head panel-head-dark">
                <div className="panel-title-block">
                  <span className="eyebrow">Document History</span>
                  <h2>Recent uploads</h2>
                  <p className="panel-subcopy">
                    Reopen a previous PDF or upload a new one anytime.
                  </p>
                </div>
              </div>
              <div className="history-list">
                <button
                  className="upload-button upload-button-primary history-upload"
                  type="button"
                  onClick={handleHistoryUploadClick}
                >
                  <FileSearch size={14} />
                  Upload new PDF
                </button>
                {uploadHistory.length === 0 ? (
                  <div className="history-empty">No previous uploads yet.</div>
                ) : (
                  uploadHistory.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      className={`history-item ${file?.name === item.name ? 'history-item-active' : ''}`}
                      onClick={() => handleHistorySelect(item)}
                    >
                      <div>
                        <strong>{item.name}</strong>
                        <span>{item.uploadedAt}</span>
                      </div>
                      <span>{item.analysis ? 'Reviewed' : 'Pending'}</span>
                    </button>
                  ))
                )}
              </div>
            </aside>

            <section className="document-stage">
              <div className="panel-head panel-head-dark">
                <div className="panel-title-block">
                  <span className="eyebrow">Uploaded file</span>
                  <h2>{file.name}</h2>
                  <p className="panel-subcopy">
                    Side-by-side document preview for clause review and verification.
                  </p>
                </div>
                <span className="status-pill status-pill-amber">Live preview</span>
              </div>
              <div className="document-frame slide-in-left">
                <PDFViewer file={file} />
              </div>
            </section>

            <aside className="analysis-stage">
              <div className="panel-head">
                <div className="panel-title-block">
                  <span className="eyebrow">AI Review</span>
                  <h3>Clause Analysis</h3>
                  <p className="panel-subcopy">
                    Risks, clause notes, and actionable suggestions in a focused review feed.
                  </p>
                </div>
                <div className="analysis-status">
                  {loading ? <span className="status-pill status-pill-loading">Reviewing...</span> : null}
                  {analysisData ? (
                    <span className={`status-pill risk-score-pill risk-score-${riskSummary.label.toLowerCase()}`}>
                      Risk Score {riskSummary.score}
                    </span>
                  ) : null}
                  <button
                    type="button"
                    className="analysis-export-button"
                    onClick={handleExportAnalysis}
                    disabled={!analysisData || loading}
                  >
                    <Download size={14} />
                    Export PDF
                  </button>
                  <Zap size={16} />
                </div>
              </div>
              <RiskSidebar loading={loading} analysisData={analysisData} riskSummary={riskSummary} />
            </aside>
          </div>
        ) : (
          <section className="landing-shell" id="features">
            <div className="landing-copy">
              <div className="landing-badge">
                <Sparkles size={14} />
                Trusted contract review workspace
              </div>

              <h2>Review legal documents with a calmer, sharper workflow.</h2>

              <p className="landing-description">
                LexGuard AI helps your team inspect clauses, uncover risk, and
                chat with uploaded contracts in one clean, professional
                workspace.
              </p>

              <div className="landing-actions">
                <FileUpload
                  onUpload={handleUpload}
                  label="Upload PDF"
                  variant="primary"
                />
              </div>

              <div className="landing-stats">
                <div className="stat-card">
                  <strong>PDF analysis</strong>
                  <span>Extract clauses and inspect legal language instantly.</span>
                </div>
                <div className="stat-card">
                  <strong>RAG-powered chat</strong>
                  <span>Ask focused questions after the document is indexed.</span>
                </div>
              </div>
            </div>

            <div className="landing-visual">
              <div className="visual-card visual-card-hero">
                <div className="hero-glow hero-glow-primary" />
                <div className="hero-glow hero-glow-secondary" />
                <div className="justice-stage">
                  <div className="justice-frame" />
                  <div className="justice-figure">
                    <span className="justice-halo" />
                    <span className="justice-head" />
                    <span className="justice-torso" />
                    <span className="justice-base" />
                    <span className="justice-arm justice-arm-left" />
                    <span className="justice-arm justice-arm-right" />
                    <span className="justice-scale justice-scale-left">
                      <span className="justice-chain justice-chain-left" />
                      <span className="justice-chain justice-chain-right" />
                      <span className="justice-bowl" />
                    </span>
                    <span className="justice-scale justice-scale-right">
                      <span className="justice-chain justice-chain-left" />
                      <span className="justice-chain justice-chain-right" />
                      <span className="justice-bowl" />
                    </span>
                  </div>
                </div>
                <div className="hero-card-copy">
                  <span className="eyebrow">Confident legal review</span>
                  <h3>Turn complex legal documents into clear decisions with confidence</h3>
                </div>
              </div>

              <div className="visual-grid">
                <div className="visual-card visual-card-document">
                  <div className="document-lines">
                    <span />
                    <span />
                    <span />
                    <span />
                  </div>
                  <div className="magnifier" />
                  <div className="feather feather-left" />
                  <div className="feather feather-right" />
                </div>

                <div className="visual-card visual-card-features">
                  <span className="eyebrow">What you get</span>
                  <div className="feature-list">
                    {featureItems.map((item) => {
                      const Icon = item.icon;
                      return (
                        <div key={item.title} className="feature-item">
                          <div className="feature-icon">
                            <Icon size={18} />
                          </div>
                          <div>
                            <strong>{item.title}</strong>
                            <p>{item.description}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}
      </main>
      <ChatWindow />
    </div>
  );
}
