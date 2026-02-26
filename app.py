import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import io

# 頁面基本設定
st.set_page_config(page_title="台灣蛙鳴空間資料地圖", layout="wide")

# 自定義標題
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🐸 台灣蛙鳴空間資料互動地圖</h1>", unsafe_allow_html=True)

# 1. 強力讀取函數：解決所有編碼問題
@st.cache_data
def load_data_safe(file_path):
    encodings = ['utf-8', 'big5', 'cp950', 'utf-8-sig']
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            return df
        except Exception:
            continue
    
    # 如果上面都失敗，使用強制讀取模式 (跳過無法解析的字元)
    return pd.read_csv(file_path, encoding='utf-8', errors='ignore')

try:
    # 讀取兩筆資料
    df_raw = load_data_safe('raw_data.csv')
    df_verified = load_data_safe('verified_data.csv')
    
    # 統一日期格式，若轉換失敗則不強制
    df_raw['Create Date'] = pd.to_datetime(df_raw['Create Date'], errors='coerce')
    df_verified['Create Date'] = pd.to_datetime(df_verified['Create Date'], errors='coerce')
    
    # 確保經緯度是數字類型，避免繪圖錯誤
    df_raw[['Latitude', 'Longitude']] = df_raw[['Latitude', 'Longitude']].apply(pd.to_numeric, errors='coerce')
    df_verified[['Latitude', 'Longitude']] = df_verified[['Latitude', 'Longitude']].apply(pd.to_numeric, errors='coerce')
    
    # 移除經緯度有缺失的資料列
    df_raw = df_raw.dropna(subset=['Latitude', 'Longitude'])
    df_verified = df_verified.dropna(subset=['Latitude', 'Longitude'])

    # 2. 建立地圖
    m = folium.Map(
        location=[23.6, 121.0], 
        zoom_start=7, 
        tiles="cartodbpositron"
    )

    # 3. 繪製 raw_data：藍色水波紋
    for _, row in df_raw.iterrows():
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
    for _, row in df_verified.iterrows():
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
    st.sidebar.metric("原始紀錄", len(df_raw))
    st.sidebar.metric("專家辨識", len(df_verified))
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💡 圖例說明")
    st.sidebar.write("🔵 藍色：原始紀錄")
    st.sidebar.write("🟡 黃色：專家已審核")

except Exception as e:
    st.error(f"抱歉，程式遇到了一個我沒料到的錯誤：{e}")
    st.info("請檢查 CSV 檔案內的欄位標頭 (Header) 是否包含：ID, Username, Latitude, Longitude")
