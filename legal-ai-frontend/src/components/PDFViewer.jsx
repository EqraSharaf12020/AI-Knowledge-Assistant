 import React from 'react';

 export default function PDFViewer({ file }) {
  const fileUrl = URL.createObjectURL(file);
  return (
    <div className="h-full w-full rounded-lg shadow-inner bg-white overflow-hidden border">
      <iframe src={`${fileUrl}#toolbar=0`} title="Contract Preview" className="w-full h-full border-none" />
    </div>
  );
 }