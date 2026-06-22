from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import papelera_bp
from ..models import Paralelo, Inscripcion, Actividad, ParametroEvaluacion
from ..extensions import db

@papelera_bp.route('/')
@login_required
def index():
    # 1. Paralelos archivados
    paralelos_archivados = Paralelo.query.filter_by(auxiliar_id=current_user.id, estado=False).all()
    
    # 2. Inscripciones dadas de baja
    inscripciones_archivadas = Inscripcion.query.join(Paralelo).filter(
        Paralelo.auxiliar_id == current_user.id, 
        Inscripcion.estado == False
    ).all()

    # 3. Actividades dadas de baja
    actividades_archivadas = Actividad.query.join(ParametroEvaluacion).join(Paralelo).filter(
        Paralelo.auxiliar_id == current_user.id,
        Actividad.estado == False
    ).all()

    return render_template('papelera/index.html', 
                           paralelos=paralelos_archivados, 
                           inscripciones=inscripciones_archivadas,
                           actividades=actividades_archivadas)


@papelera_bp.route('/paralelo/<int:id>/restaurar', methods=['POST'])
@login_required
def restaurar_paralelo(id):
    paralelo = Paralelo.query.get_or_404(id)
    if paralelo.auxiliar_id == current_user.id:
        paralelo.estado = True
        db.session.commit()
        flash(f'Paralelo {paralelo.nombre} restaurado.', 'success')
    return redirect(url_for('papelera.index'))

# --- NUEVA RUTA: ELIMINACIÓN DEFINITIVA ---
@papelera_bp.route('/paralelo/<int:id>/eliminar_definitivo', methods=['POST'])
@login_required
def eliminar_paralelo_definitivo(id):
    paralelo = Paralelo.query.get_or_404(id)
    if paralelo.auxiliar_id == current_user.id:
        db.session.delete(paralelo) # Eliminación en cascada real
        db.session.commit()
        flash(f'El paralelo {paralelo.nombre} y todos sus datos dependientes fueron destruidos definitivamente.', 'success')
    return redirect(url_for('papelera.index'))


@papelera_bp.route('/inscripcion/<int:id>/restaurar', methods=['POST'])
@login_required
def restaurar_inscripcion(id):
    inscripcion = Inscripcion.query.get_or_404(id)
    if inscripcion.paralelo.auxiliar_id == current_user.id:
        inscripcion.estado = True
        db.session.commit()
        flash('Inscripción del estudiante restaurada.', 'success')
    return redirect(url_for('papelera.index'))


@papelera_bp.route('/actividad/<int:id>/restaurar', methods=['POST'])
@login_required
def restaurar_actividad(id):
    actividad = Actividad.query.get_or_404(id)
    if actividad.parametro.paralelo.auxiliar_id != current_user.id:
        return redirect(url_for('papelera.index'))
        
    actividad.estado = True 
    db.session.commit()
    flash(f'Actividad "{actividad.titulo}" restaurada.', 'success')
    return redirect(url_for('papelera.index'))