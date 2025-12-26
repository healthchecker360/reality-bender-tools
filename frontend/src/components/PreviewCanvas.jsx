import { useEffect, useRef } from "react";

export default function PreviewCanvas() {
  const canvasRef = useRef(null);

  const drawImage = (src) => {
    const img = new Image();
    img.onload = () => {
      const canvas = canvasRef.current;
      canvas.width = img.width;
      canvas.height = img.height;
      canvas.getContext("2d").drawImage(img, 0, 0);
    };
    img.src = src;
  };

  useEffect(() => {
    const update = () => {
      if (window.sessionImage) drawImage(window.sessionImage);
    };
    window.addEventListener("image-updated", update);
    return () => window.removeEventListener("image-updated", update);
  }, []);

  return <canvas ref={canvasRef} className="preview-canvas"></canvas>;
}
