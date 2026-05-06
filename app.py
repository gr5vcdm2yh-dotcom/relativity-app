import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import distance
import time

# ==========================================
# 設定とセッション状態の初期化
# ==========================================
st.set_page_config(page_title="相対論GPSシミュレーター", layout="wide")

# アプリ内で保持する「経過時間」のデータを初期化
if 'elapsed_days' not in st.session_state:
    st.session_state.elapsed_days = 0.0

# 定数
BASE_LAT = 35.718815
BASE_LON = 139.708732
DRIFT_PER_DAY = 11.4 

# ==========================================
# サイドバーと解説
# ==========================================
st.sidebar.title("🚀 展示モード設定")
auto_mode = st.sidebar.checkbox("時間経過を自動でシミュレートする", value=False)
speed = st.sidebar.slider("シミュレーション速度 (1秒あたりの経過日数)", 0.01, 0.5, 0.1)

if st.sidebar.button("📍 現在地に修正 (補正ON)"):
    st.session_state.elapsed_days = 0.0
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("ボタンを押すとアインシュタインの補正が働き、ピンが目白キャンパスに戻ります。しかし、補正を止めると再びズレ始めます。")

# ==========================================
# メインロジック
# ==========================================
st.title("🌍 リアルタイム相対論誤差シミュレーター")

# 自動モードがONの場合、値を増やして再描画
if auto_mode:
    st.session_state.elapsed_days += speed
    # 少し待機してから再描画（アニメーション効果）
    time.sleep(0.5) 

# 現在のズレを計算
total_drift_km = DRIFT_PER_DAY * st.session_state.elapsed_days
drift_angle = 135 # 南東方向に固定

# 座標計算
start_point = (BASE_LAT, BASE_LON)
if total_drift_km > 0:
    end_point = distance(kilometers=total_drift_km).destination(start_point, bearing=drift_angle)
    drifted_lat, drifted_lon = end_point.latitude, end_point.longitude
else:
    drifted_lat, drifted_lon = BASE_LAT, BASE_LON

# ==========================================
# 地図と表示
# ==========================================
col1, col2 = st.columns([3, 1])

with col1:
    # 地図のズーム設定
    zoom = 13 if total_drift_km < 10 else (10 if total_drift_km < 30 else 8)
    m = folium.Map(location=[(BASE_LAT + drifted_lat)/2, (BASE_LON + drifted_lon)/2], zoom_start=zoom)
    
    # ピンの設置
    folium.Marker([BASE_LAT, BASE_LON], popup="学習院大学 (正解)", icon=folium.Icon(color="blue")).add_to(m)
    if total_drift_km > 0:
        folium.Marker([drifted_lat, drifted_lon], popup="ズレた位置", icon=folium.Icon(color="red")).add_to(m)
        folium.PolyLine([[BASE_LAT, BASE_LON], [drifted_lat, drifted_lon]], color="red", weight=2, dash_array='5').add_to(m)
    
    st_folium(m, width=800, height=500, key=f"map_{st.session_state.elapsed_days}")

with col2:
    st.metric("経過したシミュレーション時間", f"{st.session_state.elapsed_days:.2f} 日")
    st.metric("現在の位置誤差", f"{total_drift_km:.2f} km")
    
    if total_drift_km > 0:
        st.warning(f"相対論補正がないため、1日あたり{DRIFT_PER_DAY}kmのペースでズレ続けています！")
    else:
        st.success("現在は正確な位置を示しています。")

# 自動更新のためのトリガー
if auto_mode:
    st.rerun()
