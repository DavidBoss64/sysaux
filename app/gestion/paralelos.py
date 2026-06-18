from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import gestion_bp
from ..models import Paralelo, Materia
from ..extensions import db

@gestion_bp.route('/paralelos', methods=['GET', 'POST'])
@login_required
def paralelos():
    if request.method == 'POST':
        nombre_paralelo = request.form.get('nombre')
        materia_id = request.form.get('materia_id')
        codigo_inscripcion = request.form.get('codigo_inscripcion')
        # Capturamos la nota máxima, si viene vacía por defecto es 10.0
        nota_maxima = request.form.get('nota_maxima')
        nota_maxima = float(nota_maxima) if nota_maxima else 10.0
        
        if not nombre_paralelo or not materia_id:
            flash('Por favor, completa los campos obligatorios.', 'warning')
            return redirect(url_for('gestion.paralelos'))
            
        nuevo_paralelo = Paralelo(
            nombre=nombre_paralelo.upper(),
            materia_id=int(materia_id),
            codigo_inscripcion=codigo_inscripcion if codigo_inscripcion else None,
            nota_maxima=nota_maxima,
            auxiliar_id=current_user.id
        )
        try:
            db.session.add(nuevo_paralelo)
            db.session.commit()
            flash(f'Paralelo {nombre_paralelo} registrado con éxito.', 'success')
        except Exception:
            db.session.rollback()
            flash('Hubo un error al registrar el paralelo.', 'danger')
        return redirect(url_for('gestion.paralelos'))

    mis_paralelos = Paralelo.query.filter_by(auxiliar_id=current_user.id, estado=True).all()
    todas_materias = Materia.query.filter_by(estado=True).all()
    return render_template('gestion/paralelos.html', paralelos=mis_paralelos, materias=todas_materias)

@gestion_bp.route('/paralelo/<int:id>/editar', methods=['POST'])
@login_required
def editar_paralelo(id):
    paralelo = Paralelo.query.get_or_404(id)
    if paralelo.auxiliar_id == current_user.id:
        paralelo.nombre = request.form.get('nombre').upper()
        paralelo.materia_id = request.form.get('materia_id')
        paralelo.codigo_inscripcion = request.form.get('codigo_inscripcion') or None
        
        nota_maxima = request.form.get('nota_maxima')
        paralelo.nota_maxima = float(nota_maxima) if nota_maxima else 10.0
        
        db.session.commit()
        flash('Paralelo actualizado correctamente.', 'success')
    return redirect(url_for('gestion.paralelos'))

@gestion_bp.route('/paralelo/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_paralelo(id):
    paralelo = Paralelo.query.get_or_404(id)
    if paralelo.auxiliar_id == current_user.id:
        paralelo.estado = False
        db.session.commit()
        flash('Paralelo archivado.', 'info')
    return redirect(url_for('gestion.paralelos'))