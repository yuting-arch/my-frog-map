import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：擬真水紋波動版")

# 2. 擬真藍色水波紋 CSS (多層擴散動畫)
st.markdown("""
<style>
@keyframes ripple-wave {
  0% { transform: scale(0.3); opacity: 1; }
  100% { transform: scale(3.5); opacity: 0; }
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
.ripple-out {
    position: absolute; width: 30px; height: 30px;
    border: 2px solid #00BFFF; border-radius: 50%;
    animation: ripple-wave 2s infinite cubic-bezier(0, 0.2, 0.8, 1);
}
.ripple-out-2 {
    position: absolute; width: 30px; height: 30px;
    border: 1px solid #00BFFF; border-radius: 50%;
    animation: ripple-wave 2s infinite 1s cubic-bezier(0, 0.2, 0.8, 1);
}
</style>
""", unsafe_allow_html=True)

# 3. 超強讀取函數
def load_data_final(name):
    try:
        df = pd.read_csv(name)
        df.columns = df.columns.str.strip() # 去除標題空格
        # 強制尋找包含 lat/lon 的欄位並轉為數字
        lat_col = [c for c in df.columns if 'Lat' in c or 'lat' in c][0]
        lon_col = [c for c in df.columns if 'Lon' in c or 'lon' in c][0]
        df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
        df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')
        return df.dropna(subset=[lat_col, lon_col]), lat_col, lon_col
    except:
        return None, None, None

df_raw, lat1, lon1 = load_data_final("raw_data.csv")
df_verified, lat2, lon2 = load_data_final("verified_data.csv")

# 4. 建立地圖
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 畫出藍色水波紋 (未辨識)
if df_raw is not None:
    for _, row in df_raw.iterrows():
        icon_html = '<div class="ripple-container"><div class="ripple-core"></div><div class="ripple-out"></div><div class="ripple-out-2"></div></div>'
        folium.Marker(
            location=[row[lat1], row[lon1]],
            icon=folium.DivIcon(html=icon_html),
            popup=f"上傳者: {row.get('Username', '匿名')}"
        ).add_to(m)

# 6. 畫出亮黃燈號 (已辨識)
if df_verified is not None:
    for _, row in df_verified.iterrows():
        folium.CircleMarker(
            location=[row[lat2], row[lon2]], radius=8, color='#FFFFE0', 
            fill=True, fill_color='#FFFF00', fill_opacity=0.9, weight=2,
            popup=f"結果: {row.get('Review Identity', '已辨識')}"
        ).add_to(m)

# 7. 呈現
st_folium(m, width="100%", height=700)
