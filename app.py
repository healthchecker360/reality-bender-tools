import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from PIL import Image
import numpy as np
import cv2
from rembg import remove
import google.generativeai as genai
from groq import Groq

# ----------------------------
# Load Environment Variables
# ----------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ----------------------------
# App Configuration
# ----------------------------
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "tmp"
os.makedirs("tmp", exist_ok=True)

# ----------------------------
# AI Clients
# ----------------------------
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

groq_client = Groq(api_key=GROQ_API_KEY)

# ----------------------------
# Routes
# ----------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ----------------------------
# 1️⃣ Image Text Translator
# ----------------------------
@app.route("/translate-image", methods=["POST"])
def translate_image():
    image = request.files["image"]
    target_language = request.form.get("language")

    img = Image.open(image)

    prompt = f"""
    Extract all text from this image.
    Automatically detect the source language.
    Translate it into {target_language}.
    Return ONLY the translated text.
    """

    response = gemini_model.generate_content([prompt, img])
    return jsonify({"result": response.text})


# ----------------------------
# 2️⃣ Passport Photo Maker
# ----------------------------
@app.route("/passport-photo", methods=["POST"])
def passport_photo():
    image = request.files["image"]
    country = request.form.get("country")

    img = Image.open(image).convert("RGBA")
    no_bg = remove(img)

    if country == "US":
        width, height = 600, 600
    else:
        width, height = 413, 531  # 35x45mm ratio

    canvas = Image.new("RGBA", (width, height), (255, 255, 255, 255))

    person = no_bg.resize((int(width * 0.6), int(height * 0.85)))
    x = (width - person.width) // 2
    y = height - person.height

    canvas.paste(person, (x, y), person)

    output_path = "tmp/passport.png"
    canvas.convert("RGB").save(output_path)

    return jsonify({"status": "success", "file": output_path})


# ----------------------------
# 3️⃣ Meme Generator
# ----------------------------
@app.route("/generate-meme", methods=["POST"])
def generate_meme():
    image = request.files["image"]
    top_text = request.form.get("top")
    bottom_text = request.form.get("bottom")

    img = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, top_text.upper(), (20, 60), font, 1.5, (0, 0, 0), 6)
    cv2.putText(img, top_text.upper(), (20, 60), font, 1.5, (255, 255, 255), 2)

    h = img.shape[0]
    cv2.putText(img, bottom_text.upper(), (20, h - 30), font, 1.5, (0, 0, 0), 6)
    cv2.putText(img, bottom_text.upper(), (20, h - 30), font, 1.5, (255, 255, 255), 2)

    output_path = "tmp/meme.jpg"
    cv2.imwrite(output_path, img)

    return jsonify({"status": "success", "file": output_path})


# ----------------------------
# Run App
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
