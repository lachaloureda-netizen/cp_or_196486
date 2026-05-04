import pandas as pd
import yfinance as yf
import numpy as np
def obtenet_datos(ticker):
    tick=yf.Ticker(ticker)
    info=tick.info
    general={
        "nombre": info.get('longname', 'N/A'),
        "sector": info.get('sector'),
        "industria": info.get('industry', "N/A"),
        "pais": info.get('country', "N/A"),
    }
    valuacion={
        "P/E Ratio":         info.get("trailingPE"),
        "P/E Forward":       info.get("forwardPE"),
        "P/B Ratio":         info.get("priceToBook"),
        "P/S Ratio":         info.get("priceToSalesTrailing12Months"),
        "EV/EBITDA":         info.get("enterpriseToEbitda"),
        "EV/ventas":        info.get("enterpriseToRevenue"),
    }
    rent= {
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
    crecimiento={
        "Crecimiento Ingresos (YoY)":  info.get("revenueGrowth"),
        "Crecimiento Ganancias (YoY)": info.get("earningsGrowth"),
        "Ingresos Totales":            info.get("totalRevenue"),
        "Beneficio Neto":              info.get("netIncomeToCommon"),
    }
    deuda = {
        "Debt/Equity":               info.get("debtToEquity"),
        "Current Ratio":             info.get("currentRatio"),
        "Quick Ratio":               info.get("quickRatio"),
        "Deuda Total":               info.get("totalDebt"),
        "Cash Total":                info.get("totalCash"),
        "Cash por Acción":           info.get("totalCashPerShare"),
    }
    dividendos = {
        "Dividend Yield %":          info.get("dividendYield"),
        "Payout Ratio":              info.get("payoutRatio"),
        "Dividendo por Acción":      info.get("dividendRate"),
    }
    return general, rent, valuacion,crecimiento,deuda,dividendos
def calcular_dcf(info):
    try:
        
        fcf          = info.get("freeCashflow")
        shares       = info.get("sharesOutstanding")
        precio       = info.get("currentPrice")
        deuda        = info.get("totalDebt", 0)
        cash         = info.get("totalCash", 0)

        if not fcf or not shares or not precio:
            return {"error": "Datos insuficientes para DCF"}


        roe          = info.get("returnOnEquity", 0.10)
        payout       = info.get("payoutRatio", 0)
        payout       = min(payout, 1) if payout else 0   # evitar valores raros
        retention    = 1 - payout
        crecimiento  = roe * retention

        # Caps para evitar valores absurdos
        crecimiento  = max(0.01, min(crecimiento, 0.30))

        # ── WACC con CAPM ─────────────────────────────────
        beta         = info.get("beta", 1.0) or 1.0
        market_cap   = info.get("marketCap", 1)
        tax_rate     = info.get("effectiveTaxRate") or 0.25

        # Costo del equity (CAPM)
        rf           = 0.05    # tasa libre de riesgo
        rm           = 0.10    # retorno esperado mercado
        ke           = rf + beta * (rm - rf)

        # Costo de la deuda
        int_expense  = info.get("interestExpense") or 0
        int_expense  = abs(int_expense)
        kd           = (int_expense / deuda) if deuda > 0 else 0.05
        kd           = max(0.02, min(kd, 0.15))   # cap razonable

        # Pesos E y D
        V            = market_cap + deuda
        e_weight     = market_cap / V
        d_weight     = deuda / V

        wacc         = (e_weight * ke) + (d_weight * kd * (1 - tax_rate))
        wacc         = max(0.06, min(wacc, 0.20))   # cap entre 6% y 20%

        # ── DCF 5 años ────────────────────────────────────
        crecimiento_term = 0.03
        años             = 5

        fcfs_proyectados = []
        for i in range(1, años + 1):
            fcf_proy = fcf * ((1 + crecimiento) ** i)
            fcf_desc = fcf_proy / ((1 + wacc) ** i)
            fcfs_proyectados.append(fcf_desc)

        fcf_año5         = fcf * ((1 + crecimiento) ** años)
        valor_terminal   = fcf_año5 * (1 + crecimiento_term) / (wacc - crecimiento_term)
        vt_descontado    = valor_terminal / ((1 + wacc) ** años)

        valor_empresa    = sum(fcfs_proyectados) + vt_descontado
        valor_equity     = valor_empresa - deuda + cash
        valor_por_accion = valor_equity / shares

        upside           = ((valor_por_accion / precio) - 1) * 100

        return {
            "ROE":                      round(roe * 100, 2),
            "Retention Ratio":          round(retention * 100, 2),
            "Tasa Crecimiento (g) %":   round(crecimiento * 100, 2),
            "Beta":                     round(beta, 2),
            "Costo Equity (Ke) %":      round(ke * 100, 2),
            "Costo Deuda (Kd) %":       round(kd * 100, 2),
            "WACC %":                   round(wacc * 100, 2),
            "FCF Actual (B)":           round(fcf / 1e9, 2),
            "Valor Intrínseco/Acción":  round(valor_por_accion, 2),
            "Precio Actual":            round(precio, 2),
            "Upside/Downside %":        round(upside, 2),
            "Veredicto DCF":            "🟢 Subvaluada" if upside > 10
                                        else "🔴 Sobrevaluada" if upside < -10
                                        else "🟡 Precio justo"
        }

    except Exception as e:
        return {"error": str(e)}
