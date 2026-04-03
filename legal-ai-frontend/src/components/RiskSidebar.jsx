import React from 'react';
import { AlertCircle, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function RiskSidebar({ loading, analysisData }) {
  if (loading) return (
    <div className="p-10 text-center flex flex-col items-center gap-4 text-slate-400">
      <div className="w-12 h-12 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin"></div>
      <p className="text-sm font-medium">AI auditing document...</p>
    </div>
  );

  if (!analysisData) return (
    <div className="p-10 text-center text-slate-400 text-sm">
      No analysis available. Upload a file to start.
    </div>
  );

  // Fallback: if JSON parsing failed on backend, show raw text
  if (!analysisData.risks || analysisData.risks.length === 0) {
    if (analysisData.raw) {
      return (
        <div className="p-4">
          <div className="p-4 rounded-2xl border border-yellow-200 bg-yellow-50">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle size={14} className="text-yellow-500" />
              <span className="text-xs font-bold text-yellow-700">Raw AI Response</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed whitespace-pre-wrap">{analysisData.raw}</p>
          </div>
        </div>
      );
    }
    return (
      <div className="p-10 text-center text-slate-400 text-sm">
        ✅ No significant risks found in this document.
      </div>
    );
  }

  return (
    <div className="p-4 space-y-4">
      {analysisData.risks.map((item, index) => (
        <div key={index} className={`p-5 rounded-2xl border-l-4 shadow-sm bg-white transition-all hover:shadow-md border ${
          item.type === 'High' ? 'border-l-red-500 border-red-50' : 'border-l-yellow-500 border-yellow-50'
        }`}>
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle size={14} className={item.type === 'High' ? 'text-red-500' : 'text-yellow-500'} />
            <span className={`text-[10px] font-bold uppercase ${
              item.type === 'High' ? 'text-red-600' : 'text-yellow-600'
            }`}>{item.type} RISK — {item.risk}</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed font-medium mb-3">"{item.clause}"</p>
          <div className="p-3 bg-slate-50 rounded-xl text-[11px] text-blue-800 border border-blue-100 flex gap-2">
            <CheckCircle2 size={14} className="shrink-0 mt-0.5" />
            <span><strong>Suggestion:</strong> {item.suggestion}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
