import sys
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, State
from bcb import sgs
from datetime import datetime

# Códigos SGS para as séries de interesse
dados_sgs = {
    'Dólar': 1,
    'Euro': 21619,
    'SELIC': 11,
    'Exportações': 22708,
    'Importações': 22709,
    'Balança Comercial': 22710
}

# Consulta teste para verificar disponibilidade da API do BCB
try:
    # Realiza uma consulta com um período curto
    df_teste = sgs.get(dados_sgs, start='2010-01-01', end=datetime.today().strftime('%Y-%m-%d'))
    df_teste.reset_index(inplace=True)
    df_teste.rename(columns={'index': 'Data'}, inplace=True)
    if df_teste.empty:
        raise ValueError("Consulta retornou DataFrame vazio.")
except Exception as e:
    print("⚠️ A API do BCB está indisponível ou ocorreu um erro na consulta:")
    print(e)
    sys.exit(1)

# Layout do dashboard
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("📊 Dashboard Econômico", style={'textAlign': 'center'}),

    html.Div([
        html.H3("Ajuste o período para consulta dos dados:"),
        dcc.DatePickerRange(
            id='ds-picker',
            min_date_allowed=datetime(1950, 1, 1).date(),
            max_date_allowed=datetime.today().date(),
            start_date=datetime(2010, 1, 1).date(),
            end_date=datetime.today().date(),
            display_format='DD/MM/YYYY',
        ),
        html.Button("Atualizar Dados", id='btn-atualizar', n_clicks=0)
    ], style={'textAlign': 'center', 'margin-bottom': '30px'}),

    dcc.Store(id='dados-store'),

    html.Div([
        dcc.Graph(id='grafico-cambio'),
        dcc.Graph(id='grafico-import-export'),
        dcc.Graph(id='grafico-balanca'),
    ])
])

# Callback para atualizar os dados do BCB conforme o período selecionado
@app.callback(
    Output('dados-store', 'data'),
    Input('btn-atualizar', 'n_clicks'),
    State('ds-picker', 'start_date'),
    State('ds-picker', 'end_date')
)
def atualizar_dados(n_clicks, start_date, end_date):
    # Carrega os dados mesmo se nenhum clique foi feito (para exibir dados iniciais)
    try:
        df = sgs.get(dados_sgs, start=start_date, end=end_date)
    except Exception as e:
        print("⚠️ Erro ao consultar a API do BCB:", e)
        return []
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Data'}, inplace=True)
    df.dropna(inplace=True)
    # Converter a coluna Data para string para armazenar no dcc.Store
    df['Data'] = df['Data'].dt.strftime('%Y-%m-%d')
    return df.to_dict('records')

# Callback para atualizar os gráficos com base nos dados armazenados
@app.callback(
    [
        Output('grafico-cambio', 'figure'),
        Output('grafico-import-export', 'figure'),
        Output('grafico-balanca', 'figure')
    ],
    Input('dados-store', 'data')
)
def atualizar_graficos(data):
    if not data:
        return {}, {}, {}
    
    # Reconstrói o DataFrame a partir dos dados armazenados e converte a coluna Data para datetime
    df = pd.DataFrame(data)
    df['Data'] = pd.to_datetime(df['Data'])
    
    fig_cambio = px.line(df, x='Data', y=['Dólar', 'Euro'], title="💱 Taxas de Câmbio")
    fig_import_export = px.line(df, x='Data', y=['Exportações', 'Importações'], title="🚢 Importações e Exportações")
    fig_balanca = px.line(df, x='Data', y='Balança Comercial', title="📦 Balança Comercial")
    
    for fig in [fig_cambio, fig_import_export, fig_balanca]:
        fig.update_layout(xaxis_title='Data', yaxis_title='Valor', title_x=0.5)
        fig.update_traces(mode='lines+markers')
    
    return fig_cambio, fig_import_export, fig_balanca

if __name__ == '__main__':
    app.run_server(debug=True)