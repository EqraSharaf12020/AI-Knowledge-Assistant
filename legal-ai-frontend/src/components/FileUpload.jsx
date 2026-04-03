import React from 'react';
import { Upload } from 'lucide-react';

export default function FileUpload({ onUpload }) {
  const handleChange = (e) => {
    const file = e.target.files[0];
    if (file) onUpload(file);
  };

  return (
    <div className="relative">
      <input type="file" accept=".pdf" onChange={handleChange} className="absolute inset-0 opacity-0 cursor-pointer w-full h-full" id="fileInput" />
      <label htmlFor="fileInput" className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-full flex items-center gap-2 text-sm font-bold transition-all shadow-lg shadow-blue-500/20 cursor-pointer">
        <Upload size={18} />
        Analyze Contract
      </label>
    </div>
  );
}