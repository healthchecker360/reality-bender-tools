import React from 'react';

function ImageUploader({ setImage }) {
  return (
    <div className="mb-4">
      <input
        type="file"
        accept="image/*"
        onChange={(e) => setImage(e.target.files[0])}
        className="border p-2"
      />
    </div>
  );
}

export default ImageUploader;
