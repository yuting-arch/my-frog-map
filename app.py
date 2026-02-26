import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 1. 頁面基本設定
st.set_page_config(page_title="台灣蛙鳴環境聲景地圖", layout="wide")

# 2. 核心資料讀取函數
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

    # 3. 建立質感深藍地圖
    m = folium.Map(
        location=[23.6, 121.0], 
        zoom_start=7, 
        tiles="cartodbdarkmatter"
    )

    # 4. 繪製 raw_data：使用 #C4E1FF 的極致淡化漣漪
    for _, row in raw_data.iterrows():
        # 優化後的淡化動畫：使用淡藍色 #C4E1FF，並加強擴散後的消散感
        ripple_html = f"""
        <div style="position: relative; width: 50px; height: 50px; display: flex; justify-content: center; align-items: center;">
            <style>
                @keyframes water_fading {{
                    0% {{ transform: scale(0.6); opacity: 0; }}
                    15% {{ opacity: 0.7; }} /* 快速出現 */
                    50% {{ opacity: 0.3; }} /* 中段開始大幅淡化 */
                    100% {{ transform: scale(4.5); opacity: 0; filter: blur(5px); }} /* 最終完全消散並模糊 */
                }}
            </style>
            <div style="position: absolute; width: 6px; height: 6px; 
                        background-color: #C4E1FF; border-radius: 50%; 
                        box-shadow: 0 0 8px 2px rgba(196, 225, 255, 0.8); z-index: 1000;"></div>
            
            <div style="position: absolute; width: 12px; height: 12px; 
                        border: 0.6px solid #C4E1FF; border-radius: 50%; 
                        animation: water_fading 4.5s infinite ease-out; z-index: 999;"></div>
            
            <div style="position: absolute; width: 12px; height: 12px; 
                        border: 0.3px solid #C4E1FF; border-radius: 50%; 
                        animation: water_fading 4.5s infinite 2.25s ease-out; z-index: 998;"></div>
        </div>
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(
                html=ripple_html,
                icon_size=(50, 50),
                icon_anchor=(25, 25)
            ),
            popup=f"原始錄音者: {row['Username']}"
        ).add_to(m)

    # 5. 繪製 verified_data：黃色 6px 柔光點
    for _, row in verified_data.iterrows():
        yellow_glow_html = f"""
        <div style="position: relative; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center;">
            <div style="width: 6px; height: 6px; background-color: #f1c40f; border-radius: 50%; 
                        box-shadow: 0 0 10px 3px rgba(241, 196, 15, 0.4); z-index: 1000;"></div>
        </div>
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(
                html=yellow_glow_html,
                icon_size=(24, 24),
                icon_anchor=(12, 12)
            ),
            popup=f"專家辨識: {row['Review Identity']}"
        ).add_to(m)

    # 6. 呈現地圖與標題
    st.markdown("<h2 style='text-align: center; color: #C4E1FF; font-weight: 200; letter-spacing: 1px;'>🌿 台灣蛙鳴環境聲景地圖</h2>", unsafe_allow_html=True)
    folium_static(m, width=1100, height=600)

    # 側邊欄統計
    st.sidebar.markdown(f"### 📍 當前觀測統計")
    st.sidebar.metric("原始波動 (#C4E1FF)", len(raw_data))
    st.sidebar.metric("確定紀錄 (黃光)", len(verified_data))

except Exception as e:
    st.error(f"地圖啟動失敗：{e}")
