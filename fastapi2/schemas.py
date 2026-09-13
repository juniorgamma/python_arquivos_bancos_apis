from typing import List, Optional
from pydantic import BaseModel

class Perfil(BaseModel):
    id: int
    idade: int
    endereco: str

    class Config:
        from_attributes = True

class PerfilCreate(BaseModel):
    idade: int                       # não coloca o id pois ele é criado automaticamente
    endereco: str

class Estudante(BaseModel):
    id: int
    nome: str
    email: str
    perfil: Optional[Perfil] = None # valor padrão caso eu não passe um perfil. perfil tem que ser uma instância de Perfil

    class Config:
        from_attributes = True  # vai trazer as informações automaticamente de estudantes

class EstudanteCreate(BaseModel):
    nome: str
    email: str
    perfil: PerfilCreate # precisa ser uma instância de PerfilCreate
