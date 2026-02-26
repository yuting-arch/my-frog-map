import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：藍色漣漪水紋版")

# 2. 定義「水波紋動畫」的 CSS 樣式
# 這段代碼會讓藍色圓圈像水滴一樣擴散
ripple_style = """
<style>
@keyframes ripple {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(2.5); opacity: 0; }
}
.ripple-icon {
  background: rgba(0, 150, 255, 0.6);
  border-radius: 50%;
  animation: ripple 2s infinite;
}
</style>
"""
st.markdown(ripple_style, unsafe_allow_html=True)

# 3. 讀取資料函數
def load_data(file_name):
    try:
        return pd.read_csv(file_name)
    except:
        return None

df_raw = load_data("raw_data.csv")      # 未辨識
df_verified = load_data("verified_data.csv")  # 已辨識

# 4. 建立地圖
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB positron")

# 5. 處理「未辨識」點位：藍色漣漪
if df_raw is not None:
    for _, row in df_raw.iterrows():
        loc = [row['Latitude'], row['Longitude']]
        popup_text = f"👤 上傳者: {row['Username']}<br>⚠️ 狀態: 待辨識(水紋波動中)"
        
        # 使用 DivIcon 注入自定義的漣漪動畫
        folium.Marker(
            location=loc,
            icon=folium.DivIcon(
                html='<div class="ripple-icon" style="width:20px; height:20px;"></div>'
            ),
            popup=folium.Popup(popup_text, max_width=250)
        ).add_to(m)
        
        # 加上一個中心深藍色小點
        folium.CircleMarker(
            location=loc, radius=3, color='#0077FF', fill=True, fill_opacity=1
        ).add_to(m)

# 6. 處理「已辨識」點位：亮淺黃色燈號
if df_verified is not None:
    for _, row in df_verified.iterrows():
        loc = [row['Latitude'], row['Longitude']]
        popup_text = f"🐸 辨識結果: <b>{row['Review Identity']}</b><br>👨‍🔬 專家
