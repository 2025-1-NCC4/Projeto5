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

# Criar um DataFrame consolidado
tx = sgs.get(series, start=dt_inicio, end=hoje)
df = tx.reset_index()

# Renomear a primeira coluna para 'Data' (caso tenha outro nome)
df.rename(columns={df.columns[0]: 'Data'}, inplace=True)

# Captar a Balança Comercial mensal
balanca_comercial = sgs.get(22701, start=dt_inicio, end=hoje)

# Converter o índice para período mensal
balanca_comercial.index = balanca_comercial.index.to_period('M')

# Calcular a média diária da balança comercial para cada mês
coluna_balanca = balanca_comercial.columns[0]  # Pega o nome correto da coluna
balanca_comercial['Balança Comercial'] = balanca_comercial [coluna_balanca] / balanca_comercial.index.days_in_month
balanca_comercial = balanca_comercial[['Balança Comercial']]

# Adicionar a média da balança comercial ao DataFrame principal
df['Mes'] = df['Data'].dt.to_period('M')
df = df.merge(balanca_comercial, left_on='Mes', right_index=True, how='left')
df.drop(columns=['Mes'], inplace=True)

# Preencher valores ausentes com a média do período
df.fillna(df.mean(), inplace=True)

# Exportar para CSV
# df.to_csv(f'import_export_{dt_inicio}_{hoje}.csv', index=False)
# print("✅ Dados exportados para 'dados_import_export.csv'")

# Criar previsões para os próximos 365 dias
def preview(series):
    model = ARIMA(series, order=(5,1,0))  # Modelo ARIMA básico
    model_fit = model.fit()
    pred = model_fit.forecast(steps=365)
    return pred

# Aplicar previsões aos principais indicadores
forecast_data = {}
for coluna in ['Dólar', 'Euro', 'Iene', 'Exportações', 'Importações', 'Balança Comercial']:
    forecast_data[coluna] = preview(df[coluna])

# Criar DataFrame com previsões
df_forecast = pd.DataFrame(forecast_data, index=pd.date_range(start=hoje, periods=365))
df_forecast.reset_index(inplace=True)
df_forecast.rename(columns={'index': 'Data'}, inplace=True)

# Criar Dashboard com Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard de Importação e Exportação"),
    html.Div([
        dcc.Graph(
            id='PrevisãoCambio',
            figure={
                'data': [
                    {'x': df_forecast['Data'], 'y': df_forecast['Dólar'], 'type': 'line', 'name': 'Dólar'},
                    {'x': df_forecast['Data'], 'y': df_forecast['Euro'], 'type': 'line', 'name': 'Euro'},
                    {'x': df_forecast['Data'], 'y': df_forecast['Iene'], 'type': 'line', 'name': 'Iene'},
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
                    {'x': df_forecast['Data'], 'y': df_forecast['Exportações'], 'type': 'line', 'name': 'Exportações'},
                    {'x': df_forecast['Data'], 'y': df_forecast['Importações'], 'type': 'line', 'name': 'Importações'},
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
                    {'x': df_forecast['Data'], 'y': df_forecast['Balança Comercial'], 'type': 'line', 'name': 'Balança Comercial'},
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