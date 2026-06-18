from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError  # <-- IMPORTACIÓN CLAVE PARA ATRAPAR DUPLICADOS
from . import gestion_bp
from ..models import Paralelo, Usuario, Inscripcion, Rol
from ..extensions import db, bcrypt

@gestion_bp.route('/paralelo/<int:id>/estudiantes', methods=['GET', 'POST'])
@login_required
def estudiantes(id):
    paralelo = Paralelo.query.get_or_404(id)
    if paralelo.auxiliar_id != current_user.id:
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('gestion.paralelos'))

    if request.method == 'POST':
        nombres = request.form.get('nombres')
        apellidos = request.form.get('apellidos')
        ci = request.form.get('ci')
        ru = request.form.get('ru')

        estudiante = Usuario.query.filter_by(ci=ci).first()
        
        if not estudiante:
            rol_estudiante = Rol.query.filter_by(nombre='Estudiante').first()
            hashed_pw = bcrypt.generate_password_hash(ci).decode('utf-8')
            estudiante = Usuario(
                nombres=nombres.upper(), 
                apellidos=apellidos.upper(), 
                ci=ci, 
                ru=ru if ru else None, 
                username=ci, 
                password_hash=hashed_pw, 
                rol_id=rol_estudiante.id
            )
            db.session.add(estudiante)
            
            # Usamos try-except al crear por si ingresan un RU que ya existe en otro lado
            try:
                db.session.flush()
            except IntegrityError:
                db.session.rollback()
                flash('Error: El C.I. o el R.U. ingresado ya le pertenece a otra cuenta en el sistema.', 'danger')
                return redirect(url_for('gestion.estudiantes', id=id))

        inscripcion_previa = Inscripcion.query.filter_by(estudiante_id=estudiante.id, paralelo_id=id).first()
        
        if inscripcion_previa:
            flash('El estudiante ya está inscrito en este paralelo.', 'warning')
        else:
            nueva_inscripcion = Inscripcion(estudiante_id=estudiante.id, paralelo_id=id)
            db.session.add(nueva_inscripcion)
            flash('Estudiante inscrito exitosamente.', 'success')
            
        db.session.commit()
        return redirect(url_for('gestion.estudiantes', id=id))

    inscripciones = Inscripcion.query.filter_by(paralelo_id=id, estado=True).all()
    return render_template('gestion/estudiantes.html', paralelo=paralelo, inscripciones=inscripciones)

@gestion_bp.route('/estudiante/<int:id>/editar', methods=['POST'])
@login_required
def editar_estudiante(id):
    estudiante = Usuario.query.get_or_404(id)
    paralelo_id = request.form.get('paralelo_id')
    
    estudiante.nombres = request.form.get('nombres').upper()
    estudiante.apellidos = request.form.get('apellidos').upper()
    estudiante.ci = request.form.get('ci')
    estudiante.ru = request.form.get('ru') or None
    
    # Blindamos la actualización de datos
    try:
        db.session.commit()
        flash('Datos del estudiante actualizados correctamente.', 'success')
    except IntegrityError:
        db.session.rollback() # Cancelamos la transacción corrupta
        flash('Error de duplicidad: El C.I. o el R.U. que intentas asignar ya le pertenece a otro estudiante.', 'danger')
        
    return redirect(url_for('gestion.estudiantes', id=paralelo_id))

@gestion_bp.route('/inscripcion/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar_inscripcion(id):
    inscripcion = Inscripcion.query.get_or_404(id)
    paralelo_id = inscripcion.paralelo_id
    if inscripcion.paralelo.auxiliar_id == current_user.id:
        inscripcion.estado = False
        db.session.commit()
        flash('Estudiante dado de baja del paralelo.', 'info')
    return redirect(url_for('gestion.estudiantes', id=paralelo_id))