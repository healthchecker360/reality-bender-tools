import React, { useState } from 'react';

function BeforeAfterSlider({ original, processed }) {
  const [slider, setSlider] = useState(50);

  return (
    <div className="relative w-full h-96 overflow-hidden mb-4">
      <img src={original} alt="Original" className="absolute top-0 left-0 w-full h-full object-contain" />
      <div className="absolute top-0 left-0 h-full overflow-hidden" style={{ width: `${slider}%` }}>
        <img src={processed} alt="Processed" className="w-full h-full object-contain" />
      </div>
      <input
        type="range"
        min="0"
        max="100"
        value={slider}
        onChange={(e) => setSlider(e.target.value)}
        className="absolute bottom-0 left-0 w-full"
      />
    </div>
  );
}

export default BeforeAfterSlider;
