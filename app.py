import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：擬真水紋波動版")

# 2. 定義擬真藍色水波紋 CSS (使用最安全的單行字串組合，防止縮排報錯)
ripple_css = """
<style>
@keyframes ripple-wave {
  0% { transform: scale(0.2); opacity: 1; }
  100% { transform: scale(4.5); opacity: 0; }
}
.ripple-container {
    position: relative; width: 0; height: 0;
    display: flex; justify-content: center; align-items: center;
}
.ripple-core {
    width: 10px; height: 10px; background: #00FFFF;
    border-radius: 50%; box-shadow: 0 0 12px #00FFFF;
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
"""
st.markdown(ripple_css, unsafe_allow_html=True)

# 3. 讀取資料 (直接處理，若失敗則顯示錯誤)
df = pd.read_csv("raw_data.csv")
df.columns = df.columns.str.strip() # 強制清除欄位前後空格

# 確保經緯度是數字類型
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df = df.dropna(subset=['Latitude', 'Longitude']) # 移除無效座標

# 4. 建立地圖 (深色背景)
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 繪製藍色擬真水波紋
for index, row in df.iterrows():
    # 建立多層次水紋 HTML
    icon_html = '<div class="ripple-container"><div class="ripple-core"></div><div class="ripple-out-1"></div><div class="ripple-out-2"></div></div>'
    
    folium.Marker(
        location=[float(row['Latitude']), float(row['Longitude'])],
        icon=folium.DivIcon(html=icon_html),
        popup=f"上傳者: {row.get('Username', '匿名')}"
    ).add_to(m)

# 6. 呈現地圖
st_folium(m, width="100%", height=700)
