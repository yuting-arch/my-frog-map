# 4. 繪製 raw_data：極小化藝術漣漪 (#4F9D9D)
    for _, row in raw_data.iterrows():
        # 縮小 10 倍後的波紋 HTML/CSS
        ripple_html = f"""
        <div style="position: relative; width: 10px; height: 10px;">
            <style>
                @keyframes water_art_mini {{
                    0% {{ transform: scale(0.1); opacity: 0.9; }}
                    100% {{ transform: scale(0.5); opacity: 0; filter: blur(1px); }}
                }}
            </style>
            <div style="position: absolute; top: 4px; left: 4px; width: 2px; height: 2px; 
                        background-color: #4F9D9D; border-radius: 50%; 
                        box-shadow: 0 0 5px #4F9D9D; z-index: 1000;"></div>
            
            <div style="position: absolute; top: 0; left: 0; width: 10px; height: 10px; 
                        border: 0.3px solid #4F9D9D; border-radius: 50%; 
                        animation: water_art_mini 3s infinite ease-out; z-index: 999;"></div>
            
            <div style="position: absolute; top: 0; left: 0; width: 10px; height: 10px; 
                        border: 0.2px solid #4F9D9D; border-radius: 50%; 
                        animation: water_art_mini 3s infinite 1.5s ease-out; z-index: 998;"></div>
        </div>
        """
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            icon=folium.DivIcon(
                html=ripple_html,
                icon_size=(10, 10),
                icon_anchor=(5, 5)
            ),
            popup=f"原始錄音者: {row['Username']}"
        ).add_to(m)
