import React from 'react';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

export default function RiskSidebar({ loading, analysisData }) {
  if (loading) return (
    <div className="p-10 text-center flex flex-col items-center gap-4 text-slate-400">
      <div className="w-12 h-12 border-4 border-blue-100 border-t-blue-600 rounded-full animate-spin"></div>
      <p className="text-sm font-medium">AI auditing document...</p>
    </div>
  );

  if (!analysisData || !analysisData.risks) return (
    <div className="p-10 text-center text-slate-400 text-sm">
      No analysis available. Upload a file to start.
    </div>
  );

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
            }`}>{item.risk}</span>
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