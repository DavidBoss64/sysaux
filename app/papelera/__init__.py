from flask import Blueprint

# Creamos el blueprint global de la papelera
papelera_bp = Blueprint('papelera', __name__, template_folder='templates', url_prefix='/papelera')

from . import routes