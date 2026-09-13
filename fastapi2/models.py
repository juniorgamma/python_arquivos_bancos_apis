from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Estudante(Base):
    __tablename__ = 'estudantes'
    id = Column(Integer, primary_key = True, index = True)
    nome = Column(String(100), nullable = False)
    email = Column(String(100), nullable = False)
    perfil = relationship(
        'Perfil',                        # relacionamento com classe Perfil
        back_populates = 'estudante',    # back_populates significa que estou criando relação entre Estudante e Perfil
        uselist = False,                 # relação é 1 pra 1, cada estudante tem 1 perfil, quando acessar o objeto estudante vai retornar 1 perfil, não uma lista
        cascade = 'all, delete-orphan'   # all = tudo que for filho do estudante vai ser afetado quando mexer no estudante
    )                                     # delete-orphan - se eu deletar estudante, o objeto perfil que está relacionado com o estudante tb é deletado
    
class Perfil(Base):
    __tablename__ = 'perfis'
    id = Column(Integer, primary_key = True, index = True)
    idade = Column(Integer)
    endereco = Column(String(100), nullable = False)
    estudante_id = Column(
        Integer, 
        ForeignKey('estudantes.id'),
        unique = True                   # estudante é único, ou seja, se tentar criar um outro perfil com mesmo id de estudante ele vai falar
    )                                   # que não pode ser criado pq o id do estudante já existe na tabela de perfis
    estudante = relationship(
        'Estudante',
        back_populates = 'perfil'      # back_populates não se refere nem à classe, nem à tabela — ele aponta para o nome do atributo relationship do outro lado.
    )

    # A ForeignKey sozinha já cria o vínculo real no banco; o relationship() é uma "conveniência" do ORM para você poder escrever 
    # estudante.perfil ou perfil.estudante em vez de fazer uma query manual.
    # Sem esse atalho, para pegar as matrículas de um estudante (no caso do models da pasta fastapi) você precisaria fazer uma query separada tipo:
    # matriculas = session.query(Matricula).filter(Matricula.estudante_id == estudante.id).all()

