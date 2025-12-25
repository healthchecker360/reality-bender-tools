from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from flask_cors import CORS
from PIL import Image, ImageEnhance
from rembg import remove
import io
import os

app = Flask(__name__)
CORS(app)

# -------------------------------
# App Config
# -------------------------------
app.secret_key = os.getenv("SECRET_KEY", "reality-bender-secret")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB upload limit

# -------------------------------
# Utility Functions
# -------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "png", "jpg", "jpeg", "webp"
    }

def image_to_bytes(img, format="PNG"):
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=format)
    img_bytes.seek(0)
    return img_bytes

# -------------------------------
# Routes – Pages
# -------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/remove-background", methods=["GET", "POST"])
def remove_bg():
    if request.method == "POST":
        file = request.files.get("image")
        if not file or not allowed_file(file.filename):
            flash("Invalid image file")
            return redirect(request.url)

        input_img = Image.open(file.stream)
        output_img = remove(input_img)
        return send_file(
            image_to_bytes(output_img),
            mimetype="image/png",
            as_attachment=True,
            download_name="background_removed.png"
        )

    return render_template("remove_bg.html")

@app.route("/passport-photo", methods=["GET", "POST"])
def passport():
    if request.method == "POST":
        file = request.files.get("image")
        if not file:
            flash("No image uploaded")
            return redirect(request.url)

        img = Image.open(file.stream)
        img = img.resize((600, 600))  # Standard passport ratio
        return send_file(
            image_to_bytes(img),
            mimetype="image/png",
            as_attachment=True,
            download_name="passport_photo.png"
        )

    return render_template("passport.html")

@app.route("/resize", methods=["GET", "POST"])
def resize():
    if request.method == "POST":
        file = request.files.get("image")
        width = int(request.form.get("width"))
        height = int(request.form.get("height"))

        img = Image.open(file.stream)
        resized = img.resize((width, height))

        return send_file(
            image_to_bytes(resized),
            mimetype="image/png",
            as_attachment=True,
            download_name="resized_image.png"
        )

    return render_template("resize.html")

@app.route("/convert", methods=["GET", "POST"])
def convert():
    if request.method == "POST":
        file = request.files.get("image")
        format = request.form.get("format", "PNG").upper()

        img = Image.open(file.stream).convert("RGB")
        return send_file(
            image_to_bytes(img, format=format),
            mimetype=f"image/{format.lower()}",
            as_attachment=True,
            download_name=f"converted_image.{format.lower()}"
        )

    return render_template("convert.html")

@app.route("/enhance", methods=["GET", "POST"])
def enhance():
    if request.method == "POST":
        file = request.files.get("image")
        img = Image.open(file.stream)

        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.8)

        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)

        return send_file(
            image_to_bytes(img),
            mimetype="image/png",
            as_attachment=True,
            download_name="enhanced_image.png"
        )

    return render_template("enhance.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/security")
def security():
    return render_template("security.html")

# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
