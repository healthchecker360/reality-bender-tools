import os
import uuid
import logging
from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image, ImageEnhance
from rembg import remove
import google.generativeai as genai
from groq import Groq
from flask_cors import CORS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Use /tmp for temporary files (Render compatible)
TMP_DIR = "/tmp"
os.makedirs(TMP_DIR, exist_ok=True)

# ------------------ API CONFIG ------------------
# Get API keys from environment variables (set in Render dashboard)
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
GROQ_KEY = os.environ.get("GROQ_API_KEY")

logger.info(f"Gemini API configured: {bool(GEMINI_KEY)}")
logger.info(f"Groq API configured: {bool(GROQ_KEY)}")

# Configure Gemini
if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        logger.info("Gemini API initialized successfully")
    except Exception as e:
        logger.error(f"Gemini API configuration error: {e}")

# Configure Groq
groq_client = None
if GROQ_KEY:
    try:
        groq_client = Groq(api_key=GROQ_KEY)
        logger.info("Groq API initialized successfully")
    except Exception as e:
        logger.error(f"Groq API configuration error: {e}")

# ------------------ HELPERS ------------------
def save_temp(img, fmt="PNG"):
    """Save image to temp directory"""
    try:
        path = os.path.join(TMP_DIR, f"{uuid.uuid4()}.{fmt.lower()}")
        
        # Handle different formats
        if fmt.upper() in ["JPG", "JPEG"]:
            # Convert RGBA to RGB for JPEG
            if img.mode == "RGBA":
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            img.save(path, "JPEG", quality=95)
        else:
            img.save(path, fmt.upper())
        
        return path
    except Exception as e:
        logger.error(f"Error saving temp file: {e}")
        raise

def validate_image(file):
    """Validate uploaded file is an image"""
    if not file:
        return False, "No file uploaded"
    
    if file.filename == '':
        return False, "No file selected"
    
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp'}
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    
    if ext not in allowed_extensions:
        return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
    
    return True, "Valid"

# ------------------ ROUTES ------------------
@app.route("/")
def index():
    """Home page"""
    return render_template("index.html")

@app.route("/health")
def health():
    """Health check endpoint for Render"""
    return jsonify({
        "status": "healthy",
        "gemini_configured": bool(GEMINI_KEY),
        "groq_configured": bool(GROQ_KEY)
    }), 200

# Background Remover
@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    """Remove background from image"""
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
        
        file = request.files["image"]
        is_valid, msg = validate_image(file)
        if not is_valid:
            return jsonify({"error": msg}), 400
        
        logger.info("Processing background removal...")
        
        img = Image.open(file).convert("RGBA")
        result = remove(img)
        path = save_temp(result, "PNG")
        
        logger.info("Background removed successfully")
        return send_file(
            path, 
            mimetype="image/png",
            as_attachment=True, 
            download_name="no-background.png"
        )
    except Exception as e:
        logger.error(f"Background removal error: {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

# Passport Photo Maker
@app.route("/passport", methods=["POST"])
def passport():
    """Create passport-sized photo"""
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
        
        file = request.files["image"]
        is_valid, msg = validate_image(file)
        if not is_valid:
            return jsonify({"error": msg}), 400
        
        size = request.form.get("size", "US")
        logger.info(f"Creating passport photo: {size}")
        
        # Size specifications in pixels
        sizes = {
            "US": (600, 600),      # 2x2 inches at 300 DPI
            "PK": (413, 531),      # 35x45mm at 300 DPI
            "EU": (413, 531)       # 35x45mm at 300 DPI
        }
        
        if size not in sizes:
            return jsonify({"error": "Invalid size option"}), 400
        
        # Load and remove background
        img = Image.open(file).convert("RGBA")
        img = remove(img)

        # Create white canvas
        canvas = Image.new("RGB", sizes[size], (255, 255, 255))
        w, h = canvas.size

        # Resize image to fit (85% of height)
        target_height = int(h * 0.85)
        ratio = target_height / img.height
        new_width = int(img.width * ratio)
        img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)

        # Center the image
        x = (w - img.width) // 2
        y = (h - img.height) // 2
        
        # Paste with alpha channel
        canvas.paste(img, (x, y), img)

        path = save_temp(canvas, "PNG")
        logger.info("Passport photo created successfully")
        
        return send_file(
            path,
            mimetype="image/png",
            as_attachment=True,
            download_name=f"passport-{size}.png"
        )
    except Exception as e:
        logger.error(f"Passport photo error: {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

# Social Media Resizer
@app.route("/resize", methods=["POST"])
def resize():
    """Resize image for social media"""
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
        
        file = request.files["image"]
        is_valid, msg = validate_image(file)
        if not is_valid:
            return jsonify({"error": msg}), 400
        
        preset = request.form.get("preset", "insta_post")
        logger.info(f"Resizing image: {preset}")
        
        sizes = {
            "insta_post": (1080, 1080),
            "insta_story": (1080, 1920),
            "yt_thumb": (1280, 720),
            "linkedin": (1584, 396)
        }
        
        if preset not in sizes:
            return jsonify({"error": "Invalid preset"}), 400

        img = Image.open(file).convert("RGB")
        
        # Resize with maintaining aspect ratio (crop to fit)
        target_size = sizes[preset]
        img.thumbnail((target_size[0] * 2, target_size[1] * 2), Image.Resampling.LANCZOS)
        
        # Create canvas and center image
        canvas = Image.new("RGB", target_size, (255, 255, 255))
        offset = ((target_size[0] - img.width) // 2, (target_size[1] - img.height) // 2)
        canvas.paste(img, offset)
        
        path = save_temp(canvas, "PNG")
        logger.info("Image resized successfully")
        
        return send_file(
            path,
            mimetype="image/png",
            as_attachment=True,
            download_name=f"{preset}.png"
        )
    except Exception as e:
        logger.error(f"Resize error: {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

# Image Format Converter
@app.route("/convert", methods=["POST"])
def convert():
    """Convert image format"""
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
        
        file = request.files["image"]
        is_valid, msg = validate_image(file)
        if not is_valid:
            return jsonify({"error": msg}), 400
        
        fmt = request.form.get("format", "PNG").upper()
        logger.info(f"Converting image to {fmt}")
        
        allowed_formats = ["PNG", "JPG", "JPEG", "WEBP"]
        if fmt not in allowed_formats:
            return jsonify({"error": "Invalid format"}), 400

        img = Image.open(file)
        
        # Handle transparency for formats that don't support it
        if fmt in ["JPG", "JPEG"] and img.mode in ["RGBA", "LA", "P"]:
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            if img.mode in ["RGBA", "LA"]:
                background.paste(img, mask=img.split()[-1])
            img = background
        
        path = save_temp(img, fmt)
        logger.info("Image converted successfully")
        
        mime_types = {
            "PNG": "image/png",
            "JPG": "image/jpeg",
            "JPEG": "image/jpeg",
            "WEBP": "image/webp"
        }
        
        return send_file(
            path,
            mimetype=mime_types[fmt],
            as_attachment=True,
            download_name=f"converted.{fmt.lower()}"
        )
    except Exception as e:
        logger.error(f"Conversion error: {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

# AI Image Enhancer
@app.route("/enhance", methods=["POST"])
def enhance():
    """Enhance image quality"""
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
        
        file = request.files["image"]
        is_valid, msg = validate_image(file)
        if not is_valid:
            return jsonify({"error": msg}), 400
        
        logger.info("Enhancing image...")
        
        img = Image.open(file).convert("RGB")

        # Apply enhancements
        # 1. Sharpness
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)
        
        # 2. Contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        # 3. Color
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.1)

        path = save_temp(img, "PNG")
        logger.info("Image enhanced successfully")
        
        return send_file(
            path,
            mimetype="image/png",
            as_attachment=True,
            download_name="enhanced.png"
        )
    except Exception as e:
        logger.error(f"Enhancement error: {e}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

# AI Description Generator
@app.route("/ai-describe", methods=["POST"])
def ai_describe():
    """Generate AI text response"""
    try:
        provider = request.form.get("provider")
        text = request.form.get("text", "").strip()
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        logger.info(f"AI request: {provider}")

        if provider == "gemini":
            if not GEMINI_KEY:
                return jsonify({"error": "Gemini API not configured. Please add GEMINI_API_KEY to environment variables."}), 400
            
            try:
                model = genai.GenerativeModel("gemini-pro")
                response = model.generate_content(text)
                return jsonify({"result": response.text})
            except Exception as e:
                logger.error(f"Gemini error: {e}")
                return jsonify({"error": f"Gemini API error: {str(e)}"}), 500

        elif provider == "groq":
            if not groq_client:
                return jsonify({"error": "Groq API not configured. Please add GROQ_API_KEY to environment variables."}), 400
            
            try:
                response = groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": text}],
                    temperature=0.7,
                    max_tokens=1024
                )
                return jsonify({"result": response.choices[0].message.content})
            except Exception as e:
                logger.error(f"Groq error: {e}")
                return jsonify({"error": f"Groq API error: {str(e)}"}), 500
        
        return jsonify({"error": "Invalid provider selected"}), 400

    except Exception as e:
        logger.error(f"AI describe error: {e}")
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

# ------------------ ERROR HANDLERS ------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return jsonify({"error": "Internal server error"}), 500

# ------------------ MAIN ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)import os
import uuid
from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image, ImageEnhance
from rembg import remove
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq

load_dotenv()

app = Flask(__name__)
TMP_DIR = "/tmp"  # Runtime temp folder

# ------------------ API CONFIG ------------------
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

# ------------------ HELPERS ------------------
def save_temp(img, fmt="PNG"):
    path = os.path.join(TMP_DIR, f"{uuid.uuid4()}.{fmt.lower()}")
    img.save(path, fmt.upper())
    return path

# ------------------ ROUTES ------------------
@app.route("/")
def index():
    return render_template("index.html")

# Background Remover
@app.route("/remove-bg", methods=["POST"])
def remove_bg():
    file = request.files["image"]
    img = Image.open(file).convert("RGBA")
    result = remove(img)
    path = save_temp(result)
    return send_file(path, as_attachment=True)

# Passport Photo Maker
@app.route("/passport", methods=["POST"])
def passport():
    size = request.form.get("size")
    file = request.files["image"]

    sizes = {"US": (600, 600), "PK": (413, 531), "EU": (413, 531)}
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

# Social Media Resizer
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

# Image Format Converter
@app.route("/convert", methods=["POST"])
def convert():
    fmt = request.form.get("format")
    file = request.files["image"]

    img = Image.open(file).convert("RGB")
    path = os.path.join(TMP_DIR, f"{uuid.uuid4()}.{fmt.lower()}")
    img.save(path, fmt.upper())
    return send_file(path, as_attachment=True)

# AI Image Enhancer
@app.route("/enhance", methods=["POST"])
def enhance():
    file = request.files["image"]
    img = Image.open(file).convert("RGB")

    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)

    path = save_temp(img)
    return send_file(path, as_attachment=True)

# AI Description Generator
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
