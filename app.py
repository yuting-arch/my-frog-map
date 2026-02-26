import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：擬真水紋波動版")

# 2. 定義擬真藍色水波紋 CSS (模擬 image_bf1e98.png 的質感)
st.markdown("""
<style>
@keyframes ripple-wave {
  0% { transform: scale(0.2); opacity: 1; }
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

# 3. 超強力讀取函數 (自動處理 CSV 格式問題)
def load_data_safe():
    try:
        df = pd.read_csv("raw_data.csv")
        # 清理標題空格並統一尋找經緯度欄位
        df.columns = df.columns.str.strip()
        lat_col = [c for c in df.columns if 'lat' in c.lower()][0]
        lon_col = [c for c in df.columns if 'lon' in c.lower()][0]
        # 強制座標轉為數字，解決科學記號或文字干擾
        df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
        df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')
        return df.dropna(subset=[lat_col, lon_col]), lat_col, lon_col
    except Exception as e:
        st.error(f"讀取失敗: {e}")
        return None, None, None

df, lat_c, lon_c = load_data_safe()

# 4. 建立地圖 (深黑底圖)
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 繪製藍色水波紋
if df is not None and not df.empty:
    for _, row in df.iterrows():
        # HTML 結構：一個發光核心 + 兩層延遲波紋
        icon_html = """
        <div class="ripple-container">
            <div class="ripple-core"></div>
            <div class="ripple-out-1"></div>
            <div class="ripple-out-2"></div>
        </div>
        """
        folium.Marker(
            location=[float(row[lat_c]), float(row[lon_c])],
            icon=folium.DivIcon(html=icon_html),
            popup=f"上傳者: {row.get('Username', '匿名')}"
        ).add_to(m)
else:
    st.warning("⚠️ raw_data.csv 檔案讀取成功，但沒有包含可用的座標資料。")

# 6. 呈現地圖
st_folium(m, width="100%", height=700)
