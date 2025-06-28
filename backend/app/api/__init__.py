from flask import Flask
from flask_cors import CORS

def create_app():
    """
    The Flask application factory.
    """
    app = Flask(__name__)

    # --- CORS ---
    # This is essential for allowing your React frontend (on a different port)
    # to communicate with this backend.
    CORS(app)

    # --- REGISTER BLUEPRINTS ---
    # Import and register the prediction blueprint
    from .prediction import prediction_bp
    app.register_blueprint(prediction_bp, url_prefix='/api')

    @app.route('/health')
    def health_check():
        return "API is up and running!", 200

    return app