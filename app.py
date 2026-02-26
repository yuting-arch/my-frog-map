import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：擬真水紋波動版")

# 2. 強制顯影藍色水波紋 CSS
# 增加了 z-index 與強制寬高，確保在深色底圖上絕對可見
st.markdown("""
<style>
@keyframes ripple-wave {
  0% { transform: scale(0.3); opacity: 1; }
  100% { transform: scale(4.5); opacity: 0; }
}
.ripple-container {
    position: absolute;
    width: 20px; height: 20px;
    margin-left: -10px; margin-top: -10px;
    display: flex; justify-content: center; align-items: center;
    pointer-events: none;
}
.ripple-core {
    width: 12px; height: 12px;
    background: #00FFFF;
    border-radius: 50%;
    box-shadow: 0 0 15px #00FFFF;
    z-index: 999;
}
.ripple-out {
    position: absolute;
    width: 50px; height: 50px;
    border: 3px solid #00BFFF;
    border-radius: 50%;
    animation: ripple-wave 2s infinite cubic-bezier(0, 0.2, 0.8, 1);
}
</style>
""", unsafe_allow_html=True)

# 3. 超強力讀取函數
def load_data():
    try:
        df = pd.read_csv("raw_data.csv")
        df.columns = df.columns.str.strip()
        # 自動偵測包含 lat/lon 的欄位
        lat_col = [c for c in df.columns if 'lat' in c.lower()][0]
        lon_col = [c for c in df.columns if 'lon' in c.lower()][0]
        # 強制轉型
        df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
        df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')
        return df.dropna(subset=[lat_col, lon_col]), lat_col, lon_col
    except:
        return None, None, None

df, lat_c, lon_c = load_data()

# 4. 建立地圖
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 繪製強制顯影水波紋
if df is not None:
    for _, row in df.iterrows():
        # HTML 結構加上了強大的發光核心
        icon_html = '<div class="ripple-container"><div class="ripple-core"></div><div class="ripple-out"></div></div>'
        folium.Marker(
            location=[float(row[lat_c]), float(row[lon_c])],
            icon=folium.DivIcon(html=icon_html, icon_size=(20, 20), icon_anchor=(10, 10)),
            popup=f"上傳者: {row.get('Username', '匿名')}"
        ).add_to(m)

# 6. 呈現
st_folium(m, width="100%", height=700)

if df is not None:
    st.success(f"✅ 已成功渲染 {len(df)} 個藍色水波紋點位")
