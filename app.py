import os
import uuid
import logging
from flask import Flask, render_template, request, send_file, jsonify
from flask_cors import CORS
from PIL import Image, ImageEnhance
from rembg import remove
import google.generativeai as genai
from groq import Groq

# ------------------ LOGGING ------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------------------ APP ------------------
app = Flask(__name__)
CORS(app)

TMP_DIR = "/tmp"
os.makedirs(TMP_DIR, exist_ok=True)

# ------------------ API CONFIG ------------------
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# ------------------ HELPERS ------------------
def save_temp(img, fmt="PNG"):
    path = os.path.join(TMP_DIR, f"{uuid.uuid4()}.{fmt.lower()}")
    if fmt in ["JPG", "JPEG"] and img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    img.save(path, fmt)
    return path

def validate_image(file):
    if not file or file.filename == "":
        return False
    ext = file.filename.rsplit(".", 1)[-1].lower()
    return ext in {"png", "jpg", "jpeg", "webp", "bmp"}

# ------------------ ROUTES ------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    file = request.files.get("image")
    if not validate_image(file):
        return jsonify({"error": "Invalid image"}), 400

    img = Image.open(file).convert("RGBA")
    result = remove(img)
    path = save_temp(result, "PNG")
    return send_file(path, mimetype="image/png", as_attachment=True)

@app.route("/passport", methods=["POST"])
def passport():
    file = request.files.get("image")
    size = request.form.get("size", "US")

    sizes = {"US": (600, 600), "PK": (413, 531), "EU": (413, 531)}
    if size not in sizes or not validate_image(file):
        return jsonify({"error": "Invalid request"}), 400

    img = remove(Image.open(file).convert("RGBA"))
    canvas = Image.new("RGB", sizes[size], (255, 255, 255))

    target_h = int(canvas.height * 0.85)
    ratio = target_h / img.height
    img = img.resize((int(img.width * ratio), target_h), Image.Resampling.LANCZOS)

    x = (canvas.width - img.width) // 2
    y = (canvas.height - img.height) // 2
    canvas.paste(img, (x, y), img)

    path = save_temp(canvas, "PNG")
    return send_file(path, mimetype="image/png", as_attachment=True)

@app.route("/resize", methods=["POST"])
def resize():
    file = request.files.get("image")
    preset = request.form.get("preset", "insta_post")

    sizes = {
        "insta_post": (1080, 1080),
        "insta_story": (1080, 1920),
        "yt_thumb": (1280, 720),
        "linkedin": (1584, 396),
    }

    if preset not in sizes or not validate_image(file):
        return jsonify({"error": "Invalid request"}), 400

    img = Image.open(file).convert("RGB")
    img.thumbnail(sizes[preset], Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", sizes[preset], (255, 255, 255))
    canvas.paste(img, ((canvas.width - img.width)//2, (canvas.height - img.height)//2))

    path = save_temp(canvas, "PNG")
    return send_file(path, mimetype="image/png", as_attachment=True)

@app.route("/enhance", methods=["POST"])
def enhance():
    file = request.files.get("image")
    if not validate_image(file):
        return jsonify({"error": "Invalid image"}), 400

    img = Image.open(file).convert("RGB")
    img = ImageEnhance.Sharpness(img).enhance(1.5)
    img = ImageEnhance.Contrast(img).enhance(1.2)

    path = save_temp(img, "PNG")
    return send_file(path, mimetype="image/png", as_attachment=True)

@app.route("/ai-describe", methods=["POST"])
def ai_describe():
    provider = request.form.get("provider")
    text = request.form.get("text", "").strip()

    if not text:
        return jsonify({"error": "No text"}), 400

    if provider == "gemini" and GEMINI_KEY:
        model = genai.GenerativeModel("gemini-pro")
        res = model.generate_content(text)
        return jsonify({"result": res.text})

    if provider == "groq" and groq_client:
        res = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": text}],
        )
        return jsonify({"result": res.choices[0].message.content})

    return jsonify({"error": "API not configured"}), 400

# ------------------ MAIN ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
