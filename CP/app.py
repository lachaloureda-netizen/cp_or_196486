import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datastas import precios, retornos
from retornos import calcular_retornos
from riesgo import calcular_riego
from benchmark import comparar_bench
from fundamentals import obtenet_datos, calcular_dcf

# ── Configuración página ──────────────────────────────
st.set_page_config(
    page_title="Analisis accion",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Analyzer")
st.markdown("Análisis cuantitativo de acciones vs benchmark")

# ── Sidebar — inputs ──────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuración")
    ticker    = st.text_input("Ticker",    value="AAPL").upper()
    benchmark = st.text_input("Benchmark", value="^GSPC").upper()
    periodo   = st.selectbox("Período", ["1y", "2y", "3y", "5y"])

    st.markdown("---")
    mostrar_retornos  = st.checkbox("📈 Retornos",           value=True)
    mostrar_riesgo    = st.checkbox("⚠️ Riesgo",            value=True)
    mostrar_benchmark = st.checkbox("📊 Vs Benchmark",       value=True)
    mostrar_fund      = st.checkbox("🏢 Fundamentals + DCF", value=True)

    analizar = st.button("🚀 Analizar", use_container_width=True)

# ── Ejecución ─────────────────────────────────────────
if analizar:
    with st.spinner("⏳ Descargando datos..."):
        df      = precios(ticker, benchmark, periodo)
        returns = retornos(df)

    tabs = st.tabs(["📈 Retornos", "⚠️ Riesgo", "📊 Benchmark", "🏢 Fundamentals"])

    # ────────────────────────────────────────────────
    # TAB 1 — RETORNOS
    # ────────────────────────────────────────────────
    with tabs[0]:
        if mostrar_retornos:
            res_retornos = calcular_retornos(df, returns)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Retorno Acumulado Activo",    f"{res_retornos.get('retorno acumulado activo ', 'N/A')}%")
            col2.metric("Retorno Acumulado Benchmark", f"{res_retornos.get('retorno acumulado benchmark ', 'N/A')}%")
            col3.metric("CAGR Activo",                 f"{res_retornos.get('crec activo', 'N/A')}%")
            col4.metric("Rolling 30d",                 f"{res_retornos.get('rolling return 30d anual', 'N/A')}%")

            st.markdown("---")

            # Precios normalizados
            st.subheader("📊 Evolución de precios (base 100)")
            df_norm = df.copy()
            df_norm["activo"] = df_norm["activo"] / df_norm["activo"].iloc[0] * 100
            df_norm["bench"]  = df_norm["bench"]  / df_norm["bench"].iloc[0]  * 100

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_norm.index, y=df_norm["activo"],
                                     name=ticker,    line=dict(color="#00C9FF", width=2)))
            fig.add_trace(go.Scatter(x=df_norm.index, y=df_norm["bench"],
                                     name=benchmark, line=dict(color="#FF6B6B", width=2)))
            fig.update_layout(template="plotly_dark", height=400,
                              yaxis_title="Base 100", xaxis_title="Fecha")
            st.plotly_chart(fig, use_container_width=True)

            # Retornos diarios
            st.subheader("📉 Retornos diarios")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=returns.index, y=returns["Retornos_activo"] * 100,
                                  name=ticker, marker_color="#00C9FF"))
            fig2.update_layout(template="plotly_dark", height=350,
                               yaxis_title="Retorno %", xaxis_title="Fecha")
            st.plotly_chart(fig2, use_container_width=True)

        else:
            st.info("Activá la opción en el sidebar para ver esta sección.")

    # ────────────────────────────────────────────────
    # TAB 2 — RIESGO
    # ────────────────────────────────────────────────
    with tabs[1]:
        if mostrar_riesgo:
            res_riesgo, drawdown = calcular_riego(returns)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Volatilidad Anual", f"{res_riesgo.get('vol anual', 'N/A')}%")
            col2.metric("Sharpe Ratio",       f"{res_riesgo.get('Ratio de Sharpe', 'N/A')}")
            col3.metric("Sortino Ratio",      f"{res_riesgo.get('Sortino ratio', 'N/A')}")
            col4.metric("Max Drawdown",       f"{res_riesgo.get('Max Drawdown ', 'N/A')}%")

            st.markdown("---")

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📋 Métricas de riesgo")
                df_riesgo = pd.DataFrame(
                    list(res_riesgo.items()),
                    columns=["Métrica", "Valor"]
                )
                st.dataframe(df_riesgo, use_container_width=True, hide_index=True)

            with col2:
                st.subheader("📊 Distribución de retornos")
                r     = returns["Retornos_activo"] * 100
                var95 = res_riesgo.get("Var diario 95%", None)

                fig3 = px.histogram(r, nbins=50, template="plotly_dark",
                                    color_discrete_sequence=["#00C9FF"])
                if var95:
                    fig3.add_vline(x=var95, line_dash="dash",
                                   line_color="#FF6B6B",
                                   annotation_text="VaR 95%",
                                   annotation_position="top right")
                fig3.update_layout(height=350, showlegend=False,
                                   xaxis_title="Retorno %", yaxis_title="Frecuencia")
                st.plotly_chart(fig3, use_container_width=True)

            # Drawdown
            st.subheader("📉 Drawdown histórico")
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(x=drawdown.index, y=drawdown,
                                      fill="tozeroy", name="Drawdown",
                                      line=dict(color="#FF6B6B", width=1)))
            fig4.update_layout(template="plotly_dark", height=350,
                               yaxis_title="Drawdown %", xaxis_title="Fecha")
            st.plotly_chart(fig4, use_container_width=True)

        else:
            st.info("Activá la opción en el sidebar para ver esta sección.")

    # ────────────────────────────────────────────────
    # TAB 3 — BENCHMARK
    # ────────────────────────────────────────────────
    with tabs[2]:
        if mostrar_benchmark:
            res_benchmark = comparar_bench(returns)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Beta",              res_benchmark.get("Beta", "N/A"))
            col2.metric("Alpha Anual %",     f"{res_benchmark.get('Alpha Anual %', 'N/A')}%")
            col3.metric("Correlación",       res_benchmark.get("correlacion", "N/A"))
            col4.metric("Information Ratio", res_benchmark.get("information ratio", "N/A"))

            st.markdown("---")

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📋 Todas las métricas")
                df_bench = pd.DataFrame(
                    list(res_benchmark.items()),
                    columns=["Métrica", "Valor"]
                )
                st.dataframe(df_bench, use_container_width=True, hide_index=True)

            with col2:
                st.subheader("📊 Activo vs Benchmark")
                fig5 = px.scatter(
                    x=returns["Retorno_benchmark"] * 100,
                    y=returns["Retornos_activo"]    * 100,
                    template="plotly_dark",
                    trendline="ols",
                    labels={"x": f"Retorno {benchmark} %",
                            "y": f"Retorno {ticker} %"},
                    color_discrete_sequence=["#00C9FF"]
                )
                fig5.update_layout(height=350)
                st.plotly_chart(fig5, use_container_width=True)

        else:
            st.info("Activá la opción en el sidebar para ver esta sección.")

    # ────────────────────────────────────────────────
    # TAB 4 — FUNDAMENTALS
    # ────────────────────────────────────────────────
    with tabs[3]:
        if mostrar_fund:
            info         = yf.Ticker(ticker).info
            fundamentals = obtenet_datos(ticker)
            dcf_result   = calcular_dcf(info)
            general, rent, valuacion, crecimiento, deuda, dividendos = fundamentals

            st.subheader(f"🏢 {general.get('nombre', ticker)} — {general.get('sector', 'N/A')}")
            st.caption(f"{general.get('industria', '')} | {general.get('pais', '')}")
            st.markdown("---")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("💰 Valuación")
                st.dataframe(pd.DataFrame(list(valuacion.items()),
                             columns=["Métrica", "Valor"]),
                             use_container_width=True, hide_index=True)

                st.subheader("💵 Dividendos")
                st.dataframe(pd.DataFrame(list(dividendos.items()),
                             columns=["Métrica", "Valor"]),
                             use_container_width=True, hide_index=True)

            with col2:
                st.subheader("📈 Rentabilidad")
                st.dataframe(pd.DataFrame(list(rent.items()),
                             columns=["Métrica", "Valor"]),
                             use_container_width=True, hide_index=True)

                st.subheader("⚖️ Deuda")
                st.dataframe(pd.DataFrame(list(deuda.items()),
                             columns=["Métrica", "Valor"]),
                             use_container_width=True, hide_index=True)

            with col3:
                st.subheader("🚀 Crecimiento")
                st.dataframe(pd.DataFrame(list(crecimiento.items()),
                             columns=["Métrica", "Valor"]),
                             use_container_width=True, hide_index=True)

                st.subheader("🔮 DCF (5 años)")
                st.dataframe(pd.DataFrame(list(dcf_result.items()),
                             columns=["Métrica", "Valor"]),
                             use_container_width=True, hide_index=True)

        else:
            st.info("Activá la opción en el sidebar para ver esta sección.")
