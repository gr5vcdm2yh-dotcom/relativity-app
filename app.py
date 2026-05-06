import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.distance import distance
import time

# ページ設定
st.set_page_config(page_title="相対論GPSシミュレーター", layout="wide")

# 状態保持
if 'elapsed_days' not in st.session_state:
    st.session_state.elapsed_days = 0.0

# 物理定数
BASE_LAT = 35.718815
BASE_LON = 139.708732
DRIFT_PER_DAY = 11.4 

# --- サイドバー ---
st.sidebar.title("🚀 展示モード設定")
auto_mode = st.sidebar.checkbox("時間経過を自動でシミュレートする", value=False)
speed = st.sidebar.slider("更新の速さ", 0.01, 0.2, 0.05)

if st.sidebar.button("📍 現在地に修正 (補正ON)"):
    st.session_state.elapsed_days = 0.0
    st.rerun()

# --- ロジック ---
if auto_mode:
    st.session_state.elapsed_days += speed

total_drift_km = DRIFT_PER_DAY * st.session_state.elapsed_days
end_point = distance(kilometers=total_drift_km).destination((BASE_LAT, BASE_LON), bearing=135)

# 地図用のデータ準備
df_points = pd.DataFrame([
    {"lat": BASE_LAT, "lon": BASE_LON, "color": [0, 0, 255, 200], "size": 300},
    {"lat": end_point.latitude, "lon": end_point.longitude, "color": [255, 0, 0, 200], "size": 300}
])

# --- 地図表示 (Pydeck) ---
st.title("🌍 リアルタイム相対論誤差シミュレーター")

# ここが重要！ map_style を "light" や "dark" にするとトークンなしで動く確率が上がります
view_state = pdk.ViewState(
    latitude=BASE_LAT,
    longitude=BASE_LON,
    zoom=10,
    pitch=0
)

st.pydeck_chart(pdk.Deck(
    map_style=None, # None にすると Streamlit のデフォルト設定が使われます
    initial_view_state=view_state,
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            df_points,
            get_position="[lon, lat]",
            get_color="color",
            get_radius="size",
        ),
        pdk.Layer(
            "LineLayer",
            pd.DataFrame([{"start": [BASE_LON, BASE_LAT], "end": [end_point.longitude, end_point.latitude]}]),
            get_source_position="start",
            get_target_position="end",
            get_color=[255, 0, 0, 150],
            get_width=3,
        )
    ]
))

# 誤差の表示
st.metric("位置誤差", f"{total_drift_km:.2f} km")

# 自動更新
if auto_mode:
    time.sleep(0.1)
    st.rerun()
