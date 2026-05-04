import yfinance as yf

# PASO 1: Tenés que crear el objeto Ticker con yf.Ticker()
tnx_obj = yf.Ticker("^TNX") 

# PASO 2: Ahora sí usás .history() sobre el objeto creado
dato = tnx_obj.history(period="1d") 

# PASO 3: Extraés el valor (acordate de dividir por 100 si lo querés como decimal)
rf_anual = dato['Close'].iloc[-1] 
dias = 252





