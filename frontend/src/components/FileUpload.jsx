import React from 'react';
import { Upload } from 'lucide-react';

export default function FileUpload({
  onUpload,
  label = 'Upload PDF',
  variant = 'primary',
  isComparison = false,
}) {
  const handleChange = (e) => {
    if (isComparison) {
      const files = Array.from(e.target.files);
      if (files.length >= 2) {
        onUpload(files[0], files[1]);
      } else {
        alert('Please select at least two files for comparison.');
      }
    } else {
      const file = e.target.files[0];
      if (file) onUpload(file);
    }
  };

  return (
    <div className="upload-control">
      <input
        type="file"
        accept=".pdf"
        multiple={isComparison}
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
