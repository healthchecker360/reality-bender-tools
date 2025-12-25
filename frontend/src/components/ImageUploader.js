import React, { useState } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function ImageUploader() {
  const [file, setFile] = useState(null);
  const [processedImage, setProcessedImage] = useState(null);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("image", file);

    try {
      const response = await axios.post(`${BACKEND_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setProcessedImage(response.data.processedImage); // adjust based on backend response
    } catch (error) {
      console.error("Upload failed", error);
    }
  };

  return (
    <div className="my-4">
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
        accept="image/*"
      />
      <button onClick={handleUpload} className="bg-blue-500 text-white px-4 py-2 ml-2 rounded">
        Upload
      </button>

      {processedImage && (
        <div className="mt-4">
          <img src={processedImage} alt="Processed" className="max-w-full" />
        </div>
      )}
    </div>
  );
}

export default ImageUploader;
