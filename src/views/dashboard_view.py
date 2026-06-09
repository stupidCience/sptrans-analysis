import streamlit as st
from src.views.components.sidebar import render_sidebar
from src.views.components.metrics_board import render_metrics
from src.views.components.map_board import render_map
from src.views.components.charts_board import render_accessibility_guide, render_connectivity_guide, render_punctuality_guide

class DashboardView:
    def __init__(self, controller):
        self.controller = controller

    def render(self):
        st.set_page_config(page_title="Dashboard SPTrans", layout="wide", page_icon="🚌")

        st.markdown("""
            <style>
            div.stButton > button { background-color: #0055ff !important; color: white !important; border-radius: 8px !important; }
            [data-testid="stMetricValue"] { color: #0044ff !important; font-size: 28px !important; }
            .stTabs [data-baseweb="tab-list"] { gap: 8px; }
            .stTabs [data-baseweb="tab"] { border-radius: 4px 4px 0px 0px; padding: 10px 20px; background-color: #f4f6f9; }
            .stTabs [aria-selected="true"] { background-color: #0055ff; color: white; }
            </style>
        """, unsafe_allow_html=True)

        st.title("🚌 Data Product: Operação SPTrans")
        st.write("Análise em tempo real de mobilidade urbana da cidade de São Paulo.")

        filters = render_sidebar(self.controller)

        with st.spinner("Processando Inteligência de Dados..."):
            df_buses = self.controller.get_map_data(
                selected_line=filters["selected_line"], 
                only_accessible=filters["only_accessible"],
                search_term=filters.get("search_term"),
                zone_filter=filters["zone_filter"],
                user_lat=filters["user_lat"],
                user_lon=filters["user_lon"]
            )
            
            df_history = self.controller.get_historical_map_data(
                selected_line=filters["selected_line"], 
                zone_filter=filters["zone_filter"]
            )
            
            if df_buses is not None and not df_buses.empty:
                render_metrics(df_buses)
                
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📍 Guia 1: Visão Geral e Radar", 
                    "♿ Guia 2: Acessibilidade", 
                    "⏱️ Guia 3: Pontualidade", 
                    "🏙️ Guia 4: Conectividade"
                ])
                
                with tab1:
                    st.markdown("##### 🗺️ Onde estão os ônibus agora?")
                    render_map(df_buses, filters["user_lat"], filters["user_lon"])
                    
                with tab2:
                    render_accessibility_guide(df_buses)
                    
                with tab3:
                    render_punctuality_guide(df_history)
                    
                with tab4:
                    render_connectivity_guide(df_buses)
            else:
                st.warning("Nenhum ônibus encontrado com os filtros selecionados.")
