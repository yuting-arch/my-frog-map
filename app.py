import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# 1. 頁面基本設定
st.set_page_config(page_title="台灣蛙鳴動態地圖", layout="wide")

# 2. 核心讀取函數 (強化數值格式檢查)
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
    
    # 關鍵：強制轉換經緯度為 float，移除無法轉換的髒資料
    for df in [df_raw, df_verified]:
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    
    return df_raw.dropna(subset=['Latitude', 'Longitude']), \
           df_verified.dropna(subset=['Latitude', 'Longitude'])

try:
    raw_data, verified_data = load_data_final()

    # 3. 建立深藍色地圖
    m = folium.Map(
        location=[23.6, 121.0], 
        zoom_start=7, 
        tiles="cartodbdarkmatter"
    )

    # 4. 繪製 raw_data：使用「行內樣式 (Inline CSS)」確保動畫 100% 執行
    for _, row in raw_data.iterrows():
        # 定義一段包含關鍵幀動畫的 HTML
        # 這段 HTML 會直接塞進地圖裡，不受外部 CSS 影響
        ripple_html = f"""
        <div style="position: relative; width: 30px; height: 30px;">
            <style>
                @keyframes ripple_effect {{
                    0% {{ transform: scale(0.5); opacity: 1; }}
                    100% {{ transform: scale(3); opacity: 0; }}
                }}
            </style>
            <div style="position: absolute; top: 12px; left: 12px; width: 6px; height: 6px; 
                        background-color: #00d2ff; border-radius: 50%; z-index: 1000;"></div>
            <div style="position: absolute; top: 0; left: 0; width: 30px; height: 30px; 
                        border: 2px solid #00d2ff; border-radius: 50%; 
                        animation: ripple_effect 2s infinite; z-index: 999;"></div>
        </div>
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(
                html=ripple_html,
                icon_size=(30, 30),
                icon_anchor=(15, 15)
            ),
            popup=f"原始錄音: {row['Username']}"
        ).add_to(m)

    # 5. 繪製 verified_data：黃色燈光
    for _, row in verified_data.iterrows():
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=12,
            popup=f"專家辨識: {row['Review Identity']}",
            color="#f1c40f",
            fill=True,
            fill_color="#f1c40f",
            fill_opacity=0.5,
            weight=0
        ).add_to(m)

    # 6. 呈現地圖
    st.markdown("<h2 style='text-align: center; color: white;'>🌌 台灣蛙鳴空間資料互動地圖</h2>", unsafe_allow_html=True)
    folium_static(m, width=1100, height=600)

    # 側邊欄統計
    st.sidebar.title("📊 數據面板")
    st.sidebar.metric("原始紀錄 (藍色漣漪)", len(raw_data))
    st.sidebar.metric("專家審核 (黃色燈光)", len(verified_data))

except Exception as e:
    st.error(f"地圖啟動失敗：{e}")
    st.info("請確認 CSV 檔案中的 Latitude 與 Longitude 欄位名稱正確無誤。")
