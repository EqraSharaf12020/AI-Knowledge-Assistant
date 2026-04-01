import React, { useState } from 'react';
import PDFViewer from './components/PDFViewer';
import RiskSidebar from './components/RiskSidebar';
import FileUpload from './components/FileUpload';
import ChatWindow from './components/ChatWindow';
import { Shield, FileText, Zap } from 'lucide-react';

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = (uploadedFile) => {
    console.log("File received in App.jsx:", uploadedFile.name); // Debug line
    setFile(uploadedFile);
    setLoading(true);
    setTimeout(() => setLoading(false), 1500); 
  };

  return (
    <div className="flex flex-col h-screen bg-[#f8fafc] font-sans text-slate-900">
      {/* Navbar,mnbvbnm */}
      <header className="h-20 bg-[#0f172a] flex items-center px-10 justify-between shadow-xl border-b border-slate-700 z-20">
        <div className="flex items-center gap-3">
          <div className="bg-blue-500 p-2 rounded-lg shadow-lg shadow-blue-500/30">
            <Shield className="text-white" size={24} strokeWidth={2.5} />
          </div>
          <div>
            <h1 className="text-white font-bold text-xl tracking-tight">LexGuard <span className="text-blue-400">AI</span></h1>
            <p className="text-slate-400 text-[10px] uppercase tracking-[0.2em] font-bold">Legal Assistant</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <FileUpload onUpload={handleUpload} />
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex flex-1 overflow-hidden relative">
        {file ? (
          /* WORKSPACE VIEW: Shows after upload */
          <div className="flex w-full h-full">
            <div className="w-[65%] p-8 bg-slate-200/50 backdrop-blur-sm shadow-inner">
               <div className="h-full rounded-xl overflow-hidden border border-slate-300 shadow-2xl bg-white">
                 <PDFViewer file={file} />
               </div>
            </div>
            
            <div className="w-[35%] bg-white border-l border-slate-200 overflow-y-auto shadow-2xl">
              <div className="sticky top-0 bg-white p-6 border-b border-slate-100 flex items-center justify-between z-10">
                <h3 className="font-bold text-slate-800 flex items-center gap-2">
                  <Zap size={18} className="text-yellow-500 fill-yellow-500" />
                  Clause Analysis
                </h3>
                <span className="text-[10px] bg-green-100 text-green-700 px-2 py-1 rounded-full font-bold">READY</span>
              </div>
              <RiskSidebar loading={loading} />
            </div>
          </div>
        ) : (
          /* HOME SCREEN: Shows when file is null */
          <div className="flex-1 flex flex-col items-center justify-center relative overflow-hidden bg-white w-full">
            <div className="absolute top-[-10%] right-[-5%] w-96 h-96 bg-blue-50 rounded-full blur-3xl opacity-50"></div>
            <div className="absolute bottom-[-10%] left-[-5%] w-96 h-96 bg-indigo-50 rounded-full blur-3xl opacity-50"></div>
            
            <div className="relative z-10 flex flex-col items-center text-center max-w-2xl px-6">
              <div className="mb-8 p-6 bg-slate-50 border border-slate-100 rounded-[2.5rem] shadow-2xl shadow-slate-200/50">
                <FileText size={80} className="text-blue-600 opacity-90" strokeWidth={1} />
              </div>
              <h2 className="text-4xl font-extrabold text-slate-900 tracking-tight mb-4 leading-tight">
                Verify Contracts with <span className="text-blue-600">Confidence.</span>
              </h2>
              <p className="text-lg text-slate-500 mb-10 leading-relaxed">
                Upload your legal documents and let our AI highlight hidden risks, missing clauses, 
                and aggressive language in seconds.
              </p>
              
              <div className="grid grid-cols-3 gap-8 w-full border-t border-slate-100 pt-10">
                <div className="flex flex-col items-center">
                  <span className="text-2xl font-bold text-slate-800">100%</span>
                  <p className="text-[10px] uppercase font-bold text-slate-400">Encrypted</p>
                </div>
                <div className="flex flex-col items-center border-x border-slate-100 px-4">
                  <span className="text-2xl font-bold text-slate-800">2.4s</span>
                  <p className="text-[10px] uppercase font-bold text-slate-400">Avg. Audit Time</p>
                </div>
                <div className="flex flex-col items-center">
                  <span className="text-2xl font-bold text-slate-800">JSON</span>
                  <p className="text-[10px] uppercase font-bold text-slate-400">Exportable</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Floating Chat Window */}
      <ChatWindow />
    </div>
  );
}