import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 1. 頁面基本設定
st.set_page_config(page_title="台灣蛙鳴動態地圖", layout="wide")

# 2. 定義 CSS 漣漪動畫特效 (讓藍色點位有石頭落水的動態感)
ripple_css = """
<style>
@keyframes ripple {
  0% { transform: scale(0.5); opacity: 1; }
  100% { transform: scale(2.5); opacity: 0; }
}
.ripple-icon {
  background: rgba(52, 152, 219, 0.6);
  border-radius: 50%;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.4);
  animation: ripple 2s infinite;
}
</style>
"""
st.markdown(ripple_css, unsafe_allow_html=True)

# 3. 核心資料讀取函數
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

# 執行主程式
try:
    raw_data, verified_data = load_data_final()

    # 4. 建立地圖
    m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="cartodbpositron")

    # 5. 繪製 raw_data：動態漣漪動畫 (DivIcon)
    for _, row in raw_data.iterrows():
        # 使用 DivIcon 注入 CSS 動畫類別
        folium.map.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(
                html=f'<div class="ripple-icon" style="width: 15px; height: 15px;"></div>',
                icon_size=(15, 15),
                icon_anchor=(7.5, 7.5)
            ),
            popup=f"原始紀錄 ID: {row['ID']}"
        ).add_to(m)

    # 6. 繪製 verified_data：黃色半透明燈光 (靜態圓圈)
    for _, row in verified_data.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=12,
            popup=f"物種: {row['Review Identity']}",
            color="#ffc107",
            fill=True,
            fill_color="#fff176",
            fill_opacity=0.5,
            weight=0
        ).add_to(m)

    # 7. 呈現地圖
    st.markdown("### 🐸 台灣蛙鳴空間資料：動態漣漪地圖")
    folium_static(m, width=1100, height=600)

    # 側邊欄統計資訊
    st.sidebar.title("📊 數據面板")
    st.sidebar.metric("民眾錄音 (動態藍)", len(raw_data))
    st.sidebar.metric("專家審核 (光暈黃)", len(verified_data))

except Exception as e:
    st.error(f"地圖啟動失敗：{e}")
