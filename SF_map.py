import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# サンフランシスコの中心の緯度と経度
latitude = 37.7749
longitude = -122.4194

# 地図を生成
map = folium.Map(location=[latitude, longitude], zoom_start=12)

# Powell Stationの位置にピンを立てる
folium.Marker([37.7841, -122.4075], popup='Powell Station').add_to(map)

# Streamlitで地図を表示
folium_static(map)