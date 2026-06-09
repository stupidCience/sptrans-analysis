import folium
from folium.plugins import MarkerCluster
import streamlit as st
from streamlit_folium import st_folium

def render_map(df_buses, user_lat, user_lon):
    if df_buses is None or df_buses.empty:
        return

    center_lat = user_lat if user_lat else df_buses["latitude"].mean()
    center_lon = user_lon if user_lon else df_buses["longitude"].mean()
    
    bus_map = folium.Map(location=[center_lat, center_lon], zoom_start=14 if user_lat else 12)
    
    if user_lat and user_lon:
        folium.Marker(
            location=[user_lat, user_lon],
            tooltip="Você está aqui!",
            icon=folium.Icon(color="red", icon="user", prefix="fa")
        ).add_to(bus_map)

    marker_cluster = MarkerCluster().add_to(bus_map)
    
    for _, row in df_buses.iterrows():
        sentido_pt = "Ida" if row['direction'] == "Outbound" else "Volta" if row['direction'] == "Inbound" else "Desconhecido"
        direcao_icone = "arrow-up" if row['direction'] == "Outbound" else "arrow-down"
        tooltip_text = f"Linha: {row['line_id']} | Prefixo: {row['bus_prefix']}"
        
        popup_html = f"""
            <div style="width: 250px; font-family: Arial, sans-serif;">
                <h4 style="margin: 0; color: #0044ff;">Linha: {row['line_id']}</h4>
                <b>Prefixo:</b> {row['bus_prefix']}<br>
                <b>Origem:</b> {row['origin']}<br>
                <b>Destino:</b> {row['destination']}<br>
                <b>Sentido:</b> {sentido_pt} <i class="fa fa-{direcao_icone}"></i><br>
                <hr style="margin: 8px 0;">
                <b>Atualizado em:</b> {row['update_time']}
            </div>
        """
        
        icon_color = "green" if row['is_accessible'] else "blue"
        custom_icon = folium.Icon(color=icon_color, icon="bus", prefix="fa")
        
        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            tooltip=tooltip_text,
            popup=folium.Popup(popup_html, max_width=300),
            icon=custom_icon
        ).add_to(marker_cluster)
    
    st_folium(bus_map, width="100%", height=500, returned_objects=[], use_container_width=True)