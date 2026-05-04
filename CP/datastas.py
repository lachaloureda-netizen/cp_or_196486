import yfinance as yf
import pandas as pd 
def precios(ticker,benchmark,period="2y"):
    activo=yf.download(ticker,period=period,auto_adjust=True)['Close']
    bench=yf.download(benchmark,period=period,auto_adjust=True)['Close']
    df = pd.concat([activo, bench], axis=1)
    df.columns = ['activo', 'bench']
    return df 
def retornos(df):
    retorno=df.pct_change().dropna()
    retorno.columns=['Retornos_activo','Retorno_benchmark']
    return retorno
def fundamentals(ticker):
    info=yf.Ticker(ticker).info
    datos= {
        "ROE": info.get("returnOnEquity"),
        "ROA": info.get("returnOnAssets"),
        "debtToEquity": info.get("debtToEquity"),
        "Margen_operativo": info.get("operatingMargins"),
        "Crecimiento_Ingresos": info.get("revenueGrowth"),
        "P/E Ratio":         info.get("trailingPE"),
        "Market Cap":        info.get("marketCap"),
        "Nombre":            info.get("longName"),
        "Sector":            info.get("sector"),
    }
    return datos