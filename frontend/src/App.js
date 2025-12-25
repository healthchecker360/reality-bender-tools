import React, { useState } from 'react';
import ImageUploader from './components/ImageUploader';
import ControlsPanel from './components/ControlsPanel';
import BeforeAfterSlider from './components/BeforeAfterSlider';
import axios from 'axios';

function App() {
  const [original, setOriginal] = useState(null);
  const [processed, setProcessed] = useState(null);
  const [settings, setSettings] = useState({
    width: '',
    height: '',
    format: 'png',
    brightness: 1,
    contrast: 1,
    saturation: 1,
    sharpness: 0,
    removeBg: false
  });

  const handleUpload = async (file) => {
    setOriginal(URL.createObjectURL(file));
    const formData = new FormData();
    formData.append('image', file);
    formData.append('width', settings.width);
    formData.append('height', settings.height);
    formData.append('format', settings.format);
    formData.append('brightness', settings.brightness);
    formData.append('contrast', settings.contrast);
    formData.append('saturation', settings.saturation);
    formData.append('sharpness', settings.sharpness);
    formData.append('removeBg', settings.removeBg);

    try {
      const res = await axios.post('http://localhost:5000/api/process', formData);
      setProcessed(res.data.url);
    } catch (err) {
      console.error('Processing failed:', err);
    }
  };

  return (
    <div className="p-4 bg-gradient-to-r from-blue-400 to-purple-500 min-h-screen">
      <h1 className="text-3xl font-bold text-white mb-6">Reality Image Tool</h1>
      <ImageUploader onUpload={handleUpload} />
      <ControlsPanel settings={settings} setSettings={setSettings} />
      {original && processed && <BeforeAfterSlider original={original} processed={processed} />}
    </div>
  );
}

export default App;
