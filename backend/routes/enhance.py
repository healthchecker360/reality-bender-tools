from flask import Blueprint, request, send_file
from PIL import Image, ImageEnhance
import io

enhance_bp = Blueprint('enhance', __name__)

@enhance_bp.route("", methods=["POST"])
def enhance_image():
    image_file = request.files.get("image")
    if not image_file:
        return "No image provided", 400

    img = Image.open(image_file).convert("RGB")

    # Sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)

    # Contrast
    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(1.5)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")
