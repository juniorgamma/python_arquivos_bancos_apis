from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class Estudante(Base):
    __tablename__ = 'estudantes'

    id = Column(Integer, primary_key = True, index = True)
    nome = Column(String(100), nullable = False)
    email = Column(String(100), nullable = False, unique = True) # email repetido não faz sentido

    # 1:1 -- um estudante tem um perfil

    perfil = relationship(
        'Perfil',
        back_populates = 'estudante',
        uselist = False,                            # garante objeto único, não lista
        cascade = 'all, delete-orphan'              # apagar estudante apaga o perfil dele (dependente, correto)
    )

    # 1:N -- um estudante tem várias matrículas

    matriculas = relationship(
        'Matricula',
        back_populates = 'estudante',
        cascade = 'all, delete-orphan'             # apagar estudante apaga as matrículas dele (correto)
    )

    disciplina = relationship(
        'Disciplina',
        secondary = 'matriculas',
        back_populates = 'estudante',
        viewonly = True
    )
class Perfil(Base):
    __tablename__ = 'perfis'

    id = Column(Integer, primary_key = True, index = True)
    idade = Column(Integer)
    endereco = Column(String(100), nullable = False)
    estudante_id = Column(
        Integer,
        ForeignKey('estudantes.id'),
        unique = True,                              # garante o lado 1 do 1:1 no banco
        nullable = False
    )

    estudante = relationship(
        'Estudante',
        back_populates = 'perfil'
    )

class Matricula(Base):
    __tablename__ = 'matriculas'

    id = Column(Integer, primary_key = True, index = True)
    data_matricula = Column(Date, nullable = False)

    estudante_id = Column(
        Integer,
        ForeignKey('estudantes.id'),
        nullable = False                        
    )
    disciplina_id = Column(
        Integer,
        ForeignKey('disciplinas.id'),
        nullable = False
    )

    estudante = relationship(
        'Estudante',
        back_populates = 'matriculas'
    )

    disciplina = relationship(
        'Disciplina',
        back_populates = 'matriculas'
    )


    # Sem unique nas foreignkeys aqui de propósito: um estudante pode ter N matrículas
    # (uma por disciplina), e uma disciplina pode ter N matrículas
    # (uma por estudante). Se quiser IMPEDIR matrícula duplicada do
    # mesmo aluno na mesma disciplina, o certo é uma constraint
    # composta, não um unique simples numa das colunas isoladas:
    #
    # from sqlalchemy import UniqueConstraint
    # __table_args__ = (UniqueConstraint('estudante_id', 'disciplina_id'),)

    class Disciplina(Base):
        __tablename__ = 'disciplinas'

        id = Column(Integer, primary_key = True, index = True)
        nome = Column(String(100), nullable = False)
        descricao = Column(String(100), nullable = False)

        professor_id = Column(
            Integer,
            ForeignKey('professores.id'),
            nullable = False
        )

        professor = relationship(
            'Professor',
            back_populates = 'disciplinas'
        )

        # 1:N -- uma disciplina tem várias matrículas (vários alunos matriculados)

        matriculas = relationship(
            'Matricula',
            back_populates = 'disciplina',
            cascade = 'all, delete-orphan'               # apagar a disciplina apaga as matrículas dela (correto)
        )

        # ATALHO: lista de estudantes passando por 'matriculas'
        estudantes = relationship(
            'Estudante',
            secondary = 'matriculas',        # nome da TABELA do meio (não da classe)
            back_populates = 'disciplinas',
            viewonly = True                   # só leitura
        )

        class Professor(Base):
            __tablename__ = 'professores'

            id = Column(Integer, primary_key = True, index = True)
            nome = Column(String(100), nullable = False)

            # 1:N -- um professor leciona várias disciplinas

            disciplina = relationship(
                'Disciplina',
                back_populates = 'professor'
            )