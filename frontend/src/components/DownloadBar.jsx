export default function DownloadBar() {
  const download = () => {
    if (!window.sessionImage) return;

    alert("Show Ad Here");

    const a = document.createElement("a");
    a.href = window.sessionImage;
    a.download = "image.png";
    a.click();
  };

  return (
    <div className="card">
      <button onClick={download}>Download Image</button>
    </div>
  );
}
