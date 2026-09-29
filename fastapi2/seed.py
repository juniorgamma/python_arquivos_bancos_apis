from database import SessionLocal
import models
from datetime import date

db = SessionLocal() # cria a sessão
# SessionLocal é a mesma "fábrica de sessões" que o get_db() do main.py usa — só que lá ela é criada e fechada automaticamente 
# a cada requisição HTTP (por causa do yield/finally). Aqui, como é um script solto (sem FastAPI, sem requisição), você precisa 
# criar a sessão manualmente e fechar no final também manualmente.

professor1 = models.Professor(nome = 'Carlos Silva')
professor2 = models.Professor(nome = 'Maria Santos')

db.add_all([professor1, professor2]) 
# é o mesmo que chamar db.add() duas vezes — só um jeito mais curto de "marcar" os dois objetos pra serem inseridos.
db.commit()

db.refresh(professor1)
db.refresh(professor2)
# Por quê é necessário: o commit() manda o INSERT, mas o SQLAlchemy, por padrão, não sempre recarrega automaticamente 
# os valores gerados pelo banco (como o id autoincrementado) de volta pro objeto Python em memória. db.refresh(objeto) 
# faz exatamente isso: relê a linha do banco e atualiza o objeto Python com os valores atuais — incluindo o id que o Postgres gerou.

print('Professor 1 id:', professor1.id)
print('Professor 2 id:', professor2.id)

estudante1 = models.Estudante(
    nome = 'Ana Souza',
    email = 'ana@email.com',
    perfil = models.Perfil(idade = 20, endereco = 'Rua A, 123')
)

# Por quê perfil=models.Perfil(...) direto dentro do Estudante(...), em vez de criar separado e linkar depois: porque 
# Estudante.perfil é um relationship — o SQLAlchemy entende que, ao passar um objeto Perfil ali, ele deve criar os dois 
# (estudante e perfil) e já vincular o estudante_id da FK automaticamente. Você não precisa descobrir o id do estudante 
# manualmente pra passar pro perfil — o próprio ORM cuida disso no commit().

db.add(estudante1)
db.commit()
db.refresh(estudante1)

print('Estudante id:', estudante1.id)

disciplina1 = models.Disciplina(
    nome = 'Matemática',
    descricao = 'Álgebra e Geometria',
    professor_id = professor1.id
)
disciplina2 = models.Disciplina(
    nome = 'História',
    descricao = 'História do Brasil',
    professor_id = professor2.id
)

# Por que professor_id=professor1.id aqui, e não passar o objeto inteiro (como fizemos com perfil=models.Perfil(...) no estudante): 
# repara na diferença de tipo de coluna. Disciplina.professor_id é uma FK simples (Integer) — ela só quer o número do id, não o 
# objeto Professor inteiro. Já o Estudante.perfil é um relationship, que aceita o objeto Python direto e o SQLAlchemy se vira pra 
# extrair o id sozinho. São dois "pontos de entrada" diferentes pra fazer vínculos: você pode setar a FK diretamente (professor_id=...) 
# ou setar o relationship com o objeto (perfil=...) — ambos funcionam, a diferença é só qual dado você já tem em mãos no momento.
# Por que isso só funciona porque rodamos o commit dos professores antes: professor1.id e professor2.id só têm valor porque já foram 
# pro banco (commit + refresh) no bloco anterior. Se você tivesse tentado usar professor1.id antes daquele commit, o valor seria 
# None — é exatamente o ponto que expliquei na pergunta anterior sobre por que separar os commits aqui importa.

db.add_all([disciplina1, disciplina2])
db.commit()
db.refresh(disciplina1)
db.refresh(disciplina2)

print('Disciplina 1 id:', disciplina1.id)
print('Disciplina 2 id:', disciplina2.id)

matricula1 = models.Matricula(
    estudante_id = estudante1.id,
    disciplina_id = disciplina1.id,
    data_matricula = date.today() 
)

# Por que estudante_id=estudante1.id e disciplina_id=disciplina1.id, e não os objetos inteiros: mesma lógica das disciplinas — 
# Matricula.estudante_id e Matricula.disciplina_id são FKs simples (Integer), então esperam o número do id, não o objeto Python.

db.add(matricula1)
db.commit()
db.refresh(matricula1)

print('Matrícula id:', matricula1.id)

db.close()

