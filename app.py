import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁基本設定
st.set_page_config(page_title="台灣青蛙鳴聲監測地圖", layout="wide")
st.title("🐸 全台青蛙鳴聲監測：動態視覺版")

# 2. 讀取資料函數 (對應您的欄位名稱)
def load_data(file_name):
    try:
        return pd.read_csv(file_name)
    except:
        return None

df_raw = load_data("raw_data.csv")      # 未辨識
df_verified = load_data("verified_data.csv")  # 已辨識

# 3. 建立地圖中心點 (台灣)
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB positron")

# 4. 處理「未辨識」點位 (製作漣漪感)
if df_raw is not None:
    for _, row in df_raw.iterrows():
        loc = [row['Latitude'], row['Longitude']]
        popup_text = f"👤 上傳者: {row['Username']}<br>📅 日期: {row['Create Date']}<br>⚠️ 狀態: 待辨識"
        
        # 繪製三層圓圈來模擬「漣漪」
        # 最外層 (淡紅色大圈)
        folium.Circle(
            location=loc, radius=1200, color='red', weight=1, fill=True, fill_opacity=0.1
        ).add_to(m)
        # 中間層
        folium.Circle(
            location=loc, radius=600, color='red', weight=1, fill=True, fill_opacity=0.2
        ).add_to(m)
        # 中心點 (實心小點)
        folium.CircleMarker(
            location=loc, radius=4, color='red', fill=True, fill_opacity=0.9,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(m)

# 5. 處理「已辨識」點位 (亮淺黃色燈號)
if df_verified is not None:
    for _, row in df_verified.iterrows():
        loc = [row['Latitude'], row['Longitude']]
        popup_text = (
            f"👤 上傳者: {row['Username']}<br>"
            f"🐸 辨識結果: <b>{row['Review Identity']}</b><br>"
            f"👨‍🔬 審核專家: {row['Reviewer']}<br>"
            f"📅 審核日期: {row['Review Date']}"
        )
        
        # 使用自定義的亮淺黃色圓點，模擬燈號感
        folium.CircleMarker(
            location=loc,
            radius=8,
            color='#FFFF88', # 亮淺黃色邊框
            fill=True,
            fill_color='#FFFF00', # 純黃色填充
            fill_opacity=0.9,
            weight=3,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(m)

# 6. 顯示地圖
st_folium(m, width="100%", height=700)

# 下方統計看板
st.divider()
c1, c2, c3 = st.columns(3)
c1.metric("本月新收集 (漣漪點)", len(df_raw) if df_raw is not None else 0)
c2.metric("專家已辨識 (黃燈點)", len(df_verified) if df_verified is not None else 0)
c3.write("💡 提示：點擊地圖點位可查看詳細資訊")
