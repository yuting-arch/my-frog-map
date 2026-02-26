import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣青蛙鳴聲監測地圖", layout="wide")
st.title("🐸 全台青蛙鳴聲收集紀錄")
st.markdown("本地圖呈現民眾上傳的原始資料（紅色漣漪）與專家辨識後的紀錄（黃色燈號）。")

# 2. 讀取 CSV 資料函數
@st.cache_data
def load_frog_data():
    try:
        # 讀取剛才上傳的 data.csv
        df = pd.read_csv("data.csv")
        return df
    except Exception as e:
        st.error(f"讀取資料失敗，請確認資料夾中是否有 data.csv 檔案。錯誤訊息: {e}")
        return None

# 執行讀取
df = load_frog_data()

if df is not None:
    # 3. 建立台灣中心地圖
    # [Image of interactive map interface with color coded markers]
    m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB positron")

    # 4. 處理每一筆資料點位
    for index, row in df.iterrows():
        # 取得座標
        location = [row['lat'], row['lon']]
        
        # 判斷狀態：0 為新上傳(漣漪)，1 為專家已辨識(黃燈)
        if row['status'] == 0:
            # 製作紅色漣漪感 (外圈)
            folium.Circle(
                location=location,
                radius=800,
                color='red',
                weight=1,
                fill=False
            ).add_to(m)
            # 內點
            folium.CircleMarker(
                location=location,
                radius=8,
                color='red',
                fill=True,
                fill_opacity=0.7,
                popup="新收集：等待專業辨識"
            ).add_to(m)
            
        else:
            # 專家辨識後轉為亮黃色燈號
            folium.Marker(
                location=location,
                icon=folium.Icon(color='orange', icon='star'),
                popup="✅ 專家已確認蛙種"
            ).add_to(m)

    # 5. 將地圖渲染到網頁上
    st_folium(m, width="100
