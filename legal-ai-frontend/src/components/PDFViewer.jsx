import React, { useEffect, useMemo, useState } from 'react';

const ZOOM_LEVELS = [70, 85, 100, 115, 130, 150, 175, 200];

export default function PDFViewer({ file }) {
  const fileUrl = useMemo(() => URL.createObjectURL(file), [file]);
  const [zoom, setZoom] = useState(100);

  useEffect(() => {
    return () => URL.revokeObjectURL(fileUrl);
  }, [fileUrl]);

  useEffect(() => {
    setZoom(100);
  }, [fileUrl]);

  const zoomIndex = ZOOM_LEVELS.indexOf(zoom);

  const handleZoomChange = (direction) => {
    const nextIndex = direction === 'in' ? zoomIndex + 1 : zoomIndex - 1;
    if (nextIndex >= 0 && nextIndex < ZOOM_LEVELS.length) {
      setZoom(ZOOM_LEVELS[nextIndex]);
    }
  };

  return (
    <div className="pdf-viewer">
      <div className="pdf-viewer-controls">
        <button
          type="button"
          className="pdf-zoom-button"
          onClick={() => handleZoomChange('out')}
          disabled={zoomIndex <= 0}
        >
          -
        </button>
        <span className="pdf-zoom-label">{zoom}%</span>
        <button
          type="button"
          className="pdf-zoom-button"
          onClick={() => handleZoomChange('in')}
          disabled={zoomIndex === ZOOM_LEVELS.length - 1}
        >
          +
        </button>
      </div>
      <iframe
        src={`${fileUrl}#toolbar=0&zoom=${zoom}`}
        title="Contract Preview"
        className="pdf-frame"
      />
    </div>
  );
}
