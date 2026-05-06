import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.distance import distance
import time

# ==========================================
# 設定とセッション状態の初期化
# ==========================================
st.set_page_config(page_title="相対論GPSシミュレーター", layout="wide")

# 状態保持
if 'elapsed_days' not in st.session_state:
    st.session_state.elapsed_days = 0.0

# 物理定数
BASE_LAT = 35.718815
BASE_LON = 139.708732
DRIFT_PER_DAY = 11.4 

# ==========================================
# サイドバー
# ==========================================
st.sidebar.title("🚀 展示モード設定")
auto_mode = st.sidebar.checkbox("時間経過を自動でシミュレートする", value=False)
# 更新速度（滑らかさのために細かく設定）
speed = st.sidebar.slider("更新の速さ", 0.01, 0.2, 0.05)

if st.sidebar.button("📍 現在地に修正 (補正ON)"):
    st.session_state.elapsed_days = 0.0
    st.rerun()

# ==========================================
# ロジック（座標計算）
# ==========================================
if auto_mode:
    st.session_state.elapsed_days += speed

# ズレの計算
total_drift_km = DRIFT_PER_DAY * st.session_state.elapsed_days
start_point = (BASE_LAT, BASE_LON)
end_point = distance(kilometers=total_drift_km).destination(start_point, bearing=135)

# 地図表示用のデータフレーム作成
# Pydeckは「データフレーム」を渡すと、その中身を滑らかに更新してくれます
df_points = pd.DataFrame([
    {"lat": BASE_LAT, "lon": BASE_LON, "name": "正解", "color": [0, 0, 255, 200]}, # 青
    {"lat": end_point.latitude, "lon": end_point.longitude, "name": "ズレ", "color": [255, 0, 0, 200]} # 赤
])

# ==========================================
# メイン画面表示
# ==========================================
st.title("🌍 リアルタイム相対論誤差シミュレーター")

col1, col2 = st.columns([3, 1])

with col1:
    # Pydeckによる高速描画設定
    view_state = pdk.ViewState(
        latitude=BASE_LAT,
        longitude=BASE_LON,
        zoom=10,
        pitch=0
    )

    # ピンのレイヤー
    layer_points = pdk.Layer(
        "ScatterplotLayer",
        df_points,
        get_position="[lon, lat]",
        get_color="color",
        get_radius=500, # 半径(m)
        pickable=True,
    )

    # 正解とズレを繋ぐ線のレイヤー
    layer_line = pdk.Layer(
        "LineLayer",
        pd.DataFrame([{"start": [BASE_LON, BASE_LAT], "end": [end_point.longitude, end_point.latitude]}]),
        get_source_position="start",
        get_target_position="end",
        get_color=[255, 0, 0, 150],
        get_width=3,
    )

    # 地図の描画（ここが滑らかさの鍵！）
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=[layer_line, layer_points],
    ))

with col2:
    st.metric("シミュレーション時間", f"{st.session_state.elapsed_days:.2f} 日")
    st.metric("位置誤差", f"{total_drift_km:.2f} km")
    
    if total_drift_km > 0:
        st.warning(f"現在地からどんどん遠ざかっています！")
    else:
        st.success("アインシュタイン補正中...")

# 自動更新：0.1秒待って再実行（ブラウザの負荷を抑えつつ滑らかに見せる）
if auto_mode:
    time.sleep(0.1)
    st.rerun()
