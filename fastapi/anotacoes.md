Você não é obrigado a criar `schemas.py`, mas ele separa responsabilidades:

- **`models.py`**: representa as tabelas do banco de dados, usando SQLAlchemy ou outro ORM.
- **`schemas.py`**: define o formato dos dados recebidos e enviados pela API, usando Pydantic.

No FastAPI, os schemas permitem:

1. **Validar dados de entrada**
   ```json
   {
     "nome": "Ana",
     "idade": 20
   }
   ```

2. **Controlar os dados de saída**  
   Você pode evitar expor campos internos, como senhas ou informações administrativas.

3. **Documentar automaticamente a API**  
   O Swagger usa os schemas para mostrar os formatos esperados.

4. **Separar a API do banco**  
   Se o modelo do banco mudar, o contrato da API não precisa mudar necessariamente.

5. **Converter objetos do ORM em respostas JSON**  
   `from_attributes = True` permite que o Pydantic leia atributos diretamente do objeto do modelo.

Em resumo: **models cuidam do banco; schemas cuidam da entrada e saída da API**. Em projetos pequenos, eles podem parecer repetitivos, mas essa separação evita problemas e facilita a manutenção.

Iniciando o POSTGRESQL

Entrar na pasta bin do POSTGRESQL

Digitar:

.\initdb.exe -D "C:\Users\SEU_USUARIO\pgsql\data" -U postgres -W (lenovo)

"C:\Program Files\PostgreSQL\18\bin\initdb.exe" -D "C:\Program Files\PostgreSQL\18\data" --locale=C --encoding=UTF8 (dell)

initdb.exe → cria a estrutura inicial que o PostgreSQL precisa.
-D ...\data → diz onde essa estrutura será criada.
-U postgres → cria o usuário administrador do PostgreSQL chamado postgres.
-W → vai pedir uma senha para esse usuário postgres.

Depois pra iniciar, ainda dentro da bin:

.\pg_ctl.exe -D "C:\Users\SEU_USUARIO\pgsql\data" start
ou
.\pg_ctl.exe -D "C:\Users\jeovah.junior_prf\pgsql\data" -l "C:\Users\jeovah.junior_prf\pgsql\postgres.log" start   (com arquivo log)

Rodar esse comando preferencialmente em um terminal exclusivo pra isso

O que estamos fazendo
pg_ctl.exe → programa que controla o PostgreSQL.
-D "...data" → informa onde está o banco que acabamos de inicializar.
-l "...postgres.log" → manda as mensagens do PostgreSQL para um arquivo de log.
start → manda o PostgreSQL iniciar.

Comandos dentro do shell do POSTGRESQL: (psql -U postgres) WSL = psql -h ip_do_windows -U postgres -d nome_do_banco -p 5432

CREATE DATABASE escola;

Pra alterar senha: ALTER USER postgres WITH PASSWORD 'postgres';

Rodar app: uvicorn main:app --reload

ip route show default


Comandos úteis pra explorar (não são SQL puro, são atalhos do próprio psql — começam com \)
sql
\dt

Lista todas as tabelas do banco escola. Deve mostrar estudantes, perfis, matriculas, disciplinas, professores.

sql
\d matriculas

Mostra a estrutura da tabela matriculas — colunas, tipos, constraints. É aqui que você vai confirmar visualmente se disciplina_id existe ou não (a causa do erro anterior).