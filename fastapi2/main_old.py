from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal
from typing import List
from sqlalchemy.orm import joinedload

# Criar tabelas no Postgresql caso não existam
models.Base.metadata.create_all(bind = engine)

app = FastAPI()

# Escrevendo conexão com o banco de dados

def get_db():
    db = SessionLocal()  # Cria uma nova sessão do SQLAlchemy (SessionLocal é a fábrica de sessões que você configurou, 
    try:                 # geralmente com sessionmaker(bind=engine)). Cada chamada a get_db() gera uma sessão nova e independente.
        yield db         # em vez de return, usa-se yield. Isso transforma a função em um generator. .
    finally:             # O yield db "entrega" a sessão para quem está usando (no FastAPI, geralmente uma rota), e a execução da função pausa nesse ponto — ela não termina ainda
        db.close()

# Define que a função abaixo será executada quando recebermos uma requisição POST
# no endereço /estudantes/. O response_model informa o formato da resposta da API.
@app.post('/estudantes/', response_model = schemas.Estudante)
# estudante recebe os dados enviados pelo cliente, já validados por EstudanteCreate.
# db recebe uma sessão do banco criada pela função get_db através do Depends.
def criar_estudante(estudante: schemas.EstudanteCreate, db: Session = Depends(get_db)):
    # Cria um objeto Estudante do SQLAlchemy, que representa um registro no banco.
    db_estudante = models.Estudante(
        # Copia o nome recebido no corpo da requisição para o novo estudante.
        nome = estudante.nome,
        # Cria também o perfil relacionado ao estudante.
        # dict() transforma o objeto PerfilCreate em um dicionário.
        # O ** distribui as chaves do dicionário como argumentos nomeados,
        # equivalendo a models.Perfil(idade=..., endereco=...).
        email = estudante.email,
        perfil = models.Perfil(**estudante.perfil.dict())
    )
    db.add(db_estudante)
    db.commit()
    db.refresh(db_estudante)
    return db_estudante

@app.get('/estudantes/', response_model = List[schemas.Estudante])
def listar_estudantes(db: Session = Depends(get_db)):
    estudantes = db.query(models.Estudante).options(joinedload(models.Estudante.perfil)).all()
    return estudantes
