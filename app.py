import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：藍色漣漪水紋版")

# 2. 定義「藍色水波紋」動畫樣式
ripple_style = """
<style>
@keyframes ripple {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(3.0); opacity: 0; }
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

# 5. 處理「未辨識」點位：藍色漣漪動畫
if df_raw is not None:
    for _, row in df_raw.iterrows():
        loc = [row['Latitude'], row['Longitude']]
        # 修正後的 Popup 寫法，避免 f-string 錯誤
        user_name = str(row['Username'])
        create_date = str(row['Create Date'])
        popup_html = f"👤 上傳者: {user_name}<br>📅 日期: {create_date}<br>⚠️ 狀態: 待辨識(水紋波動中)"
        
        folium.Marker(
            location=loc,
            icon=folium.DivIcon(html='<div class="ripple-icon" style="width:20px; height:20px;"></div>'),
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(m)
        
        # 中心深藍點
        folium.CircleMarker(location=loc, radius=3, color='#0077FF', fill=True, fill_opacity=1).add_to(m)

# 6. 處理「已辨識」點位：亮淺黃色圓燈
if df_verified is not None:
    for _, row in df_verified.iterrows():
        loc = [row['Latitude'], row['Longitude']]
        review_id = str(row['Review Identity'])
        reviewer = str(row['Reviewer'])
        popup_html = f"🐸 辨識結果: <b>{review_id}</b><br>👨‍🔬 專家: {reviewer}"
        
        folium.CircleMarker(
            location=loc,
            radius=8,
            color='#FFFFBB',      # 淺黃色邊框
            fill=True,
            fill_color='#FFFF00', # 鮮黃色中心
            fill_opacity=0.9,
            weight=2,
            popup=folium.Popup(popup_html, max_width=2
