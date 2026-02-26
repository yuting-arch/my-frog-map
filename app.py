import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：擬真水紋波動版")

# 2. 擬真水波紋 CSS
st.markdown("""
<style>
@keyframes ripple-wave {
  0% { transform: scale(0.2); opacity: 1; }
  100% { transform: scale(4.0); opacity: 0; }
}
.water-ripple {
  position: relative;
  width: 12px; height: 12px;
  background: #00FFFF;
  border-radius: 50%;
  box-shadow: 0 0 10px #00FFFF;
}
.water-ripple::before {
  content: "";
  position: absolute;
  top: -14px; left: -14px;
  width: 40px; height: 40px;
  border: 2px solid #00BFFF;
  border-radius: 50%;
  animation: ripple-wave 2s infinite;
}
</style>
""", unsafe_allow_html=True)

# 3. 強大的讀取函數 (自動處理欄位名稱問題)
def load_data_safe(name):
    try:
        df = pd.read_csv(name)
        # 自動修正：去除標題空格，並統一找尋包含 lat/lon 的欄位
        df.columns = [c.strip().lower() for c in df.columns]
        lat_col = [c for c in df.columns if 'lat' in c][0]
        lon_col = [c for c in df.columns if 'lon' in c][0]
        user_col = [c for c in df.columns if 'user' in c][0]
        # 重新命名以便程式讀取
        df = df.rename(columns={lat_col: 'lat', lon_col: 'lon', user_col: 'user'})
        return df
    except Exception as e:
        return None

df_raw = load_data_safe("raw_data.csv")
df_verified = load_data_safe("verified_data.csv")

# 4. 建立地圖
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 畫出藍色水波紋 (未辨識)
if df_raw is not None:
    for _, row in df_raw.iterrows():
        folium.Marker(
            location=[row['lat'], row['lon']],
            icon=folium.DivIcon(html='<div class="water-ripple"></div>'),
            popup=f"上傳者: {row['user']}"
        ).add_to(m)

# 6. 畫出亮黃燈號 (已辨識)
if df_verified is not None:
    for _, row in df_verified.iterrows():
        folium.CircleMarker(
            location=[row['lat'], row['lon']], radius=8, color='#FFFFE0', 
            fill=True, fill_color='#FFFF00', fill_opacity=0.9, weight=2
        ).add_to(m)

# 7. 呈現
st_folium(m, width="100%", height=700)

# 偵錯資訊 (若沒資料，網頁下方會顯示原因)
if df_raw is None:
    st.error("無法正確讀取 raw_data.csv，請檢查欄位是否包含 Latitude 與 Longitude")
