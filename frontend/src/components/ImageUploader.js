import React from 'react';

const ImageUploader = ({ onUpload }) => {
  const handleChange = (e) => {
    const file = e.target.files[0];
    if (file) onUpload(file);
  };

  return (
    <div className="mb-4">
      <label className="block text-white font-semibold mb-2">Upload Image</label>
      <input
        type="file"
        accept="image/*"
        onChange={handleChange}
        className="p-2 rounded border border-gray-300 bg-white cursor-pointer"
      />
    </div>
  );
};

export default ImageUploader;
