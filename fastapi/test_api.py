import httpx

url = "http://127.0.0.1:8000"

# Criar estudante
response = httpx.post(
    f"{url}/estudantes/",
    json={"nome": "Ana", "idade": 25}
)

print(response.status_code)
print(response.json())

student_id = response.json()["id"]

# Criar matrícula
response = httpx.post(
    f"{url}/matriculas/",
    json={
        "estudante_id": student_id,
        "nome_disciplina": "Python"
    }
)

print(response.status_code)
print(response.json())

# Listar estudantes
response = httpx.get(f"{url}/estudantes/")
print(response.json())

# Excluir estudante e suas matrículas
# response = httpx.delete(f"{url}/estudantes/{student_id}")
# print(response.status_code)
# print(response.json())