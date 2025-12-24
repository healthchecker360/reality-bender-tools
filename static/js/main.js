document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("all-in-one-form");
    const resultBox = document.getElementById("result-box");
    const featureSelect = document.getElementById("feature-select");
    const presetSelect = document.getElementById("preset-select");
    const sizeSelect = document.getElementById("size-select");
    const formatSelect = document.getElementById("format-select");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const fileInput = document.getElementById("image");
        const file = fileInput.files[0];

        if (!file) {
            alert("Please upload an image.");
            return;
        }

        const feature = featureSelect.value;
        let formData = new FormData();
        formData.append("image", file);

        // Add extra options based on feature
        if (feature === "passport") {
            formData.append("size", sizeSelect.value);
        } else if (feature === "resize") {
            formData.append("preset", presetSelect.value);
        } else if (feature === "convert") {
            formData.append("format", formatSelect.value);
        }

        // Show loading
        resultBox.innerHTML = `<p>Processing ${feature}...</p>`;

        try {
            const res = await fetch(`/${feature}-ajax`, {
                method: "POST",
                body: formData
            });

            if (!res.ok) {
                const err = await res.json();
                resultBox.innerHTML = `<p style="color:red;">Error: ${err.error}</p>`;
                return;
            }

            // Create download link
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            resultBox.innerHTML = `
                <p>${feature} ready!</p>
                <a href="${url}" download="${feature}.png" class="btn">Download</a>
                <img src="${url}" alt="Result" style="max-width:300px;margin-top:10px;">
            `;
        } catch (error) {
            console.error(error);
            resultBox.innerHTML = `<p style="color:red;">Something went wrong!</p>`;
        }
    });

    // Dynamic display of options based on feature
    featureSelect.addEventListener("change", () => {
        const feature = featureSelect.value;
        document.querySelectorAll(".extra-options").forEach(el => el.style.display = "none");

        if (feature === "passport") {
            document.getElementById("size-options").style.display = "block";
        } else if (feature === "resize") {
            document.getElementById("preset-options").style.display = "block";
        } else if (feature === "convert") {
            document.getElementById("format-options").style.display = "block";
        }
    });
});
