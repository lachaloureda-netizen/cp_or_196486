import yfinance as yf
from datastas import precios, retornos           
from riesgo import calcular_riego                
from fundamentals import obtenet_datos, calcular_dcf 
from retornos import calcular_retornos           
from benchmark import comparar_bench             
from ia import analisis_ia
def imprimir(titulo, datos):
    print(f"\n{'='*45}")
    print(f"  {titulo}")
    print(f"{'='*45}")
    for k, v in datos.items():
        if v is None:
            v = "N/A"
        elif isinstance(v, float):
            v = round(v, 4)
        print(f"  {k:<35} {str(v):>10}")

# ── Input base ────────────────────────────────────────
ticker    = input("Ticker (ej: AAPL): ").upper()
benchmark = input("Benchmark (ej: ^GSPC): ").upper()
periodo   = input("Período (1y / 2y / 5y): ")

print("\n⏳ Descargando datos...\n")

df      = precios(ticker, benchmark, periodo)
returns = retornos(df)

# ── Menú ──────────────────────────────────────────────
print("\n¿Qué querés analizar?")
print("  1 → Retornos")
print("  2 → Riesgo")
print("  3 → Comparación vs Benchmark")
print("  4 → Análisis Fundamental + DCF")
print("  5 → Todo")

opcion = input("\nElegí una opción: ").strip()

# ── Ejecución según opción ────────────────────────────
if opcion in ["1", "5"]:
    res_retornos = calcular_retornos(df, returns)
    imprimir("📈 RETORNOS", res_retornos)

if opcion in ["2", "5"]:
    res_riesgo, drawdown = calcular_riego(returns)
    imprimir("⚠️  RIESGO", res_riesgo)

if opcion in ["3", "5"]:
    res_benchmark = comparar_bench(returns)
    imprimir("📊 VS BENCHMARK", res_benchmark)

if opcion in ["4", "5"]:
    info = yf.Ticker(ticker).info
    general, rent, valuacion, crecimiento, deuda, dividendos = obtenet_datos(ticker)
    dcf = calcular_dcf(info)

    print(f"\n{'='*45}")
    print(f"  🏢 GENERAL")
    print(f"{'='*45}")
    for k, v in general.items():
        print(f"  {k:<35} {str(v):>10}")

    imprimir("💰 VALUACIÓN",     valuacion)
    imprimir("📈 RENTABILIDAD",  rent)
    imprimir("🚀 CRECIMIENTO",   crecimiento)
    imprimir("⚖️  DEUDA",        deuda)
    imprimir("💵 DIVIDENDOS",    dividendos)
    imprimir("🔮 DCF (5 años)",  dcf)

if opcion not in ["1", "2", "3", "4", "5"]:
    print("\n❌ Opción no válida")


