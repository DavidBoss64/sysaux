from app import create_app

# Usamos la "Fábrica" para construir nuestra aplicación
app = create_app()

if __name__ == '__main__':
    # Ejecutamos el servidor en modo debug para ver errores en tiempo real
    app.run(debug=True)