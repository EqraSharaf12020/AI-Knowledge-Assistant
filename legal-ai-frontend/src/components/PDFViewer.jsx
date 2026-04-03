import React, { useEffect, useMemo } from 'react';

export default function PDFViewer({ file }) {
  const fileUrl = useMemo(() => URL.createObjectURL(file), [file]);

  useEffect(() => {
    return () => URL.revokeObjectURL(fileUrl);
  }, [fileUrl]);

  return (
    <div className="pdf-viewer">
      <iframe
        src={`${fileUrl}#toolbar=0`}
        title="Contract Preview"
        className="pdf-frame"
      />
    </div>
  );
}
