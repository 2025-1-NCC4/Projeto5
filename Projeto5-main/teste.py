import requests as rq
import pandas as pd

dtInicio = input("Informe a data de início do período que deseja ver: ")
dtFim = input("Informe a data de fim do período que deseja ver: ")

# URL para a requisição da cotação histórica do ano de 2017
url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados?formato=csv&dataInicial={dtInicio}&dataFinal={dtFim}"

# Realiza a requisição
response = rq.get(url)

# Verifica se a resposta foi bem-sucedida
if response.status_code == 200 and response.text.strip():
    # A resposta vem como CSV, vamos ler os dados com pandas
    from io import StringIO
    dados = StringIO(response.text)
    
    # Lê os dados CSV diretamente para um DataFrame
    df = pd.read_csv(dados, sep=";")
    
    # Renomeia as colunas para algo mais legível
    df.columns = ['Data', 'Valor']

    # Exibe as primeiras linhas para verificar os dados
    print(df.head())

    # Define o nome do arquivo, incluindo a data de início
    nome_arquivo = f'cotacao_dolar_{dtInicio.replace("/", "-")}_a_{dtFim.replace("/", "-")}.csv'

    # Exporta o DataFrame para um arquivo CSV
    df.to_csv(nome_arquivo, index=False, encoding='utf-8')

    print("Arquivo CSV exportado com sucesso!")
else:
    print("Erro ao acessar a API ou resposta vazia.")
