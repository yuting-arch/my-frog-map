import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：擬真水紋波動版")

# 2. 擬真水波紋 CSS
st.markdown("""
<style>
@keyframes ripple-wave {
  0% { transform: scale(0.2); opacity: 1; }
  100% { transform: scale(4.0); opacity: 0; }
}
.water-ripple {
  position: relative;
  width: 12px; height: 12px;
  background: #00FFFF;
  border-radius: 50%;
  box-shadow: 0 0 10px #00FFFF;
  display: flex; justify-content: center; align-items: center;
}
.water-ripple::before {
  content: ""; position: absolute;
  width: 40px; height: 40px;
  border: 2px solid #00BFFF;
  border-radius: 50%;
  animation: ripple-wave 2s infinite;
}
</style>
""", unsafe_allow_html=True)

# 3. 超強相容讀取函數
def load_data_extreme(name):
    try:
        # 強制使用 utf-8 讀取，並處理可能的欄位空格
        df = pd.read_csv(name, skipinitialspace=True)
        # 統一將欄位名稱轉為小寫
        df.columns = df.columns.str.strip().str.lower()
        
        # 自動尋找包含 lat 和 lon 字眼的欄位
        lat_col = [c for c in df.columns if 'lat' in c][0]
        lon_col = [c for c in df.columns if 'lon' in c][0]
        
        # 強制轉換經緯度為數字，若出錯則設為空值並刪除
        df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
        df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')
        df = df.dropna(subset=[lat_col, lon_col])
        
        return df, lat_col, lon_col
    except Exception as e:
        return None, str(e), ""

# 讀取資料
df_raw, err_raw, _ = load_data_extreme("raw_data.csv")
df_verified, err_ver, _ = load_data_extreme("verified_data.csv")

# 4. 建立地圖
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 畫出藍色水波紋 (未辨識)
if df_raw is not None:
    for _, row in df_raw.iterrows():
        # 自動抓取對應欄位
        folium.Marker(
            location=[row.iloc[df_raw.columns.get_loc([c for c in df_raw.columns if 'lat' in c][0])], 
                      row.iloc[df_raw.columns.get_loc([c for c in df_raw.columns if 'lon' in c][0])]],
            icon=folium.DivIcon(html='<div class="water-ripple"></div>'),
            popup="新收集點位"
        ).add_to(m)

# 6. 畫出亮黃燈號 (已辨識)
if df_verified is not None:
    for _, row in df_verified.iterrows():
        folium.CircleMarker(
            location=[row.iloc[df_verified.columns.get_loc([c for c in df_verified.columns if 'lat' in c][0])], 
                      row.iloc[df_verified.columns.get_loc([c for c in df_verified.columns if 'lon' in c][0])]],
            radius=8, color='#FFFFE0', fill=True, fill_color='#FFFF00', fill_opacity=0.9, weight=2
        ).add_to(m)

# 7. 呈現地圖
st_folium(m, width="100%", height=700)

# --- 偵錯面板 (只有沒資料時會顯示) ---
if df_raw is None or len(df_raw) == 0:
    st.error(f"❌ 無法顯示藍色點位。錯誤原因：{err_raw}")
    if df_raw is not None: st.write("您的原始欄位有：", list(df_raw.columns))
