from bcb import sgs
import datetime
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from statsmodels.tsa.arima.model import ARIMA

# Definir período de captação (personalizado com timedelta)
hoje = datetime.date.today()
dt_inicio = hoje - datetime.timedelta(days=365)

# Dicionário de séries relevantes para importação e exportação (Diários)
series = {
    'Dólar': 1,                  # Taxa de câmbio (Venda) - dólar
    'Euro': 21619,               # Taxa de câmbio (Venda) - euro
    'Iene': 21621,               # Taxa de câmbio (Venda) - iene
    'Exportações': 13966,        # Total de exportações
    'Importações': 13962,        # Total de importações
    'SELIC': 432                 # Taxa SELIC
}

# # Criar um DataFrame consolidado
# tx = sgs.get(series, start=dt_inicio, end=hoje)
# df = tx.reset_index()

# # Renomear a primeira coluna para 'Data' (caso tenha outro nome)
# df.rename(columns={df.columns[0]: 'Data'}, inplace=True)

# # Captar a Balança Comercial mensal
# balanca_comercial = sgs.get(22701, start=dt_inicio, end=hoje)

# # Converter o índice para período mensal
# balanca_comercial.index = balanca_comercial.index.to_period('M')

# # Calcular a média diária da balança comercial para cada mês
# coluna_balanca = balanca_comercial.columns[0]  # Pega o nome correto da coluna
# balanca_comercial['Balança Comercial'] = balanca_comercial [coluna_balanca] / balanca_comercial.index.days_in_month
# balanca_comercial = balanca_comercial[['Balança Comercial']]

# # Adicionar a média da balança comercial ao DataFrame principal
# df['Mes'] = df['Data'].dt.to_period('M')
# df = df.merge(balanca_comercial, left_on='Mes', right_index=True, how='left')
# df.drop(columns=['Mes'], inplace=True)

# # Preencher valores ausentes com a média do período
# df.fillna(df.mean(), inplace=True)

# Exportar para CSV
# df.to_csv(f'import_export_{dt_inicio}_{hoje}.csv', index=False)
# print("✅ Dados exportados para 'dados_import_export.csv'")

# --------------------------------------------------------

# O arquivo CSV deve conter colunas semelhantes às que são geradas pelo código anterior, como "Data", "Dólar", "Euro", "Iene", "Exportações", "Importações", "Balança Comercial"
df = pd.read_csv('import_export_2024-02-22_2025-02-21.csv', sep=';', encoding='ISO-8859-1')

df.rename(columns={df.columns[0]: 'Data'}, inplace=True)
df.rename(columns={df.columns[1]: 'Dólar'}, inplace=True)
df.rename(columns={df.columns[4]: 'Exportações'}, inplace=True)
df.rename(columns={df.columns[5]: 'Importações'}, inplace=True)
df.rename(columns={df.columns[7]: 'Balança Comercial'}, inplace=True)

# Certificar-se de que a coluna 'Data' está no formato datetime
df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')

# Convertendo para o tipo int
df['Dólar'] = pd.to_numeric(df['Dólar'], errors='coerce')
df['Exportações'] = pd.to_numeric(df['Exportações'], errors='coerce')
df['Importações'] = pd.to_numeric(df['Importações'], errors='coerce')
df['Balança Comercial'] = pd.to_numeric(df['Balança Comercial'], errors='coerce')

# Preencher valores ausentes com a média do período
df.fillna(df.mean(), inplace=True)

# Criar previsões para os próximos 365 dias
def preview(series):
    model = ARIMA(series, order=(5,1,0))  # Modelo ARIMA básico
    model_fit = model.fit()
    pred = model_fit.forecast(steps=365)
    return pred

# Criar um loop que gera as previsões e incrementa a data
forecast_data = {}
forecast_dates = []

for coluna in ['Dólar', 'Euro', 'Iene', 'Exportações', 'Importações', 'Balança Comercial']:
    # Gerar previsões para cada coluna
    forecast_data[coluna] = preview(df[coluna])
    
    # Criar lista de datas para cada previsão
    future_dates = [hoje + datetime.timedelta(days=i+1) for i in range(365)]  # Incrementa 1 dia a cada iteração
    forecast_dates.append(future_dates)

# Criar DataFrame com previsões e associar as datas futuras corretamente
df_forecast = pd.DataFrame(forecast_data, index=forecast_dates[0])
df_forecast.reset_index(inplace=True)
df_forecast.rename(columns={'index': 'Data'}, inplace=True)

# Agora, a DataFrame df contém os dados históricos e as previsões para os próximos 365 dias
# Concatenar dados históricos e as previsões para cada coluna
df['Data'] = df['Data']._append(df_forecast['Data'], ignore_index=True)
df['Dólar'] = df['Dólar']._append(df_forecast['Dólar'], ignore_index=True)
df['Exportações'] = df['Exportações']._append(df_forecast['Exportações'], ignore_index=True)
df['Importações'] = df['Importações']._append(df_forecast['Importações'], ignore_index=True)
df['Balança Comercial'] = df['Balança Comercial']._append(df_forecast['Balança Comercial'], ignore_index=True)

# Criar Dashboard com Dash
app = dash.Dash(__name__)

# Ajustar layout do Dash para incluir tanto os dados históricos quanto as previsões
app.layout = html.Div([
    html.H1("Dashboard de Importação e Exportação"),
    
    # Gráfico da Previsão de Taxas de Câmbio
    html.Div([
        dcc.Graph(
            id='PrevisãoCambio',
            figure={
                'data': [
                    {'x': df['Data'], 'y': df['Dólar'], 'type': 'line', 'name': 'Dólar (Histórico + Previsão)'},
                    {'x': df['Data'], 'y': df['Euro'], 'type': 'line', 'name': 'Euro Previsão'},
                    {'x': df_forecast['Data'], 'y': df_forecast['Iene'], 'type': 'line', 'name': 'Iene Previsão'},
                ],
                'layout': {
                    'title': 'Previsão de Taxas de Câmbio'
                }
            }
        )
    ]),

    # Gráfico da Previsão de Importações e Exportações
    html.Div([
        dcc.Graph(
            id='PrevisãoImportExport',
            figure={
                'data': [
                    {'x': df['Data'], 'y': df['Exportações'], 'type': 'line', 'name': 'Exportações (Histórico + Previsão)'},
                    {'x': df['Data'], 'y': df['Importações'], 'type': 'line', 'name': 'Importações (Histórico + Previsão)'},
                ],
                'layout': {
                    'title': 'Previsão de Importações e Exportações'
                }
            }
        )
    ]),

    # Gráfico da Previsão da Balança Comercial Média Diária
    html.Div([
        dcc.Graph(
            id='PrevisãoBalançaComercial',
            figure={
                'data': [
                    {'x': df['Data'], 'y': df['Balança Comercial'], 'type': 'line', 'name': 'Balança Comercial (Histórico + Previsão)'},
                ],
                'layout': {
                    'title': 'Previsão da Balança Comercial Média Diária'
                }
            }
        )
    ]),
])

if __name__ == '__main__':
    app.run_server(debug=True)