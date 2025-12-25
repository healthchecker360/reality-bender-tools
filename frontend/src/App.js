import React, { useState } from 'react';
import ImageUploader from './components/ImageUploader';
import ControlsPanel from './components/ControlsPanel';
import BeforeAfterSlider from './components/BeforeAfterSlider';
import axios from 'axios';

function App() {
  const [originalImage, setOriginalImage] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);
  const [controls, setControls] = useState({
    width: '',
    height: '',
    rotate: '',
    flip: '',
    format: 'png',
    quality: 80,
    brightness: 1,
    contrast: 1,
    saturation: 1,
    sharpness: 1,
    aiBackground: false
  });

  const handleProcess = async () => {
    if (!originalImage) return;
    const formData = new FormData();
    formData.append('image', originalImage);
    Object.keys(controls).forEach(key => formData.append(key, controls[key]));

    try {
      const res = await axios.post('https://YOUR_BACKEND_URL/api/process', formData);
      setProcessedImage(res.data.url);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-4">Reality Image Tool</h1>
      <ImageUploader setImage={setOriginalImage} />
      <ControlsPanel controls={controls} setControls={setControls} onProcess={handleProcess} />
      {originalImage && processedImage && (
        <BeforeAfterSlider original={URL.createObjectURL(originalImage)} processed={`https://YOUR_BACKEND_URL${processedImage}`} />
      )}
    </div>
  );
}

export default App;
