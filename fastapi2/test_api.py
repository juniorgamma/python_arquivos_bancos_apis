import httpx

url = 'http://127.0.0.1:8000'

response = httpx.get(f'{url}/estudantes/')

print('Status code:', response.status_code)
print('Corpo da resposta:', response.json())

novo_professor = {'nome': 'Fernanda Lima'}

response = httpx.post(f'{url}/professores/', json = novo_professor)

print('Status Code:', response.status_code)
print('Corpo da resposta:', response.json())

disciplina_invalida = {
    'nome': 'Física',
    'descricao': 'Mecânica e Termodinâmica',
    'professor_id': 999 
}

response = httpx.post(f'{url}/disciplinas/', json = disciplina_invalida)

print('Status Code:', response.status_code)
print('Corpo da resposta:', response.json())

# tenta deletar o professor 2 (Maria), que tem a disciplina de Matemática vinculada,
# sem informar novo_professor_id

response = httpx.delete(f'{url}/professores/2')

print('Status Code:', response.status_code)
print('Corpo da resposta:', response.json())

# deletando professor com disciplina vinculada informando novo_professor_id
response = httpx.delete(f'{url}/professores/2', params = {'novo_professor_id': 7})

print('Status code:', response.status_code)
print('Corpo da resposta:', response.json())

# cria um professor novo, só pra esse teste, e já guarda o id retornado
professor_teste = {'nome': 'Professor Descartável'}
response_criacao = httpx.post(f'{url}/professores/', json = professor_teste)
id_professor_teste = response_criacao.json()['id']

print('Status code:', response_criacao.status_code)
print('Corpo da resposta:', response_criacao.json())

# agora deleta esse mesmo professor -- sem disciplina vinculada, deve dar sucesso direto
response = httpx.delete(f'{url}/professores/{id_professor_teste}')

print('Status code:', response.status_code)
print('Corpo da resposta:', response.json())

