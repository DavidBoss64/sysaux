from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import gestion_bp
from ..models import Paralelo, Inscripcion, Actividad, ParametroEvaluacion
from ..extensions import db

@gestion_bp.route('/papelera')
@login_required
def papelera():
    # 1. Paralelos archivados
    paralelos_archivados = Paralelo.query.filter_by(auxiliar_id=current_user.id, estado=False).all()
    
    # 2. Inscripciones dadas de baja
    inscripciones_archivadas = Inscripcion.query.join(Paralelo).filter(
        Paralelo.auxiliar_id == current_user.id, 
        Inscripcion.estado == False
    ).all()

    # 3. NUEVO: Actividades dadas de baja (Prácticas, Asistencias, etc.)
    actividades_archivadas = Actividad.query.join(ParametroEvaluacion).join(Paralelo).filter(
        Paralelo.auxiliar_id == current_user.id,
        Actividad.estado == False
    ).all()

    return render_template('gestion/papelera.html', 
                           paralelos=paralelos_archivados, 
                           inscripciones=inscripciones_archivadas,
                           actividades=actividades_archivadas) # <-- Pasamos las actividades a la vista


@gestion_bp.route('/paralelo/<int:id>/restaurar', methods=['POST'])
@login_required
def restaurar_paralelo(id):
    paralelo = Paralelo.query.get_or_404(id)
    if paralelo.auxiliar_id == current_user.id:
        paralelo.estado = True
        db.session.commit()
        flash(f'Paralelo {paralelo.nombre} restaurado.', 'success')
    return redirect(url_for('gestion.papelera'))


@gestion_bp.route('/inscripcion/<int:id>/restaurar', methods=['POST'])
@login_required
def restaurar_inscripcion(id):
    inscripcion = Inscripcion.query.get_or_404(id)
    if inscripcion.paralelo.auxiliar_id == current_user.id:
        inscripcion.estado = True
        db.session.commit()
        flash('Inscripción restaurada.', 'success')
    return redirect(url_for('gestion.papelera'))


# --- NUEVA RUTA: RESTAURAR ACTIVIDAD ---
@gestion_bp.route('/actividad/<int:id>/restaurar', methods=['POST'])
@login_required
def restaurar_actividad(id):
    actividad = Actividad.query.get_or_404(id)
    
    if actividad.parametro.paralelo.auxiliar_id != current_user.id:
        return redirect(url_for('gestion.papelera'))
        
    actividad.estado = True # Devolvemos la actividad al estado activo
    db.session.commit()
    
    flash(f'Actividad "{actividad.titulo}" y sus calificaciones han sido restauradas.', 'success')
    return redirect(url_for('gestion.papelera'))