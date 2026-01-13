import dash
from dash import html, dcc, Output, Input, callback, dash_table
import dash_leaflet as dl
import pandas as pd
from shapely.geometry import Point, Polygon
from flood_evacuation_zones import flood_zones
from naples_ward.dnc_moved_list import dnc_moved_list
import time
from pathlib import Path
import re
import os
from dash import register_page

register_page(__name__, path="/")
# --- Load household data ---
path = str(Path.home() / "Documents/church_stuff/dash_app")
os.chdir(path)

# --- Config ---
CSV_PATH = "naples_ward/Naples_Ward_Household_List_01_04_2026.csv"
# --- Read CSV ---
df = pd.read_csv(CSV_PATH, sep="^", header=0)
print(f"Row count (heads of household only): {df.shape[0]}")
df_clean = df[
    df["Street Address 1"].notna() & (df["Street Address 1"].str.strip() != "")
]
df_clean = df_clean[df_clean["Street Address 1"].astype(str).str.strip() != ""]
df_clean["City"] = df_clean["City"].replace("", pd.NA)
df_clean["City"] = df_clean["City"].fillna("Naples")
df_clean_hoh = df_clean[(df_clean["HOH"] == "TRUE") | (df_clean["HOH"] == "1")].copy()
df_clean_hoh = df_clean[
    (df_clean["HOH"] == True) & (~df_clean["Name"].isin(dnc_moved_list))
].copy()
print(f"Row count (heads of household only): {df_clean_hoh.shape[0]}")


def build_clean_address(row):
    street1 = re.sub(
        r"(Apt|Unit|#)\s*\w+",
        "",
        str(row.get("Street Address 1", "")).strip(),
        flags=re.IGNORECASE,
    )
    street2 = re.sub(
        r"(Apt|Unit|#)\s*\w+",
        "",
        str(row.get("Address 2", "")).strip(),
        flags=re.IGNORECASE,
    )
    city = str(row.get("City", "")).strip()
    state = str(row.get("State", "")).strip()
    postal_code = str(row.get("zip", "")).strip()
    address_parts = [street1, street2, city, state, postal_code]
    return ", ".join([part for part in address_parts if part])


def color_coding(row):
    assigned = row["Assignment to Minister"] in ("TRUE", "1")
    brother_ministers_to_you = row["Brothers Ministering to You"] not in (
        "",
        None,
    ) and not pd.isna(row["Brothers Ministering to You"])
    sister_ministers_to_you = row["Sisters Ministering to You"] not in (
        "",
        None,
    ) and not pd.isna(row["Sisters Ministering to You"])

    if assigned and brother_ministers_to_you and not sister_ministers_to_you:
        return "green"
    elif assigned and brother_ministers_to_you and sister_ministers_to_you:
        return "blue"
    elif not assigned and brother_ministers_to_you and sister_ministers_to_you:
        return "yellow"
    elif assigned and not brother_ministers_to_you and sister_ministers_to_you:
        return "purple"
    elif not assigned and brother_ministers_to_you and not sister_ministers_to_you:
        return "lightblue"
    elif assigned and not brother_ministers_to_you and not sister_ministers_to_you:
        return "pink"
    elif not assigned and not brother_ministers_to_you and sister_ministers_to_you:
        return "orange"
    elif not assigned and not brother_ministers_to_you and not sister_ministers_to_you:
        return "red"
    else:
        return "lightgray"


df_clean_hoh["color_coding_ministering"] = df_clean_hoh.apply(color_coding, axis=1)
df_clean_hoh_filtered = (
    df_clean_hoh[
        [
            "Name",
            "HOH",
            "Individual Phone",
            "Age",
            "Gender",
            "Street Address 1",
            "Address 2",
            "City",
            "State",
            "zip",
            "Latitude",
            "Longitude",
            "Assignment to Minister",
            "Brothers Ministering to You",
            "Sisters Ministering to You",
            "color_coding_ministering",
        ]
    ]
    .dropna(subset=["Name", "Latitude", "Longitude"])
    .copy()
)

print(f"Row count (heads of household only): {df_clean_hoh.shape[0]}")


# --- Assign households to zones ---
def point_in_flood_zone(lat, lon):
    point = Point(lon, lat)
    for zid, zdata in flood_zones.items():
        for poly in zdata["polygons"]:
            polygon = Polygon(poly)
            if polygon.contains(point):
                return zid, zdata["name"], zdata["risk_level"]
    return None, "Outside Flood Zones", "Unknown"


households = []
for _, row in df_clean_hoh_filtered.iterrows():
    try:
        lat, lon = float(row["Latitude"]), float(row["Longitude"])
        zid, zname, risk = point_in_flood_zone(lat, lon)
        households.append(
            {
                "Name": row["Name"],
                "Phone": row["Individual Phone"],
                "Street Address 1": row["Street Address 1"],
                "Address 2": row["Address 2"],
                "Assignment to Minister": row["Assignment to Minister"],
                "Brothers Ministering to You": row["Brothers Ministering to You"],
                "Sisters Ministering to You": row["Sisters Ministering to You"],
                "lat": lat,
                "lon": lon,
                "zone": zname,
                "risk": risk,
                "color_coding_ministering": row["color_coding_ministering"],
            }
        )
    except Exception:
        continue


# Flood zone polygons as layers
flood_layers = [
    dl.Polygon(
        positions=[[lat, lon] for lon, lat in zone["polygons"][0]],
        color=zone["color"],
        fillOpacity=0.3,
        children=dl.Popup([html.B(zone["name"]), html.Br(), zone["risk_level"]]),
    )
    for zone in flood_zones.values()
]

# Household markers
household_markers = [
    dl.CircleMarker(
        center=(h["lat"], h["lon"]),
        radius=6,
        color="black",
        fillColor=h["color_coding_ministering"],
        fillOpacity=0.7,
        children=dl.Popup([html.B(h["Name"]), html.Br(), f"Flood Zone: {h['zone']}"]),
    )
    for h in households
]

legend = html.Div(
    children=[
        html.Div(
            "Household Assignment", style={"fontWeight": "bold", "marginBottom": "5px"}
        ),
        html.Div(
            [
                html.Span(
                    style={
                        "backgroundColor": "green",
                        "display": "inline-block",
                        "width": "12px",
                        "height": "12px",
                        "marginRight": "6px",
                    }
                ),
                "Assigned + Brother Ministering Only",
            ]
        ),
        html.Div(
            [
                html.Span(
                    style={
                        "backgroundColor": "blue",
                        "display": "inline-block",
                        "width": "12px",
                        "height": "12px",
                        "marginRight": "6px",
                    }
                ),
                "Assigned + Both Brothers and Sisters Ministering",
            ]
        ),
        html.Div(
            [
                html.Span(
                    style={
                        "backgroundColor": "yellow",
                        "display": "inline-block",
                        "width": "12px",
                        "height": "12px",
                        "marginRight": "6px",
                    }
                ),
                "Not Assigned + Both Brothers and Sisters Ministering",
            ]
        ),
        html.Div(
            [
                html.Span(
                    style={
                        "backgroundColor": "purple",
                        "display": "inline-block",
                        "width": "12px",
                        "height": "12px",
                        "marginRight": "6px",
                    }
                ),
                "Assigned + Sister Ministering Only",
            ]
        ),
        html.Div(
            [
                html.Span(
                    style={
                        "backgroundColor": "lightblue",
                        "display": "inline-block",
                        "width": "12px",
                        "height": "12px",
                        "marginRight": "6px",
                    }
                ),
                "Not Assigned + Brother Ministering Only",
            ]
        ),
        html.Div(
            [
                html.Span(
                    style={
                        "backgroundColor": "pink",
                        "display": "inline-block",
                        "width": "12px",
                        "height": "12px",
                        "marginRight": "6px",
                    }
                ),
                "Assigned + No Ministering",
            ]
        ),
        html.Div(
            [
                html.Span(
                    style={
                        "backgroundColor": "orange",
                        "display": "inline-block",
                        "width": "12px",
                        "height": "12px",
                        "marginRight": "6px",
                    }
                ),
                "Not Assigned + Sister Ministering Only",
            ]
        ),
        html.Div(
            [
                html.Span(
                    style={
                        "backgroundColor": "red",
                        "display": "inline-block",
                        "width": "12px",
                        "height": "12px",
                        "marginRight": "6px",
                    }
                ),
                "Not Assigned + No Ministering",
            ]
        ),
        html.Div(
            [
                html.Span(
                    style={
                        "backgroundColor": "lightgray",
                        "display": "inline-block",
                        "width": "12px",
                        "height": "12px",
                        "marginRight": "6px",
                    }
                ),
                "Other / Unknown",
            ]
        ),
    ],
    style={
        "position": "absolute",
        "bottom": "20px",
        "right": "20px",
        "zIndex": "1000",
        "background": "white",
        "padding": "10px",
        "border": "2px solid gray",
        "borderRadius": "5px",
        "boxShadow": "2px 2px 6px rgba(0,0,0,0.3)",
    },
)
layout = [
    html.H1(
        "Hurricane Evacuation Zones",
        style={
            "textAlign": "center",
            "color": "rgb(0, 128, 255)",
            "backgroundColor": "black",
            "fontSize": 50,
            "fontWeight": "bold",
        },
    ),
    html.Div(
        [
            dcc.Dropdown(
                id="risk-filter",
                options=[
                    {"label": r, "value": r}
                    for r in ["Severe", "Elevated", "Moderate", "Low", "Very Low"]
                ],
                value=[],
                multi=True,
                placeholder="Filter by Flood Risk",
            ),
            dl.Map(
                center=[26.14, -81.79],
                zoom=10,
                zoomControl=False,
                children=[
                    dl.TileLayer(),
                    dl.ZoomControl(position="topright"),
                    dl.LayerGroup(flood_layers, id="flood-layer"),
                    dl.LayerGroup(household_markers, id="household-layer"),
                    legend,
                ],
                style={"width": "100%", "height": "600px"},
            ),
            dash_table.DataTable(
                # id is defined below in the callback,
                # my_table is the same as the table:
                # avg_perc_mode.to_dict('records') returned by the function
                id="final_table",
                # columns as they appear in the app table are name,
                # id is from the dataframe, and type is the datatype of the column
                columns=[
                    {"name": "Name", "id": "Name", "type": "text"},
                    {"name": "Phone", "id": "Phone", "type": "text"},
                    {
                        "name": "Street Address 1",
                        "id": "Street Address 1",
                        "type": "text",
                    },
                    {"name": "Address 2", "id": "Address 2", "type": "text"},
                    {
                        "name": "Brothers Ministering to You",
                        "id": "Brothers Ministering to You",
                    },
                    {
                        "name": "Sisters Ministering to You",
                        "id": "Sisters Ministering to You",
                    },
                    {"name": "zone", "id": "zone", "type": "text"},
                ],
                # allows filtering columns in the datatable
                page_action="none",
                export_format="xlsx",
                # sort by column
                sort_action="native",
                # Allows to sort by multiple columns
                sort_mode="multi",
                # Paging front-end
                virtualization=False,
                # center text in cells
                style_cell_conditional=[{"textAlign": "center"}],
                # Styling the cells in the datatable
                style_data={"color": "white", "backgroundColor": "rgb(32,32,32)"},
                # setting the padding of the cell
                # to 5 pixels
                style_cell={"padding": "5px"},
                # Defining a dictionary named `style_header`
                # which contains CSS style properties for a header element.
                # The properties include a background color of dark gray,
                # white text color, and bold font weight.
                style_header={
                    "backgroundColor": "rgb(32,32,32)",
                    "color": "white",
                    "fontWeight": "bold",
                },
                style_data_conditional=(
                    [
                        {
                            "if": {
                                "filter_query": "{zone} = 'Zone A'",
                                "column_id": "zone",
                            },
                            "color": "#FD0707",
                        },
                        {
                            "if": {
                                "filter_query": "{zone} = 'Zone B'",
                                "column_id": "zone",
                            },
                            "color": "#F55E06",
                        },
                        {
                            "if": {
                                "filter_query": "{zone} = 'Zone C'",
                                "column_id": "zone",
                            },
                            "color": "#F9C74F",
                        },
                        {
                            "if": {
                                "filter_query": "{zone} = 'Zone D'",
                                "column_id": "zone",
                            },
                            "color": "#90BE6D",
                        },
                        {
                            "if": {
                                "filter_query": "{zone} = 'Zone E'",
                                "column_id": "zone",
                            },
                            "color": "#43AA8B",
                            "if": {
                                "filter_query": "{zone} = 'Outside Flood Zones'",
                                "column_id": "zone",
                            },
                            "color": "#787A7A",
                        },
                    ]
                ),
            ),
        ]
    ),
]


# --- Callback to update markers based on dropdown ---
@callback(
    Output("household-layer", "children"),
    Output("final_table", "data"),
    Input("risk-filter", "value"),
)
def update_markers(selected_risks):
    if not selected_risks:
        filtered = households  # no filter applied
    else:
        filtered = [h for h in households if h["risk"] in selected_risks]

    # Ensure all dict values are strings (or plain types)
    table_data = [
        {
            "Name": h.get("Name", ""),
            "Phone": h.get("Phone", ""),
            "Street Address 1": h.get("Street Address 1", ""),
            "Address 2": h.get("Address 2", ""),
            "Brothers Ministering to You": h.get("Brothers Ministering to You"),
            "Sisters Ministering to You": h.get("Sisters Ministering to You"),
            "zone": h.get("zone", ""),
        }
        for h in filtered
    ]

    return [
        dl.CircleMarker(
            center=(h["lat"], h["lon"]),
            radius=6,
            color="black",
            fillColor=h.get("color_coding_ministering", "lightgray"),
            fillOpacity=0.7,
            children=dl.Popup(
                [
                    html.B(h["Name"]),
                    html.Br(),
                    h["Phone"],
                    html.Br(),
                    h["Street Address 1"],
                    html.Br(),
                    h["Address 2"],
                    html.Br(),
                    h["Brothers Ministering to You"],
                    html.Br(),
                    h["Sisters Ministering to You"],
                    html.Br(),
                    f"Flood Zone: {h['zone']}",
                ]
            ),
        )
        for h in filtered
    ], table_data
