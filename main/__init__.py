from flask import Flask, jsonify
from config import Config
from models import db
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from routes.auth import auth_bp
from routes.posts import posts_bp
from routes.comments import comments_bp
from routes.tags import tags_bp
from flask_cors import CORS
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
import os
import logging


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.json.sort_keys = False
    

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    ma = Marshmallow(app)
    ma.init_app(app)

    # Enable CORS
    CORS(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix = '/auth')
    app.register_blueprint(posts_bp, url_prefix = '/posts')
    app.register_blueprint(comments_bp)
    app.register_blueprint(tags_bp, url_prefix = '/tags')
    
    #setup logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/blogapi.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s:%(message)s:[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Blog API startup')



    # Global error handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {str(e)}")
        if app.debug:
            return jsonify({"message":str(e)}), 500
        else:
            return {"message": "An unexpected error occurred"}, 500


    return app


