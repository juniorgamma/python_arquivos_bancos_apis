import models
from database import engine

models.Base.metadata.drop_all(bind = engine)
print('Tabelas apagadas.')

models.Base.metadata.create_all(bind = engine)
print('Tabelas recriadas')

# models.Base é a classe da qual todas as suas classes (Estudante, Professor, etc.) herdam. Ela guarda, dentro de metadata, 
# o "mapa" de todas as tabelas que você definiu no models.py. drop_all() percorre esse mapa e manda um DROP TABLE pra cada 
# uma — é literalmente o SQLAlchemy gerando e executando o mesmo SQL que você digitou manualmente no psql, só que 
# automaticamente, lendo a estrutura direto do models.py (não precisa você listar os nomes das tabelas na mão).

# Alternativa: psql -h 172.17.80.1 -U postgres -d escola
# Confirmar o que existe antes de apagar: /dt
# Apagar tudo: DROP TABLE IS EXISTS matriculas, perfis, disciplinas, estudantes, professores, CASCADE;
# Confirmar que zerou: \dt
# Sair do psql: \q
# Depois, rodar o uvicorn main:app --reload pra recriar as tabelas com o models.Base.metadata.create_all(bind=engine) do main.py