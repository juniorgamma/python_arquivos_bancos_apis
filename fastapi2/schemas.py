from typing import List, Optional
from pydantic import BaseModel
from datetime import date

class Perfil(BaseModel):
    id: int
    idade:int
    endereco: str

    class Config:
        from_attributes = True


class PerfilCreate(BaseModel):
    idade: int
    endereco: str

class Professor(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True

class ProfessorCreate(BaseModel):
    nome: str

class Disciplina(BaseModel):
    id: int
    nome: str
    descricao: str
    professor: Professor                  # sempre existe (professor_id é nullable = False no models)

    class Config:
        from_attributes = True

class DisciplinaCreate(BaseModel):
    nome: str
    descricao:str
    professor_id: int                      # não recebe o objeto Professor inteiro, só o id para vincular

class Matricula(BaseModel):
    id: int
    data_matricula: date
    estudante_id: int
    disciplina: Disciplina     # devolve a disciplina completa (nome, descrição, professor)

    class Config:
        from_attributes = True

class MatriculaCreate(BaseModel):
    disciplina_id: int
    data_matricula: date

class Estudante(BaseModel):
    id: int
    nome:str
    perfil: Optional[Perfil] = None
    matriculas: List[Matricula] = []    # lista de matrículas do estudante

    class Config:
        from_attributes = True

class EstudanteCreate(BaseModel):
    nome: str
    email: str
    perfil: PerfilCreate

class EstudanteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None