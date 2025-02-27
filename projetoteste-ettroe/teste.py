from bcb import sgs
import datetime

# Teste pegando apenas uma série
hoje = datetime.date.today()
dt_inicio = hoje - datetime.timedelta(days=60)

try:
    df_teste = sgs.get(1, start=dt_inicio, end=hoje)  # Teste com a série do dólar
    print(df_teste.head())
except Exception as e:
    print(f"Erro ao buscar dados: {e}")
