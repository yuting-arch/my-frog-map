# 4. 繪製 raw_data：#4F9D9D 不隨縮放變形的小比例藝術漣漪
    for _, row in raw_data.iterrows():
        # 這裡設定 icon_size 為較大的範圍，但透過 CSS 控制視覺呈現
        ripple_html = f"""
        <div style="position: relative; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center;">
            <style>
                @keyframes soft_breathing {{
                    0% {{ transform: scale(0.5); opacity: 0; }}
                    30% {{ opacity: 0.8; }}
                    100% {{ transform: scale(1.5); opacity: 0; filter: blur(1px); }}
                }}
            </style>
            <div style="position: absolute; width: 4px; height: 4px; 
                        background-color: #4F9D9D; border-radius: 50%; 
                        box-shadow: 0 0 6px 1px #4F9D9D; z-index: 1000;"></div>
            
            <div style="position: absolute; width: 20px; height: 20px; 
                        border: 0.8px solid #4F9D9D; border-radius: 50%; 
                        animation: soft_breathing 4s infinite ease-out; z-index: 999;"></div>
            
            <div style="position: absolute; width: 20px; height: 20px; 
                        border: 0.5px solid #4F9D9D; border-radius: 50%; 
                        animation: soft_breathing 4s infinite 2s ease-out; z-index: 998;"></div>
        </div>
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(
                html=ripple_html,
                icon_size=(40, 40),      # 增加容器感應範圍
                icon_anchor=(20, 20)     # 嚴格中心對齊
            ),
            popup=f"原始錄音者: {row['Username']}"
        ).add_to(m)
