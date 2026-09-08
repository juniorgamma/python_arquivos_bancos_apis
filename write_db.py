import sqlite3

conn = sqlite3.connect('school.db')

cursor = conn.cursor()

# cursor.execute(
#     '''
#         INSERT INTO estudantes(nome, idade) VALUES (?, ?)
#     ''',
#     ('Joana', 16)
# )

cursor.execute(
    '''
        INSERT INTO disciplinas(estudante_id, nome_disciplina)
        VALUES(?, ?)
    ''',
    (2, 'Física')
)

conn.commit()

conn.close()
