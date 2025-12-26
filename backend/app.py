from flask import Flask
from routes.resize import resize_bp
from routes.bg_remove import bg_bp
from routes.enhance import enhance_bp  # optional if you have enhancement route

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(resize_bp, url_prefix="/resize")
app.register_blueprint(bg_bp, url_prefix="/remove-bg")
app.register_blueprint(enhance_bp, url_prefix="/enhance")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
