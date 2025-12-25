import os
import uuid
from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image, ImageEnhance
from rembg import remove
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Temp directory (Render safe)
TMP_DIR = "/tmp"
os.makedirs(TMP_DIR, exist_ok=True)

# ---------------- HELPERS ----------------
def save_temp(img, fmt="PNG"):
    path = os.path.join(TMP_DIR, f"{uuid.uuid4()}.{fmt.lower()}")

    if fmt.upper() in ["JPG", "JPEG"] and img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg

    img.save(path, fmt.upper())
    return path

def validate_image(file):
    if not file or file.filename == "":
        return False, "No image uploaded"
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ["png", "jpg", "jpeg", "webp", "bmp"]:
        return False, "Unsupported file type"
    return True, "OK"

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/remove-bg", methods=["GET", "POST"])
def remove_bg():
    if request.method == "POST":
        file = request.files.get("image")
        valid, msg = validate_image(file)
        if not valid:
            return jsonify({"error": msg}), 400

        img = Image.open(file).convert("RGBA")
        result = remove(img)
        path = save_temp(result)
        return send_file(path, as_attachment=True, download_name="no-background.png")

    return render_template("remove_bg.html")

@app.route("/passport", methods=["GET", "POST"])
def passport():
    sizes = {"US": (600,600), "PK": (413,531), "EU": (413,531)}

    if request.method == "POST":
        file = request.files.get("image")
        size = request.form.get("size", "US")

        img = Image.open(file).convert("RGBA")
        img = remove(img)

        canvas = Image.new("RGB", sizes[size], "white")
        w, h = canvas.size
        ratio = int(h * 0.85) / img.height
        img = img.resize((int(img.width * ratio), int(h * 0.85)))

        canvas.paste(img, ((w-img.width)//2, (h-img.height)//2), img)
        path = save_temp(canvas)

        return send_file(path, as_attachment=True, download_name="passport.png")

    return render_template("passport.html")

@app.route("/resize", methods=["GET", "POST"])
def resize():
    presets = {
        "insta": (1080,1080),
        "story": (1080,1920),
        "youtube": (1280,720),
        "linkedin": (1584,396)
    }

    if request.method == "POST":
        file = request.files.get("image")
        preset = request.form.get("preset")

        img = Image.open(file).convert("RGB")
        img.thumbnail(presets[preset])

        canvas = Image.new("RGB", presets[preset], "white")
        canvas.paste(img, ((canvas.width-img.width)//2, (canvas.height-img.height)//2))

        path = save_temp(canvas)
        return send_file(path, as_attachment=True, download_name="resized.png")

    return render_template("resize.html")

@app.route("/convert", methods=["GET", "POST"])
def convert():
    if request.method == "POST":
        file = request.files.get("image")
        fmt = request.form.get("format", "PNG").upper()
        img = Image.open(file)
        path = save_temp(img, fmt)
        return send_file(path, as_attachment=True, download_name=f"converted.{fmt.lower()}")

    return render_template("convert.html")

@app.route("/enhance", methods=["GET", "POST"])
def enhance():
    if request.method == "POST":
        file = request.files.get("image")
        img = Image.open(file).convert("RGB")

        img = ImageEnhance.Sharpness(img).enhance(1.5)
        img = ImageEnhance.Contrast(img).enhance(1.2)
        img = ImageEnhance.Color(img).enhance(1.1)

        path = save_temp(img)
        return send_file(path, as_attachment=True, download_name="enhanced.png")

    return render_template("enhance.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/security")
def security():
    return render_template("security.html")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
