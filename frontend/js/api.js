const API_BASE = "https://reality-bender-tools.onrender.com";

async function sendImage(endpoint, formData) {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      body: formData
    });

    if (!response.ok) throw new Error("Processing failed");

    return await response.blob();
  } catch (err) {
    alert(err.message);
  }
}
