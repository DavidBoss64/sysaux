from flask import render_template
from flask_login import login_required, current_user
from . import gestion_bp
from ..models import Paralelo

@gestion_bp.route('/control-diario')
@login_required
def panel_operativo():
    # Listamos los paralelos activos para que seleccionemos a cuál queremos entrar a pasar asistencia o prácticas
    mis_paralelos = Paralelo.query.filter_by(auxiliar_id=current_user.id, estado=True).all()
    return render_template('gestion/panel_operativo.html', paralelos=mis_paralelos)