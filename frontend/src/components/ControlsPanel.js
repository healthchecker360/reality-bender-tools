import React from 'react';

function ControlsPanel({ controls, setControls, onProcess }) {
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setControls(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  return (
    <div className="mb-4 grid grid-cols-2 gap-2">
      <input type="number" name="width" placeholder="Width" value={controls.width} onChange={handleChange} className="border p-2" />
      <input type="number" name="height" placeholder="Height" value={controls.height} onChange={handleChange} className="border p-2" />
      <input type="number" name="rotate" placeholder="Rotate (deg)" value={controls.rotate} onChange={handleChange} className="border p-2" />
      <select name="flip" value={controls.flip} onChange={handleChange} className="border p-2">
        <option value="">Flip</option>
        <option value="horizontal">Horizontal</option>
        <option value="vertical">Vertical</option>
      </select>
      <select name="format" value={controls.format} onChange={handleChange} className="border p-2">
        <option value="png">PNG</option>
        <option value="jpeg">JPEG</option>
        <option value="webp">WEBP</option>
      </select>
      <input type="number" name="quality" placeholder="Quality 0-100" value={controls.quality} onChange={handleChange} className="border p-2" />
      <input type="number" name="brightness" step="0.1" placeholder="Brightness" value={controls.brightness} onChange={handleChange} className="border p-2" />
      <input type="number" name="contrast" step="0.1" placeholder="Contrast" value={controls.contrast} onChange={handleChange} className="border p-2" />
      <input type="number" name="saturation" step="0.1" placeholder="Saturation" value={controls.saturation} onChange={handleChange} className="border p-2" />
      <input type="number" name="sharpness" step="0.1" placeholder="Sharpness" value={controls.sharpness} onChange={handleChange} className="border p-2" />
      <label className="flex items-center">
        <input type="checkbox" name="aiBackground" checked={controls.aiBackground} onChange={handleChange} className="mr-2" />
        AI Background Remove
      </label>
      <button onClick={onProcess} className="col-span-2 bg-blue-500 text-white p-2 rounded">Process Image</button>
    </div>
  );
}

export default ControlsPanel;
