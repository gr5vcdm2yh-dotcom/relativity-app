import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.distance import distance
import time

# ==========================================
# 設定とセッション状態
# ==========================================
st.set_page_config(page_title="GPS相対論シミュレーター", layout="wide")

if 'elapsed_days' not in st.session_state:
    st.session_state.elapsed_days = 0.0
if 'last_run_time' not in st.session_state:
    st.session_state.last_run_time = time.time()

# 定数
BASE_LAT, BASE_LON = 35.718815, 139.708732
DRIFT_PER_DAY = 11.4 

# ==========================================
# UI部
# ==========================================
st.sidebar.title("🚀 制御パネル")

# 加速倍率（負荷軽減のため、少し控えめの範囲を推奨）
time_multiplier = st.sidebar.select_slider(
    "時間加速倍率", 
    options=[1, 10, 30, 60, 300, 600], 
    value=60,
    help="倍率が高いほど、赤い点が早く動きます。"
)

auto_mode = st.sidebar.checkbox("シミュレーション開始", value=False)

if st.sidebar.button("📍 補正を実行（リセット）"):
    st.session_state.elapsed_days = 0.0
    st.session_state.last_run_time = time.time()
    st.rerun()

# ==========================================
# 軽量ロジック
# ==========================================
current_real_time = time.time()
delta_real_time = current_real_time - st.session_state.last_run_time
st.session_state.last_run_time = current_real_time

if auto_mode:
    # 経過時間を計算
    st.session_state.elapsed_days += (delta_real_time * time_multiplier) / 86400

total_drift_km = DRIFT_PER_DAY * st.session_state.elapsed_days
end_point = distance(kilometers=total_drift_km).destination((BASE_LAT, BASE_LON), bearing=135)

# 地図用データ（軽量なリスト形式で作成）
points_data = [
    {"lat": BASE_LAT, "lon": BASE_LON, "color": [0, 120, 255], "label": "正解"},
    {"lat": end_point.latitude, "lon": end_point.longitude, "color": [255, 50, 50], "label": "誤差"}
]
df_points = pd.DataFrame(points_data)

# ==========================================
# メイン表示
# ==========================================
st.title("🌍 GPS相対論誤差シミュレーター")

col1, col2 = st.columns([3, 1])

with col1:
    # 視認性の高いレイヤー設定
    layer = pdk.Layer(
        "ScatterplotLayer",
        df_points,
        get_position="[lon, lat]",
        get_fill_color="color",
        get_line_color=[255, 255, 255], # 白い縁取りで視認性アップ
        line_width_min_pixels=2,
        stroked=True,
        get_radius=15, # 半径を小さく設定
        radius_min_pixels=6, # ズームアウトしても小さくなりすぎない
        radius_max_pixels=15,
    )

    line_layer = pdk.Layer(
        "LineLayer",
        pd.DataFrame([{"start": [BASE_LON, BASE_LAT], "end": [end_point.longitude, end_point.latitude]}]),
        get_source_position="start",
        get_target_position="end",
        get_color=[255, 50, 50, 150],
        get_width=2,
    )

    # 地図描画（スタイルをNoneにしてロードを最速化）
    st.pydeck_chart(pdk.Deck(
        map_style=None, 
        initial_view_state=pdk.ViewState(latitude=BASE_LAT, longitude=BASE_LON, zoom=12),
        layers=[line_layer, layer]
    ))

with col2:
    st.metric("位置誤差", f"{total_drift_km * 1000:.1f} m")
    st.write(f"加速: {time_multiplier}倍")
    st.caption("※スマホでの動作を優先し、更新間隔を調整しています。")

# ==========================================
# スマホ・軽量化のためのインターバル
# ==========================================
if auto_mode:
    # 0.5秒待機。これにより通信回数が減り、スマホでも安定します。
    time.sleep(0.5)
    st.rerun()
