import dash
from dash import html, dcc, Output, Input, callback, dash_table
import dash_leaflet as dl
import pandas as pd
from shapely.geometry import Point, Polygon
from naples_ward.dnc_moved_list import dnc_moved_list
import time
from pathlib import Path
import re
import os
from dash import register_page
import random
import numpy as np
from districts_by_geography import district_zones

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
df_clean_hoh = df_clean[
    (df_clean["HOH"] == True) | (df_clean["Available to Minister"] == True)
].copy()


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


# --- Haversine function ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def color_coding(row):
    if row["Available to Minister"] != True:
        return "lightgray"  # Non-ministers always gray
    if row["Gender"] == "F":
        return "pink"
    if row["Gender"] == "M":
        return "blue"
    return "lightgray"


def jitter(lat, lon, amount=0.0003):
    """Return jittered lat/lon to avoid overlapping markers."""
    return lat + random.uniform(-amount, amount), lon + random.uniform(-amount, amount)


df_clean_hoh["color_coding_ministering"] = df_clean_hoh.apply(color_coding, axis=1)
df_clean_hoh_filtered = (
    df_clean_hoh[
        [
            "Name",
            "HOH",
            "Priesthood",
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
            "Available to Minister",
            "EQ Ministering District By Geography",
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
# Initialize new columns with NaN

print(f"Row count (heads of household only): {df_clean_hoh.shape[0]}")
df_clean_hoh_filtered["first_closest"] = np.nan
df_clean_hoh_filtered["second_closest"] = np.nan
df_clean_hoh_filtered["third_closest"] = np.nan
df_clean_hoh_filtered["fourth_closest"] = np.nan
df_clean_hoh_filtered["fifth_closest"] = np.nan

for idx, m in df_clean_hoh_filtered.iterrows():
    if m["Available to Minister"] != True:
        continue  # skip calculations for non-ministers
    if (m["Gender"] == "M") and (m["Priesthood"] not in (["Elder", "High Priest"])):
        # Pool of available melkezedek priesthood holder ministers for non-melkezedek priesthood holders
        pool = df_clean_hoh_filtered[
            (df_clean_hoh_filtered["Available to Minister"] == True)
            & (df_clean_hoh_filtered["Gender"] == m["Gender"])
            & (df_clean_hoh_filtered["Name"] != m["Name"])
            & (df_clean_hoh_filtered["Priesthood"].isin(["Elder", "High Priest"]))
        ].copy()
    else:
        # Pool of available ministers of the same gender, excluding self
        pool = df_clean_hoh_filtered[
            (df_clean_hoh_filtered["Available to Minister"] == True)
            & (df_clean_hoh_filtered["Gender"] == m["Gender"])
            & (df_clean_hoh_filtered["Name"] != m["Name"])
        ].copy()

    if pool.empty:
        continue  # leave NaN

    # Compute distances
    pool["distance"] = haversine(
        m["Latitude"], m["Longitude"], pool["Latitude"], pool["Longitude"]
    )
    closest = pool.nsmallest(10, "distance")

    # Fill up with NaN if fewer than 3
    names = list(closest["Name"])
    while len(names) < 10:
        names.append(np.nan)

    # Assign directly to df_ministers
    df_clean_hoh_filtered.at[idx, "first_closest"] = names[0]
    df_clean_hoh_filtered.at[idx, "second_closest"] = names[1]
    df_clean_hoh_filtered.at[idx, "third_closest"] = names[2]
    df_clean_hoh_filtered.at[idx, "fourth_closest"] = names[3]
    df_clean_hoh_filtered.at[idx, "fifth_closest"] = names[4]
    df_clean_hoh_filtered.at[idx, "sixth_closest"] = names[5]
    df_clean_hoh_filtered.at[idx, "seventh_closest"] = names[6]
    df_clean_hoh_filtered.at[idx, "eighth_closest"] = names[7]
    df_clean_hoh_filtered.at[idx, "ninth_closest"] = names[8]
    df_clean_hoh_filtered.at[idx, "tenth_closest"] = names[9]

# 1. Define all closest columns
closest_cols = [
    "first_closest",
    "second_closest",
    "third_closest",
    "fourth_closest",
    "fifth_closest",
    "sixth_closest",
    "seventh_closest",
    "eighth_closest",
    "ninth_closest",
    "tenth_closest",
]

# 2. Stack all closest households into one column
all_closest = df_clean_hoh_filtered[closest_cols].melt(value_name="Closest_Household")
all_closest = all_closest.dropna(subset=["Closest_Household"])

# 3. Count appearances
appearance_counts = all_closest["Closest_Household"].value_counts()

# 4. Append counts back into each closest column
for col in closest_cols:
    df_clean_hoh_filtered[col] = df_clean_hoh_filtered[col].apply(
        lambda x: f"{x} ({appearance_counts.get(x, 0)})" if pd.notnull(x) else x
    )


# Initialize new columns
for i in range(1, 11):
    df_clean_hoh_filtered[f"closest_household_{i}"] = np.nan
for idx, m in df_clean_hoh_filtered.iterrows():
    if m["Available to Minister"] != True:
        continue  # skip non-ministers

    # Define the pool according to gender rules
    if m["Gender"] == "M":
        # Men can be assigned to anyone except themselves
        pool = df_clean_hoh_filtered[
            (df_clean_hoh_filtered["Name"] != m["Name"])
            & (df_clean_hoh_filtered["HOH"] == True)
        ].copy()
    else:
        # Women can only be assigned to women except themselves
        pool = df_clean_hoh_filtered[
            (df_clean_hoh_filtered["Gender"] == "F")
            & (df_clean_hoh_filtered["Name"] != m["Name"])
        ].copy()

    if pool.empty:
        continue  # leave NaN if no eligible person

    # Compute distances
    pool["distance"] = haversine(
        m["Latitude"], m["Longitude"], pool["Latitude"], pool["Longitude"]
    )

    # Get up to 20 closest
    closest = pool.nsmallest(30, "distance")["Name"].tolist()

    # Fill with NaN if fewer than 20
    while len(closest) < 30:
        closest.append(np.nan)

    # Assign to dataframe
    for i in range(30):
        df_clean_hoh_filtered.at[idx, f"closest_household_{i + 1}"] = closest[i]

# -------------------------------------------------------------------
# NEW: Count appearances across all top-30 lists and append (n)
# -------------------------------------------------------------------
closest_cols = [f"closest_household_{i}" for i in range(1, 31)]

# Long-format for counting
all_closest = df_clean_hoh_filtered.melt(
    id_vars=["Name"], value_vars=closest_cols, value_name="Closest_Household"
).dropna(subset=["Closest_Household"])

print(all_closest)
# Count how many times each household shows up globally
appearance_counts = all_closest["Closest_Household"].value_counts()

# Append (count) next to each household name
for col in closest_cols:
    df_clean_hoh_filtered[col] = df_clean_hoh_filtered[col].apply(
        lambda x: f"{x} ({appearance_counts.get(x, 0)})" if pd.notna(x) else x
    )


# Household markers
household_markers = [
    dl.CircleMarker(
        center=jitter(row["Latitude"], row["Longitude"]),
        radius=6,
        color="black",
        fillColor=row["color_coding_ministering"],
        fillOpacity=0.7,
        children=dl.Popup(
            [
                html.B(row["Name"]),
                html.Br(),
            ]
        ),
    )
    for _, row in df_clean_hoh_filtered.iterrows()
]
gender_map = {"M": "EQ", "F": "RS"}
legend = html.Div(
    children=[
        html.Div(
            "Household Assignment", style={"fontWeight": "bold", "marginBottom": "5px"}
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
                "Sister Available to Minister",
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
                "Brother Available to Minister",
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
                "Not Available to Minister",
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

# district zones polygons as layers
district_layers = [
    dl.Polygon(
        positions=[[lat, lon] for lon, lat in zone["polygons"][0]],
        color=zone["color"],
        fillOpacity=0.3,
        children=dl.Popup([html.B(zone["name"])]),
    )
    for zone in district_zones.values()
]

district_legend = html.Div(
    children=[
        html.Div(
            "Geographical Districts",
            style={"fontWeight": "bold", "marginBottom": "5px"},
        )
    ]
    + [
        html.Div(
            [
                html.Span(
                    style={
                        "backgroundColor": color,
                        "display": "inline-block",
                        "width": "12px",
                        "height": "12px",
                        "marginRight": "6px",
                    }
                ),
                district,
            ]
        )
        for district, color in {
            "1": "#F9C74F",
            "2": "#90BE6D",
            "3": "#43AA8B",
        }.items()
    ],
    style={
        "position": "absolute",
        "bottom": "20px",
        "left": "20px",  # place on opposite side of your existing legend
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
        "Naples Ministering Availability",
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
                id="ministering-availability-district-filter",
                options=[
                    {"label": r, "value": r}
                    for r in sorted(
                        df["EQ Ministering District By Geography"].dropna().unique()
                    )
                ],
                value=[],
                multi=True,
                placeholder="Filter by Geographical District",
            ),
            # dcc.Dropdown(
            #     id="gender_filter",
            #     options=[{"label": gender_map[r], "value": r} for r in sorted(df["Gender"].dropna().unique())],
            #     value=[],
            #     multi=True,
            #     placeholder="Filter by Elders or Sisters"
            # ),
            dl.Map(
                center=[26.14, -81.79],
                zoom=10,
                zoomControl=False,
                children=[
                    dl.TileLayer(),
                    dl.ZoomControl(position="topright"),
                    dl.LayerGroup(
                        household_markers, id="ministering-for-household-layer"
                    ),
                    dl.LayerGroup(district_layers),
                    legend,
                    district_legend,
                ],
                style={"width": "100%", "height": "600px"},
            ),
            dash_table.DataTable(
                # id is defined below in the callback,
                # my_table is the same as the table:
                # avg_perc_mode.to_dict('records') returned by the function
                id="final_ministering_table",
                # columns as they appear in the app table are name,
                # id is from the dataframe, and type is the datatype of the column
                columns=[
                    {"name": "Name", "id": "Name", "type": "text"},
                    {"name": "Gender", "id": "Gender"},
                    {"name": "Phone", "id": "Individual Phone", "type": "text"},
                    {
                        "name": "Street Address 1",
                        "id": "Street Address 1",
                        "type": "text",
                    },
                    {"name": "Address 2", "id": "Address 2", "type": "text"},
                    {"name": "zip", "id": "zip"},
                    {
                        "name": "District By Geo",
                        "id": "EQ Ministering District By Geography",
                    },
                    {"name": "1st Avail. Companion", "id": "first_closest"},
                    {"name": "2nd Avail. Companion", "id": "second_closest"},
                    {"name": "3rd Avail. Companion", "id": "third_closest"},
                    {"name": "4th Avail. Companion", "id": "fourth_closest"},
                    {"name": "5th Avail. Companion", "id": "fifth_closest"},
                    {"name": "6th Avail. Companion", "id": "sixth_closest"},
                    {"name": "7th Avail. Companion", "id": "seventh_closest"},
                    {"name": "8th Avail. Companion", "id": "eighth_closest"},
                    {"name": "9th Avail. Companion", "id": "ninth_closest"},
                    {"name": "10th Avail. Companion", "id": "tenth_closest"},
                    {"name": "1st Closest Household", "id": "closest_household_1"},
                    {"name": "2nd Closest Household", "id": "closest_household_2"},
                    {"name": "3rd Closest Household", "id": "closest_household_3"},
                    {"name": "4th Closest Household", "id": "closest_household_4"},
                    {"name": "5th Closest Household", "id": "closest_household_5"},
                    {"name": "6th Closest Household", "id": "closest_household_6"},
                    {"name": "7th Closest Household", "id": "closest_household_7"},
                    {"name": "8th Closest Household", "id": "closest_household_8"},
                    {"name": "9th Closest Household", "id": "closest_household_9"},
                    {"name": "10th Closest Household", "id": "closest_household_10"},
                    {"name": "11th Closest Household", "id": "closest_household_11"},
                    {"name": "12th Closest Household", "id": "closest_household_12"},
                    {"name": "13th Closest Household", "id": "closest_household_13"},
                    {"name": "14th Closest Household", "id": "closest_household_14"},
                    {"name": "15th Closest Household", "id": "closest_household_15"},
                    {"name": "16th Closest Household", "id": "closest_household_16"},
                    {"name": "17th Closest Household", "id": "closest_household_17"},
                    {"name": "18th Closest Household", "id": "closest_household_18"},
                    {"name": "19th Closest Household", "id": "closest_household_19"},
                    {"name": "20th Closest Household", "id": "closest_household_20"},
                    {"name": "21st Closest Household", "id": "closest_household_21"},
                    {"name": "22nd Closest Household", "id": "closest_household_22"},
                    {"name": "23rd Closest Household", "id": "closest_household_23"},
                    {"name": "24th Closest Household", "id": "closest_household_24"},
                    {"name": "25th Closest Household", "id": "closest_household_25"},
                    {"name": "26th Closest Household", "id": "closest_household_26"},
                    {"name": "27th Closest Household", "id": "closest_household_27"},
                    {"name": "28th Closest Household", "id": "closest_household_28"},
                    {"name": "29th Closest Household", "id": "closest_household_29"},
                    {"name": "30th Closest Household", "id": "closest_household_30"},
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
    Output("ministering-for-household-layer", "children"),
    Output("final_ministering_table", "data"),
    Input("ministering-availability-district-filter", "value"),
    # Input("gender_filter", "value")
)
def update_markers(selected_district):
    filtered = df_clean_hoh_filtered.copy()

    # Apply district filter
    if selected_district:
        filtered = filtered[
            filtered["EQ Ministering District By Geography"].isin(selected_district)
        ]

    # Recompute colors for the filtered dataframe
    filtered["color_coding_ministering"] = filtered.apply(color_coding, axis=1)

    # Convert to list-of-dicts once
    records = filtered.to_dict(orient="records")

    # Marker list
    markers = [
        dl.CircleMarker(
            center=jitter(r["Latitude"], r["Longitude"]),
            radius=6,
            color="black",
            fillColor=r.get("color_coding_ministering", "lightgray"),
            fillOpacity=0.7,
            children=dl.Popup(
                [
                    html.Br(),
                    r.get("Name", ""),
                    html.Br(),
                    r.get("Gender", ""),
                    html.Br(),
                    r.get("Individual Phone", ""),
                    html.Br(),
                    r.get("Street Address 1", ""),
                    html.Br(),
                    r.get("Address 2", ""),
                    html.Br(),
                    r.get("zip", ""),
                    html.Br(),
                    r.get("EQ Ministering District By Geography", ""),
                    html.Br(),
                    r.get("Brothers Ministering to You", ""),
                    html.Br(),
                    r.get("first_closest", ""),
                    html.Br(),
                    r.get("second_closest", ""),
                    html.Br(),
                    r.get("third_closest", ""),
                    html.Br(),
                    r.get("fourth_closest", ""),
                    html.Br(),
                    r.get("fifth_closest", ""),
                    html.Br(),
                    r.get("sixth_closest", ""),
                    html.Br(),
                    r.get("seventh_closest", ""),
                    html.Br(),
                    r.get("eighth_closest", ""),
                    html.Br(),
                    r.get("ninth_closest", ""),
                    html.Br(),
                    r.get("tenth_closest", ""),
                    html.Br(),
                    r.get("closest_household_1", ""),
                    html.Br(),
                    r.get("closest_household_2", ""),
                    html.Br(),
                    r.get("closest_household_3", ""),
                    html.Br(),
                    r.get("closest_household_4", ""),
                    html.Br(),
                    r.get("closest_household_5", ""),
                    html.Br(),
                    r.get("closest_household_6", ""),
                    html.Br(),
                    r.get("closest_household_7", ""),
                    html.Br(),
                    r.get("closest_household_8", ""),
                    html.Br(),
                    r.get("closest_household_9", ""),
                    html.Br(),
                    r.get("closest_household_10", ""),
                    html.Br(),
                    r.get("closest_household_11", ""),
                    html.Br(),
                    r.get("closest_household_12", ""),
                    html.Br(),
                    r.get("closest_household_13", ""),
                    html.Br(),
                    r.get("closest_household_14", ""),
                    html.Br(),
                    r.get("closest_household_15", ""),
                    html.Br(),
                    r.get("closest_household_16", ""),
                    html.Br(),
                    r.get("closest_household_17", ""),
                    html.Br(),
                    r.get("closest_household_18", ""),
                    html.Br(),
                    r.get("closest_household_19", ""),
                    html.Br(),
                    r.get("closest_household_20", ""),
                    html.Br(),
                    r.get("closest_household_21", ""),
                    html.Br(),
                    r.get("closest_household_22", ""),
                    html.Br(),
                    r.get("closest_household_23", ""),
                    html.Br(),
                    r.get("closest_household_24", ""),
                    html.Br(),
                    r.get("closest_household_25", ""),
                    html.Br(),
                    r.get("closest_household_26", ""),
                    html.Br(),
                    r.get("closest_household_27", ""),
                    html.Br(),
                    r.get("closest_household_28", ""),
                    html.Br(),
                    r.get("closest_household_29", ""),
                    html.Br(),
                    r.get("closest_household_30", ""),
                ]
            ),
        )
        for r in records
    ]

    return markers, records
