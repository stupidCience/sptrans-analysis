import streamlit as st
import plotly.express as px
import pandas as pd

SPTRANS_COLORS = {
    "1": "#85C441", "2": "#002B5C", "3": "#FFD100", "4": "#ED1C24",
    "5": "#006B3F", "6": "#00A0E3", "7": "#780032", "8": "#F37021", "9": "#808080"
}

def extract_zone_from_prefix(bus_prefix):
    if bus_prefix and str(bus_prefix).strip():
        first_digit = str(bus_prefix).strip()[0]
        if first_digit in SPTRANS_COLORS:
            return first_digit
    return "9"

def render_accessibility_guide(df_buses):
    st.markdown("### ♿ Acessibilidade da Frota Ativa")
    col1, col2 = st.columns(2)
    
    with col1:
        access_counts = df_buses['is_accessible'].value_counts().reset_index()
        access_counts.columns = ['is_accessible', 'Quantidade']
        access_counts['Status'] = access_counts['is_accessible'].map(
            {True: 'Adaptado (♿)', False: 'Não Adaptado', 1: 'Adaptado (♿)', 0: 'Não Adaptado'}
        )
        fig1 = px.pie(
            access_counts, values='Quantidade', names='Status', hole=0.5,
            color='Status', color_discrete_map={'Adaptado (♿)': '#006B3F', 'Não Adaptado': '#ED1C24'},
            title="Panorama de Inclusão da Frota"
        )
        st.plotly_chart(fig1, width='stretch')

    with col2:
        df_buses['Zona'] = df_buses['bus_prefix'].apply(extract_zone_from_prefix)
        zone_access = df_buses.groupby(['Zona', 'is_accessible']).size().reset_index(name='Total')
        zone_access['Status'] = zone_access['is_accessible'].map(
            {True: 'Adaptado', False: 'Não Adaptado', 1: 'Adaptado', 0: 'Não Adaptado'}
        )
        fig2 = px.bar(
            zone_access, x='Zona', y='Total', color='Status', barmode='stack',
            title="Desigualdade Sobre Rodas: Acessibilidade por Zona",
            category_orders={"Zona": ["1", "2", "3", "4", "5", "6", "7", "8", "9"]},
            color_discrete_map={'Adaptado': '#00A0E3', 'Não Adaptado': '#808080'}
        )
        st.plotly_chart(fig2, width='stretch')

def render_connectivity_guide(df_buses):
    st.markdown("### 🏙️ Conectividade e Volume de Frota")
    
    df_working = df_buses.copy()
    df_working['Zona'] = df_working['bus_prefix'].apply(extract_zone_from_prefix)
    
    zone_names = {
        "1": "Noroeste", "2": "Norte", "3": "Nordeste", "4": "Leste",
        "5": "Sudeste", "6": "Sul", "7": "Sudoeste", "8": "Oeste", "9": "Centro"
    }
    df_working['Nome_Zona'] = df_working['Zona'].map(zone_names)
    
    df_working = df_working.dropna(subset=['Nome_Zona', 'line_id'])
    
    fig_tree = px.treemap(
        df_working, path=['Nome_Zona', 'line_id'], color='Zona',
        color_discrete_map=SPTRANS_COLORS,
        title="Dependência de Terminais: Volume de Ônibus por Zona e Linha (Clique para expandir)"
    )
    fig_tree.update_traces(root_color="lightgrey")
    st.plotly_chart(fig_tree, width='stretch')

def render_punctuality_guide(df_hist):
    st.markdown("### ⏱️ Pontualidade e Efeito Comboio")
    if df_hist is None or df_hist.empty or len(df_hist) < 500:
        st.info("⏳ Coletando dados históricos espaciais... Deixe a aplicação rodando por mais alguns minutos.")
        return

    df_hist['captured_at'] = pd.to_datetime(df_hist['captured_at'])
    df_hist = df_hist.sort_values(by=['bus_prefix', 'captured_at'])
    df_hist['prev_lat'] = df_hist.groupby('bus_prefix')['latitude'].shift(1)
    df_hist['prev_lon'] = df_hist.groupby('bus_prefix')['longitude'].shift(1)
    df_hist['prev_time'] = df_hist.groupby('bus_prefix')['captured_at'].shift(1)

    df_calc = df_hist.dropna(subset=['prev_lat']).copy()
    df_calc['time_diff_hours'] = (df_calc['captured_at'] - df_calc['prev_time']).dt.total_seconds() / 3600.0
    df_calc['dist_km'] = (((df_calc['latitude'] - df_calc['prev_lat'])**2 + (df_calc['longitude'] - df_calc['prev_lon'])**2) ** 0.5) * 111.0
    df_calc['speed_kmh'] = df_calc['dist_km'] / df_calc['time_diff_hours']
    df_calc = df_calc[(df_calc['speed_kmh'] >= 5) & (df_calc['speed_kmh'] <= 80)]

    col1, col2 = st.columns(2)
    with col1:
        if not df_calc.empty:
            df_calc['minute'] = df_calc['captured_at'].dt.strftime('%H:%M')
            speed_trend = df_calc.groupby('minute')['speed_kmh'].mean().reset_index()
            fig_speed = px.line(
                speed_trend, x='minute', y='speed_kmh',
                title="Fluidez do Trânsito: Velocidade Média da Frota",
                labels={'minute': 'Horário', 'speed_kmh': 'Velocidade Média (km/h)'},
                markers=True
            )
            fig_speed.update_traces(line_color='#F37021')
            st.plotly_chart(fig_speed, width='stretch')
        else:
            st.warning("Dados de deslocamento insuficientes.")

    with col2:
        df_hist['lat_round'] = df_hist['latitude'].round(3)
        df_hist['lon_round'] = df_hist['longitude'].round(3)
        df_hist['time_round'] = df_hist['captured_at'].dt.floor('Min')
        comboios = df_hist.groupby(['line_id', 'time_round', 'lat_round', 'lon_round'])['bus_prefix'].nunique().reset_index()
        comboios = comboios[comboios['bus_prefix'] >= 3]
        top_comboios = comboios.groupby('line_id').size().reset_index(name='Ocorrencias')
        top_comboios = top_comboios.sort_values(by='Ocorrencias', ascending=False).head(10)

        if not top_comboios.empty:
            fig_convoy = px.bar(
                top_comboios, x='line_id', y='Ocorrencias',
                title="Gargalos: Top 10 Linhas com Efeito 'Comboio' (3+ veículos juntos)",
                labels={'line_id': 'Identificação da Linha', 'Ocorrencias': 'Minutos em Comboio'},
                color='Ocorrencias', color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_convoy, width='stretch')
        else:
            st.info("Nenhum Efeito Comboio grave detectado no momento.")