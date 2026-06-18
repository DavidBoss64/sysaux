import os
from flask import Flask
from config import Config
from .extensions import db, login_manager, bcrypt # Importamos las nuevas extensiones

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # Inicializamos todas las extensiones
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    with app.app_context():
        from . import models
        db.create_all()
        
        # Registramos los Blueprints
        from .main import main_bp
        app.register_blueprint(main_bp)
        
        from .auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth') # Todas las rutas de login empezarán con /auth
        
        from .gestion import gestion_bp
        app.register_blueprint(gestion_bp, url_prefix='/gestion')

    return app