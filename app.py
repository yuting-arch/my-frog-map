import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 1. 頁面基本設定
st.set_page_config(page_title="台灣蛙鳴動態地圖 - 深色模式", layout="wide")

# 2. 強化版 CSS 漣漪動畫 (針對深色底圖微調顏色)
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
  background: #00d2ff; /* 亮藍色核心 */
  border-radius: 50%;
  top: 6px;
  left: 6px;
  z-index: 999;
}
.ripple-wave {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 3px solid #00d2ff;
  border-radius: 50%;
  animation: ripple 2s infinite;
  z-index: 998;
}
</style>
"""
st.markdown(ripple_css, unsafe_allow_html=True)

# 3. 穩定讀取資料函數 (包含編碼與數值轉換)
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
        df['Create Date'] = pd.to_datetime(df['Create Date'], errors='coerce')
    
    return df_raw.dropna(subset=['Latitude', 'Longitude']), \
           df_verified.dropna(subset=['Latitude', 'Longitude'])

try:
    raw_data, verified_data = load_data_final()

    # 4. 建立深藍色地圖 (底圖換成 cartodbdarkmatter)
    m = folium.Map(
        location=[23.6, 121.0], 
        zoom_start=7, 
        tiles="cartodbdarkmatter", # 這是深藍黑色的底圖關鍵
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
    )

    # 5. 繪製 raw_data：亮藍色動態漣漪
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

    # 6. 繪製 verified_data：黃色半透明燈光
    for _, row in verified_data.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=12,
            popup=f"專家辨識: {row['Review Identity']}",
            color="#f1c40f",       # 鮮豔黃色
            fill=True,
            fill_color="#f1c40f", 
            fill_opacity=0.4,      # 半透明燈光感
            weight=0
        ).add_to(m)

    # 7. 呈現地圖與標題
    st.markdown("<h2 style='text-align: center;'>🌌 台灣蛙鳴空間資料互動地圖</h2>", unsafe_allow_html=True)
    folium_static(m, width=1100, height=600)

    # 側邊欄
    st.sidebar.title("📊 實時統計面板")
    st.sidebar.metric("原始紀錄 (藍色漣漪)", len(raw_data))
    st.sidebar.metric("專家審核 (黃色燈光)", len(verified_data))
    
    st.sidebar.markdown("---")
    st.sidebar.write("💡 **視覺提示**：")
    st.sidebar.write("🔵 藍色波動代表民眾即時錄音")
    st.sidebar.write("🟡 黃色亮點代表專家已完成鑑定")

except Exception as e:
    st.error(f"地圖渲染發生錯誤：{e}")
