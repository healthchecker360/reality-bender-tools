from flask import Blueprint, request, send_file
from rembg import remove
import io

bg_bp = Blueprint('bg_remove', __name__)

@bg_bp.route("", methods=["POST"])
def remove_bg():
    image_file = request.files.get("image")
    if not image_file:
        return "No image provided", 400

    input_bytes = image_file.read()
    output_bytes = remove(input_bytes)

    return send_file(io.BytesIO(output_bytes), mimetype="image/png")
