// Tabs
const tabBtns = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");

tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        tabBtns.forEach(b => b.classList.remove("active"));
        tabContents.forEach(c => c.classList.remove("active"));
        btn.classList.add("active");
        document.getElementById(btn.dataset.tab).classList.add("active");
    });
});

// Placeholder AJAX submissions for All-in-One forms
const forms = ["remove", "passport", "resize", "convert", "enhance"];

forms.forEach(f => {
    const form = document.getElementById(`${f}-form`);
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const resultDiv = document.getElementById(`${f}-result`);
        resultDiv.innerHTML = "<p>Processing...</p>";

        try {
            const res = await fetch(`/${f}-bg`, {  // We'll handle route mapping later
                method: "POST",
                body: formData
            });
            if (!res.ok) throw new Error("Processing failed");
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            resultDiv.innerHTML = `<a href="${url}" download="result.png" class="btn primary-btn">Download Result</a>`;
        } catch (err) {
            resultDiv.innerHTML = `<p style="color:red;">${err.message}</p>`;
        }
    });
});
