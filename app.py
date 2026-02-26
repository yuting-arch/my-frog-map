import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：擬真水紋波動版")

# 2. 定義「擬真水波紋」的 CSS 樣式和動畫
# 這段 CSS 會創建多層次的波紋擴散效果
ripple_animation_css = """
<style>
.water-ripple {
  position: relative;
  width: 20px; /* 控制中心點大小 */
  height: 20px;
  border-radius: 50%;
  background-color: rgba(0, 191, 255, 0.7); /* 中心點顏色 */
  display: flex;
  justify-content: center;
  align-items: center;
}

.water-ripple::before, .water-ripple::after {
  content: '';
  position: absolute;
  border: 1px solid rgba(0, 191, 255, 0.7); /* 波紋顏色 */
  border-radius: 50%;
  animation: expand-ripple 2s ease-out infinite; /* 動畫速度 */
}

.water-ripple::after {
  animation-delay: 1s; /* 第二層波紋延遲出現 */
}

@keyframes expand-ripple {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(3.5); opacity: 0; }
}
</style>
"""
st.markdown(ripple_animation_css, unsafe_allow_html=True)

# 3. 讀取資料函數
def load_data(file_name):
    try:
        df = pd.read_csv(file_name)
        return df
    except:
        return None

df_raw = load_data("raw_data.csv")      # 未辨識
df_verified = load_data("verified_data.csv")  # 已辨識

# 4. 建立地圖 (深藍色底圖)
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 處理「未辨識」點位：擬真藍色水波紋
if df_raw is not None:
    for _, row in df_raw.iterrows():
        loc = [row['Latitude'], row['Longitude']]
        popup_text = f"👤 上傳者: {row['Username']}<br>📅 日期: {row['Create Date']}<br>🌊 狀態: 新增待辨識 (水紋波動中)"
        
        # 使用自定義的 HTML 元素來承載水波紋動畫
        folium.Marker(
            location=loc,
            icon=folium.DivIcon(html='<div class="water-ripple"></div>'),
            popup=folium.Popup(popup_text, max_width=280)
        ).add_to(m)

# 6. 處理「已辨識」點位：亮淺黃色圓燈
if df_verified is not None:
    for _, row in df_verified.iterrows():
        loc = [row['Latitude'], row['Longitude']]
        popup_text = (
            f"🐸 辨識結果: <b>{row['Review Identity']}</b><br>"
            f"👨‍🔬 專家: {row['Reviewer']}<br>"
            f"📅 審核日期: {row['Review Date']}"
        )
        
        folium.CircleMarker(
            location=loc,
            radius=8,
            color='#FFFFBB',      # 淺黃色邊框
            fill=True,
            fill_color='#FFFF00', # 鮮黃色中心
            fill_opacity=0.9,
            weight=2,
            popup=folium.Popup(popup_text, max_width=280)
        ).add_to(m)

# 7. 顯示地圖
st_folium(m, width="100%", height=700)

# 底部統計看板
st.divider()
c1, c2 = st.columns(2)
c1.metric("🌊 本月新收集 (藍色水紋)", len(df_raw) if df_raw is not None else 0)
c2.metric("🌟 專家已辨識 (黃色燈號)", len(df_verified) if df_verified is not None else 0)
