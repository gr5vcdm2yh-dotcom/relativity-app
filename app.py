import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import distance

st.set_page_config(page_title="スマホの裏の「相対論」体験", layout="wide")

BASE_LAT = 35.718815
BASE_LON = 139.708732

DRIFT_PER_DAY = 11.4 

st.sidebar.header("📐 なぜズレるのか？")
st.sidebar.markdown("""
GPS衛星の時計は、2つの相対性理論の影響を受けています。

**1. 特殊相対性理論（速度の影響）**
衛星は秒速約3.9kmで移動しています。動いている時計は遅れるため、地上より **1日約7.2マイクロ秒遅れます**。

**2. 一般相対性理論（重力の影響）**
衛星は高度約2万kmにあり、地上より重力が弱いです。重力が弱い場所では時計が早く進むため、地上より **1日約45.9マイクロ秒進みます**。

**【結論】**
差し引きで、衛星の時計は地上より **1日約38.7マイクロ秒早く進みます**。
電波は光速（約30万km/s）で伝わるため、このわずかな時間のズレが、**1日で約11.4km** もの距離の誤差を生み出してしまうのです。
""")

st.title("🌍相対論迷子シュミレーター")
st.write("もしGPSにアインシュタインの相対性理論（時間の補正）が組み込まれていなかったら、あなたの現在地はどれくらいズレてしまうのでしょうか？")

days_off = st.slider(
    "補正をオフにしてからの経過時間（日）を選択してください", 
    min_value=0.0, 
    max_value=7.0, 
    value=0.0, 
    step=0.1
)

total_drift_km = DRIFT_PER_DAY * days_off

drift_angle = 135 

start_point = (BASE_LAT, BASE_LON)
if total_drift_km > 0:
    end_point = distance(kilometers=total_drift_km).destination(start_point, bearing=drift_angle)
    drifted_lat = end_point.latitude
    drifted_lon = end_point.longitude
else:
    drifted_lat = BASE_LAT
    drifted_lon = BASE_LON

zoom_level = 13 if total_drift_km < 15 else (10 if total_drift_km < 40 else 9)

center_lat = (BASE_LAT + drifted_lat) / 2
center_lon = (BASE_LON + drifted_lon) / 2
m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level)

folium.Marker(
    [BASE_LAT, BASE_LON],
    popup="本当の現在地（補正あり）",
    icon=folium.Icon(color="blue", icon="info-sign")
).add_to(m)

if total_drift_km > 0:
    folium.Marker(
        [drifted_lat, drifted_lon],
        popup=f"アインシュタイン不在の現在地（{total_drift_km:.1f}kmズレ）",
        icon=folium.Icon(color="red", icon="remove-circle")
    ).add_to(m)

    folium.PolyLine(
        locations=[[BASE_LAT, BASE_LON], [drifted_lat, drifted_lon]],
        color="red",
        weight=3,
        dash_array='5, 5',
        opacity=0.7
    ).add_to(m)

st_folium(m, width=900, height=500)

if total_drift_km == 0:
    st.success("✅ アインシュタインのおかげで、正確な位置が取得できています。")
else:
    st.error(f"⚠️ **致命的なエラー：現在地が約 {total_drift_km:.1f} km ズレています！**")


