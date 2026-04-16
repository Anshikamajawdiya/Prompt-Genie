import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS
from config import Config

from app.routes.prompt_routes import prompt_bp
from app.routes.ai_routes import ai_bp
from app.routes.tracking_routes import tracking_bp
from app.routes.chatbot_routes import chatbot_bp 


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(prompt_bp)
    app.register_blueprint(ai_bp) 
    app.register_blueprint(tracking_bp)
    app.register_blueprint(chatbot_bp)
   
    CORS(app, resources={
        r"/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    return app