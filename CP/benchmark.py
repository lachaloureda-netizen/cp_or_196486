import numpy as np
import pandas as pd
from scipy import stats
from confif import rf_anual,dias
def comparar_bench(returns):
    Ra=returns['Retornos_activo']
    Rb=returns['Retorno_benchmark']
    rf=rf_anual/dias
    resultado={}
    pendiente, intercepto, coefcorr, p_value, std_err=stats.linregress(Ra,Rb)
    resultado["Beta"]           = round(pendiente, 4)
    resultado["Alpha (diario)"] = round(intercepto, 6)
    resultado["Alpha Anual %"]  = round(intercepto * dias * 100, 4)
    resultado["R²"]             = round(coefcorr ** 2, 4)
    resultado['correlacion']=round(Ra.corr(Rb),4)
    dif=Ra-Rb
    resultado['tacking error']=round(dif.std()*np.sqrt(dias)*100,4)
    resultado['information ratio']=round(dif.mean()/dif.std()*np.sqrt(dias),4)
    return resultado
