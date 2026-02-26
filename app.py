import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：純藍水紋波浪版")

# 2. 定義擬真藍色水波紋 CSS (水滴擴散感)
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
    border-radius: 50%; box-shadow: 0 0 10px #00FFFF;
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

# 3. 讀取 raw_data.csv
def load_data():
    try:
        # 強制讀取 raw_data.csv
        df = pd.read_csv("raw_data.csv")
        df.columns = df.columns.str.strip() # 去除標題空格
        # 強制將座標轉為數字，錯誤的會變成空值 NaN
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        # 移除沒有經緯度的資料列
        return df.dropna(subset=['Latitude', 'Longitude'])
    except Exception as e:
        st.error(f"檔案讀取失敗，請確認 raw_data.csv 是否正確存在。錯誤資訊: {e}")
        return None

df = load_data()

# 4. 建立地圖 (深色背景)
m = folium.Map(location=[23.6, 121
