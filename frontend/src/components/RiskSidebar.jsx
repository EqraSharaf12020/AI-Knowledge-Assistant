import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function RiskSidebar({ loading, analysisData, riskSummary }) {
  if (loading) {
    return (
      <div className="risk-state">
        <div className="risk-spinner" />
        <p>AI auditing document...</p>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="risk-empty">
        <p>No analysis available yet.</p>
        <span>Upload a PDF to begin clause screening.</span>
      </div>
    );
  }

  if (!analysisData.risks || analysisData.risks.length === 0) {
    if (analysisData.raw) {
      return (
        <div className="risk-list">
          <div className="risk-raw-card">
            <div className="risk-card-title">
              <AlertTriangle size={14} />
              <span>Raw AI Response</span>
            </div>
            <p>{analysisData.raw}</p>
          </div>
        </div>
      );
    }

    return (
      <div className="risk-empty">
        <p>No significant risks found in this document.</p>
      </div>
    );
  }

  return (
    <div className="risk-scroll">
      <div className="risk-list">
        {riskSummary ? (
          <div className="risk-summary-card">
            <div>
              <span className="risk-summary-label">Overall Risk Score</span>
              <div className="risk-summary-score-row">
                <strong>{riskSummary.score}/100</strong>
                <span className={`risk-summary-badge risk-summary-${riskSummary.label.toLowerCase()}`}>
                  {riskSummary.label}
                </span>
              </div>
            </div>
            <p className="risk-summary-meta">
              {riskSummary.counts.high} high, {riskSummary.counts.medium} medium, {riskSummary.counts.low} low
            </p>
          </div>
        ) : null}
        {analysisData.risks.map((item, index) => (
          <div
            key={index}
            className={`risk-card ${item.type === 'High' ? 'risk-card-high' : 'risk-card-medium'}`}
          >
            <div className="risk-card-title">
              <AlertCircle size={14} />
              <span>
                {item.type} Risk - {item.risk}
              </span>
            </div>
            <p className="risk-clause">"{item.clause}"</p>
            <div className="risk-suggestion">
              <CheckCircle2 size={14} />
              <span>
                <strong>Suggestion:</strong> {item.suggestion}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
