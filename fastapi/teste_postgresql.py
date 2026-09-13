import psycopg2

try:
    conn = psycopg2.connect(
        host="172.17.80.1",
        dbname="postgres",
        user="postgres",
        password="senha"
    )
    print("Conectou!")
except Exception as e:
    print("TIPO:", type(e))
    print("ERRO:", repr(e))