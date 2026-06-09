import streamlit as st

def render_metrics(df_buses):
    if df_buses is None or df_buses.empty:
        return

    # Cálculos dos KPIs
    total_buses = len(df_buses)
    accessible_buses = int(df_buses['is_accessible'].sum())
    accessible_pct = (accessible_buses / total_buses) * 100 if total_buses > 0 else 0
    active_lines = df_buses['line_id'].nunique()

    st.markdown("### 📊 Indicadores da Operação")
    
    # Cria 3 colunas para os "Cards" do Dashboard
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total de Ônibus Rodando", f"{total_buses:,}".replace(',', '.'))
    with col2:
        st.metric("Linhas em Operação", f"{active_lines:,}".replace(',', '.'))
    with col3:
        # Mostra a porcentagem e a quantidade absoluta como "delta"
        st.metric("Acessibilidade (Cadeirantes)", f"{accessible_pct:.1f}%", f"{accessible_buses} veículos", delta_color="normal")

    st.markdown("---")