from database import SessionLocal
import models

db = SessionLocal()

estudantes = db.query(models.Estudante).all()

for estudante in estudantes:
    print(estudante.nome, estudante.email)


db.close()