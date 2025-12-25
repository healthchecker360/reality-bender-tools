import React, { useRef, useEffect } from 'react';

const BeforeAfterSlider = ({ original, processed }) => {
  const sliderRef = useRef(null);

  useEffect(() => {
    const slider = sliderRef.current;
    const handleMove = (e) => {
      const rect = slider.getBoundingClientRect();
      const offsetX = e.clientX - rect.left;
      slider.querySelector('.after').style.width = `${Math.max(0, Math.min(offsetX, rect.width))}px`;
    };
    slider.addEventListener('mousemove', handleMove);
    return () => slider.removeEventListener('mousemove', handleMove);
  }, []);

  return (
    <div
      ref={sliderRef}
      className="relative w-full h-96 mt-4 overflow-hidden cursor-ew-resize rounded shadow-lg bg-gray-200"
    >
      {/* Original Image */}
      <img
        src={original}
        alt="original"
        className="absolute top-0 left-0 w-full h-full object-contain"
      />

      {/* Processed Image */}
      <img
        src={processed}
        alt="processed"
        className="after absolute top-0 left-0 h-full object-contain"
        style={{ width: '50%' }}
      />
    </div>
  );
};

export default BeforeAfterSlider;
