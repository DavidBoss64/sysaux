from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import gestion_bp
from ..models import Paralelo, ParametroEvaluacion
from ..extensions import db

@gestion_bp.route('/paralelo/<int:id>/parametros', methods=['GET', 'POST'])
@login_required
def parametros(id):
    paralelo = Paralelo.query.get_or_404(id)
    if paralelo.auxiliar_id != current_user.id:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('gestion.paralelos'))

    parametros_actuales = ParametroEvaluacion.query.filter_by(paralelo_id=id, estado=True).all()
    total_puntos = sum(p.ponderacion for p in parametros_actuales if p.tipo != 'liberacion')
    tiene_liberacion = any(p.tipo == 'liberacion' for p in parametros_actuales)

    if request.method == 'POST':
        nombre_parametro = request.form.get('nombre_parametro')
        ponderacion = float(request.form.get('ponderacion'))
        tipo = request.form.get('tipo', 'normal') 
        
        # Capturamos el modo de liberación (por defecto 'maximo')
        modo_liberacion = request.form.get('modo_liberacion', 'maximo') if tipo == 'liberacion' else 'maximo'
        
        if tipo == 'liberacion' and tiene_liberacion:
            flash('Error: Ya tienes un Examen de Liberación registrado.', 'danger')
            return redirect(url_for('gestion.parametros', id=id))

        if tipo != 'liberacion' and (total_puntos + ponderacion > paralelo.nota_maxima):
            flash(f'Error: Has excedido el límite. Te quedan {paralelo.nota_maxima - total_puntos} pts.', 'danger')
        else:
            nuevo_parametro = ParametroEvaluacion(
                nombre_parametro=nombre_parametro, 
                ponderacion=ponderacion, 
                tipo=tipo,
                modo_liberacion=modo_liberacion, # <-- Guardamos la estrategia elegida
                paralelo_id=id
            )
            db.session.add(nuevo_parametro)
            db.session.commit()
            flash('Parámetro agregado exitosamente.', 'success')
        return redirect(url_for('gestion.parametros', id=id))

    return render_template('gestion/parametros.html', 
                        paralelo=paralelo, 
                        parametros=parametros_actuales, 
                        total_puntos=total_puntos,
                        tiene_liberacion=tiene_liberacion)

@gestion_bp.route('/parametro/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_parametro(id):
    parametro = ParametroEvaluacion.query.get_or_404(id)
    if parametro.paralelo.auxiliar_id == current_user.id:
        db.session.delete(parametro)
        db.session.commit()
        flash('Parámetro eliminado.', 'info')
    return redirect(url_for('gestion.parametros', id=parametro.paralelo_id))