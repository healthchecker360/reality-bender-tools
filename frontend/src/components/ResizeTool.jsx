export default function ResizeTool() {
  const resize = () => {
    const canvas = document.querySelector("canvas");
    if (!canvas) return;

    const width = parseInt(document.getElementById("w").value);
    const height = parseInt(document.getElementById("h").value);

    const temp = document.createElement("canvas");
    temp.width = width;
    temp.height = height;

    temp.getContext("2d").drawImage(canvas, 0, 0, width, height);
    window.sessionImage = temp.toDataURL();
    window.dispatchEvent(new Event("image-updated"));
  };

  return (
    <div className="card">
      <h3>Resize</h3>
      <input id="w" placeholder="Width (px)" />
      <input id="h" placeholder="Height (px)" />
      <button onClick={resize}>Apply</button>
    </div>
  );
}
