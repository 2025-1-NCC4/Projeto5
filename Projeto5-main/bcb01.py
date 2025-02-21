from bcb import sgs
import datetime
import pandas as pd

# Definir datas
hoje = datetime.date.today().strftime('%Y-%m-%d')
ano_atras = '2000-01-01'

# Dicionário de séries do SGS do Banco Central
series = {
    'Dólar': 1,
    'Euro': 21619,
    'Yuan': 10813,
    'IPCA': 433,
    'IGP-M': 189,
    'SELIC': 432,
    'PIB Diário': 22099,
    'Balança Comercial': 22701
}

# Validando se os códigos sgs estão corretos
# dados = {}
# for nome, codigo in series.items():
#     try:
#         df = sgs.get(codigo, start=ano_atras, end=hoje)
#         dados[nome] = df
#         print(f"✔ Série {nome} baixada com sucesso!")
#     except Exception as e:
#         print(f"❌ Erro ao buscar {nome} ({codigo}): {e}")

df = sgs.get(series, start=ano_atras, end=hoje)
# Resetando índice
df = df.reset_index()
df = df.dropna()

df.to_csv('teste_bcb.csv')