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

    # 4. 繪製 raw_data：#4F9D9D 藝術化 6px 漣漪
    for _, row in raw_data.iterrows():
        ripple_html = f"""
        <div style="position: relative; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center;">
            <style>
                @keyframes artistic_ripple_6px {{
                    0% {{ transform: scale(1); opacity: 0; }}
                    20% {{ opacity: 0.8; }}
                    100% {{ transform: scale(2.5); opacity: 0; filter: blur(2px); }}
                }}
            </style>
            <div style="position: absolute; width: 6px; height: 6px; 
                        background-color: #4F9D9D; border-radius: 50%; 
                        box-shadow: 0 0 8px 1px #4F9D9D; z-index: 1000;"></div>
            
            <div style="position: absolute; width: 15px; height: 15px; 
                        border: 0.8px solid #4F9D9D; border-radius: 50%; 
                        animation: artistic_ripple_6px 4s infinite ease-out; z-index: 999;"></div>
            
            <div style="position: absolute; width: 15px; height: 15px; 
                        border: 0.4px solid #4F9D9D; border-radius: 50%; 
                        animation: artistic_ripple_6px 4s infinite 2s ease-out; z-index: 998;"></div>
        </div>
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(
                html=ripple_html,
                icon_size=(40, 40),
                icon_anchor=(20, 20)
            ),
            popup=f"原始錄音者: {row['Username']}"
        ).add_to(m)

    # 5. 繪製 verified_data：黃色 6px 質感柔光
    for _, row in verified_data.iterrows():
        yellow_glow_html = f"""
        <div style="position: relative; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center;">
            <div style="width: 6px; height: 6px; background-color: #f1c40f; border-radius: 50%; 
                        box-shadow: 0 0 10px 3px rgba(241, 196, 15, 0.5); z-index: 1000;"></div>
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

    # 6. 呈現地圖
    st.markdown("<h2 style='text-align: center; color: #4F9D9D; font-weight: 200;'>🌿 台灣蛙鳴環境聲景地圖</h2>", unsafe_allow_html=True)
    folium_static(m, width=1100, height=600)

    # 側邊欄
    st.sidebar.markdown(f"### 🌙 聲景統計")
    st.sidebar.metric("原始波動 (#4F9D9D)", len(raw_data))
    st.sidebar.metric("已驗證點位 (黃光)", len(verified_data))

except Exception as e:
    st.error(f"地圖啟動失敗：{e}")
