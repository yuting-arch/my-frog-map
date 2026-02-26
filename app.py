import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 1. 頁面基本設定
st.set_page_config(page_title="台灣蛙鳴聲景地圖", layout="wide")

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

    # 4. 繪製 raw_data：#4F9D9D 藝術化微型柔光漣漪
    for _, row in raw_data.iterrows():
        # 微型動畫：縮放幅度極小(1.0->1.3)，並搭配模糊與慢速淡出
        ripple_html = f"""
        <div style="position: relative; width: 30px; height: 30px; display: flex; justify-content: center; align-items: center;">
            <style>
                @keyframes soft_micro_ripple {{
                    0% {{ transform: scale(1); opacity: 0; }}
                    20% {{ opacity: 0.7; }}
                    100% {{ transform: scale(1.3); opacity: 0; filter: blur(2px); }}
                }}
            </style>
            <div style="position: absolute; width: 3px; height: 3px; 
                        background-color: #4F9D9D; border-radius: 50%; 
                        box-shadow: 0 0 6px 1px #4F9D9D; z-index: 1000;"></div>
            
            <div style="position: absolute; width: 15px; height: 15px; 
                        border: 0.5px solid #4F9D9D; border-radius: 50%; 
                        animation: soft_micro_ripple 4s infinite ease-out; z-index: 999;"></div>
            
            <div style="position: absolute; width: 15px; height: 15px; 
                        border: 0.3px solid #4F9D9D; border-radius: 50%; 
                        animation: soft_micro_ripple 4s infinite 2s ease-out; z-index: 998;"></div>
        </div>
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(
                html=ripple_html,
                icon_size=(30, 30),
                icon_anchor=(15, 15)
            ),
            popup=f"原始錄音者: {row['Username']}"
        ).add_to(m)

    # 5. 繪製 verified_data：微型黃色質感柔光 (不再隨縮放變形)
    for _, row in verified_data.iterrows():
        yellow_glow_html = f"""
        <div style="position: relative; width: 20px; height: 20px; display: flex; justify-content: center; align-items: center;">
            <div style="width: 4px; height: 4px; background-color: #f1c40f; border-radius: 50%; 
                        box-shadow: 0 0 8px 2px rgba(241, 196, 15, 0.6); z-index: 1000;"></div>
        </div>
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(
                html=yellow_glow_html,
                icon_size=(20, 20),
                icon_anchor=(10, 10)
            ),
            popup=f"專家辨識: {row['Review Identity']}"
        ).add_to(m)

    # 6. 呈現地圖
    st.markdown("<h2 style='text-align: center; color: #4F9D9D; font-weight: 200; letter-spacing: 2px;'>🌿 台灣蛙鳴環境聲景地圖</h2>", unsafe_allow_html=True)
    folium_static(m, width=1100, height=600)

    # 側邊欄
    st.sidebar.markdown(f"### 🌙 聲景統計")
    st.sidebar.metric("活躍波動 (#4F9D9D)", len(raw_data))
    st.sidebar.metric("已驗證點位", len(verified_data))

except Exception as e:
    st.error(f"地圖啟動失敗：{e}")
