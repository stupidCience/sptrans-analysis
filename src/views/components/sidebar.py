import streamlit as st
from streamlit_geolocation import streamlit_geolocation

def render_sidebar(controller):
    st.sidebar.header("📍 Sua Localização")
    st.sidebar.write("Busque ônibus próximos num raio de 5km:")
    
    with st.sidebar:
        location = streamlit_geolocation()
        
    user_lat, user_lon = None, None
    if location and location.get('latitude') and location.get('longitude'):
        user_lat = location['latitude']
        user_lon = location['longitude']
        if 'gps_notified' not in st.session_state:
            st.toast("Localização capturada com sucesso!", icon="✅")
            st.session_state.gps_notified = True

    st.sidebar.header("🔍 Filtros e Navegação")
    
    search_term = st.sidebar.text_input("Buscar Bairro ou Destino (Ex: Pinheiros):")
    
    zonas = [
        "Todas as Zonas", "Noroeste (Verde Claro)", "Norte (Azul Escuro)", 
        "Nordeste (Amarelo)", "Leste (Vermelho)", "Sudeste (Verde Escuro)", 
        "Sul (Azul Claro)", "Sudoeste (Vinho)", "Oeste (Laranja)", "Centro (Cinza)"
    ]
    selected_zone = st.sidebar.selectbox("Filtrar por Zona:", zonas)

    available_lines = controller.get_available_lines()
    line_options = ["Todas as Linhas"] + available_lines
    selected_line = st.sidebar.selectbox("Selecione uma Linha Específica:", line_options)
    
    only_accessible = st.sidebar.checkbox("♿ Apenas Veículos Acessíveis")
    
    if st.sidebar.button("🔄 Forçar Limpeza de Cache", type="primary"):
        st.cache_data.clear()

    return {
        "selected_line": None if selected_line == "Todas as Linhas" else selected_line,
        "only_accessible": only_accessible,
        "search_term": search_term if search_term.strip() else None,
        "zone_filter": None if selected_zone == "Todas as Zonas" else selected_zone,
        "user_lat": user_lat,
        "user_lon": user_lon
    }