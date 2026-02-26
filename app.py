import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：擬真水紋波動版")

# 2. 定義「擬真藍色水波紋」CSS (模擬 image_bf1e98.png 的多層擴散感)
st.markdown("""
<style>
@keyframes ripple-wave {
  0% { transform: scale(0.2); opacity: 1; }
  100% { transform: scale(4.0); opacity: 0; }
}
.ripple-container {
    position: relative; width: 0; height: 0;
    display: flex; justify-content: center; align-items: center;
}
.ripple-core {
    width: 8px; height: 8px; background: #00FFFF;
    border-radius: 50%; box-shadow: 0 0 10px #00FFFF;
    position: absolute; z-index: 10;
}
.ripple-out-1 {
    position: absolute; width: 35px; height: 35px;
    border: 2px solid #00BFFF; border-radius: 50%;
    animation: ripple-wave 2.5s infinite cubic-bezier(0, 0.2, 0.8, 1);
}
.ripple-out-2 {
    position: absolute; width: 35px; height: 35px;
    border: 1px solid #00BFFF; border-radius: 50%;
    animation: ripple-wave 2.5s infinite 1.25s cubic-bezier(0, 0.2, 0.8, 1);
}
</style>
""", unsafe_allow_html=True)

# 3. 讀取函數
def load_data(name):
    try:
        df = pd.read_csv(name)
        df.columns = df.columns.str.strip()
        # 強制轉換經緯度為數字
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        return df.dropna(subset=['Latitude', 'Longitude'])
    except:
        return None

df_raw = load_data("raw_data.csv")
df_verified = load_data("verified_data.csv")

# 4. 建立地圖 (深色質感背景)
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 畫出藍色擬真水波紋 (對應 raw_data.csv)
if df_raw is not None:
    for _, row in df_raw.iterrows():
        # HTML 結構包含核心點與兩層動態波紋
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
            popup=f"👤 上傳者: {row['Username']}<br>⚠️ 狀態: 新增待辨識"
        ).add_to(m)

# 6. 畫出亮黃燈號 (對應 verified_data.csv)
if df_verified is not None:
    for _, row in df_verified.iterrows():
        pop_text = f"🐸 辨識結果: <b>{row['Review Identity']}</b><br>👨‍🔬 專家: {row.get('Reviewer', '已審核')}"
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=8, color='#FFFFE0', fill=True,
            fill_color='#FFFF00', fill_opacity=0.9, weight=2,
            popup=folium.Popup(pop_text, max_width=250)
        ).add_to(m)

# 7. 呈現地圖
st_folium(m, width="100%", height=700)
