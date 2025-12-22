# File: app.py
from flask import Flask, request, send_file, render_template
import os
from PIL import Image, ImageDraw, ImageFont
import tempfile
from rembg import remove
import io
import numpy as np

# Import API clients (assuming you installed google-generativeai and groq)
import google.generativeai as genai
import groq

# Initialize Flask app
app = Flask(__name__)

# Load API keys from Render environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --------- Routes ---------

@app.route("/")
def home():
    return render_template("index.html")

# ---------- 1. Image Translator ----------
@app.route("/translate", methods=["POST"])
def translate_image():
    if "image" not in request.files:
        return "No image uploaded", 400

    image_file = request.files["image"]
    target_language = request.form.get("language", "en")

    img_bytes = image_file.read()

    # Call Gemini API (pseudo code, replace with your exact call)
    translated_text = genai.translate_image(img_bytes, target_language=target_language, api_key=GEMINI_API_KEY)

    return {"translated_text": translated_text}

# ---------- 2. Passport Photo Maker ----------
@app.route("/passport", methods=["POST"])
def passport_photo():
    if "image" not in request.files:
        return "No image uploaded", 400

    image_file = request.files["image"]
    img = Image.open(image_file)

    # Remove background
    output = remove(np.array(img))
    img_no_bg = Image.fromarray(output)

    # Resize & center
    canvas = Image.new("RGBA", (350, 450), (255, 255, 255, 255))  # EU/PK size
    img_no_bg.thumbnail((int(canvas.width * 0.85), int(canvas.height * 0.85)))
    canvas.paste(img_no_bg, ((canvas.width - img_no_bg.width)//2, (canvas.height - img_no_bg.height)//2), img_no_bg)

    # Save to temp
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    canvas.save(tmp_file.name)
    return send_file(tmp_file.name, as_attachment=True, download_name="passport.png")

# ---------- 3. Meme Generator ----------
@app.route("/meme", methods=["POST"])
def meme_generator():
    if "image" not in request.files:
        return "No image uploaded", 400

    image_file = request.files["image"]
    top_text = request.form.get("top", "")
    bottom_text = request.form.get("bottom", "")

    img = Image.open(image_file)
    draw = ImageDraw.Draw(img)
    font_size = max(20, img.width // 15)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Draw top text
    draw.text((img.width//2, 10), top_text, fill="white", stroke_width=2, stroke_fill="black", anchor="ms", font=font)
    # Draw bottom text
    draw.text((img.width//2, img.height-10), bottom_text, fill="white", stroke_width=2, stroke_fill="black", anchor="ms", font=font)

    # Save temp
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tmp_file.name)
    return send_file(tmp_file.name, as_attachment=True, download_name="meme.png")

# ---------- 4. Simple Text API Example (Groq) ----------
@app.route("/text-analyze", methods=["POST"])
def text_analyze():
    text = request.form.get("text", "")
    if not text:
        return "No text provided", 400

    # Example pseudo call
    result = groq.process_text(text, api_key=GROQ_API_KEY)
    return {"result": result}

# ---------- Run ----------
if __name__ == "__main__":
    # Only for local testing; Render uses gunicorn
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
