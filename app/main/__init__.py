from flask import Blueprint

# Creamos el Blueprint llamado 'main'
main_bp = Blueprint('main', __name__)


from . import routes