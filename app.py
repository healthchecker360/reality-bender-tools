from flask import Flask, render_template, request, send_file
from PIL import Image, ImageOps
import os, uuid

app = Flask(__name__)
TMP = "/tmp"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        img = request.files["image"]
        tool = request.form["tool"]
        fmt = request.form["format"]

        uid = str(uuid.uuid4())
        in_path = f"{TMP}/{uid}_in"
        out_path = f"{TMP}/{uid}_out.{fmt}"

        image = Image.open(img).convert("RGB")
        image.save(in_path)

        sizes = {
            "passport_us": (600, 600),
            "passport_pk": (413, 531),
            "insta_post": (1080, 1080),
            "insta_story": (1080, 1920),
            "yt_thumb": (1280, 720)
        }

        image = ImageOps.fit(image, sizes[tool], centering=(0.5, 0.5))
        image.save(out_path, optimize=True, quality=85)

        return send_file(out_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run()
