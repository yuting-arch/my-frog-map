import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="全台青蛙鳴聲監測地圖", layout="wide")
st.title("🐸 青蛙鳴聲監測計畫：即時回報與專家審核地圖")

# 定義讀取函數，增加處理欄位名稱的邏輯
def load_data(file_name):
    try:
        df = pd.read_csv(file_name)
        # 統一將欄位轉為小寫方便後續處理，但保留原始資料顯示
        return df
    except:
        return None

# 讀取你的兩份報表
df_raw = load_data("raw_data.csv")      # 未辨識
df_verified = load_data("verified_data.csv")  # 已辨識

# 建立地圖中心點 (台灣)
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB positron")

# 1. 處理「未辨識」點位 (紅色漣漪)
if df_raw is not None:
    for _, row in df_raw.iterrows():
        # 注意：這裡使用你提供的欄位名稱 Latitude, Longitude
        loc = [row['Latitude'], row['Longitude']]
        popup_text = f"👤 上傳者: {row['Username']}<br>📅 日期: {row['Create Date']}<br>⚠️ 狀態: 等待辨識中"
        
        folium.Circle(loc, radius=1000, color='red', weight=1, fill=False).add_to(m)
        folium.CircleMarker(
            loc, radius=6, color='red', fill=True, fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(m)

# 2. 處理「已辨識」點位 (黃色亮星)
if df_verified is not None:
    for _, row in df_verified.iterrows():
        loc = [row['Latitude'], row['Longitude']]
        # 這裡多加入了 Reviewer 資訊
        popup_text = (
            f"👤 上傳者: {row['Username']}<br>"
            f"🐸 辨識結果: <b>{row['Review Identity']}</b><br>"
            f"👨‍🔬 審核專家: {row['Reviewer']}<br>"
            f"📅 審核日期: {row['Review Date']}"
        )
        
        folium.Marker(
            loc, 
            icon=folium.Icon(color='orange', icon='star'),
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(m)

# 顯示地圖
st_folium(m, width="100%", height=700)

# 數據看板
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("本月新收集", len(df_raw) if df_raw is not None else 0)
with col2:
    st.metric("專家已辨識", len(df_verified) if df_verified is not None else 0)
with col3:
    total = (len(df_raw) if df_raw is not None else 0) + (len(df_verified) if df_verified is not None else 0)
    st.metric("總點位數", total)
