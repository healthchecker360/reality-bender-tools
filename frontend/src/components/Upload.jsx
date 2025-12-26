export default function Upload() {
  const handleUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      window.sessionImage = reader.result;
      window.dispatchEvent(new Event("image-updated"));
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="card">
      <input type="file" accept="image/*" onChange={handleUpload} />
    </div>
  );
}
