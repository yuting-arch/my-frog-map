import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：精準分流版")

# 2. 定義藍色水波紋 CSS (模擬您要的動態感)
st.markdown("""
<style>
@keyframes ripple-wave {
  0% { transform: scale(0.3); opacity: 1; }
  100% { transform: scale(4.0); opacity: 0; }
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
.ripple-out {
    position: absolute; width: 40px; height: 40px;
    border: 2px solid #00BFFF; border-radius: 50%;
    animation: ripple-wave 2.5s infinite cubic-bezier(0, 0.2, 0.8, 1);
}
</style>
""", unsafe_allow_html=True)

# 3. 合併讀取並精準判斷
def load_all_and_split():
    try:
        # 讀取兩個檔案
        df1 = pd.read_csv("raw_data.csv")
        df2 = pd.read_csv("verified_data.csv")
        # 合併後移除重複項
        df = pd.concat([df1, df2], ignore_index=True).drop_duplicates()
        
        # 清理格式
        df.columns = df.columns.str.strip()
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        return df.dropna(subset=['Latitude', 'Longitude'])
    except:
        return None

df_all = load_all_and_split()

# 4. 建立地圖
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 根據『內容』決定點位樣式
if df_all is not None:
    for _, row in df_all.iterrows():
        loc = [row['Latitude'], row['Longitude']]
        
        # 重要判斷：檢查 Review Identity 是否真的有字
        # 如果是空的 (NaN) 或字數為 0，就視為待辨識
        review_val = str(row.get('Review Identity', ''))
        is_verified = pd.notna(row.get('Review Identity')) and review_val.strip() != "" and review_val.lower() != "nan"
        
        if not is_verified:
            # 🌊 顯示藍色擬真波紋 (代表真的 Raw Data)
            icon_html = '<div class="ripple-container"><div class="ripple-core"></div><div class="ripple-out"></div></div>'
            folium.Marker(
                location=loc,
                icon=folium.DivIcon(html=icon_html),
                popup=f"👤 待辨識點位<br>上傳者: {row.get('Username', '匿名')}"
            ).add_to(m)
        else:
            # 🌟 顯示亮黃色燈號 (代表已專家辨識)
            folium.CircleMarker(
                location=loc,
                radius=8, color='#FFFFE0', fill=True,
                fill_color='#FFFF00', fill_opacity=0.9, weight=2,
                popup=f"🐸 辨識結果: {review_val}"
            ).add_to(m)

# 6. 呈現
st_folium(m, width="100%", height=700)
