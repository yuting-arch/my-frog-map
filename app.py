import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：藍色漣漪水紋版")

# 2. 定義藍色水波紋 CSS
ripple_style = """
<style>
@keyframes ripple {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(3.5); opacity: 0; }
}
.ripple-icon {
  background: rgba(0, 150, 255, 0.7);
  border-radius: 50%;
  animation: ripple 2s infinite;
}
</style>
"""
st.markdown(ripple_style, unsafe_allow_html=True)

# 3. 讀取資料函數
def load_data(file_name):
    try:
        df = pd.read_csv(file_name)
        return df
    except:
        return None

df_raw = load_data("raw_data.csv")      # 未辨識
df_verified = load_data("verified_data.csv")  # 已辨識

# 4. 建立地圖
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB positron")

# 5. 處理「未辨識」：藍色漣漪
if df_raw is not None:
    for _, row in df_raw.iterrows():
        loc = [row['Latitude'], row['Longitude']]
        # 彈出視窗資訊
        p_text = f"👤 上傳者: {row['Username']}<br>📅 日期: {row['Create Date']}"
        
        # 動態水紋
        folium.Marker(
            location=loc,
            icon=folium.DivIcon(html='<div class="ripple-icon" style="width:20px; height:20px;"></div>'),
            popup=folium.Popup(p_text, max_width=250)
        ).add_to(m)
        
        # 中心點
        folium.CircleMarker(location=loc, radius=3, color='#0077FF', fill=True, fill_opacity=1).add_to(m)

# 6. 處理「已辨識」：亮淺黃色燈號
if df_verified is not None:
    for _, row in df_verified.iterrows():
        loc = [row['Latitude'], row['Longitude']]
        # 彈出視窗資訊
        v_text = f"🐸 辨識結果: {row['Review Identity']}<br>👨‍🔬 專家: {row['Reviewer']}"
        
        folium.CircleMarker(
            location=loc,
            radius=8,
            color='#FFFFBB',      # 淺黃色邊框
            fill=True,
            fill_color='#FFFF00', # 鮮黃色中心
            fill_opacity=0.9,
            weight=2,
            popup=folium.Popup(v_text, max_width=250)
        ).add_to(m)

# 7. 顯示地圖
st_folium(m, width="100%", height=700)

# 底部統計
st.divider()
c1, c2 = st.columns(2)
c1.metric("🌊 本月新收集 (藍色漣漪)", len(df_raw) if df_raw is not None else 0)
c2.metric("🌟 專家已辨識 (黃色燈號)", len(df_verified) if df_verified is not None else 0)
