import os
import io
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont, ImageOps
from rembg import remove
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = '/tmp' if os.environ.get('RENDER') else 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Get API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configure APIs
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None

# Platform sizes
PLATFORM_SIZES = {
    'instagram_story': (1080, 1920),
    'instagram_post': (1080, 1080),
    'facebook_post': (1200, 630),
    'linkedin_banner': (1584, 396),
    'youtube_thumbnail': (1280, 720),
    'twitter_post': (1200, 675)
}

PASSPORT_SIZES = {
    'us': (600, 600),
    'pk_uk': (413, 531),
    'eu': (413, 531),
    'china': (390, 567)
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_file(filepath):
    """Safely remove temporary files"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error cleaning up file: {e}")

@app.route('/')
def index():
    return render_template('index.html')

# ========== AI IMAGE TRANSLATOR (GEMINI) ==========
@app.route('/translate', methods=['POST'])
def translate_image():
    if not GEMINI_API_KEY:
        return jsonify({'error': 'Gemini API Key not configured'}), 500
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Use PNG, JPG, JPEG, or WEBP'}), 400
    
    target_lang = request.form.get('language', 'English')
    
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)
    
    try:
        # Upload to Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        uploaded_file = genai.upload_file(path)
        
        # Create prompt for translation
        prompt = f"""Extract all visible text from this image and translate it to {target_lang}.
        
Rules:
- Extract ALL text you see
- Translate it accurately to {target_lang}
- Return ONLY the translated text
- No explanations or additional commentary
- Preserve formatting if possible"""
        
        result = model.generate_content([uploaded_file, prompt])
        
        cleanup_file(path)
        return jsonify({'success': True, 'text': result.text})
        
    except Exception as e:
        cleanup_file(path)
        return jsonify({'error': f'Translation failed: {str(e)}'}), 500

# ========== BACKGROUND REMOVER ==========
@app.route('/remove-bg', methods=['POST'])
def remove_background():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        input_img = Image.open(file.stream).convert("RGBA")
        output_img = remove(input_img)
        
        output = io.BytesIO()
        output_img.save(output, 'PNG')
        output.seek(0)
        
        return send_file(
            output,
            mimetype='image/png',
            as_attachment=True,
            download_name='no_background.png'
        )
    except Exception as e:
        return jsonify({'error': f'Background removal failed: {str(e)}'}), 500

# ========== PASSPORT PHOTO MAKER ==========
@app.route('/passport', methods=['POST'])
def passport_photo():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    country = request.form.get('country', 'us')
    
    try:
        input_img = Image.open(file.stream).convert("RGBA")
        
        # Remove background
        no_bg_img = remove(input_img)
        
        # Create white canvas with target size
        target_size = PASSPORT_SIZES.get(country, (600, 600))
        final_img = Image.new("RGB", target_size, "white")
        
        # Resize while maintaining aspect ratio (85% of canvas)
        no_bg_img.thumbnail(
            (int(target_size[0] * 0.85), int(target_size[1] * 0.85)),
            Image.Resampling.LANCZOS
        )
        
        # Center the image (bottom aligned for passport style)
        x = (target_size[0] - no_bg_img.width) // 2
        y = target_size[1] - no_bg_img.height
        final_img.paste(no_bg_img, (x, y), no_bg_img)
        
        output = io.BytesIO()
        final_img.save(output, 'JPEG', quality=95)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name=f'passport_{country}.jpg'
        )
    except Exception as e:
        return jsonify({'error': f'Passport photo generation failed: {str(e)}'}), 500

# ========== MEME GENERATOR ==========
@app.route('/meme', methods=['POST'])
def meme_generator():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    top_text = request.form.get('top_text', '').upper()
    bottom_text = request.form.get('bottom_text', '').upper()
    
    try:
        img = Image.open(file.stream).convert("RGB")
        draw = ImageDraw.Draw(img)
        
        # Calculate font size based on image height
        font_size = int(img.height * 0.08)
        
        # Try to load a better font, fallback to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
                font_size = 40
        
        def draw_text_with_outline(text, position):
            if not text:
                return
            
            x, y = position
            
            # Calculate text width using textbbox
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            
            # Center the text
            x = (img.width - text_width) // 2
            
            # Draw black outline
            outline_range = max(2, font_size // 15)
            for adj_x in range(-outline_range, outline_range + 1):
                for adj_y in range(-outline_range, outline_range + 1):
                    draw.text((x + adj_x, y + adj_y), text, font=font, fill='black')
            
            # Draw white text
            draw.text((x, y), text, font=font, fill='white')
        
        # Draw top and bottom text
        margin = int(img.height * 0.02)
        draw_text_with_outline(top_text, (0, margin))
        draw_text_with_outline(bottom_text, (0, img.height - font_size - margin))
        
        output = io.BytesIO()
        img.save(output, 'JPEG', quality=90)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='meme.jpg'
        )
    except Exception as e:
        return jsonify({'error': f'Meme generation failed: {str(e)}'}), 500

# ========== SOCIAL MEDIA RESIZER ==========
@app.route('/resize', methods=['POST'])
def resize_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    platform = request.form.get('platform', 'instagram_post')
    
    try:
        img = Image.open(file.stream).convert("RGB")
        target_size = PLATFORM_SIZES.get(platform, (1080, 1080))
        
        # Crop and resize to fit exactly
        final_img = ImageOps.fit(
            img,
            target_size,
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5)
        )
        
        output = io.BytesIO()
        final_img.save(output, 'JPEG', quality=90)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name=f'{platform}.jpg'
        )
    except Exception as e:
        return jsonify({'error': f'Image resize failed: {str(e)}'}), 500

# ========== TEXT ANALYSIS WITH GROQ (BONUS FEATURE) ==========
@app.route('/text-analyze', methods=['POST'])
def text_analyze():
    if not groq_client:
        return jsonify({'error': 'Groq API Key not configured'}), 500
    
    text = request.form.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # Use Groq for text analysis
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that analyzes text and provides insights."
                },
                {
                    "role": "user",
                    "content": f"Analyze this text and provide key insights: {text}"
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=500
        )
        
        result = chat_completion.choices[0].message.content
        return jsonify({'success': True, 'analysis': result})
        
    except Exception as e:
        return jsonify({'error': f'Text analysis failed: {str(e)}'}), 500

# ========== HEALTH CHECK ==========
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'gemini_configured': bool(GEMINI_API_KEY),
        'groq_configured': bool(GROQ_API_KEY)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
