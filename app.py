import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：擬真水紋波動版")

# 2. 擬真藍色水波紋 CSS 動畫 (多層次擴散)
st.markdown("""
<style>
@keyframes ripple-wave {
  0% { transform: scale(0.2); opacity: 1; }
  50% { opacity: 0.5; }
  100% { transform: scale(4.0); opacity: 0; }
}
.water-ripple {
  position: relative;
  width: 12px; height: 12px;
  background: #00FFFF;
  border-radius: 50%;
  box-shadow: 0 0 10px #00FFFF;
}
.water-ripple::before, .water-ripple::after {
  content: "";
  position: absolute;
  top: -14px; left: -14px;
  width: 40px; height: 40px;
  border: 2px solid #00BFFF;
  border-radius: 50%;
  animation: ripple-wave 2.5s infinite;
}
.water-ripple::after { animation-delay: 1.2s; }
</style>
""", unsafe_allow_html=True)

# 3. 讀取資料函數 (包含自動檢查)
def load_frog_data(name):
    try:
        df = pd.read_csv(name)
        # 移除空行與空格
        df.columns = df.columns.str.strip()
        return df
    except:
        return None

df_raw = load_frog_data("raw_data.csv")
df_verified = load_frog_data("verified_data.csv")

# 4. 建立地圖
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 畫出藍色水波紋 (未辨識)
if df_raw is not None and not df_raw.empty:
    for _, row in df_raw.iterrows():
        try:
            loc = [row['Latitude'], row['Longitude']]
            folium.Marker(
                location=loc,
                icon=folium.DivIcon(html='<div class="water-ripple"></div>'),
                popup=f"👤 上傳者: {row['Username']}<br>⚠️ 狀態: 待辨識"
            ).add_to(m)
        except: continue
else:
    st.sidebar.warning("⚠️ 找不到 raw_data.csv 或資料格式錯誤")

# 6. 畫出亮黃燈號 (已辨識)
if df_verified is not None and not df_verified.empty:
    for _, row in df_verified.iterrows():
        try:
            loc = [row['Latitude'], row['Longitude']]
            v_text = f"🐸 結果: {row['Review Identity']}<br>👨‍🔬 專家: {row['Reviewer']}"
            folium.CircleMarker(
                location=loc, radius=8, color='#FFFFE0', fill=True,
                fill_color='#FFFF00', fill_opacity=0.9, weight=2, 
                popup=folium.Popup(v_text, max_width=250)
            ).add_to(m)
        except: continue
else:
    st.sidebar.warning("⚠️ 找不到 verified_data.csv 或資料格式錯誤")

# 7. 呈現地圖
st_folium(m, width="100%", height=700)
