import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：擬真水紋波動版")

# 2. 定義藍色水波紋 CSS
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
""", unsafe_allow_html=True)

# 3. 強力座標修復函數
def force_fix_data(file_name):
    try:
        df = pd.read_csv(file_name)
        df.columns = df.columns.str.strip()
        # 強制轉換並排除非數字內容
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        return df.dropna(subset=['Latitude', 'Longitude'])
    except:
        return None

df_blue = force_fix_data("raw_data.csv")
df_yellow = force_fix_data("verified_data.csv")

# 4. 建立地圖
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 強制畫出藍色水波紋 (raw_data.csv)
if df_blue is not None:
    for _, row in df_blue.iterrows():
        # 這裡強制轉為 float 確保 folium 讀得懂
        lat, lon = float(row['Latitude']), float(row['Longitude'])
        icon_html = '<div class="ripple-container"><div class="ripple-core"></div><div class="ripple-out-1"></div><div class="ripple-out-2"></div></div>'
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=icon_html),
            popup=f"上傳者: {row.get('Username', '未知')}"
        ).add_to(m)

# 6. 強制畫出黃色燈號 (verified_data.csv)
if df_yellow is not None:
    for _, row in df_yellow.iterrows():
        lat, lon = float(row['Latitude']), float(row['Longitude'])
        folium.CircleMarker(
            location=[lat, lon],
            radius=8, color='#FFFFE0', fill=True,
            fill_color='#FFFF00', fill_opacity=0.9, weight=2,
            popup=f"結果: {row.get('Review Identity', '已辨識')}"
        ).add_to(m)

# 7. 呈現
st_folium(m, width="100%", height=700)
