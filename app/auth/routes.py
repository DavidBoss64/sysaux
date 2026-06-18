from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from ..models import Usuario
from ..extensions import bcrypt

@auth_bp.route('/login',methods = ['GET','POST'])
def login():
    #Si el usuario ya inicio sesion lo mandamos al main dashbpard
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method =='POST':
        username = request.form.get('username')
        password = request.form.get('password')

        #Buscamos al usuario en la base de datos
        usuario = Usuario.query.filter_by(username=username).first()

        #Verificamos que exista y que la contra encriptada coincida
        if usuario and bcrypt.check_password_hash(usuario.password_hash, password):
            login_user(usuario)
            return redirect(url_for('main.index'))
        else:
            flash('Usuario o contraseña incorrectos. Intenta nuevamente','danger')

    #Si es una peticion GET (solo entrar a la pagina). Y mostramos el form del login
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
