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

register_page(__name__)
# --- Load household data ---
path = str(Path.home() / "Documents/church_stuff/dash_app")
os.chdir(path)

# --- Config ---
CSV_PATH = "naples_ward/Naples_Ward_Household_List_01_04_2026.csv"

# --- Read CSV ---
df = pd.read_csv(CSV_PATH, sep="^", header=0)

df_clean = df[
    df["Street Address 1"].notna() & (df["Street Address 1"].str.strip() != "")
]
df_clean = df_clean[df_clean["Street Address 1"].astype(str).str.strip() != ""]
df_clean["City"] = df_clean["City"].replace("", pd.NA)
df_clean["City"] = df_clean["City"].fillna("Naples")
# df_clean_hoh = df_clean[(df_clean['HOH'] =='TRUE') | (df_clean['HOH'] == '1') ].copy()
df_clean_hoh = df_clean[(df_clean["HOH"] == True)].copy()


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
    # assigned = ((row['Assignment to Minister'] in ('TRUE', '1')) and (row['Gender'] =="M"))
    assigned = (row["Assignment to Minister"] == True) and (row["Gender"] == "M")
    brother_ministers_to_you = row["Brothers Ministering to You"] not in (
        "",
        None,
    ) and not pd.isna(row["Brothers Ministering to You"])
    capable_to_minister = (row["Available to Minister"] == True) and (
        row["Gender"] == "M"
    )
    # sister_ministers_to_you = row['Sisters Ministering to You'] not in ('', None) and not pd.isna(row['Sisters Ministering to You'])

    if assigned and brother_ministers_to_you and capable_to_minister:
        return "green"
    elif assigned and not brother_ministers_to_you and capable_to_minister:
        return "blue"
    elif not assigned and brother_ministers_to_you and capable_to_minister:
        return "yellow"
    elif not assigned and not brother_ministers_to_you and capable_to_minister:
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
df_clean_hoh_filtered = df_clean_hoh_filtered[
    ~df_clean_hoh_filtered["Name"].isin(dnc_moved_list)
]
print(f"Row count (heads of household only): {df_clean_hoh.shape[0]}")

# Household markers
household_markers = [
    dl.CircleMarker(
        center=(row["Latitude"], row["Longitude"]),
        radius=6,
        color="black",
        fillColor=row["color_coding_ministering"],
        fillOpacity=0.7,
        children=[
            dl.Tooltip(row["Name"], permanent=True, direction="top"),
            dl.Popup(
                [
                    html.B(row["Name"]),
                    html.Br(),
                ]
            ),
        ],
    )
    for _, row in df_clean_hoh_filtered.iterrows()
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
                "Assigned + Brother Ministering to You",
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
                "Assigned + No Ministering to You",
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
                "Not Assigned + Brother Ministering to You",
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
                "Not Assigned + No Ministering to You",
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
        "Naples Elders Quorum Ministering",
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
                id="ministering-filter",
                options=[
                    {"label": r, "value": r}
                    for r in df["Brothers Ministering to You"].dropna().unique()
                ],
                value=[],
                multi=True,
                placeholder="Filter by Ministering Companionship",
            ),
            dl.Map(
                center=[26.14, -81.79],
                zoom=10,
                zoomControl=False,
                children=[
                    dl.TileLayer(),
                    dl.ZoomControl(position="topright"),
                    dl.LayerGroup(household_markers, id="ministering-household-layer"),
                    legend,
                ],
                style={"width": "100%", "height": "600px"},
            ),
            dash_table.DataTable(
                # id is defined below in the callback,
                # my_table is the same as the table:
                # avg_perc_mode.to_dict('records') returned by the function
                id="final_ministering_brethren_table",
                # columns as they appear in the app table are name,
                # id is from the dataframe, and type is the datatype of the column
                columns=[
                    {"name": "Name", "id": "Name", "type": "text"},
                    {"name": "Phone", "id": "Individual Phone", "type": "text"},
                    {
                        "name": "Street Address 1",
                        "id": "Street Address 1",
                        "type": "text",
                    },
                    {"name": "Address 2", "id": "Address 2", "type": "text"},
                    {"name": "zip", "id": "zip"},
                    {
                        "name": "Brothers Ministering to You",
                        "id": "Brothers Ministering to You",
                    },
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
            ),
        ]
    ),
]


# --- Callback to update markers based on dropdown ---
@callback(
    Output("ministering-household-layer", "children"),
    Output("final_ministering_brethren_table", "data"),
    Input("ministering-filter", "value"),
)
def update_markers(selected_companionships):
    # Filter dataframe
    if selected_companionships:
        filtered = df_clean_hoh_filtered[
            df_clean_hoh_filtered["Brothers Ministering to You"].isin(
                selected_companionships
            )
            | df_clean_hoh_filtered["Name"].isin(selected_companionships)
        ]
    else:
        filtered = df_clean_hoh_filtered

    # Convert to list-of-dicts once
    records = filtered.to_dict(orient="records")

    # Marker list
    markers = [
        dl.CircleMarker(
            center=(r["Latitude"], r["Longitude"]),
            radius=6,
            color="black",
            fillColor=r.get("color_coding_ministering", "lightgray"),
            fillOpacity=0.7,
            children=[
                dl.Tooltip(r["Name"], permanent=True, direction="top"),
                dl.Popup(
                    [
                        html.Br(),
                        r.get("Name", ""),
                        html.Br(),
                        r.get("Individual Phone", ""),
                        html.Br(),
                        r.get("Street Address 1", ""),
                        html.Br(),
                        r.get("Address 2", ""),
                        html.Br(),
                        r.get("zip", ""),
                        html.Br(),
                        r.get("Brothers Ministering to You", ""),
                    ]
                ),
            ],
        )
        for r in records
    ]

    return markers, records
