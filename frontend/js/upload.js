export function setupUpload(inputId) {
  const input = document.getElementById(inputId);

  input.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      window.sessionImage = reader.result;
      window.dispatchEvent(new Event("image-updated"));
    };
    reader.readAsDataURL(file);
  });
}
