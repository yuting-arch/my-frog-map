import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 頁面基本設定
st.set_page_config(page_title="台灣蛙鳴空間資料地圖", layout="wide")

# 自定義標題與樣式
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🐸 台灣蛙鳴空間資料互動地圖</h1>", unsafe_allow_html=True)
st.write("本網頁展示民眾錄製的原始蛙鳴點位（藍色）與經過專家審核後的點位（黃色）。")

# 1. 讀取資料 (路徑已修正為根目錄)
@st.cache_data
def load_data():
    # 讀取原始資料
    df_raw = pd.read_csv('raw_data.csv')
    # 讀取專家辨識資料
    df_verified = pd.read_csv('verified_data.csv')
    
    # 轉換日期格式 (確保排序正確)
    df_raw['Create Date'] = pd.to_datetime(df_raw['Create Date'])
    df_verified['Create Date'] = pd.to_datetime(df_verified['Create Date'])
    
    return df_raw, df_verified

try:
    raw_data, verified_data = load_data()

    # 2. 建立地圖：中心點設在台灣
    m = folium.Map(
        location=[23.6, 121.0], 
        zoom_start=7, 
        tiles="cartodbpositron",
        control_scale=True
    )

    # 3. 繪製 raw_data：藍色水波紋感
    for _, row in raw_data.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=7,
            popup=f"<b>原始紀錄</b><br>ID: {row['ID']}<br>使用者: {row['Username']}<br>日期: {row['Create Date'].strftime('%Y-%m-%d')}",
            color="#1f77b4",       # 深藍色邊框
            fill=True,
            fill_color="#a1c4fd",  # 水藍色填充
            fill_opacity=0.7,
            weight=2               # 邊框粗度營造水波感
        ).add_to(m)

    # 4. 繪製 verified_data：黃色半透明燈光感
    for _, row in verified_data.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=12,             # 較大半徑營造光暈效果
            popup=f"<b>✅ 專家已審核</b><br>物種: {row['Review Identity']}<br>審核者: {row['Reviewer']}<br>日期: {row['Create Date'].strftime('%Y-%m-%d')}",
            color="#ffc107",       # 金黃色邊框
            fill=True,
            fill_color="#fff176",  # 燈光黃
            fill_opacity=0.5,      # 較低透明度營造柔和感
            weight=0               # 移除邊框讓它更像光
        ).add_to(m)

    # 5. 在 Streamlit 中顯示地圖
    folium_static(m, width=1100, height=600)

    # 側邊欄：統計資訊與更新日期
    st.sidebar.title("📊 資料統計")
    st.sidebar.metric("原始紀錄總數", len(raw_data))
    st.sidebar.metric("專家辨識總數", len(verified_data))
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"📅 最後更新日期：{raw_data['Create Date'].max().strftime('%Y-%m-%d')}")
    
    st.sidebar.markdown("""
    ### 🔴 圖例說明
    * 🔵 **藍色小點**：民眾上傳的原始錄音
    * 🟡 **黃色大點**：已由專家完成物種辨識
    """)

except Exception as e:
    st.error(f"❌ 發生錯誤：{e}")
    st.info("請確認您的 CSV 檔案中包含 ID, Username, Latitude, Longitude 等正確欄位名稱。")
