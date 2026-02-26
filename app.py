import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：擬真水紋波動版")

# 2. 擬真藍色水波紋 CSS (加強多層次感)
st.markdown("""
<style>
@keyframes ripple-wave {
  0% { transform: scale(0.3); opacity: 1; }
  100% { transform: scale(4.0); opacity: 0; }
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
.ripple-out {
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

# 3. 讀取函數 (針對您的 CSV 欄位優化)
def load_frog_data(name):
    try:
        df = pd.read_csv(name)
        df.columns = df.columns.str.strip() # 清除標題空格
        # 強制將經緯度轉為數字
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        return df.dropna(subset=['Latitude', 'Longitude'])
    except:
        return None

df_raw = load_frog_data("raw_data.csv")
df_verified = load_frog_data("verified_data.csv")

# 4. 建立地圖
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 畫出藍色水波紋 (未辨識 - raw_data.csv)
if df_raw is not None:
    for _, row in df_raw.iterrows():
        # 建立擬真水紋 HTML
        icon_html = '<div class="ripple-container"><div class="ripple-core"></div><div class="ripple-out"></div><div class="ripple-out-2"></div></div>'
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(html=icon_html),
            popup=f"上傳者: {row['Username']}<br>身份: {row['Identity']}"
        ).add_to(m)

# 6. 畫出亮黃燈號 (已辨識 - verified_data.csv)
if df_verified is not None:
    for _, row in df_verified.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=8, color='#FFFFE0', fill=True,
            fill_color='#FFFF00', fill_opacity=0.9, weight=2,
            popup=f"結果: {row['Review Identity']}"
        ).add_to(m)

# 7. 呈現
st_folium(m, width="100%", height=700)
