import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 1. 頁面基本設定
st.set_page_config(page_title="台灣蛙鳴聲景地圖", layout="wide")

# 2. 核心讀取函數 (自動處理編碼)
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

    # 3. 建立深藍色質感地圖
    m = folium.Map(
        location=[23.6, 121.0], 
        zoom_start=7, 
        tiles="cartodbdarkmatter"
    )

    # 4. 繪製 raw_data：#4F9D9D 藝術柔和漣漪
    for _, row in raw_data.iterrows():
        # 藝術化波紋：使用指定色號 #4F9D9D，並加入模糊與淡出效果
        ripple_html = f"""
        <div style="position: relative; width: 60px; height: 60px;">
            <style>
                @keyframes water_art {{
                    0% {{ transform: scale(0.3); opacity: 0.9; }}
                    100% {{ transform: scale(4); opacity: 0; filter: blur(3px); }}
                }}
            </style>
            <div style="position: absolute; top: 27px; left: 27px; width: 6px; height: 6px; 
                        background-color: #4F9D9D; border-radius: 50%; 
                        box-shadow: 0 0 10px #4F9D9D; z-index: 1000;"></div>
            
            <div style="position: absolute; top: 0; left: 0; width: 60px; height: 60px; 
                        border: 0.8px solid #4F9D9D; border-radius: 50%; 
                        animation: water_art 4s infinite ease-out; z-index: 999;"></div>
            
            <div style="position: absolute; top: 0; left: 0; width: 60px; height: 60px; 
                        border: 0.5px solid #4F9D9D; border-radius: 50%; 
                        animation: water_art 4s infinite 2s ease-out; z-index: 998;"></div>
        </div>
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(
                html=ripple_html,
                icon_size=(60, 60),
                icon_anchor=(30, 30)
            ),
            popup=f"原始錄音者: {row['Username']}"
        ).add_to(m)

    # 5. 繪製 verified_data：黃色柔光點
    for _, row in verified_data.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=10,
            popup=f"鑑定物種: {row['Review Identity']}",
            color="#f1c40f",
            fill=True,
            fill_color="#f1c40f",
            fill_opacity=0.3,
            weight=0
        ).add_to(m)

    # 6. 呈現地圖
    st.markdown("<h2 style='text-align: center; color: #4F9D9D; font-weight: 300;'>🌿 台灣蛙鳴環境聲景地圖</h2>", unsafe_allow_html=True)
    folium_static(m, width=1100, height=600)

    # 側邊欄統計
    st.sidebar.markdown(f"### 📍 當前觀測統計")
    st.sidebar.metric("原始波動 (#4F9D9D)", len(raw_data))
    st.sidebar.metric("確定紀錄 (黃光)", len(verified_data))
    
    st.sidebar.markdown("---")
    st.sidebar.write("這是一項致力於紀錄台灣自然聲音的公民科學計畫。")

except Exception as e:
    st.error(f"地圖加載異常: {e}")
