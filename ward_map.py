import pandas as pd
import googlemaps
import folium
import time
from pathlib import Path
import os
import re
from branca.element import Template, MacroElement
import numpy as np
from shapely.geometry import Point, Polygon
import json

# Set your Google API key here
API_KEY = ""

# Initialize Google Maps client
gmaps = googlemaps.Client(key=API_KEY)

downloads_path = str(Path.home() / "Downloads")
os.chdir(downloads_path)

# --- Config ---
CSV_PATH = "naples_ward_list_07_06_2025.csv"

# --- Updated Flood Zone Data for Collier County ---
# Based on the actual FEMA flood zone map provided
flood_zones = {
    'A': {
        'name': 'Zone A',
        'description': 'High-risk flood zone covering southern coastal areas and Ten Thousand Islands',
        'color': '#FD0707',
        'risk_level': 'High',
        'polygons': [[
               [
            -81.85032534913698,
            26.341591800866894
          ],
          [
            -81.7527367904673,
            26.342739783274055
          ],
          [
            -81.75026052255919,
            26.33188984890458
          ],
          [
            -81.81923159845039,
            26.330658496767555
          ],
          [
            -81.81886477688138,
            26.316683087827386
          ],
          [
            -81.8050149669697,
            26.315860627038447
          ],
          [
            -81.80446460814186,
            26.304267886542917
          ],
          [
            -81.80207985967,
            26.296620892458662
          ],
          [
            -81.79987759885277,
            26.171597338002968
          ],
          [
            -81.76707101490466,
            26.174009473892525
          ],
          [
            -81.76656371902152,
            26.126973120155213
          ],
          [
            -81.7202504066937,
            26.0765072179331
          ],
          [
            -81.5948558786264,
            25.996360475194535
          ],
          [
            -81.58429201091752,
            25.988275297306004
          ],
          [
            -81.56985854733729,
            25.98705319324759
          ],
          [
            -81.55330130446703,
            25.974086199139478
          ],
          [
            -81.51309930774737,
            25.959416991072644
          ],
          [
            -81.51058911116279,
            25.959605069700686
          ],
          [
            -81.51079855389081,
            25.97878747176587
          ],
          [
            -81.50431388057831,
            25.978411377042022
          ],
          [
            -81.50431362280466,
            25.960263342475187
          ],
          [
            -81.49531875049469,
            25.960733535003712
          ],
          [
            -81.47139324253419,
            25.942309474430374
          ],
          [
            -81.39828012869555,
            25.919075883029308
          ],
          [
            -81.3792816212243,
            25.916801605175806
          ],
          [
            -81.33660787999604,
            25.901278446942314
          ],
          [
            -81.29613105214572,
            25.901654875632545
          ],
          [
            -81.23907471159801,
            25.878032589101068
          ],
          [
            -81.10093362293215,
            25.864045236404536
          ],
          [
            -81.28554059529705,
            25.665466278397815
          ],
          [
            -81.79032968157061,
            25.84412170835772
          ],
          [
            -81.8508126551343,
            26.341739764771845
          ]
        ]]
    },
    'B': {
        'name': 'Zone B',
        'description': 'Moderate to high-risk zone in northern Naples area',
        'color': '#F55E06',
        'risk_level': 'Moderate to high',
        'polygons': [[
   [
            -81.80153714520621,
            26.27248210413002
          ],
          [
            -81.76978897846617,
            26.272436370517937
          ],
          [
            -81.76973791473911,
            26.26649578609849
          ],
          [
            -81.76861777928195,
            26.232034663456574
          ],
          [
            -81.76836360305273,
            26.212014534751063
          ],
          [
            -81.76705735366582,
            26.173979263020072
          ],
          [
            -81.7872072262379,
            26.17345955504031
          ],
          [
            -81.79156918252285,
            26.17179664684302
          ],
          [
            -81.79955968021389,
            26.17172733406059
          ],
          [
            -81.80158305410734,
            26.272561609885756
          ]
]]
    },
    'C': {
        'name': 'Zone C',
        'description': 'Moderate to Minimal-risk zone in western Naples',
        'color': '#F9C74F',
        'risk_level': 'Moderate',
        'polygons': [[
            [
            -81.8058861363581,
            26.330666391086382
          ],
          [
            -81.76257960137326,
            26.33119808089947
          ],
          [
            -81.76244777021677,
            26.327417122506446
          ],
          [
            -81.76271143253048,
            26.32537889840539
          ],
          [
            -81.76228298127097,
            26.298140056323675
          ],
          [
            -81.7614590365413,
            26.296189958727382
          ],
          [
            -81.76043734507655,
            26.295126255305092
          ],
          [
            -81.75611987469378,
            26.29282153108197
          ],
          [
            -81.75486747870464,
            26.29107818361355
          ],
          [
            -81.75427782692131,
            26.289304482182914
          ],
          [
            -81.7539875079372,
            26.268899669000717
          ],
          [
            -81.75345875363439,
            26.26209070185928
          ],
          [
            -81.75307805053698,
            26.244758024462968
          ],
          [
            -81.75199939175874,
            26.216210874852734
          ],
          [
            -81.75142833711158,
            26.210290672092952
          ],
          [
            -81.75102648384288,
            26.171181099503826
          ],
          [
            -81.75079383194975,
            26.1686754666147
          ],
          [
            -81.75066693091664,
            26.153599426207165
          ],
          [
            -81.74257139263341,
            26.153904924314887
          ],
          [
            -81.7351444272414,
            26.1542438771628
          ],
          [
            -81.71884312136115,
            26.154300387530057
          ],
          [
            -81.71820760266766,
            26.132824872352685
          ],
          [
            -81.71821409595861,
            26.128330216772326
          ],
          [
            -81.71825926815355,
            26.124882902058232
          ],
          [
            -81.717988234985,
            26.123260601110886
          ],
          [
            -81.71789636611214,
            26.10916362747642
          ],
          [
            -81.70189954547251,
            26.109020704416878
          ],
          [
            -81.68728117048113,
            26.10962545397703
          ],
          [
            -81.68736891474329,
            26.079965265281558
          ],
          [
            -81.6896995815538,
            26.075517217812134
          ],
          [
            -81.69911100247447,
            26.063461853332626
          ],
          [
            -81.72017063942188,
            26.07673026752518
          ],
          [
            -81.7652441710033,
            26.126246454971422
          ],
          [
            -81.7654690512303,
            26.126549811904212
          ],
          [
            -81.76647522038104,
            26.12717087061617
          ],
          [
            -81.76697827199473,
            26.173628066159807
          ],
          [
            -81.76828757641279,
            26.202928608820713
          ],
          [
            -81.76831755998889,
            26.222054553586403
          ],
          [
            -81.76843748203954,
            26.23133384539551
          ],
          [
            -81.76936688397991,
            26.243811542395633
          ],
          [
            -81.7698765690747,
            26.272490137074115
          ],
          [
            -81.80160865839429,
            26.272556140840706
          ],
          [
            -81.8021782952978,
            26.29697386586959
          ],
          [
            -81.80463668476435,
            26.305708828646672
          ],
          [
            -81.8058658821365,
            26.330708586355655
          ]
        ]]
    },
    'D': {
        'name': 'Zone D',
        'description': 'Minimal-risk zone west of Zone A/C, bounded by I-75 on east and north',
        'color': '#90BE6D',
        'risk_level': 'Minimal',
        'polygons': [[
            [
            -81.76231515751302,
            26.331196769642588
          ],
          [
            -81.75006639414391,
            26.33156536275351
          ],
          [
            -81.74768971180335,
            26.320996596777206
          ],
          [
            -81.74321078379747,
            26.308214480661334
          ],
          [
            -81.74247954992427,
            26.261704570534803
          ],
          [
            -81.73690355794835,
            26.243966152136778
          ],
          [
            -81.73534936878018,
            26.178883322283326
          ],
          [
            -81.73370394092092,
            26.17264861133995
          ],
          [
            -81.72876781048008,
            26.167207418406804
          ],
          [
            -81.72424301899345,
            26.1647871708837
          ],
          [
            -81.71871077175541,
            26.163925758011544
          ],
          [
            -81.70321690657458,
            26.164295006619028
          ],
          [
            -81.68488935507666,
            26.159905648034226
          ],
          [
            -81.66584988775351,
            26.15522692949996
          ],
          [
            -81.59964014821944,
            26.153544876051626
          ],
          [
            -81.51513181967762,
            26.153052568730075
          ],
          [
            -81.25885209653316,
            26.155836398040876
          ],
          [
            -81.24309931056176,
            26.165965796519714
          ],
          [
            -81.24331013792221,
            26.167184776938015
          ],
          [
            -81.02449809322653,
            26.170010606624288
          ],
          [
            -80.92169607573597,
            25.845547820286015
          ],
          [
            -81.24020623354781,
            25.878491549631434
          ],
          [
            -81.26144024406823,
            25.88573793757267
          ],
          [
            -81.26006643764833,
            25.88674433938141
          ],
          [
            -81.29458711546653,
            25.901501803780647
          ],
          [
            -81.33410093910122,
            25.901501547816267
          ],
          [
            -81.36491264170476,
            25.910868490532437
          ],
          [
            -81.38040210612802,
            25.91748745729545
          ],
          [
            -81.39894626668976,
            25.919540270648895
          ],
          [
            -81.40864627650761,
            25.921721344717554
          ],
          [
            -81.43446537912516,
            25.929290634013782
          ],
          [
            -81.46870056105797,
            25.94134915084524
          ],
          [
            -81.49466200283267,
            25.960845353349242
          ],
          [
            -81.50478993525569,
            25.960588845842594
          ],
          [
            -81.50507489824875,
            25.97841475400776
          ],
          [
            -81.51120869998655,
            25.978542987925238
          ],
          [
            -81.51078110144152,
            25.960717099667164
          ],
          [
            -81.5132061106776,
            25.96007582911176
          ],
          [
            -81.55214838145268,
            25.974054715575406
          ],
          [
            -81.56963182233301,
            25.987518210713958
          ],
          [
            -81.58461046565475,
            25.988928577503316
          ],
          [
            -81.6201133037733,
            26.012717878468663
          ],
          [
            -81.6990739119774,
            26.06334888384542
          ],
          [
            -81.68927832315008,
            26.07583435324993
          ],
          [
            -81.68755191875249,
            26.079323177812626
          ],
          [
            -81.68717381776871,
            26.109748863042313
          ],
          [
            -81.70288381264155,
            26.10909753844348
          ],
          [
            -81.71766570018448,
            26.10919442377815
          ],
          [
            -81.71798935010585,
            26.123193713964383
          ],
          [
            -81.71836698329196,
            26.125034325120765
          ],
          [
            -81.71835865020805,
            26.129157339267806
          ],
          [
            -81.71807100928862,
            26.13081008288141
          ],
          [
            -81.71864625719655,
            26.154152569195404
          ],
          [
            -81.73529805547399,
            26.15430511408765
          ],
          [
            -81.75068343496865,
            26.153606391584987
          ],
          [
            -81.75088256642965,
            26.170780084814126
          ],
          [
            -81.7512989322148,
            26.17857209221019
          ],
          [
            -81.75146185795987,
            26.206693996170216
          ],
          [
            -81.7516066808413,
            26.21375144038909
          ],
          [
            -81.75202304662442,
            26.21639285056635
          ],
          [
            -81.753018703936,
            26.24599368694608
          ],
          [
            -81.75360956117827,
            26.260056315556938
          ],
          [
            -81.75351904687665,
            26.261940573065303
          ],
          [
            -81.75373628119802,
            26.267344825358165
          ],
          [
            -81.75411644126115,
            26.269309066750623
          ],
          [
            -81.75417074984274,
            26.28914351675995
          ],
          [
            -81.75473193850831,
            26.290961317171295
          ],
          [
            -81.75622303087532,
            26.292794669870943
          ],
          [
            -81.76044502015363,
            26.29509618401164
          ],
          [
            -81.76191135182816,
            26.296962579306395
          ],
          [
            -81.76234582047239,
            26.298666653120605
          ],
          [
            -81.76259926051422,
            26.32559097556556
          ],
          [
            -81.76240012905347,
            26.327602905752386
          ],
          [
            -81.76241823191283,
            26.331204822474433
          ]
        ]]
    },
    'E': {
        'name': 'Zone E',
        'description': 'Very minimal-risk zone east and north of I-75',
        'color': '#43AA8B',
        'risk_level': 'Very Minimal',
        'polygons': [[
  [
            -81.75034621471349,
            26.33166871631019
          ],
          [
            -81.59498144214004,
            26.33481134904629
          ],
          [
            -81.59520697289923,
            26.292819395884166
          ],
          [
            -81.59498065785499,
            26.291906338099366
          ],
          [
            -81.56227881551452,
            26.293123443927087
          ],
          [
            -81.5455316281073,
            26.293630682625036
          ],
          [
            -81.54417147389181,
            26.202594401411034
          ],
          [
            -81.54360703210018,
            26.153383315225327
          ],
          [
            -81.60740893627606,
            26.15394181305024
          ],
          [
            -81.66589899449204,
            26.155659795156083
          ],
          [
            -81.70251395048214,
            26.16442373405289
          ],
          [
            -81.71863702003579,
            26.164208813931708
          ],
          [
            -81.7239500517775,
            26.164939106141233
          ],
          [
            -81.72878404966342,
            26.1673018746295
          ],
          [
            -81.7336660915742,
            26.17288644092619
          ],
          [
            -81.73558044260197,
            26.17898618724807
          ],
          [
            -81.73610527695357,
            26.217423510621884
          ],
          [
            -81.73663061362814,
            26.24394121650444
          ],
          [
            -81.74232593088294,
            26.261676144502886
          ],
          [
            -81.7430445942921,
            26.307960233958084
          ],
          [
            -81.74784876225608,
            26.320619974852875
          ],
          [
            -81.74995456763101,
            26.33163589561768
          ]
]]
    }
}




def point_in_flood_zone(lat, lon):
    """Determine which flood zone a point falls into."""
    point = Point(lon, lat)  # Note: Point takes (lon, lat)
    
    for zone_id, zone_data in flood_zones.items():
        for polygon_coords in zone_data['polygons']:
            polygon = Polygon(polygon_coords)
            if polygon.contains(point):
                return zone_id, zone_data['name'], zone_data['risk_level']
    
    return None, 'Outside Flood Zones', 'Unknown'

def get_flood_zone_icon_color(zone_id):
    """Get marker color based on flood zone risk - matches the provided map."""
    if zone_id == 'A':
        return 'red'
    elif zone_id == 'B':
        return 'orange'
    elif zone_id == 'C':
        return 'yellow'
    elif zone_id == 'D':
        return 'lightgreen'
    elif zone_id == 'E':
        return 'green'
    else:
        return 'gray'


# --- Read CSV ---
df = pd.read_csv(CSV_PATH)
print(df)
df_clean = df[df['Street Address 1'].notna() & (df['Street Address 1'].str.strip() != '')]
df_clean = df_clean[df_clean['Street Address 1'].astype(str).str.strip() != '']
df_clean['City'] = df_clean['City'].replace('', pd.NA) 
df_clean['City'] = df_clean['City'].fillna('Naples')
def build_clean_address(row):
    street1 = re.sub(r'(Apt|Unit|#)\s*\w+', '', str(row.get('Street Address 1', '')).strip(), flags=re.IGNORECASE)
    street2 = re.sub(r'(Apt|Unit|#)\s*\w+', '', str(row.get('Address 2', '')).strip(), flags=re.IGNORECASE)
    city = str(row.get('City', '')).strip()
    state = str(row.get('State', '')).strip()
    postal_code = str(row.get('zip', '')).strip()
    address_parts = [street1, street2, city, state, postal_code]
    return ", ".join([part for part in address_parts if part])

def color_coding(row):
    if ((row['has_ministering_assignment'] == 'TRUE') or (row['has_ministering_assignment']=='1')) and row['has_ministering_brother'] == 'TRUE':
        return 'green'
    elif ((row['has_ministering_assignment'] == 'TRUE') or (row['has_ministering_assignment']=='1')) and (row['has_ministering_brother'] != 'TRUE' and row['has_ministering_brother'] != '1'):
        return 'blue'
    elif ((row['has_ministering_assignment'] != 'TRUE') and (row['has_ministering_assignment']!='1')) and ((row['has_ministering_brother'] == 'TRUE') or (row['has_ministering_brother'] =='1')):
        return 'purple'
    elif ((row['has_ministering_assignment'] != 'TRUE') and (row['has_ministering_assignment']!='1')) and (row['has_ministering_brother'] != 'TRUE' and row['has_ministering_brother'] != '1'):
        return 'red'
    else: 
        return 'lightgray'

df_clean['color_coding_ministering'] = df.apply(color_coding, axis=1)

rows = df_clean[['Name','HOH', 'Age', 'Gender', 'Street Address 1', 'Address 2', 'City', 'State', 'zip', 'has_ministering_assignment', 'has_ministering_brother', 'has_ministering_sister', 'color_coding_ministering']].dropna(subset=['Name', 'Street Address 1'])

# Filter for heads of household only
rows = rows[(rows['HOH'] =='TRUE') | (rows['HOH'] == '1') ]
print(f"Row count (heads of household only): {rows.shape[0]}")

def google_geocode(address):
    try:
        geocode_result = gmaps.geocode(address)
        if geocode_result:
            result = geocode_result[0]
            location = result['geometry']['location']
            
            # Check if result is in Florida
            states = [comp['short_name'].lower() for comp in result['address_components'] if 'administrative_area_level_1' in comp['types']]
            if 'fl' in states:
                return location['lat'], location['lng']
            else:
                print(f"Discarded (not FL): {address}")
        else:
            print(f"No results for: {address}")
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
    return None

# --- Geocoding ---
locations = []

for index, row in rows.iterrows():
    address = build_clean_address(row)
    location = google_geocode(address)
    if location:
        lat, lon = location
        print(f"{address} -> ({lat}, {lon})")

        # Determine flood zone
        flood_zone_id, flood_zone_name, flood_risk = point_in_flood_zone(lat, lon)
        
        record = row.to_dict()
        record["address"] = address
        record["lat"] = lat
        record["lon"] = lon
        record["flood_zone_id"] = flood_zone_id
        record["flood_zone_name"] = flood_zone_name
        record["flood_risk"] = flood_risk
        locations.append(record)
        
        print(f"  -> Flood Zone: {flood_zone_name} ({flood_risk} risk)")
    else:
        print(f"Could not geocode: {address}")
    time.sleep(1)  # Respect Google API rate limits

if locations:
    # Create map centered on Naples area
    m = folium.Map(location=[26.1420, -81.7948], zoom_start=11)
    
    # Add flood zone polygons as overlays
    flood_zone_group = folium.FeatureGroup(name="Collier County Flood Zones")
    
    for zone_id, zone_data in flood_zones.items():
        for polygon_coords in zone_data['polygons']:
            folium.Polygon(
                locations=[[lat, lon] for lon, lat in polygon_coords],
                color=zone_data['color'],
                weight=2,
                opacity=0.8,
                fill=True,
                fillColor=zone_data['color'],
                fillOpacity=0.3,
                popup=folium.Popup(
                    f"<b>{zone_data['name']}</b><br>"
                    f"Risk Level: {zone_data['risk_level']}<br>"
                    f"{zone_data['description']}", 
                    max_width=350
                )
            ).add_to(flood_zone_group)
    
    flood_zone_group.add_to(m)
    
    # Add household markers
    household_group = folium.FeatureGroup(name="Households")
    
    for loc in locations:
        # Use flood zone color for border, ministering color for icon
        flood_zone_color = get_flood_zone_icon_color(loc["flood_zone_id"])
        ministering_color = loc["color_coding_ministering"]

        # Create popup HTML with flood zone info
        popup_html = ""
        for key, value in loc.items():
            if key in ["lat", "lon"]:  # Skip coordinates
                continue
            popup_html += f"<b>{key}:</b> {value}<br>"

        # Create a custom icon that shows both ministering status and flood risk
        folium.CircleMarker(
            [loc["lat"], loc["lon"]],
            radius=8,
            popup=folium.Popup(popup_html, max_width=400),
            color=flood_zone_color,  # Border color indicates flood risk
            weight=3,
            fill=True,
            fillColor=ministering_color,  # Fill color indicates ministering status
            fillOpacity=0.7,
            tooltip=f"{loc['Name']} - {loc['flood_zone_name']}"
        ).add_to(household_group)
    
    household_group.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # --- Updated Legend ---
    legend_html = """
    {% macro html(this, kwargs) %}

    <div style="
        position: fixed; 
        bottom: 50px;
        left: 50px;
        width: 300px;
        z-index:9999;
        background-color: white;
        border:2px solid grey;
        padding: 15px;
        font-size:12px;
        box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
    ">
    <b>Household Ministering Status (Fill Color):</b><br>
    <i style="background:green; width:10px; height:10px; float:left; margin-right:8px; margin-top:2px;"></i>
        Ministering Assigned & Has Ministering Brother<br>
    <i style="background:blue; width:10px; height:10px; float:left; margin-right:8px; margin-top:2px;"></i>
        Ministering Assigned & Has No Ministering Brother<br>
    <i style="background:purple; width:10px; height:10px; float:left; margin-right:8px; margin-top:2px;"></i>
        No Ministering Assignment & Has Ministering Brother<br>
    <i style="background:red; width:10px; height:10px; float:left; margin-right:8px; margin-top:2px;"></i>
        No Ministering Assignment & Has No Ministering Brother<br>
    <i style="background:grey; width:10px; height:10px; float:left; margin-right:8px; margin-top:2px;"></i>
        Unknown / Other<br><br>
    
    <b>Collier County Flood Risk (Border Color):</b><br>
    <i style="background:red; width:10px; height:10px; float:left; margin-right:8px; margin-top:2px;"></i>
    High Risk (Zone A)<br>
    <i style="background:orange; width:10px; height:10px; float:left; margin-right:8px; margin-top:2px;"></i>
    Moderate Risk (Zone B)<br>
    <i style="background:yellow; width:10px; height:10px; float:left; margin-right:8px; margin-top:2px;"></i>
    Moderate to Minimal Risk (Zone C)<br>
    <i style="background:lightgreen; width:10px; height:10px; float:left; margin-right:8px; margin-top:2px;"></i>
    Minimal Risk (Zone D)<br>
    <i style="background:green; width:10px; height:10px; float:left; margin-right:8px; margin-top:2px;"></i>
    Very Minimal Risk (Zone E)<br>
    <i style="background:grey; width:10px; height:10px; float:left; margin-right:8px; margin-top:2px;"></i>
    Outside Mapped Zones
    </div>

    {% endmacro %}
    """

    legend = MacroElement()
    legend._template = Template(legend_html)
    m.get_root().add_child(legend)
    
    # Save map
    m.save("mapped_addresses_with_collier_flood_zones.html")
    print("✅ Map with Collier County flood zones saved to 'mapped_addresses_with_collier_flood_zones.html'")
    
    # Create summary report
    print("\n🌊 COLLIER COUNTY FLOOD ZONE SUMMARY:")
    flood_summary = {}
    for loc in locations:
        zone = loc['flood_zone_name']
        if zone not in flood_summary:
            flood_summary[zone] = 0
        flood_summary[zone] += 1
    
    for zone, count in sorted(flood_summary.items()):
        print(f"  {zone}: {count} households")
    
    # Save locations data with flood zones
    locations_df = pd.DataFrame(locations)
    locations_df.to_csv("households_with_collier_flood_zones.csv", index=False)
    print("✅ Household data with Collier County flood zones saved to 'households_with_collier_flood_zones.csv'")
    
else:
    print("❌ No addresses were geocoded successfully.")
