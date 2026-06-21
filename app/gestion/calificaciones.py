from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import gestion_bp
from ..models import Actividad, Inscripcion, Calificacion
from ..extensions import db

@gestion_bp.route('/actividad/<int:id>/calificar', methods=['GET', 'POST'])
@login_required
def calificar_actividad(id):
    actividad = Actividad.query.get_or_404(id)
    paralelo = actividad.parametro.paralelo
    tipo_parametro = actividad.parametro.tipo  # 'normal' o 'asistencia'
    
    if paralelo.auxiliar_id != current_user.id:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('gestion.paralelos'))

    # Consultamos las inscripciones activas y las ordenamos exactamente igual que en los reportes
    inscripciones_bd = Inscripcion.query.filter_by(paralelo_id=paralelo.id, estado=True).all()
    inscripciones = sorted(inscripciones_bd, key=lambda i: (i.estudiante.apellidos, i.estudiante.nombres))
    calificaciones_bd = Calificacion.query.filter_by(actividad_id=actividad.id).all()
    notas_actuales = {c.estudiante_id: c.puntaje for c in calificaciones_bd}

    if request.method == 'POST':
        for inscripcion in inscripciones:
            estudiante_id = inscripcion.estudiante_id
            calificacion_existente = Calificacion.query.filter_by(actividad_id=actividad.id, estudiante_id=estudiante_id).first()

            if tipo_parametro == 'asistencia':
                # Los checkbox en HTML solo se envían si están tiqueados
                asistio = request.form.get(f'asistencia_{estudiante_id}')
                # Si asistió, gana el puntaje total de la actividad (manejado de forma entera)
                puntaje = actividad.parametro.ponderacion if asistio else 0.0
                
                if calificacion_existente:
                    calificacion_existente.puntaje = puntaje
                else:
                    nueva_nota = Calificacion(actividad_id=actividad.id, estudiante_id=estudiante_id, puntaje=puntaje)
                    db.session.add(nueva_nota)
            else:
                # Lógica normal para prácticas o exámenes
                nota_input = request.form.get(f'nota_{estudiante_id}')
                if nota_input is not None and nota_input.strip() != '':
                    puntaje = float(nota_input)
                    max_pts = actividad.parametro.ponderacion
                    if puntaje > max_pts: puntaje = max_pts
                    if puntaje < 0: puntaje = 0

                    if calificacion_existente:
                        calificacion_existente.puntaje = puntaje
                    else:
                        nueva_nota = Calificacion(actividad_id=actividad.id, estudiante_id=estudiante_id, puntaje=puntaje)
                        db.session.add(nueva_nota)
                else:
                    if calificacion_existente:
                        db.session.delete(calificacion_existente)
                        
        db.session.commit()
        flash('Calificaciones actualizadas con éxito.', 'success')
        return redirect(url_for('gestion.calificar_actividad', id=actividad.id))

    return render_template('gestion/calificaciones.html', 
                           actividad=actividad, 
                           paralelo=paralelo, 
                           inscripciones=inscripciones, 
                           notas=notas_actuales,
                           tipo_parametro=tipo_parametro)