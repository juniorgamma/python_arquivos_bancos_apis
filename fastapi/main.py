from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
from database import SessionLocal, engine

# Criar tabelas no Postgresql caso não existam
models.Base.metadata.create_all(bind = engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/estudantes/', response_model = schemas.EstudanteResponse)
def create_student(student: schemas.EstudanteCreate, db: Session = Depends(get_db)):
    db_student = models.Estudante(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@app.get('/estudantes/', response_model = List[schemas.EstudanteResponse])
def read_students(db: Session = Depends(get_db)):
    students = db.query(models.Estudante).all()
    return students

@app.delete('/estudantes/{student_id}')
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(models.Estudante, student_id)
    if student is None:
        raise HTTPException(status_code = 404, detail = 'Estudante nao encontrado')

    db.query(models.Matricula).filter(
        models.Matricula.estudante_id == student_id
    ).delete(synchronize_session = False)
    db.delete(student)
    db.commit()
    return {'detail': 'Estudante excluído com sucesso'}

@app.get('/estudantes/{student_id}', response_model = schemas.EstudanteResponse)
def read_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(models.Estudante, student_id)
    if student is None:
        raise HTTPException(status_code = 404, detail = 'Estudante não encontrado!')
    return student

    
@app.post('/matriculas/', response_model = schemas.MatriculaResponse)
def create_matricula(matricula: schemas.MatriculaCreate, db: Session = Depends(get_db)):
    db_matricula = models.Matricula(**matricula.model_dump())
    db.add(db_matricula)
    db.commit()
    db.refresh(db_matricula)
    return db_matricula

@app.get('/matriculas/', response_model = List[schemas.MatriculaResponse])
def read_matriculas(db: Session = Depends(get_db)):
    matriculas = db.query(models.Matricula).all()
    return matriculas

@app.delete('/matriculas/{matricula_id}')
def delete_matricula(matricula_id: int, db: Session = Depends(get_db)):
    matricula = db.get(models.Matricula, matricula_id)
    if matricula is None:
        raise HTTPException(status_code = 404, detail = 'Matricula nao encontrada')

    db.delete(matricula)
    db.commit()
    return {'detail': 'Matricula excluida com sucesso'}
