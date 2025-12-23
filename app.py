import os
import uuid
from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image, ImageEnhance
from rembg import remove
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq

load_dotenv()

app = Flask(__name__)
TMP_DIR = "/tmp"

# ------------------ API CONFIG ------------------
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# ------------------ HELPERS ------------------
def save_temp(img):
    path = os.path.join(TMP_DIR, f"{uuid.uuid4()}.png")
    img.save(path)
    return path

# ------------------ ROUTES ------------------
@app.route("/")
def index():
    return render_template("index.html")

# 1. Background Remover
@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    file = request.files["image"]
    img = Image.open(file).convert("RGBA")
    result = remove(img)
    path = save_temp(result)
    return send_file(path, as_attachment=True)

# 2. Passport Photo Maker
@app.route("/passport", methods=["POST"])
def passport():
    size = request.form.get("size")
    file = request.files["image"]

    sizes = {
        "US": (600, 600),
        "PK": (413, 531),
        "EU": (413, 531)
    }

    img = Image.open(file).convert("RGBA")
    img = remove(img)

    canvas = Image.new("RGB", sizes[size], "white")
    w, h = canvas.size

    scale = int(h * 0.85)
    ratio = scale / img.height
    img = img.resize((int(img.width * ratio), scale))

    x = (w - img.width) // 2
    y = (h - img.height) // 2
    canvas.paste(img, (x, y), img)

    path = save_temp(canvas)
    return send_file(path, as_attachment=True)

# 3. Social Media Resizer
@app.route("/resize", methods=["POST"])
def resize():
    preset = request.form.get("preset")
    file = request.files["image"]

    sizes = {
        "insta_post": (1080, 1080),
        "insta_story": (1080, 1920),
        "yt_thumb": (1280, 720),
        "linkedin": (1584, 396)
    }

    img = Image.open(file).convert("RGB")
    img = img.resize(sizes[preset])
    path = save_temp(img)
    return send_file(path, as_attachment=True)

# 4. Image Format Converter
@app.route("/convert", methods=["POST"])
def convert():
    fmt = request.form.get("format")
    file = request.files["image"]

    img = Image.open(file).convert("RGB")
    path = os.path.join(TMP_DIR, f"{uuid.uuid4()}.{fmt}")
    img.save(path, fmt.upper())
    return send_file(path, as_attachment=True)

# 5. AI Image Enhancer (Sharpen)
@app.route("/enhance", methods=["POST"])
def enhance():
    file = request.files["image"]
    img = Image.open(file).convert("RGB")

    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)

    path = save_temp(img)
    return send_file(path, as_attachment=True)

# ------------------ AI FEATURES ------------------
@app.route("/ai-describe", methods=["POST"])
def ai_describe():
    provider = request.form.get("provider")
    text = request.form.get("text")

    if provider == "gemini" and GEMINI_KEY:
        model = genai.GenerativeModel("gemini-pro")
        res = model.generate_content(text)
        return jsonify({"result": res.text})

    if provider == "groq" and groq_client:
        res = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": text}]
        )
        return jsonify({"result": res.choices[0].message.content})

    return jsonify({"result": "API not configured"})

# ------------------ MAIN ------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
