import numpy as np
import pandas as pd
from confif import dias,rf_anual
def calcular_riego(returns):
    r=returns['Retornos_activo']
    resultado={}
    rf_diaria= rf_anual/dias
    resultado['vol anual']=round(r.std()*np.sqrt(dias)*100,2)
    exeso=r.mean()-rf_diaria
    resultado['Ratio de Sharpe']=round((exeso/r.std()*np.sqrt(dias)),4)
    neg=r[r<0]
    resultado['Sortino ratio']=round((exeso/neg.std()*np.sqrt(dias)),4)
    resultado['Var diario 95%']= round(np.percentile(r,5)*100,4)
    resultado['Var diario 99%']= round(np.percentile(r,1)*100,4)
    var95=np.percentile(r,5)
    resultado['cVAR']=round(r[r<=var95].mean()*100,4)
    precios=(1+r).cumprod()
    rolling_max=precios.cummax()
    drawon=(precios-rolling_max)/rolling_max *100
    resultado['Max Drawdown ']=round(drawon.min(),4)
    return resultado, drawon
