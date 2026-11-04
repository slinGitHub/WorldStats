"""Erzeugt eine Choroplethen-Weltkarte und legt den Jekyll-Post dazu an.

Aufruf:
    python weltkarte_lebenserwartung.py              # Post-Datum = heute (UTC)
    python weltkarte_lebenserwartung.py 2026-11-04   # festes Post-Datum
"""
import datetime as dt
import json
import sys
import webbrowser
from pathlib import Path

import folium
import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------
SLUG = "lebenserwartung"                      # Dateiname der Karte / des Posts
TITLE = "Lebenserwartung Männer weltweit"     # Titel des Posts
DESCRIPTION = "Durchschnittliche Lebenserwartung von Männern nach Ländern."  # Untertitel/Kachel-Text
VALUE_LABEL = "Lebenserwartung Männer"        # Tooltip-Beschriftung
LEGEND = "Durchschnittliche Lebenserwartung für Männer (Jahre)"
CSV_FILE = None   # z. B. "daten/lebenserwartung.csv" (Spalten: Country_Code, Wert)
OPEN_BROWSER = True

GEOJSON_URL = (
    "https://raw.githubusercontent.com/python-visualization/folium/"
    "main/examples/data/world-countries.json"
)

ROOT = Path(__file__).resolve().parent
MAP_FILE = ROOT / "maps" / f"{SLUG}.html"
POSTS_DIR = ROOT / "_posts"

# ---------------------------------------------------------------------------
# 1. Daten (ISO-3 Ländercode + Wert)
# ---------------------------------------------------------------------------
if CSV_FILE:
    df = pd.read_csv(ROOT / CSV_FILE).iloc[:, :2]
    df.columns = ["Country_Code", "Wert"]
else:
    # Platzhalter-Daten: vor der Veröffentlichung durch echte Daten ersetzen!
    df = pd.DataFrame(
        {
            "Country_Code": ["DEU", "USA", "FRA", "CHN", "IND", "BRA", "ZAF", "JPN", "CAN", "AUS"],
            "Wert": [78.5, 76.3, 79.2, 75.0, 68.2, 72.8, 62.1, 81.5, 80.2, 81.3],
        }
    )
df["Wert"] = df["Wert"].round(1)

# ---------------------------------------------------------------------------
# 2. GeoJSON laden und Tooltip-Werte eintragen (vor folium.Choropleth!)
# ---------------------------------------------------------------------------
response = requests.get(GEOJSON_URL, timeout=15)
response.raise_for_status()
geojson_data = response.json()

values = df.set_index("Country_Code")["Wert"].to_dict()
for feature in geojson_data["features"]:
    value = values.get(feature["id"])
    feature["properties"]["wert"] = f"{value:.1f}" if value is not None else "Keine Daten"

# ---------------------------------------------------------------------------
# 3. Karte
# ---------------------------------------------------------------------------
world_map = folium.Map(
    location=[20, 0],
    zoom_start=2,
    min_zoom=2,
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/"
    "World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",
    attr="Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ",
)

choropleth = folium.Choropleth(
    geo_data=geojson_data,
    name=VALUE_LABEL,
    data=df,
    columns=["Country_Code", "Wert"],
    key_on="feature.id",
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    nan_fill_color="lightgray",
    legend_name=LEGEND,
    highlight=True,
).add_to(world_map)

choropleth.geojson.add_child(
    folium.GeoJsonTooltip(
        fields=["name", "wert"],
        aliases=["Land:", f"{VALUE_LABEL}:"],
        style="background-color: white; color: #333333; font-family: arial; "
        "font-size: 12px; padding: 10px;",
    )
)

MAP_FILE.parent.mkdir(exist_ok=True)
world_map.save(str(MAP_FILE))
print(f"Karte gespeichert: {MAP_FILE}")

# ---------------------------------------------------------------------------
# 4. Jekyll-Post anlegen (nur wenn für diesen SLUG noch keiner existiert)
# ---------------------------------------------------------------------------
POSTS_DIR.mkdir(exist_ok=True)
if any(POSTS_DIR.glob(f"*-{SLUG}.md")):
    print("Post existiert bereits, wird nicht überschrieben.")
else:
    post_date = sys.argv[1] if len(sys.argv) > 1 else dt.datetime.now(dt.timezone.utc).date().isoformat()
    post_file = POSTS_DIR / f"{post_date}-{SLUG}.md"
    post_file.write_text(
        "---\n"
        "layout: post\n"
        f"title: {json.dumps(TITLE, ensure_ascii=False)}\n"
        f"description: {json.dumps(DESCRIPTION, ensure_ascii=False)}\n"
        f"map: {SLUG}\n"
        "---\n",
        encoding="utf-8",
    )
    print(f"Post angelegt: {post_file}")

if OPEN_BROWSER:
    try:
        webbrowser.open(MAP_FILE.as_uri())
    except Exception as exc:
        print(f"Browser konnte nicht geöffnet werden: {exc}")
