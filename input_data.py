nome = input('Digite seu nome: ')
idade = input('Digite sua idade: ')

with open('input_data.txt', 'w', encoding = 'utf-8') as f:
    f.write(f'Nome: {nome}\n')
    f.write(f'Idade: {idade}\n')


cor = input('Digite sua cor favorita: ')
cidade = input('Digite sua cidade natal: ')

with open('input_data.txt', 'a', encoding = 'utf-8') as f:
    f.write(f'Cor: {cor}\n')
    f.write(f'Cidade: {cidade}\n')