from flask import Blueprint

# Creamos el blueprint con el prefijo de URL /reportes
reportes_bp = Blueprint('reportes', __name__, template_folder='templates', url_prefix='/reportes')

# Importamos las rutas para que se registren en el blueprint
from . import centralizador, exportar