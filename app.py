import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：擬真水紋波動版")

# 2. 定義藍色水波紋 CSS (加強發光感與層次)
st.markdown("""
<style>
@keyframes ripple-wave {
  0% { transform: scale(0.3); opacity: 1; }
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

# 3. 合併讀取函數
def get_all_data():
    try:
        # 同時讀取兩個檔案並合併
        df1 = pd.read_csv("raw_data.csv")
        df2 = pd.read_csv("verified_data.csv")
        all_df = pd.concat([df1, df2], ignore_index=True).drop_duplicates()
        
        # 清理標題與格式
        all_df.columns = all_df.columns.str.strip()
        all_df['Latitude'] = pd.to_numeric(all_df['Latitude'], errors='coerce')
        all_df['Longitude'] = pd.to_numeric(all_df['Longitude'], errors='coerce')
        return all_df.dropna(subset=['Latitude', 'Longitude'])
    except:
        return None

df = get_all_data()

# 4. 建立地圖 (深黑背景)
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 繪製點位 (根據狀態自動分類)
if df is not None:
    for _, row in df.iterrows():
        loc = [row['Latitude'], row['Longitude']]
        # 判斷標準：如果 'Review Identity' 欄位是空的，或者是原本 raw 檔案裡的點位
        is_verified = pd.notna(row.get('Review Identity')) and str(row.get('Review Identity')).strip() != ""
        
        if not is_verified:
            # 🌊 顯示藍色擬真波紋
            icon_html = '<div class="ripple-container"><div class="ripple-core"></div><div class="ripple-out-1"></div><div class="ripple-out-2"></div></div>'
            folium.Marker(
                location=loc,
                icon=folium.DivIcon(html=icon_html),
                popup=f"👤 待辨識點位<br>上傳者: {row.get('Username', '匿名')}"
            ).add_to(m)
        else:
            # 🌟 顯示亮黃色燈號
            folium.CircleMarker(
                location=loc,
                radius=8, color='#FFFFE0', fill=True,
                fill_color='#FFFF00', fill_opacity=0.9, weight=2,
                popup=f"🐸 已辨識: {row.get('Review Identity')}"
            ).add_to(m)

# 6. 呈現地圖
st_folium(m, width="100%", height=700)
