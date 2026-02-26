import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：深藍質感水紋版")

# 2. 藍色水波紋 CSS
st.markdown("""
<style>
@keyframes ripple {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(3.5); opacity: 0; }
}
.ripple-icon {
  background: rgba(0, 191, 255, 0.7);
  border-radius: 50%;
  animation: ripple 2s infinite;
}
</style>
""", unsafe_allow_html=True)

# 3. 讀取資料
def load_csv(name):
    try:
        return pd.read_csv(name)
    except:
        return None

df_raw = load_csv("raw_data.csv")
df_verified = load_csv("verified_data.csv")

# 4. 建立深色地圖
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 畫出藍色漣漪 (未辨識)
if df_raw is not None:
    for _, row in df_raw.iterrows():
        loc = [row['Latitude'], row['Longitude']]
        folium.Marker(
            location=loc,
            icon=folium.DivIcon(html='<div class="ripple-icon" style="width:20px; height:20px;"></div>'),
            popup=f"上傳者: {row['Username']}"
        ).add_to(m)
        folium.CircleMarker(location=loc, radius=3, color='#00FFFF', fill=True).add_to(m)

# 6. 畫出亮黃燈號 (已辨識)
if df_verified is not None:
    for _, row in df_verified.iterrows():
        loc = [row['Latitude'], row['Longitude']]
        pop = f"結果: {row['Review Identity']} | 專家: {row['Reviewer']}"
        folium.CircleMarker(
            location=loc, radius=8, color='#FFFFE0', fill=True, fill_color='#FFFF00',
            fill_opacity=0.9, weight=2, popup=pop
        ).add_to(m)

# 7. 呈現
st_folium(m, width="100%", height=700)
