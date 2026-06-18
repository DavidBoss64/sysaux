from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from . import gestion_bp
from ..models import Paralelo, ParametroEvaluacion, Actividad
from ..extensions import db

# 1. EL DASHBOARD INTERMEDIO (Tarjetas de Categorías)
@gestion_bp.route('/paralelo/<int:id>/dashboard-actividades')
@login_required
def dashboard_actividades(id):
    paralelo = Paralelo.query.get_or_404(id)
    if paralelo.auxiliar_id != current_user.id:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('gestion.panel_operativo'))

    parametros = ParametroEvaluacion.query.filter_by(paralelo_id=id, estado=True).all()
    return render_template('gestion/dashboard_actividades.html', paralelo=paralelo, parametros=parametros)

# 2. LA LISTA DE ACTIVIDADES (Filtrada por categoría)
@gestion_bp.route('/parametro/<int:parametro_id>/actividades', methods=['GET', 'POST'])
@login_required
def lista_actividades(parametro_id):
    parametro = ParametroEvaluacion.query.get_or_404(parametro_id)
    paralelo = parametro.paralelo
    
    if paralelo.auxiliar_id != current_user.id:
        return redirect(url_for('gestion.panel_operativo'))

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        fecha_str = request.form.get('fecha')
        codigo_asistencia = request.form.get('codigo_asistencia') or None

        fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d') if fecha_str else datetime.utcnow()
        
        nueva_actividad = Actividad(
            titulo=titulo, 
            fecha=fecha_obj, 
            codigo_asistencia=codigo_asistencia, 
            parametro_id=parametro.id, # Asignación automática
            esta_abierta=False 
        )
        db.session.add(nueva_actividad)
        db.session.commit()
        flash('Actividad creada exitosamente.', 'success')
        return redirect(url_for('gestion.lista_actividades', parametro_id=parametro.id))

    actividades = Actividad.query.filter_by(parametro_id=parametro.id, estado=True).order_by(Actividad.fecha.desc()).all()
    return render_template('gestion/actividades.html', parametro=parametro, paralelo=paralelo, actividades=actividades)

# 3. CONMUTAR ASISTENCIA
@gestion_bp.route('/actividad/<int:id>/conmutar-asistencia', methods=['POST'])
@login_required
def conmutar_asistencia(id):
    actividad = Actividad.query.get_or_404(id)
    actividad.esta_abierta = not actividad.esta_abierta
    db.session.commit()
    estado_str = "ABIERTA" if actividad.esta_abierta else "CERRADA"
    flash(f'La asistencia ha sido {estado_str}.', 'info')
    return redirect(url_for('gestion.lista_actividades', parametro_id=actividad.parametro_id))

# 4. EDITAR ACTIVIDAD
@gestion_bp.route('/actividad/<int:id>/editar', methods=['POST'])
@login_required
def editar_actividad(id):
    actividad = Actividad.query.get_or_404(id)
    actividad.titulo = request.form.get('titulo')
    fecha_str = request.form.get('fecha')
    if fecha_str:
        actividad.fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
    actividad.codigo_asistencia = request.form.get('codigo_asistencia') or None
    db.session.commit()
    flash('Actividad actualizada.', 'success')
    return redirect(url_for('gestion.lista_actividades', parametro_id=actividad.parametro_id))

# 5. ELIMINAR ACTIVIDAD
@gestion_bp.route('/actividad/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_actividad(id):
    actividad = Actividad.query.get_or_404(id)
    actividad.estado = False
    db.session.commit()
    flash('Actividad archivada.', 'info')
    return redirect(url_for('gestion.lista_actividades', parametro_id=actividad.parametro_id))