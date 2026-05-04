from google import genai

# Inicializamos el cliente
client = genai.Client(api_key="AIzaSyA7edC4grJvK1Gr79shaGjQIqN-77LzOxk")

def analisis_ia(ticker, res_retornos=None, res_riesgo=None, 
                res_benchmark=None, fundamentals=None, dcf=None):
    
    # 1. Armamos la base de datos para la IA
    datos_mercado = f"Analiza la accion {ticker}.\n"
    if res_retornos: datos_mercado += f"Retornos: {res_retornos}\n"
    if res_riesgo: datos_mercado += f"Riesgo: {res_riesgo}\n"
    if res_benchmark: datos_mercado += f"Benchmark: {res_benchmark}\n"
    if fundamentals:
        gen, rent, val, crec, deu, div = fundamentals
        datos_mercado += f"Fundamentales: {val}, {rent}, {deu}\n"
    if dcf: datos_mercado += f"DCF: {dcf}\n"

    contexto = """
Con todos estos datos, genera un analisis profesional en espanol que incluya:

1. Resumen ejecutivo (3 lineas maximo)
2. Fortalezas principales de la accion
3. Riesgos y debilidades
4. Perspectiva y conclusion
5. Decision de inversion: COMPRAR / MANTENER / VENDER con justificacion

Se directo, tecnico y fundamentado en los datos. No uses frases genericas.
"""

    try:
        # Enviamos a Gemini[cite: 2]
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=contexto
        )
        
        # 3. SOLUCION AL ERROR DE CODEC: 
        # Limpiamos la respuesta de caracteres que Windows no puede mostrar en consola[cite: 2]
        return response.text.encode('ascii', 'ignore').decode('ascii')
    
    except Exception as e:
        return f"Error: {str(e)}"