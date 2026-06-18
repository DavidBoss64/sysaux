import os

# Obtiene la ruta absoluta del proyecto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Llave secreta para proteger las sesiones y contraseñas
    SECRET_KEY = "clave-secreta-super-segura-byte-soft"
    

    
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "sysaux.db")
    
    # Apagamos esto para ahorrar memoria en el servidor
    SQLALCHEMY_TRACK_MODIFICATIONS = False