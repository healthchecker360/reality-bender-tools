// ---------------- Global ----------------
document.addEventListener("DOMContentLoaded", () => {
    console.log("Reality Bender Web Loaded");

    // Scroll to top button
    const scrollBtn = document.createElement("button");
    scrollBtn.innerText = "↑";
    scrollBtn.id = "scrollTopBtn";
    scrollBtn.style.position = "fixed";
    scrollBtn.style.bottom = "20px";
    scrollBtn.style.right = "20px";
    scrollBtn.style.padding = "10px 15px";
    scrollBtn.style.border = "none";
    scrollBtn.style.borderRadius = "50%";
    scrollBtn.style.background = "#0d6efd";
    scrollBtn.style.color = "#fff";
    scrollBtn.style.cursor = "pointer";
    scrollBtn.style.display = "none";
    document.body.appendChild(scrollBtn);

    scrollBtn.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    window.addEventListener("scroll", () => {
        scrollBtn.style.display = window.scrollY > 300 ? "block" : "none";
    });

    // Image preview for upload forms
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (!file) return;

            let preview = input.parentElement.querySelector(".preview-img");
            if (!preview) {
                preview = document.createElement("img");
                preview.className = "preview-img";
                preview.style.maxWidth = "200px";
                preview.style.marginTop = "10px";
                input.parentElement.appendChild(preview);
            }
            preview.src = URL.createObjectURL(file);
        });
    });

    // Form submission loader
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("submit", () => {
            const btn = form.querySelector('button, input[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.innerText = "Processing...";
            }
        });
    });
});
