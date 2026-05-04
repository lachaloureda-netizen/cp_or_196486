import numpy as np
import pandas as pd 
from confif import dias
def calcular_retornos(df,returns):
    rtd={}
    rtd['retorno acumulado activo ']=round((df['activo'].iloc[-1]/df['activo'].iloc[0]-1)*100,2)
    rtd['retorno acumulado benchmark ']=round((df['bench'].iloc[-1]/df['bench'].iloc[0]-1)*100,2)
    años=len(df)/dias
    rtd['crec activo']=round((df['activo'].iloc[-1]/df['activo'].iloc[0]**(1/años)-1)*100,2)
    rtd['crec bench']=round((df['bench'].iloc[-1]/df['bench'].iloc[0]**(1/años)-1)*100,2)
    mensual=returns['Retornos_activo'].rolling(30).sum()*100
    rtd['rolling return 30d anual']=round(mensual.iloc[-1],2)
    return rtd



