from app import create_app
from app.extensions import db
from app.models import Materia

app = create_app()

with app.app_context():
    # Verificamos si ya existen materias para no duplicarlas
    if not Materia.query.first():
        # Creamos las materias exactas de tu auxiliatura
        materia1 = Materia(sigla='MAT-114', nombre='Matemática Discreta')
        materia2 = Materia(sigla='MAT-100', nombre='Álgebra 1')
        
        db.session.add_all([materia1, materia2])
        db.session.commit()
        print("¡Materias sembradas con éxito!")
        print("- MAT-114: Matemática Discreta")
        print("- MAT-100: Álgebra 1")
    else:
        print("Las materias ya existen en la base de datos.")