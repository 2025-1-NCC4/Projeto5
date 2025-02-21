from bcb import sgs
import datetime

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
df.to_csv(f'import_export_{dt_inicio}_{hoje}.csv', index=False)

print("✅ Dados exportados para 'dados_import_export.csv'")
