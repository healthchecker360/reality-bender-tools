import Upload from "./components/Upload";
import PreviewCanvas from "./components/PreviewCanvas";
import ResizeTool from "./components/ResizeTool";
import DownloadBar from "./components/DownloadBar";

export default function App() {
  return (
    <div className="app-container">
      <h1>Image Tools</h1>

      <Upload />
      <PreviewCanvas />
      <ResizeTool />
      <DownloadBar />
    </div>
  );
}
