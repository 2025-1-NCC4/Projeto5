import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, dash_table
import warnings
import os
from datetime import datetime, timedelta
import numpy as np

# Suprimir avisos de ARIMA para melhor legibilidade
warnings.filterwarnings("ignore")

# Nome do arquivo CSV
darq_csv = 'import_export_2024-02-22_2025-02-21.csv'

# Verificar se o arquivo existe
if not os.path.exists(darq_csv):
    print(f"⚠️ Arquivo '{darq_csv}' não encontrado. Certifique-se de que o arquivo esteja no mesmo diretório do código.")
    exit()

# Carregar dados da planilha fornecida
try:
    df = pd.read_csv(darq_csv, sep=';', encoding='ISO-8859-1')

    colunas_renomeadas = {
        df.columns[0]: 'Data',
        df.columns[1]: 'Dólar',
        df.columns[2]: 'Euro',
        df.columns[3]: 'Iene',
        df.columns[4]: 'Exportações',
        df.columns[5]: 'Importações',
        df.columns[6]: 'SELIC',
        df.columns[7]: 'Balança Comercial'
    }

    if len(df.columns) < 8:
        raise ValueError("O arquivo CSV não possui o número esperado de colunas.")

    df.rename(columns=colunas_renomeadas, inplace=True)
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')

    colunas_numericas = ['Dólar', 'Euro', 'Iene', 'Exportações', 'Importações', 'SELIC', 'Balança Comercial']
    for coluna in colunas_numericas:
        df[coluna] = pd.to_numeric(df[coluna], errors='coerce')

    df.dropna(subset=['Data'], inplace=True)
    df.fillna(df.mean(numeric_only=True), inplace=True)

    print("✅ Dados carregados e processados com sucesso.")

except Exception as e:
    print(f"⚠️ Erro ao carregar ou processar a planilha: {e}")
    exit()

# Função para gerar previsões com ARIMA ajustado
def gerar_previsao(df, coluna, data_final):
    try:
        serie = df.set_index('Data')[coluna].dropna()
        if serie.empty:
            print(f"⚠️ Série '{coluna}' vazia ou com dados insuficientes.")
            return pd.Series(dtype=float)

        ultima_data = serie.index.max()
        dias_necessarios = (data_final - ultima_data).days

        if dias_necessarios <= 0:
            return pd.Series(dtype=float)

        modelo = ARIMA(serie, order=(3, 1, 3))
        modelo_fit = modelo.fit()
        previsao = modelo_fit.forecast(steps=dias_necessarios)

        # Adiciona variação aleatória controlada para tornar as previsões mais dinâmicas
        variacao_percentual = np.random.normal(0, 0.02, size=dias_necessarios)
        previsao *= (1 + variacao_percentual)

        datas_futuras = pd.date_range(start=ultima_data + timedelta(days=1), periods=dias_necessarios)
        return pd.Series(previsao, index=datas_futuras)

    except Exception as e:
        print(f"⚠️ Erro ao gerar previsão para '{coluna}': {e}")
        return pd.Series(dtype=float)

# Função para expandir o DataFrame com previsões até a data final
def expandir_previsao(df, data_final):
    previsoes = {coluna: gerar_previsao(df, coluna, data_final) for coluna in colunas_numericas}
    df_previsao = pd.DataFrame(previsoes)

    if not df_previsao.empty:
        df_previsao.reset_index(inplace=True)
        df_previsao.rename(columns={'index': 'Data'}, inplace=True)
        df_previsao['Data'] = pd.to_datetime(df_previsao['Data'])
        df_expandido = pd.concat([df, df_previsao], ignore_index=True)
        print(f"✅ Previsões geradas até {data_final.strftime('%d/%m/%Y')}.")
        return df_expandido

    print("ℹ️ Nenhuma previsão necessária para o período selecionado.")
    return df.copy()

# Função para criar uma tabela com amostras específicas (7, 30, 90 dias após a última data do período selecionado)
def criar_tabela_amostral(df_filtrado, datas_amostrais):
    df_tabela = df_filtrado[df_filtrado['Data'].isin(datas_amostrais)].copy()
    df_tabela.sort_values('Data', inplace=True)
    df_tabela['Data'] = df_tabela['Data'].dt.strftime('%d/%m/%Y')
    return df_tabela[['Data'] + colunas_numericas]

# Criar o dashboard com seleção de datas
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("📊 Dashboard de Importação e Exportação", style={'textAlign': 'center'}),

    html.Div([
        html.Label("📅 Selecione o intervalo de datas:", style={'fontSize': '16px'}),
        dcc.DatePickerRange(
            id='date-picker',
            min_date_allowed=df['Data'].min().date(),
            max_date_allowed=(df['Data'].max() + timedelta(days=180)).date(),
            start_date=df['Data'].min().date(),
            end_date=df['Data'].max().date(),
            display_format='DD/MM/YYYY',
            first_day_of_week=1
        ),
    ], style={'margin-bottom': '30px', 'textAlign': 'center'}),

    html.Div([
        dcc.Graph(id='grafico-cambio'),
        dcc.Graph(id='grafico-import-export'),
        dcc.Graph(id='grafico-balanca'),
    ]),

    html.Div([
        html.H3("📅 Dados Amostrais (7, 30, 90 dias)", style={'textAlign': 'center', 'margin-top': '40px'}),
        dash_table.DataTable(
            id='tabela-amostral',
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'padding': '8px'},
            style_header={'backgroundColor': '#f4f4f4', 'fontWeight': 'bold'},
            page_size=10
        )
    ])
])

# Callback para atualizar gráficos e tabela com base nas datas selecionadas
@app.callback(
    [
        Output('grafico-cambio', 'figure'),
        Output('grafico-import-export', 'figure'),
        Output('grafico-balanca', 'figure'),
        Output('tabela-amostral', 'data'),
        Output('tabela-amostral', 'columns')
    ],
    [
        Input('date-picker', 'start_date'),
        Input('date-picker', 'end_date')
    ]
)
def atualizar_graficos_e_tabela(start_date, end_date):
    data_final = pd.to_datetime(end_date)
    df_expandido = expandir_previsao(df, data_final)

    df_filtrado = df_expandido[(df_expandido['Data'] >= pd.to_datetime(start_date)) &
                               (df_expandido['Data'] <= data_final)]

    # Definir datas amostrais baseadas na data final selecionada
    datas_amostrais = [data_final + timedelta(days=dias) for dias in [7, 30, 90]]
    df_tabela = criar_tabela_amostral(df_filtrado, datas_amostrais)

    # Criar gráficos
    fig_cambio = px.line(df_filtrado, x='Data', y=['Dólar', 'Euro', 'Iene'],
                         title="💱 Previsão de Taxas de Câmbio",
                         labels={'value': 'Valor', 'variable': 'Moeda'})

    fig_import_export = px.line(df_filtrado, x='Data', y=['Exportações', 'Importações'],
                                title="🚢 Previsão de Importações e Exportações",
                                labels={'value': 'Valor (USD)', 'variable': 'Categoria'})

    fig_balanca = px.line(df_filtrado, x='Data', y='Balança Comercial',
                          title="📦 Previsão da Balança Comercial",
                          labels={'Balança Comercial': 'Valor (USD)'})

    for fig in [fig_cambio, fig_import_export, fig_balanca]:
        fig.update_layout(xaxis_title='Data', yaxis_title='Valor', title_x=0.5)
        fig.update_traces(mode='lines+markers')

    # Preparar dados para a tabela
    columns = [{'name': col, 'id': col} for col in df_tabela.columns]
    data = df_tabela.to_dict('records')

    return fig_cambio, fig_import_export, fig_balanca, data, columns

if __name__ == '__main__':
    app.run_server(debug=True)
