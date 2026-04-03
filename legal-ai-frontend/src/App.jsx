import React, { useState } from 'react';
import axios from 'axios';
import PDFViewer from './components/PDFViewer';
import RiskSidebar from './components/RiskSidebar';
import FileUpload from './components/FileUpload';
import ChatWindow from './components/ChatWindow';
import { Shield, FileText, Zap, Loader2 } from 'lucide-react';


export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);

  const handleUpload = async (uploadedFile) => {
    setFile(uploadedFile);
    setLoading(true);
    setAnalysisData(null);

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      // Connects to Person 3's API
      const response = await axios.post('http://localhost:8000/analyze/', formData);
      setAnalysisData(response.data.analysis);
    } catch (error) {
      console.error("Upload failed:", error);
      alert("Backend connection failed. Is the server running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-[#f8fafc] font-sans text-slate-900">
      <header className="h-20 bg-[#0f172a] flex items-center px-10 justify-between shadow-xl z-20">
        <div className="flex items-center gap-3">
          <div className="bg-blue-500 p-2 rounded-lg">
            <Shield className="text-white" size={24} />
          </div>
          <div>
            <h1 className="text-white font-bold text-xl">LexGuard <span className="text-blue-400">AI</span></h1>
            <p className="text-slate-400 text-[10px] uppercase font-bold">MNNIT Project</p>
          </div>
        </div>
        <FileUpload onUpload={handleUpload} />
      </header>

      <main className="flex flex-1 overflow-hidden relative">
        {file ? (
          <div className="flex w-full h-full">
            <div className="w-[65%] p-8 bg-slate-200/50">
               <div className="h-full rounded-xl overflow-hidden border bg-white shadow-2xl">
                 <PDFViewer file={file} />
               </div>
            </div>
            
            <div className="w-[35%] bg-white border-l overflow-y-auto shadow-2xl">
              <div className="sticky top-0 bg-white p-6 border-b flex items-center justify-between z-10">
                <h3 className="font-bold text-slate-800 flex items-center gap-2">
                  <Zap size={18} className="text-yellow-500 fill-yellow-500" />
                  Clause Analysis
                </h3>
                {loading ? <Loader2 className="animate-spin text-blue-600" size={18} /> : 
                  <span className="text-[10px] bg-green-100 text-green-700 px-2 py-1 rounded-full font-bold">READY</span>
                }
              </div>
              <RiskSidebar loading={loading} analysisData={analysisData} />
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center max-w-2xl mx-auto px-6">
            <div className="mb-8 p-6 bg-slate-50 border rounded-[2.5rem] shadow-xl">
              <FileText size={80} className="text-blue-600" strokeWidth={1} />
            </div>
            <h2 className="text-4xl font-extrabold mb-4">Verify Contracts with <span className="text-blue-600">Confidence.</span></h2>
            <p className="text-lg text-slate-500 mb-10">Upload a PDF to identify hidden risks and missing clauses using RAG technology.</p>
          </div>
        )}
      </main>
      <ChatWindow />
    </div>
  );
}