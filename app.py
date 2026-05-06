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
    st.session_state.elapsed_days = 0.0 # シミュレーション上の累積経過日
if 'last_run_time' not in st.session_state:
    st.session_state.last_run_time = time.time() # 前回の更新時刻

# 物理定数
BASE_LAT = 35.718815
BASE_LON = 139.708732
DRIFT_PER_DAY = 11.4 

# ==========================================
# サイドバー：時間制御
# ==========================================
st.sidebar.title("🚀 シミュレーション制御")

# スライダー：1秒（最小）〜 60秒（最大：1分）
# 単位は「1秒あたりのシミュレーション進行秒数」
time_multiplier = st.sidebar.slider(
    "時間加速倍率 (1秒につき何秒進めるか)", 
    min_value=1, 
    max_value=60, 
    value=10,
    help="1に設定すると現実と同じ速さ、60に設定すると1秒で1分分の時間が経過します。"
)

auto_mode = st.sidebar.checkbox("シミュレーション開始", value=False)

if st.sidebar.button("📍 補正を実行（リセット）"):
    st.session_state.elapsed_days = 0.0
    st.session_state.last_run_time = time.time()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write("### 現在の状態")
# 秒単位での表示
total_sim_seconds = st.session_state.elapsed_days * 86400
st.sidebar.write(f"累積経過時間: {total_sim_seconds:.1f} 秒")

# ==========================================
# 物理ロジック（時間更新）
# ==========================================
current_real_time = time.time()
# 前回の更新からの経過実時間を計算（IT的工夫）
delta_real_time = current_real_time - st.session_state.last_run_time
st.session_state.last_run_time = current_real_time

if auto_mode:
    # シミュレーション上の経過秒数 = 実経過秒数 × 倍率
    delta_sim_seconds = delta_real_time * time_multiplier
    # 日単位に変換して累積
    st.session_state.elapsed_days += delta_sim_seconds / 86400

# ズレの計算
total_drift_km = DRIFT_PER_DAY * st.session_state.elapsed_days
end_point = distance(kilometers=total_drift_km).destination((BASE_LAT, BASE_LON), bearing=135)

# ==========================================
# メイン画面表示
# ==========================================
st.title("🌍 リアルタイム相対論誤差シミュレーター")

col1, col2 = st.columns([3, 1])

with col1:
    # 地図の描画
    view_state = pdk.ViewState(latitude=BASE_LAT, longitude=BASE_LON, zoom=12)
    
    df_points = pd.DataFrame([
        {"lat": BASE_LAT, "lon": BASE_LON, "color": [0, 0, 255, 200]},
        {"lat": end_point.latitude, "lon": end_point.longitude, "color": [255, 0, 0, 200]}
    ])

    st.pydeck_chart(pdk.Deck(
        map_style=None,
        initial_view_state=view_state,
        layers=[
            pdk.Layer("ScatterplotLayer", df_points, get_position="[lon, lat]", get_color="color", get_radius=300),
            pdk.Layer(
                "LineLayer",
                pd.DataFrame([{"start": [BASE_LON, BASE_LAT], "end": [end_point.longitude, end_point.latitude]}]),
                get_source_position="start", get_target_position="end", get_color=[255, 0, 0, 150], get_width=3
            )
        ]
    ))

with col2:
    # 物理学的な「ズレ」のリアルタイム表示
    st.metric("位置誤差 (m)", f"{total_drift_km * 1000:.2f} m")
    st.write(f"**加速倍率:** {time_multiplier}倍速")
    
    if total_drift_km > 0:
        # 秒速換算の解説（物理学科らしい補足）
        drift_speed_ms = (DRIFT_PER_DAY * 1000 / 86400) * time_multiplier
        st.write(f"現在のズレる速さ: 約 {drift_speed_ms:.4f} m/s")
        st.info("相対論補正を行わない場合、この速度で現在地が『逃げて』いきます。")

# 再描画のループ（自動モード時）
if auto_mode:
    time.sleep(0.05) # 描画負荷を抑えつつ滑らかさを維持
    st.rerun()
