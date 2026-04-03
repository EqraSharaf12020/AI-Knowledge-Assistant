import React from 'react';
import { Upload } from 'lucide-react';

export default function FileUpload({
  onUpload,
  label = 'Upload PDF',
  variant = 'primary',
}) {
  const handleChange = (e) => {
    const file = e.target.files[0];
    if (file) onUpload(file);
  };

  return (
    <div className="upload-control">
      <input
        type="file"
        accept=".pdf"
        onChange={handleChange}
        className="upload-input"
        id="fileInput"
      />
      <label htmlFor="fileInput" className={`upload-button upload-button-${variant}`}>
        <Upload size={18} />
        {label}
      </label>
    </div>
  );
}
