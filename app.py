import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 1. 頁面基本設定
st.set_page_config(page_title="台灣蛙鳴動態地圖", layout="wide")

# 2. 強化版 CSS 漣漪動畫 (確保 z-index 在最前方)
ripple_css = """
<style>
@keyframes ripple {
  0% { transform: scale(0.4); opacity: 0.9; }
  100% { transform: scale(2.8); opacity: 0; }
}
.ripple-container {
  position: relative;
  width: 20px;
  height: 20px;
}
.ripple-core {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #3498db;
  border-radius: 50%;
  top: 6px;
  left: 6px;
  z-index: 999;
}
.ripple-wave {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 3px solid #3498db;
  border-radius: 50%;
  animation: ripple 2s infinite;
  z-index: 998;
}
</style>
"""
st.markdown(ripple_css, unsafe_allow_html=True)

# 3. 穩定讀取資料函數
@st.cache_data
def load_data_final():
    def try_read(file_name):
        for enc in ['utf-8', 'big5', 'cp950', 'utf-8-sig']:
            try:
                return pd.read_csv(file_name, encoding=enc)
            except:
                continue
        return pd.read_csv(file_name, encoding='latin1')

    df_raw = try_read('raw_data.csv')
    df_verified = try_read('verified_data.csv')
    
    for df in [df_raw, df_verified]:
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    
    return df_raw.dropna(subset=['Latitude', 'Longitude']), \
           df_verified.dropna(subset=['Latitude', 'Longitude'])

try:
    raw_data, verified_data = load_data_final()

    # 4. 建立地圖
    m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="cartodbpositron")

    # 5. 繪製 raw_data：藍色動態漣漪
    # 我們改用 Marker 並簡化 HTML 結構確保渲染
    for _, row in raw_data.iterrows():
        icon_html = '<div class="ripple-container"><div class="ripple-core"></div><div class="ripple-wave"></div></div>'
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(
                html=icon_html,
                icon_size=(20, 20),
                icon_anchor=(10, 10)
            ),
            popup=f"原始紀錄: {row['Username']}"
        ).add_to(m)

    # 6. 繪製 verified_data：黃色燈光
    for _, row in verified_data.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=12,
            popup=f"專家辨識: {row['Review Identity']}",
            color="#ffc107",
            fill=True,
            fill_color="#fff176",
            fill_opacity=0.6,
            weight=0
        ).add_to(m)

    # 7. 呈現地圖
    st.markdown("### 🐸 台灣蛙鳴空間資料：動態漣漪地圖")
    folium_static(m, width=1100, height=600)

    # 側邊欄
    st.sidebar.title("📊 數據面板")
    st.sidebar.metric("民眾錄音 (藍色漣漪)", len(raw_data))
    st.sidebar.metric("專家審核 (黃色燈光)", len(verified_data))

except Exception as e:
    st.error(f"地圖啟動失敗：{e}")
