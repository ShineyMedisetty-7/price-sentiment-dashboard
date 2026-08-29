# ---- pages/overview_page.py ----
import streamlit as st
import plotly.graph_objects as go
from config import CFG

def render(price_df, kpis):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([1,1,1,1])
    col1.markdown("<div class='kpi-title'>Last Price</div>", unsafe_allow_html=True)
    col1.markdown(f"<div class='big-metric'>₹{kpis['last']:,.2f}</div>", unsafe_allow_html=True)
    col2.markdown("<div class='kpi-title'>30d Average</div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='big-metric'>₹{kpis['mean_30']:,.2f}</div>", unsafe_allow_html=True)
    col3.markdown("<div class='kpi-title'>30d Volatility (σ)</div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='big-metric'>{kpis['volatility_30']:.2f}</div>", unsafe_allow_html=True)
    col4.markdown("<div class='kpi-title'>Change (1d)</div>", unsafe_allow_html=True)
    delta_str = f"{kpis['pct_change_1d']:+.2f}%"
    col4.markdown(f"<div class='big-metric'>{delta_str}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Interactive Price History")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=price_df['date'], y=price_df['price'], mode='lines', name='Price', line=dict(color=CFG.COLORS['primary'])))
    fig.update_layout(template='plotly_white', hovermode='x unified', margin=dict(t=30))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Data (last 20 rows)")
    st.dataframe(price_df.tail(20).assign(date=price_df.tail(20)['date'].dt.strftime('%Y-%m-%d')))
    st.markdown("</div>", unsafe_allow_html=True)
