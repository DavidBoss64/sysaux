from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from ..models import Usuario
from ..extensions import db,bcrypt

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si intento entrar al login ya estando logueado, me auto-redirijo al Dashboard
    if current_user.is_authenticated:
        if current_user.rol.nombre.lower() in ['administrador', 'auxiliar']:
            return redirect(url_for('main.index'))
        return redirect(url_for('estudiante.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')

        # Busco mis credenciales en la tabla unificada de Usuarios
        usuario = Usuario.query.filter_by(username=username).first()

        # Valido la existencia y la contraseña encriptada
        if usuario and bcrypt.check_password_hash(usuario.password_hash, password):
            if not usuario.estado:
                flash('Esta cuenta se encuentra inactiva. Comunícate con el administrador.', 'danger')
                return redirect(url_for('auth.login'))

            # Levanto la sesión segura en Flask
            login_user(usuario)
            
            # --- CORRECCIÓN DE FLUJO ---
            # Redirección inteligente al Dashboard Principal de mi rol
            if usuario.rol.nombre.lower() in ['administrador', 'auxiliar']:
                flash(f'Bienvenido al sistema, {usuario.nombres}.', 'success')
                return redirect(url_for('main.index'))
            else:
                flash(f'Hola {usuario.nombres}, has iniciado sesión correctamente.', 'success')
                return redirect(url_for('estudiante.dashboard'))
        else:
            flash('Credenciales incorrectas. Por favor, intenta de nuevo.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        password_actual = request.form.get('password_actual')
        password_nueva = request.form.get('password_nueva')
        password_confirmar = request.form.get('password_confirmar')

        # 1. Verificamos que la contraseña actual sea correcta
        if not bcrypt.check_password_hash(current_user.password_hash, password_actual):
            flash('La contraseña actual ingresada es incorrecta.', 'danger')
            return redirect(url_for('auth.perfil'))

        # 2. Verificamos que las contraseñas nuevas coincidan
        if password_nueva != password_confirmar:
            flash('Las contraseñas nuevas no coinciden.', 'warning')
            return redirect(url_for('auth.perfil'))

        # 3. Validamos longitud por seguridad
        if len(password_nueva) < 6:
            flash('La nueva contraseña debe tener al menos 6 caracteres.', 'warning')
            return redirect(url_for('auth.perfil'))

        # 4. Encriptamos y guardamos la nueva clave
        current_user.password_hash = bcrypt.generate_password_hash(password_nueva).decode('utf-8')
        db.session.commit()
        
        flash('¡Tu contraseña ha sido actualizada con éxito! Utilízala en tu próximo inicio de sesión.', 'success')
        return redirect(url_for('auth.perfil'))

    return render_template('auth/perfil.html')