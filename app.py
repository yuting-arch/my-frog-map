import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：擬真水紋波動版")

# 2. 定義擬真藍色水波紋 CSS (模擬您想要的擴散感)
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

# 3. 讀取資料 (專注處理 raw_data.csv)
def load_data():
    try:
        df = pd.read_csv("raw_data.csv")
        # 清理標題空格
        df.columns = df.columns.str.strip()
        # 強制座標轉為數字，解決長小數點問題
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        return df.dropna(subset=['Latitude', 'Longitude'])
    except Exception as e:
        st.error(f"讀取失敗: {e}")
        return None

df = load_data()

# 4. 建立地圖 (深深藍底色)
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 畫出擬真藍色水波紋
if df is not None and not df.empty:
    for index, row in df.iterrows():
        # 確保經緯度是浮點數，解決 Folium 繪圖報錯
        lat = float(row['Latitude'])
        lon = float(row['Longitude'])
        
        # HTML 結構：核心點 + 兩層延遲波紋
        icon_html = """
        <div class="ripple-container">
            <div class="ripple-core"></div>
            <div class="ripple-out-1"></div>
            <div class="ripple-out-2"></div>
        </div>
        """
        
        folium.Marker(
            location=[lat, lon],
            icon=folium.DivIcon(html=icon_html),
            popup=f"上傳者: {row.get('Username', '匿名')}"
        ).add_to(m)
else:
    st.warning("⚠️ 檔案中沒有找到有效的座標資料點位。")

# 6. 呈現地圖
st_folium(m, width="100%", height=700)
