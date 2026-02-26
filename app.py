import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：強制分色波動版")

# 2. 定義擬真藍色水波紋 CSS (模擬水滴擴散感)
st.markdown("""
<style>
@keyframes ripple-wave {
  0% { transform: scale(0.3); opacity: 1; }
  100% { transform: scale(4.5); opacity: 0; }
}
.ripple-container {
    position: relative; width: 0; height: 0;
    display: flex; justify-content: center; align-items: center;
}
.ripple-core {
    width: 10px; height: 10px; background: #00FFFF;
    border-radius: 50%; box-shadow: 0 0 10px #00FFFF;
    position: absolute; z-index: 10;
}
.ripple-out-1 {
    position: absolute; width: 40px; height: 40px;
    border: 2px solid #00BFFF; border-radius: 50%;
    animation: ripple-wave 2.5s infinite cubic-bezier(0, 0.2, 0.8, 1);
}
.ripple-out-2 {
    position: absolute; width: 40px; height: 40px;
    border: 1px solid #00BFFF; border-radius: 50%;
    animation: ripple-wave 2.5s infinite 1.25s cubic-bezier(0, 0.2, 0.8, 1);
}
</style>
""", unsafe_allow_html=True)

# 3. 讀取函數 (強制轉換座標並跳過錯誤列)
def force_load(name):
    try:
        df = pd.read_csv(name)
        df.columns = df.columns.str.strip() # 去除空格
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        return df.dropna(subset=['Latitude', 'Longitude'])
    except:
        return None

df_raw = force_load("raw_data.csv")
df_verified = force_load("verified_data.csv")

# 4. 建立地圖 (深黑背景)
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 【強制】畫出藍色水波紋 (只要在 raw_data.csv 裡面的)
if df_raw is not None:
    for _, row in df_raw.iterrows():
        icon_html = '''
        <div class="ripple-container">
            <div class="ripple-core"></div>
            <div class="ripple-out-1"></div>
            <div class="ripple-out-2"></div>
        </div>
        '''
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(html=icon_html),
            popup=f"🟦 原始點位<br>上傳者: {row.get('Username', '匿名')}"
        ).add_to(m)

# 6. 【強制】畫出黃色燈號 (只要在 verified_data.csv 裡面的)
if df_verified is not None:
    for _, row in df_verified.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=8, color='#FFFFE0', fill=True,
