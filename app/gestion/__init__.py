from flask import Blueprint

# Creamos el Blueprint
gestion_bp = Blueprint('gestion', __name__)

# Importamos los submódulos ordenados
from . import paralelos, parametros, estudiantes, actividades, calificaciones, panel_operativo