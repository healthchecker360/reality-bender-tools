// ----------------------------
// IMAGE TEXT TRANSLATOR
// ----------------------------
async function translateImage() {
    const imageInput = document.getElementById("translateImage");
    const language = document.getElementById("language").value;
    const resultBox = document.getElementById("translateResult");

    if (!imageInput.files[0] || !language) {
        alert("Please upload image and enter language");
        return;
    }

    resultBox.textContent = "Processing...";

    const formData = new FormData();
    formData.append("image", imageInput.files[0]);
    formData.append("language", language);

    const response = await fetch("/translate-image", {
        method: "POST",
        body: formData
    });

    const data = await response.json();
    resultBox.textContent = data.result;
}


// ----------------------------
// PASSPORT PHOTO MAKER
// ----------------------------
async function makePassport() {
    const imageInput = document.getElementById("passportImage");
    const country = document.getElementById("country").value;
    const status = document.getElementById("passportStatus");

    if (!imageInput.files[0]) {
        alert("Please upload image");
        return;
    }

    status.textContent = "Creating passport photo...";

    const formData = new FormData();
    formData.append("image", imageInput.files[0]);
    formData.append("country", country);

    const response = await fetch("/passport-photo", {
        method: "POST",
        body: formData
    });

    const data = await response.json();
    status.innerHTML = `✔ Done! <br><small>Download will be enabled after ad (next step)</small>`;
}


// ----------------------------
// MEME GENERATOR
// ----------------------------
async function generateMeme() {
    const imageInput = document.getElementById("memeImage");
    const topText = document.getElementById("topText").value;
    const bottomText = document.getElementById("bottomText").value;
    const status = document.getElementById("memeStatus");

    if (!imageInput.files[0] || !topText || !bottomText) {
        alert("Upload image and enter both texts");
        return;
    }

    status.textContent = "Generating meme...";

    const formData = new FormData();
    formData.append("image", imageInput.files[0]);
    formData.append("top", topText);
    formData.append("bottom", bottomText);

    const response = await fetch("/generate-meme", {
        method: "POST",
        body: formData
    });

    const data = await response.json();
    status.innerHTML = `😂 Meme ready! <br><small>Download after ad (next step)</small>`;
}
