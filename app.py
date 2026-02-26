# 4. 繪製 raw_data：極細水波紋動畫
    for _, row in raw_data.iterrows():
        # 微調後的極細波紋 HTML/CSS
        ripple_html = f"""
        <div style="position: relative; width: 40px; height: 40px;">
            <style>
                @keyframes water_ripple {{
                    0% {{ transform: scale(0.3); opacity: 0.8; border-width: 1px; }}
                    50% {{ opacity: 0.4; border-width: 0.5px; }}
                    100% {{ transform: scale(4); opacity: 0; border-width: 0.1px; }}
                }}
            </style>
            <div style="position: absolute; top: 18px; left: 18px; width: 4px; height: 4px; 
                        background-color: #00d2ff; border-radius: 50%; 
                        box-shadow: 0 0 8px #00d2ff; z-index: 1000;"></div>
            <div style="position: absolute; top: 0; left: 0; width: 40px; height: 40px; 
                        border: 0.5px solid #00d2ff; border-radius: 50%; 
                        animation: water_ripple 3s infinite cubic-bezier(0.25, 0.46, 0.45, 0.94); 
                        z-index: 999;"></div>
            <div style="position: absolute; top: 0; left: 0; width: 40px; height: 40px; 
                        border: 0.5px solid #00d2ff; border-radius: 50%; 
                        animation: water_ripple 3s infinite 1s cubic-bezier(0.25, 0.46, 0.45, 0.94); 
                        z-index: 998;"></div>
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
