from flask import Blueprint, request, send_file
from utils.image_io import read_image
import io
from PIL import Image

resize_bp = Blueprint('resize', __name__)

@resize_bp.route("", methods=["POST"])
def resize_image():
    image_file = request.files.get("image")
    width = int(request.form.get("width", 0))
    height = int(request.form.get("height", 0))

    if not image_file or not width or not height:
        return "Invalid request", 400

    img = Image.open(image_file)
    img = img.resize((width, height))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")
