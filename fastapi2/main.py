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
    db = SessionLocal()  # criada e fechada automaticamente a cada requisição HTTP (por causa do yield/finally)
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
        joinedload(models.Estudante.matriculas).joinedload(models.Matricula.disciplina)
    ).all()
    return estudantes

@app.get('/estudantes/{estudante_id}', response_model = schemas.Estudante)
def buscar_estudante(estudante_id: int, db: Session = Depends(get_db)):
    estudante = db.query(models.Estudante).options(
        joinedload(models.Estudante.perfil),
        joinedload(models.Estudante.matriculas).joinedload(models.Matricula.disciplina)
    ).filter(models.Estudante.id == estudante_id).first()
    if estudante is None:
        raise HTTPException(status_code = 404, detail = 'Estudante não encontrado.')
    return estudante

@app.put('/estudantes/{estudante_id}', response_model = schemas.Estudante)
def atualizar_estudante(estudante_id: int, dados: schemas.EstudanteCreate, db: Session = Depends(get_db)):
    db_estudante = db.query(models.Estudante).filter(models.Estudante.id == estudante_id).first()
    if db_estudante is None:
        raise HTTPException(status_code = 404, detail = 'Estudante não encontrado.')
    # atualiza campo por campo em vez de recriar o objeto -- assim o
    # SQLAlchemy só gera um UPDATE, e o id/relacionamentos existentes
    # não se perdem
    db_estudante.nome = dados.nome
    db_estudante.email = dados.email
    # perfil é 1:1 -- se já existe, atualiza os campos dele;
    # se não existe (estudante criado sem perfil), cria agora
    if db_estudante.perfil:
        db_estudante.perfil.idade = dados.perfil.idade
        db_estudante.perfil.endereco = dados.perfil.endereco
    else:
        db_estudante.perfil = models.Perfil(**dados.perfil.dict())
    db.commit()
    db.refresh(db_estudante)
    return db_estudante

@app.patch('/estudantes/{estudante_id}', response_model = schemas.Estudante)
def atualizar_estudante_parcial(estudante_id: int, dados: schemas.EstudanteUpdate, db: Session = Depends(get_db)):
    db_estudante = db.query(models.Estudante).filter(models.Estudante.id == estudante_id).first()
    if db_estudante is None:
        raise HTTPException(status_code = 404, detail = 'Estudante não encontrado.')
    # exclude_unset=True é a peça-chave: pega só os campos que o
    # cliente realmente enviou no corpo, ignora os que ficaram None
    # por padrão (que não significam "apague isso", significam
    # "não mexi nisso")
    atualizacoes = dados.dict(exclude_unset = True)
    for campo, valor in atualizacoes.items():
        setattr(db_estudante, campo, valor)
    db.commit()
    db.refresh(db_estudante)
    return db_estudante

@app.delete('/estudantes/{estudante_id}')
def deletar_estudante(estudante_id: int, db: Session = Depends(get_db)):
    db_estudante = db.query(models.Estudante).filter(models.Estudante.id == estudante_id).first()
    if db_estudante is None:
        raise HTTPException(status_code = 404, detail = 'Estudante não encontrado.')
    db.delete(db_estudante)
    db.commit()
    # sem response_model aqui de propósito -- não tem um "recurso" pra
    # devolver depois de apagado, só uma confirmação
    return {'detail': 'Estudante removido com sucesso.'}


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
    return professores

@app.put('/professores/{professor_id}', response_model = schemas.Professor)
def atualizar_professor(professor_id: int, dados: schemas.ProfessorCreate, db: Session = Depends(get_db)):
    db_professor = db.query(models.Professor).filter(models.Professor.id == professor_id).first()
    if db_professor is None:
        raise HTTPException(status_code = 404, detail = 'Professor não encontrado.')
    db_professor.nome = dados.nome
    db.commit()
    db.refresh(db_professor)
    return db_professor

@app.delete('/professores/{professor_id}')
def deletar_professor(professor_id: int, novo_professor_id: int = None, db: Session = Depends(get_db)):
    db_professor = db.query(models.Professor).filter(models.Professor.id == professor_id).first()
    if db_professor is None:
        raise HTTPException(status_code = 404, detail = 'Professor não encontrado.')
    # busca as disciplinas desse professor -- sem isso não temos como
    # saber se existe algo bloqueando a exclusão
    disciplinas = db.query(models.Disciplina).filter(models.Disciplina.professor_id == professor_id).all()
    if disciplinas:
        # tem disciplinas vinculadas -- só prossegue se o cliente
        # informou pra quem transferir
        if novo_professor_id is None:
            raise HTTPException(
                status_code = 400, 
                detail = f'Professor possui {len(disciplinas)} disciplina(s) vinculada(s). Informe novo_professor_id para reatribuí-las antes de excluir'
            )
        # não pode "transferir" pra ele mesmo -- isso não resolveria nada
        if novo_professor_id == professor_id:
            raise HTTPException(status_code = 400, detail = 'novo_professor_id deve ser diferente do professor a ser excluído')
        # confirma que o novo professor de destino existe
        novo_professor = db.query(models.Professor).filter(models.Professor.id == novo_professor_id).first()
        if novo_professor is None:
            raise HTTPException(status_code = 404, detail = 'Novo professor não encontrado.')
        # reatribui cada disciplina antes de apagar o professor original
        for disciplina in disciplinas:
            disciplina.professor = novo_professor # objeto, não o id
    db.delete(db_professor)
    db.commit()
    return {'detail': 'Professor removido com sucesso.'}

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
    return db_disciplina

@app.get('/disciplinas/', response_model = List[schemas.Disciplina])
def listar_disciplinas(db: Session = Depends(get_db)):
    disciplinas = db.query(models.Disciplina).options(joinedload(models.Disciplina.professor)).all()
    return disciplinas

@app.put('/disciplinas/{disciplina_id}', response_model = schemas.Disciplina)
def atualizar_disciplina(disciplina_id: int, dados: schemas.DisciplinaCreate, db: Session = Depends(get_db)):
    db_disciplina = db.query(models.Disciplina).options(joinedload(models.Disciplina.professor)).filter(models.Disciplina.id == disciplina_id).first()
    if db_disciplina is None:
        raise HTTPException(status_code = 404, detail = 'Disciplina não encontrada.')
    # se o professor_id vier diferente, precisa confirmar que esse
    # professor existe -- mesma checagem que já fazemos em criar_disciplina
    professor = db.query(models.Professor).filter(models.Professor.id == dados.professor_id).first()
    if professor is None:
        raise HTTPException(status_code = 404, detail = 'Professor não encontrado.')
    db_disciplina.nome = dados.nome
    db_disciplina.descricao = dados.descricao
    db_disciplina.professor_id = dados.professor_id     # troca o vínculo, não o nome do professor
    db.commit()
    db.refresh(db_disciplina)
    return db_disciplina

@app.delete('/disciplinas/{disciplina_id}')
def deletar_disciplina(disciplina_id:int, db: Session = Depends(get_db)):
    db_disciplina = db.query(models.Disciplina).filter(models.Disciplina.id == disciplina_id).first()
    # Também tirei o joinedload(models.Disciplina.professor) — pra deletar, você não precisa carregar o professor junto, 
    # é uma query a mais sem necessidade. joinedload só compensa quando você vai devolver dados relacionados na resposta, 
    # como no PUT e nos GET.
    if db_disciplina is None:
        raise HTTPException(status_code = 404, detail = 'Disciplina não encontrada.')
    db.delete(db_disciplina)
    db.commit()
    return {'detail': 'Disciplina removida com sucesso.'}

# ---------- Matrícula ----------

# fluxo escolhido: estudante_id vem da URL, disciplina_id e data vêm do corpo
# (bate com o MatriculaCreate sem estudante_id que fizemos no schemas.py)

@app.post('/estudantes/{estudante_id}/matriculas', response_model = schemas.Matricula)
def matricular_estudante(estudante_id: int, matricula: schemas.MatriculaCreate, db: Session = Depends(get_db)):
    estudante = db.query(models.Estudante).filter(models.Estudante.id == estudante_id).first()
    if estudante is None:
        raise HTTPException(status_code = 404, detail = 'Estudante não encontrado.')
    
    disciplina = db.query(models.Disciplina).filter(models.Disciplina.id == matricula.disciplina_id).first()
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

# PUT usa EstudanteCreate, não um schema novo. Os dados que você precisa pra
# atualizar são os mesmos que você precisa pra criar (nome, email, perfil) —
# reaproveitar evita duplicar schema à toa. Se um dia você quiser permitir
# atualização parcial (só o nome, por exemplo, sem mexer no resto), aí sim
# precisaria de um schema EstudanteUpdate com todos os campos Optional, e um
# PATCH em vez de PUT.
#
# Por que atualizar campo por campo em vez de
# db_estudante = models.Estudante(**dados.dict()). Essa segunda forma criaria
# um objeto novo, sem id, sem estar ligado à sessão do banco — o SQLAlchemy não
# saberia que é pra atualizar a linha existente, e você perderia o controle sobre
# o que fazer com o perfil já existente.
#
# Por que checar if db_estudante.perfil antes de atualizar. Porque seu model
# deixa perfil ser opcional na leitura (Optional[Perfil] = None), mas na hora de
# criar (EstudanteCreate) você exige perfil sempre. Ainda assim, é mais seguro
# checar — protege contra um estudante que, por qualquer motivo (import direto no
# banco, migração, etc.), tenha ficado sem perfil.
#
# Por que db.delete() sozinho já basta, sem apagar perfil/matrículas manualmente.
# Você já configurou cascade='all, delete-orphan' em Estudante.perfil e
# Estudante.matriculas no models.py. Isso diz ao SQLAlchemy: "quando esse
# estudante for apagado, apague também tudo que está pendurado nesses
# relationships". Sem esse cascade, apagar o estudante daria erro de violação de
# FK (o banco recusaria, porque ainda existem linhas em perfis/matriculas
# apontando pra um estudante_id que não existe mais).
#
# Sem response_model no DELETE. response_model serve pra validar/formatar o
# retorno como um schema Pydantic — mas depois de deletar, não faz sentido
# devolver "o estudante" (ele não existe mais). Por isso retorno um dicionário
# simples de confirmação.
#
# Quer tentar escrever você mesmo o PUT/DELETE de Disciplina (que tem uma FK a
# mais, professor_id, pra você praticar a checagem de existência) e eu reviso?

# Por que exclude_unset=True é essencial aqui: sem ele, dados.dict() devolveria
# {"nome": None, "email": None} pra quem mandou só {"nome": "Ana"} — porque os
# campos Optional têm None como valor padrão. Aí você acabaria apagando o email
# do estudante sem querer. exclude_unset=True distingue "o cliente não mandou
# esse campo" de "o cliente mandou null de propósito".
#
# Resumo prático
#                   PUT                     PATCH
# Schema            campos obrigatórios     campos Optional
# Cliente envia     recurso completo        só o que muda
# Campo faltando    erro 422                ignorado (não altera)
# No código         atribui direto          exclude_unset=True + loop

# Por que cada decisão
#
# Por que 400, não 404, quando falta novo_professor_id. 404 significa
# "o recurso que você pediu não existe" — mas o professor existe,
# o problema é que a exclusão dele, do jeito que foi pedida, é
# inválida (falta informação). 400 Bad Request é o código certo pra
# "sua requisição está incompleta/mal formada".
#
# Por que buscar as disciplinas com uma query separada, em vez de usar
# db_professor.disciplinas. As duas formas funcionariam aqui
# (o relationship já te devolveria a lista). Usei a query direta só
# porque acho mais explícito nesse contexto — mas se você preferir
# db_professor.disciplinas, funciona igual, é escolha de estilo.
#
# Por que checar novo_professor_id == professor_id. Sem essa checagem,
# alguém poderia mandar DELETE /professores/5?novo_professor_id=5 —
# o código passaria pela checagem de "professor existe" (ele existe,
# é o mesmo!), mas o professor está prestes a ser apagado, então a
# "reatribuição" não faria sentido nenhum.
#
# Por que o reassign acontece antes do db.delete(), e não depois.
# Se você tentasse db.delete(db_professor) primeiro, o Postgres
# recusaria imediatamente (violação de FK), porque ainda existiriam
# disciplinas apontando pro professor_id que está sendo removido —
# nem chegaria a executar o resto.
#
# Sem response_model de novo — mesmo raciocínio do
# deletar_estudante/deletar_disciplina: depois de apagar, não sobra
# um "recurso professor" pra formatar.