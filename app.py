import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：純藍水紋波浪版")

# 2. 定義擬真藍色水波紋 CSS
ripple_css = """
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
"""
st.markdown(ripple_css, unsafe_allow_html=True)

# 3. 強力讀取資料
try:
    df = pd.read_csv("raw_data.csv")
    # 強制去除所有欄位名稱的前後空格
    df.columns = df.columns.str.strip()
    
    # 【自動偵測欄位】不論大小寫或空格，只要包含 'lat' 或 'lon' 就抓
    lat_col = [c for c in df.columns if 'lat' in c.lower()][0]
    lon_col = [c for c in df.columns if 'lon' in c.lower()][0]
    
    # 強制轉為數字型態
    df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
    df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')
    
    # 移除真的無法轉換的空值
    df_clean = df.dropna(subset=[lat_col, lon_col])
    
    # 4. 建立地圖
    m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

    # 5. 繪製藍色水波紋
    for _, row in df_clean.iterrows():
        icon_html = '<div class="ripple-container"><div class="ripple-core"></div><div class="ripple-out-1"></div><div class="ripple-out-2"></div></div>'
        folium.Marker(
            location=[float(row[lat_col]), float(row[lon_col])],
            icon=folium.DivIcon(html=icon_html),
            popup=f"上傳者: {row.get('Username', '匿名')}"
        ).add_to(m)

    st_folium(m, width="100%", height=700)
    
    # 底部顯示讀取到的筆數，幫助確認資料有沒有進來
    st.write(f"✅ 成功在地圖上標記 {len(df_clean)} 個待辨識點位")

except Exception as e:
    st.error(f"❌ 發生錯誤：{e}")
    st.write("請檢查 raw_data.csv 檔案內容。")
