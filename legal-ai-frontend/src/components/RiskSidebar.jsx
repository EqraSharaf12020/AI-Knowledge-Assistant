import React from 'react';
import { AlertTriangle, CheckCircle, Info, Download } from 'lucide-react';

const RiskCard = ({ type, clause, risk, suggestion }) => (
  <div className="mb-6 p-4 border border-slate-300 rounded-md bg-white shadow-sm">
    <div className="flex items-center gap-2 mb-3">
      <span className={`text-[11px] font-bold px-2 py-0.5 rounded border ${
        type === 'High' ? 'bg-red-50 text-red-600 border-red-200' : 'bg-orange-50 text-orange-600 border-orange-200'
      }`}>
        {type} Priority
      </span>
    </div>

    <div className="space-y-3">
      <div>
        <h5 className="text-[10px] uppercase font-bold text-slate-500 tracking-wide">Found Clause:</h5>
        <p className="text-sm text-slate-800 font-medium bg-slate-50 p-2 rounded mt-1">
          "{clause}"
        </p>
      </div>

      <div className="flex gap-2 text-sm text-slate-600">
        <AlertTriangle size={16} className="text-slate-400 mt-0.5 flex-shrink-0" />
        <p><span className="font-bold">Observation:</span> {risk}</p>
      </div>

      <div className="flex gap-2 text-sm text-green-700 bg-green-50/50 p-3 rounded border border-green-100">
        <CheckCircle size={16} className="mt-0.5 flex-shrink-0" />
        <p><span className="font-bold">Suggested Edit:</span> {suggestion}</p>
      </div>
    </div>
  </div>
);

export default function RiskSidebar({ loading }) {
  if (loading) return <div className="p-10 text-center text-slate-500 italic">Analyzing document...</div>;

  return (
    <div className="flex flex-col h-full bg-slate-50">
      {/* Header - Simple and Clean */}
      <div className="p-5 border-b bg-white">
        <h3 className="font-bold text-slate-700 text-lg flex items-center gap-2">
          Contract Audit Results
        </h3>
        <p className="text-xs text-slate-500">Review the identified issues and suggested changes below.</p>
      </div>

      {/* Main List */}
      <div className="p-5 flex-1 overflow-y-auto">
        <RiskCard 
          type="High" 
          clause="Liability is not capped for indirect damages or lost profits." 
          risk="No financial cap exposes the company to claims exceeding the total contract value." 
          suggestion="Add: 'The total liability of either party shall not exceed 100% of the fees paid.'"
        />
        <RiskCard 
          type="Medium" 
          clause="Governing law: State of Delaware." 
          risk="International litigation costs can be prohibitive for local operations." 
          suggestion="Change governing law to local jurisdiction (e.g., India/New Delhi)."
        />
      </div>

      {/* Standard Button */}
      <div className="p-5 border-t bg-white">
        <button 
          onClick={() => alert("Report downloaded.")}
          className="w-full bg-slate-800 hover:bg-slate-900 text-white py-2.5 rounded font-semibold text-sm flex items-center justify-center gap-2 transition-colors"
        >
          <Download size={16} />
          Export Audit Report
        </button>
      </div>
    </div>
  );
}