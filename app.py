import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 頁面基本設定
st.set_page_config(page_title="台灣蛙鳴空間資料地圖", layout="wide")

# 自定義標題
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🐸 台灣蛙鳴空間資料互動地圖</h1>", unsafe_allow_html=True)
st.write("本網頁展示民眾錄製的原始蛙鳴點位（藍色）與經過專家審核後的點位（黃色）。")

# 1. 讀取資料 (加入編碼自動判定)
@st.cache_data
def load_data():
    def read_csv_with_encoding(file_path):
        # 先嘗試 UTF-8 (國際標準)，失敗則嘗試 Big5 (繁體中文常見格式)
        try:
            return pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            return pd.read_csv(file_path, encoding='big5')

    df_raw = read_csv_with_encoding('raw_data.csv')
    df_verified = read_csv_with_encoding('verified_data.csv')
    
    # 轉換日期格式
    df_raw['Create Date'] = pd.to_datetime(df_raw['Create Date'])
    df_verified['Create Date'] = pd.to_datetime(df_verified['Create Date'])
    
    return df_raw, df_verified

try:
    raw_data, verified_data = load_data()

    # 2. 建立地圖
    m = folium.Map(
        location=[23.6, 121.0], 
        zoom_start=7, 
        tiles="cartodbpositron"
    )

    # 3. 繪製 raw_data：藍色水波紋感
    for _, row in raw_data.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=7,
            popup=f"ID: {row['ID']}<br>使用者: {row['Username']}",
            color="#1f77b4",
            fill=True,
            fill_color="#a1c4fd",
            fill_opacity=0.7,
            weight=2
        ).add_to(m)

    # 4. 繪製 verified_data：黃色燈光感
    for _, row in verified_data.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=12,
            popup=f"物種: {row['Review Identity']}<br>審核者: {row['Reviewer']}",
            color="#ffc107",
            fill=True,
            fill_color="#fff176",
            fill_opacity=0.5,
            weight=0
        ).add_to(m)

    # 5. 顯示地圖
    folium_static(m, width=1100, height=600)

    # 側邊欄
    st.sidebar.title("📊 資料統計")
    st.sidebar.metric("原始紀錄總數", len(raw_data))
    st.sidebar.metric("專家辨識總數", len(verified_data))
    st.sidebar.info(f"📅 最後更新：{raw_data['Create Date'].max().strftime('%Y-%m-%d')}")

except Exception as e:
    st.error(f"❌ 發生錯誤：{e}")
    st.info("若錯誤持續發生，請確認 CSV 欄位名稱是否包含 ID, Username, Latitude, Longitude, Review Identity, Reviewer")
