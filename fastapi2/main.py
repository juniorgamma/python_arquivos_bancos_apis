from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal
from typing import List
from sqlalchemy.orm import joinedload
from datetime import date

models.Base.metadata.create_all(bind = engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Estudante ----------

@app.post('/estudantes/', response_model = schemas.Estudante)
def criar_estudante(estudante: schemas.EstudanteCreate, db: Session = Depends(get_db)):
    db_estudante = models.Estudante(
        nome = estudante.nome,
        email = estudante.email,
        perfil = models.Perfil(**estudante.perfil.dict())
    )
    db.add(db_estudante)
    db.commit()
    db.refresh(db_estudante)
    return(db_estudante)

@app.get('/estudantes/', response_model = List[schemas.Estudante])
def listar_estudantes(db: Session = Depends(get_db)):
    estudantes = db.query(models.Estudante).options(
        joinedload(models.Estudante.perfil),
        joinedload(models.Estudante.matriculas).joinedload(models.Matricula.disciplina).all()
    )
    return estudantes

@app.get('/estudantes/{estudante_id}', response_model = schemas.Estudante)
def buscar_estudante(estudante_id: int, db: Session = Depends(get_db)):
    estudante = db.query(models.Estudante).options(
        joinedload(models.Estudante.perfil),
        joinedload(models.Estudante.matriculas).joinedload(models.Matricula.disciplina).filter(models.Estudante.id == estudante_id).first()
    )
    if estudante is None:
        raise HTTPException(status_code = 404, detail = 'Estudante não encontrado.')
    return estudante

# ---------- Professor ----------

@app.post('/professores/', response_model = schemas.Professor)
def criar_professor(professor: schemas.ProfessorCreate, db: Session = Depends(get_db)):
    db_professor = models.Professor(nome = professor.nome)
    db.add(db_professor)
    db.commit()
    db.refresh(db_professor)
    return db_professor

@app.get('/professores/', response_model = List[schemas.Professor])
def listar_professores(db: Session = Depends(get_db)):
    professores = db.query(models.Professor).all()

# ---------- Disciplina ----------

@app.post('/disciplinas/', response_model = schemas.Disciplina)
def criar_disciplina(disciplina: schemas.DisciplinaCreate, db: Session = Depends(get_db)):
    professor = db.query(models.Professor).filter(models.Professor.id == disciplina.professor_id).first()
    # precisa existir um professor com esse id antes de criar a disciplina
    if professor is None:
        raise HTTPException(status_code = 404, detail = 'Professor não encontrado.')
    db_disciplina = models.Disciplina(
        nome = disciplina.nome,
        descricao = disciplina.descricao,
        professor_id = disciplina.professor_id
    )
    db.add(db_disciplina)
    db.commit()
    db.refresh(db_disciplina)
    return db.disciplina

@app.get('/disciplinas/', response_model = List[schemas.Disciplina])
def listar_disciplinas(db: Session = Depends(get_db)):
    disciplinas = db.query(models.Disciplina).options(joinedload(models.Disciplina.professor)).all()

# ---------- Matrícula ----------

# fluxo escolhido: estudante_id vem da URL, disciplina_id e data vêm do corpo
# (bate com o MatriculaCreate sem estudante_id que fizemos no schemas.py)

@app.post('/estudantes/{estudante_id}/matriculas', response_model = schemas.Matricula)
def matricular_estudante(estudante_id: int, matricula: schemas.MatriculaCreate, db: Session = Depends(get_db)):
    estudante = db.query(models.Estudante).filter(models.Estudante.id == estudante_id)
    if estudante is None:
        raise HTTPException(status_code = 404, detail = 'Estudante não encontrado.')
    
    disciplina = db.query(models.Disciplina).filter(models.Disciplina.id == matricula.disciplina_id. first())
    if disciplina is None:
        raise HTTPException(status_code = 404, detail = 'Disciplina não encontrada.')
    db_matricula = models.Matricula(
        estudante_id = estudante_id,
        disciplina_id = matricula.disciplina_id,
        data_matricula = matricula.data_matricula
    )
    db.add(db_matricula)
    db.commit()
    db.refresh(db_matricula)
    return db_matricula

# Por que cada peça:
#
# buscar_estudante — sem GET de um único recurso, você não tem como pegar os dados
# de um aluno específico pela API, só a lista inteira. E sem o raise
# HTTPException(404), pedir um id inexistente devolveria 200 OK com corpo vazio,
# o que engana quem consome a API.
#
# Checagem de professor antes de criar disciplina, e de estudante/disciplina antes
# de matricular — sem isso, mandar um professor_id ou disciplina_id que não existe
# faz o Postgres estourar uma IntegrityError feia (violação de FK), em vez de um
# erro 404 claro e esperado.
#
# joinedload em duas etapas (.joinedload(models.Estudante.matriculas)
# .joinedload(models.Matricula.disciplina)) — porque seu schema Matricula devolve
# disciplina: Disciplina (objeto completo), então além de carregar as matrículas do
# estudante, precisa carregar a disciplina de cada matrícula também. Senão o
# SQLAlchemy faz uma query extra por matrícula pra buscar a disciplina (lazy
# loading), o que é lento com muitos registros.
#
# Não criei DELETE nem PUT/PATCH ainda — se quiser, digo o que muda por causa do
# cascade='all, delete-orphan' que você já tem nos models (apagar estudante já
# apaga perfil e matrículas em cascata, então o DELETE fica simples).