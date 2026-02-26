import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 網頁設定
st.set_page_config(page_title="台灣蛙鳴監測地圖", layout="wide")
st.title("🐸 台灣青蛙鳴聲監測：擬真水紋波動版")

# 2. 擬真藍色水波紋 CSS
st.markdown("""
<style>
@keyframes ripple-wave {
  0% { transform: scale(0.3); opacity: 1; }
  100% { transform: scale(3.5); opacity: 0; }
}
.ripple-container { position: relative; width: 0; height: 0; display: flex; justify-content: center; align-items: center; }
.ripple-core { width: 8px; height: 8px; background: #00FFFF; border-radius: 50%; box-shadow: 0 0 10px #00FFFF; position: absolute; z-index: 10; }
.ripple-out { position: absolute; width: 30px; height: 30px; border: 2px solid #00BFFF; border-radius: 50%; animation: ripple-wave 2s infinite cubic-bezier(0, 0.2, 0.8, 1); }
</style>
""", unsafe_allow_html=True)

# 3. 超強讀取函數 (加入偵錯顯示)
def load_data_diagnostic(name):
    try:
        df = pd.read_csv(name)
        df.columns = df.columns.str.strip()
        # 尋找經緯度欄位
        lat_c = [c for c in df.columns if 'lat' in c.lower()][0]
        lon_c = [c for c in df.columns if 'lon' in c.lower()][0]
        # 強制轉換並回傳
        df[lat_c] = pd.to_numeric(df[lat_c], errors='coerce')
        df[lon_c] = pd.to_numeric(df[lon_c], errors='coerce')
        valid_df = df.dropna(subset=[lat_c, lon_c])
        return valid_df, lat_c, lon_c, df # 回傳有效資料與原始資料
    except Exception as e:
        return None, None, None, str(e)

df_raw, lat1, lon1, raw_info = load_data_diagnostic("raw_data.csv")
df_verified, lat2, lon2, ver_info = load_data_diagnostic("verified_data.csv")

# 4. 建立地圖
m = folium.Map(location=[23.6, 121.0], zoom_start=7, tiles="CartoDB dark_matter")

# 5. 畫出藍色水波紋 (未辨識)
if df_raw is not None and not isinstance(df_raw, str):
    for _, row in df_raw.iterrows():
        icon_html = '<div class="ripple-container"><div class="ripple-core"></div><div class="ripple-out"></div></div>'
        folium.Marker(location=[row[lat1], row[lon1]], icon=folium.DivIcon(html=icon_html)).add_to(m)

# 6. 畫出亮黃燈號 (已辨識)
if df_verified is not None and not isinstance(df_verified, str):
    for _, row in df_verified.iterrows():
        folium.CircleMarker(location=[row[lat2], row[lon2]], radius=8, color='#FFFFE0', fill=True, fill_color='#FFFF00', fill_opacity=0.9).add_to(m)

# 7. 呈現
st_folium(m, width="100%", height=600)

# --- 💡 博士的超級診斷面板 ---
st.divider()
st.subheader("🛠️ 資料讀取診斷 (若沒看到點位請看這裡)")
col1, col2 = st.columns(2)

with col1:
    st.write("🟦 **raw_data.csv (藍色水紋資料)**")
    if isinstance(raw_info, str):
        st.error(f"檔案讀取失敗: {raw_info}")
    else:
        st.write(f"成功讀取列數: {len(raw_info)}，有效座標列數: {len(df_raw)}")
        st.dataframe(raw_info.head(3)) # 顯示前三行看內容

with col2:
    st.write("🟨 **verified_data.csv (黃色燈號資料)**")
    if isinstance(ver_info, str):
        st.error(f"檔案讀取失敗: {ver_info}")
    else:
        st.write(f"成功讀取列數: {len(ver_info)}，有效座標列數: {len(df_verified)}")
        st.dataframe(ver_info.head(3))
