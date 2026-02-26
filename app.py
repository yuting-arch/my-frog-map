import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 設定頁面標題
st.set_page_config(page_title="台灣蛙鳴紀錄地圖", layout="wide")
st.title("🐸 台灣蛙鳴空間資料互動地圖")

# 1. 讀取資料 (加上簡單的錯誤處理)
@st.cache_data
def load_data():
    raw_df = pd.read_csv('data/raw_data.csv')
    verified_df = pd.read_csv('data/verified_data.csv')
    return raw_df, verified_df

try:
    df_raw, df_verified = load_data()
except Exception as e:
    st.error(f"資料讀取失敗，請檢查檔案路徑。錯誤: {e}")
    st.stop()

# 2. 建立地圖底圖 (中心點設在台灣)
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="cartodbpositron")

# 3. 繪製 raw_data (藍色水波紋感)
for _, row in df_raw.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=8,
        popup=f"ID: {row['ID']}<br>錄音者: {row['Username']}",
        color="#3498db",       # 藍色邊框
        fill=True,
        fill_color="#85c1e9",  # 淺藍填充
        fill_opacity=0.6,
        weight=2               # 邊框厚度增加，模擬波紋邊緣
    ).add_to(m)

# 4. 繪製 verified_data (黃色半透明燈光感)
for _, row in df_verified.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=10,             # 稍微大一點點，像光暈
        popup=f"專家辨識: {row['Review Identity']}<br>審核者: {row['Reviewer']}",
        color="#f1c40f",       # 金黃色邊框
        fill=True,
        fill_color="#f4d03f",  # 燈光黃
        fill_opacity=0.4,      # 較低透明度營造燈光感
        weight=0               # 無邊框，更像光暈
    ).add_to(m)

# 5. 在 Streamlit 顯示地圖
folium_static(m, width=1000, height=600)

# 側邊欄資訊
st.sidebar.info(f"📅 資料最後更新日期: {df_raw['Create Date'].max()}")
st.sidebar.markdown("""
### 圖例說明
- 🔵 **藍色點位**：民眾原始錄音紀錄
- 🟡 **黃色光暈**：專家已辨識紀錄
""")
