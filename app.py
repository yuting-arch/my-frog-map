import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 頁面基本設定
st.set_page_config(page_title="台灣蛙鳴空間資料地圖", layout="wide")

# 自定義標題
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🐸 台灣蛙鳴空間資料互動地圖</h1>", unsafe_allow_html=True)

# 1. 核心讀取函數：使用萬用編碼相容模式
@st.cache_data
def load_data_final():
    def try_read(file_name):
        # 嘗試清單：UTF-8 -> Big5 -> CP950
        for enc in ['utf-8', 'big5', 'cp950', 'utf-8-sig']:
            try:
                return pd.read_csv(file_name, encoding=enc)
            except:
                continue
        # 如果都失敗，使用最暴力的方式讀取，無視錯誤字元
        return pd.read_csv(file_name, encoding='latin1')

    df_raw = try_read('raw_data.csv')
    df_verified = try_read('verified_data.csv')
    
    # 數值轉換與清洗 (確保經緯度正確)
    for df in [df_raw, df_verified]:
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        df['Create Date'] = pd.to_datetime(df['Create Date'], errors='coerce')
    
    return df_raw.dropna(subset=['Latitude', 'Longitude']), \
           df_verified.dropna(subset=['Latitude', 'Longitude'])

try:
    raw_data, verified_data = load_data_final()

    # 2. 建立地圖
    m = folium.Map(
        location=[23.6, 121.0], 
        zoom_start=7, 
        tiles="cartodbpositron"
    )

    # 3. 繪製 raw_data：藍色水波紋
    for _, row in raw_data.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=6,
            popup=f"ID: {row['ID']}<br>錄音者: {row['Username']}",
            color="#3498db",
            fill=True,
            fill_color="#85c1e9",
            fill_opacity=0.6,
            weight=2
        ).add_to(m)

    # 4. 繪製 verified_data：黃色燈光
    for _, row in verified_data.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=10,
            popup=f"專家辨識: {row['Review Identity']}<br>審核者: {row['Reviewer']}",
            color="#f1c40f",
            fill=True,
            fill_color="#f4d03f",
            fill_opacity=0.4,
            weight=0
        ).add_to(m)

    # 5. 顯示地圖
    folium_static(m, width=1100, height=600)

    # 側邊欄統計
    st.sidebar.title("📊 資料統計")
    st.sidebar.metric("原始紀錄", len(raw_data))
    st.sidebar.metric("專家辨識", len(verified_data))
    
    if not raw_data.empty:
        latest_date = raw_data['Create Date'].max()
        if pd.notnull(latest_date):
            st.sidebar.info(f"📅 最後更新：{latest_date.strftime('%Y-%m-%d')}")

except Exception as e:
    st.error(f"偵測到報錯：{e}")
    st.info("請確認 CSV 檔案中的標頭欄位名稱是否正確。")
