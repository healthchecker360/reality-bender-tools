from flask import Flask, render_template, request, send_file
from PIL import Image, ImageOps
import uuid, os, base64
from io import BytesIO

app = Flask(__name__)
TMP = "/tmp"

@app.route("/", methods=["GET", "POST"])
def index():
    preview_image = None
    download_id = None

    if request.method == "POST":
        image_file = request.files["image"]
        tool = request.form["tool"]
        fmt = request.form["format"]

        uid = str(uuid.uuid4())
        out_path = f"{TMP}/{uid}.{fmt}"

        image = Image.open(image_file).convert("RGB")

        sizes = {
            "passport_us": (600, 600),
            "passport_pk": (413, 531),
            "insta_post": (1080, 1080),
            "insta_story": (1080, 1920),
            "yt_thumb": (1280, 720)
        }

        image = ImageOps.fit(image, sizes[tool], centering=(0.5, 0.5))
        image.save(out_path, optimize=True, quality=85)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        preview_image = base64.b64encode(buffer.getvalue()).decode()
        download_id = uid + "." + fmt

    return render_template(
        "index.html",
        preview_image=preview_image,
        download_id=download_id
    )

@app.route("/download/<filename>")
def download(filename):
    path = f"{TMP}/{filename}"
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
