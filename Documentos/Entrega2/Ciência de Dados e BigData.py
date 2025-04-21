from bcb import sgs
from datetime import datetime
import pandas as pd
import scipy.stats as stats
import numpy as np

series = {'Preço de Commodities Agropecuárias': 29041, 'Taxa de Cambio (Dólar)': 3698, 'Exportacoes': 22708}
dados = sgs.get(series, start='2015-01-01', end=datetime.today().strftime('%Y-%m-%d'))

dados = dados.reset_index()
dados = dados.dropna()

# Levantando análise descritiva sobre os dados
n = len(dados)

media_commodities = dados['Preço de Commodities Agropecuárias'].mean()
desvio_commodities = dados['Preço de Commodities Agropecuárias'].std()

media_cambio = dados['Taxa de Cambio (Dólar)'].mean()
desvio_cambio = dados['Taxa de Cambio (Dólar)'].std()

media_exportacoes = dados['Exportacoes'].mean()
desvio_exportacoes = dados['Exportacoes'].std()

# Levantando Intervalo de Confiança das médias analisadas
ic_commodities = stats.t.interval(confidence=0.95, df=n-1, loc=media_commodities, scale=desvio_commodities/np.sqrt(n))
ic_cambio = stats.t.interval(confidence=0.95, df=n-1, loc=media_cambio, scale=desvio_cambio/np.sqrt(n))
ic_exportacoes = stats.t.interval(confidence=0.95, df=n-1, loc=media_exportacoes, scale=desvio_exportacoes/np.sqrt(n))

def format_ic(label, intervalo):
    print(f"{label}: entre {round(intervalo[0], 2)} e {round(intervalo[1], 2)}")

format_ic("IC do Preço Médio das Commodities Agropecuárias", ic_commodities)
format_ic("IC da Taxa de Câmbio Média (Dólar)", ic_cambio)
format_ic("IC da Média das Exportações", ic_exportacoes)

# Levantando indice de correlação
correlacoes = dados.corr(numeric_only=True)
print(f"Correlação entre Preço de Commodities Agropecuárias e Exportações: {correlacoes.loc['Preço de Commodities Agropecuárias', 'Exportacoes']:.2f}")
print(f"Correlação entre Taxa de Câmbio (Dólar) e Exportações: {correlacoes.loc['Taxa de Cambio (Dólar)', 'Exportacoes']:.2f}")