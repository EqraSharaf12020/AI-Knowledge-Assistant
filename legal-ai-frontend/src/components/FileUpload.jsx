import React from 'react';
import { Upload } from 'lucide-react';

export default function FileUpload({ onUpload }) {
  const handleChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") {
      onUpload(file);
    }
  };

  return (
    <label className="group flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-full cursor-pointer transition-all duration-300 shadow-lg shadow-blue-500/25 active:scale-95 border border-blue-400/20">
      <Upload size={18} className="group-hover:-translate-y-0.5 transition-transform" />
      <span className="text-sm font-semibold tracking-wide">Upload Contract</span>
      <input type="file" className="hidden" accept=".pdf" onChange={handleChange} />
    </label>
  );
}