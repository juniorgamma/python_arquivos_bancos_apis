import sqlite3

conn = sqlite3.connect('school.db')

cursor = conn.cursor()

# cursor.execute(
#     '''
#         SELECT * FROM estudantes
#     '''
# )

cursor.execute(
    '''
        SELECT * FROM disciplinas
    '''
)

conn.commit()

# estudantes = cursor.fetchall()

# for estudante in estudantes:
#     print(estudante)

disciplinas = cursor.fetchall()

for disciplina in disciplinas:
    print(disciplina)

conn.close()