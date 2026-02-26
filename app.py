import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 1. 頁面基本設定
st.set_page_config(page_title="台灣蛙鳴動態地圖", layout="wide")

# 2. 核心讀取函數 (自動處理編碼與數值格式)
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

# 主程式邏輯
try:
    raw_data, verified_data = load_data_final()

    # 3. 建立深藍色地圖
    m = folium.Map(
        location=[23.6, 121.0], 
        zoom_start=7, 
        tiles="cartodbdarkmatter"
    )

    # 4. 繪製 raw_data：極細水波紋動畫
    for _, row in raw_data.iterrows():
        # 定義多重極細波紋動畫
        ripple_html = f"""
        <div style="position: relative; width: 40px; height: 40px;">
            <style>
                @keyframes fine_ripple {{
                    0% {{ transform: scale(0.2); opacity: 0.9; border-width: 0.8px; }}
                    100% {{ transform: scale(4.5); opacity: 0; border-width: 0.1px; }}
                }}
            </style>
            <div style="position: absolute; top: 18.5px; left: 18.5px; width: 3px; height: 3px; 
                        background-color: #00d2ff; border-radius: 50%; box-shadow: 0 0 5px #00d2ff;"></div>
            <div style="position: absolute; top: 0; left: 0; width: 40px; height: 40px; 
                        border: 0.5px solid #00d2ff; border-radius: 50%; 
                        animation: fine_ripple 3s infinite cubic-bezier(0.2, 0.5, 0.4, 0.9);"></div>
            <div style="position: absolute; top: 0; left: 0; width: 40px; height: 40px; 
                        border: 0.5px solid #00d2ff; border-radius: 50%; 
                        animation: fine_ripple 3s infinite 1.5s cubic-bezier(0.2, 0.5, 0.4, 0.9);"></div>
        </div>
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(
                html=ripple_html,
                icon_size=(40, 40),
                icon_anchor=(20, 20)
            ),
            popup=f"原始錄音: {row['Username']}"
        ).add_to(m)

    # 5. 繪製 verified_data：黃色半透明光點
    for _, row in verified_data.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=10,
            popup=f"專家辨識: {row['Review Identity']}",
            color="#f1c40f",
            fill=True,
            fill_color="#f1c40f",
            fill_opacity=0.4,
            weight=0
        ).add_to(m)

    # 6. 在網頁上呈現
    st.markdown("<h2 style='text-align: center; color: white;'>🌌 台灣蛙鳴空間資料互動地圖</h2>", unsafe_allow_html=True)
    folium_static(m, width=1100, height=600)

    # 側邊欄資訊
    st.sidebar.title("📊 資料統計")
    st.sidebar.metric("原始紀錄 (藍色細波紋)", len(raw_data))
    st.sidebar.metric("專家辨識 (黃色光點)", len(verified_data))

except Exception as e:
    st.error(f"地圖啟動失敗，請檢查原始資料內容。錯誤訊息: {e}")
