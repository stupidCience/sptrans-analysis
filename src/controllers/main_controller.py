import polars as pl
import streamlit as st
from src.models.bus_model import BusModel

@st.cache_data(show_spinner=False, ttl=60)
def fetch_cached_data():
    model = BusModel()
    return model.get_current_positions()

@st.cache_data(show_spinner=False, ttl=60)
def fetch_historical_cached_data():
    model = BusModel()
    return model.get_historical_positions()

class MainController:

    def get_available_lines(self):
        df = fetch_cached_data()
        if not df.is_empty():
            return sorted(df.select("line_id").unique().drop_nulls().to_series().to_list())
        return []

    def get_map_data(self, selected_line=None, only_accessible=False, search_term=None, zone_filter=None, user_lat=None, user_lon=None):
        df = fetch_cached_data()
        
        if df.is_empty():
            return None

        if selected_line:
            df = df.filter(pl.col("line_id") == selected_line)
            
        if only_accessible:
            df = df.filter((pl.col("is_accessible") == True) | (pl.col("is_accessible") == 1))
            
        if search_term:
            term = search_term.lower()
            df = df.filter(
                pl.col("origin").str.to_lowercase().str.contains(term) |
                pl.col("destination").str.to_lowercase().str.contains(term)
            )

        if zone_filter and zone_filter != "Todas as Zonas":
            zone_map = {
                "Noroeste (Verde Claro)": "1", "Norte (Azul Escuro)": "2",
                "Nordeste (Amarelo)": "3", "Leste (Vermelho)": "4",
                "Sudeste (Verde Escuro)": "5", "Sul (Azul Claro)": "6",
                "Sudoeste (Vinho)": "7", "Oeste (Laranja)": "8", "Centro (Cinza)": "9"
            }
            prefix = zone_map.get(zone_filter)
            if prefix:
                df = df.filter(pl.col("line_id").str.starts_with(prefix))

        if user_lat is not None and user_lon is not None:
            lat_tolerance = 0.045
            lon_tolerance = 0.045
            df = df.filter(
                (pl.col("latitude") < user_lat + lat_tolerance) &
                (pl.col("latitude") > user_lat - lat_tolerance) &
                (pl.col("longitude") < user_lon + lon_tolerance) &
                (pl.col("longitude") > user_lon - lon_tolerance)
            )

        return df.to_pandas()

    def get_historical_map_data(self, selected_line=None, zone_filter=None):
        df = fetch_historical_cached_data()
        if df.is_empty():
            return None

        if selected_line:
            df = df.filter(pl.col("line_id") == selected_line)

        if zone_filter and zone_filter != "Todas as Zonas":
            zone_map = {
                "Noroeste (Verde Claro)": "1", "Norte (Azul Escuro)": "2",
                "Nordeste (Amarelo)": "3", "Leste (Vermelho)": "4",
                "Sudeste (Verde Escuro)": "5", "Sul (Azul Claro)": "6",
                "Sudoeste (Vinho)": "7", "Oeste (Laranja)": "8", "Centro (Cinza)": "9"
            }
            prefix = zone_map.get(zone_filter)
            if prefix:
                df = df.filter(pl.col("line_id").str.starts_with(prefix))

        return df.to_pandas()