import React from 'react';

const ControlsPanel = ({ settings, setSettings }) => {
  return (
    <div className="mb-4 p-4 bg-white rounded shadow-md">
      <h2 className="text-lg font-semibold mb-2">Image Controls</h2>

      {/* Resize */}
      <div className="flex gap-2 mb-2">
        <input
          type="number"
          placeholder="Width"
          value={settings.width}
          onChange={(e) => setSettings({ ...settings, width: e.target.value })}
          className="p-2 border rounded w-24"
        />
        <input
          type="number"
          placeholder="Height"
          value={settings.height}
          onChange={(e) => setSettings({ ...settings, height: e.target.value })}
          className="p-2 border rounded w-24"
        />
      </div>

      {/* Format */}
      <div className="flex gap-2 mb-2">
        <label className="font-medium">Format:</label>
        <select
          value={settings.format}
          onChange={(e) => setSettings({ ...settings, format: e.target.value })}
          className="p-2 border rounded"
        >
          <option value="png">PNG</option>
          <option value="jpg">JPG</option>
          <option value="webp">WebP</option>
          <option value="avif">AVIF</option>
          <option value="bmp">BMP</option>
          <option value="gif">GIF</option>
          <option value="tiff">TIFF</option>
        </select>
      </div>

      {/* Enhancement sliders */}
      <div className="mb-2">
        <label className="block font-medium">Brightness: {settings.brightness}</label>
        <input
          type="range"
          min="0.1"
          max="3"
          step="0.1"
          value={settings.brightness}
          onChange={(e) => setSettings({ ...settings, brightness: e.target.value })}
          className="w-full"
        />
      </div>

      <div className="mb-2">
        <label className="block font-medium">Contrast: {settings.contrast}</label>
        <input
          type="range"
          min="0.1"
          max="3"
          step="0.1"
          value={settings.contrast}
          onChange={(e) => setSettings({ ...settings, contrast: e.target.value })}
          className="w-full"
        />
      </div>

      <div className="mb-2">
        <label className="block font-medium">Saturation: {settings.saturation}</label>
        <input
          type="range"
          min="0.1"
          max="3"
          step="0.1"
          value={settings.saturation}
          onChange={(e) => setSettings({ ...settings, saturation: e.target.value })}
          className="w-full"
        />
      </div>

      <div className="mb-2">
        <label className="block font-medium">Sharpness: {settings.sharpness}</label>
        <input
          type="range"
          min="0"
          max="10"
          step="0.5"
          value={settings.sharpness}
          onChange={(e) => setSettings({ ...settings, sharpness: e.target.value })}
          className="w-full"
        />
      </div>

      {/* AI Background Removal */}
      <div className="flex items-center gap-2 mt-2">
        <input
          type="checkbox"
          checked={settings.removeBg}
          onChange={(e) => setSettings({ ...settings, removeBg: e.target.checked })}
        />
        <label className="font-medium">AI Background Removal</label>
      </div>
    </div>
  );
};

export default ControlsPanel;
