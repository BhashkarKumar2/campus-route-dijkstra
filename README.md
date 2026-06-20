# Campus Route Finder with Dijkstra

Python web app for finding the shortest-time route between DTU campus locations. It uses OpenStreetMap tiles for the map and a local campus graph for routing, so the Dijkstra algorithm is visible and testable.

The bundled sample is centered on Delhi Technological University and the map is locked to the DTU campus bounding box.

Official DTU campus map reference: `app/static/img/dtu-official-campus-map.png`, extracted from DTU Annual Report 2023-24 page 2.

## Features

- Flask backend with a readable Dijkstra implementation in `app/dijkstra.py`.
- Edge costs are computed from node latitude/longitude using the haversine formula.
- Walking, fast-walking, and cycling speed profiles.
- Leaflet map with OpenStreetMap tiles and visible attribution.
- Map panning is constrained to the DTU campus area.
- Official DTU campus map reference is shown inside the app.
- Marker popups show official DTU campus map numbers where a location can be matched confidently.
- Route summary with time, distance, stops, and per-edge steps.
- Dijkstra trace showing settled nodes and relaxed distances.
- Node Builder for collecting coordinates from map clicks.
- Render, Vercel, and Procfile deployment metadata.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
python wsgi.py
```

Open `http://127.0.0.1:5000`.

## Test

```powershell
pytest
```

## Customize DTU nodes

Edit `data/campus_graph.json`.

Each node needs:

```json
{
  "id": "library",
  "name": "Central Library",
  "lat": 28.7506425,
  "lng": 77.1165275,
  "category": "academic"
}
```

Each edge connects two nodes:

```json
{
  "from": "main_gate",
  "to": "library",
  "label": "Main walkway",
  "walk_factor": 1.0
}
```

If `distance_m` is omitted, the app computes distance from coordinates. Increase `walk_factor` for crowded, steep, or slow paths.

Use the Node Builder pin button in the UI and click on the map to collect coordinates inside DTU.

## Map data freshness

The app uses live OpenStreetMap tiles, but the campus graph is local JSON so the Dijkstra demo remains deterministic.

Latest map audit:

- Checked Overpass OSM database snapshot: `2026-06-20T15:22:58Z`.
- DTU campus OSM way: `111212532`.
- DTU campus OSM way version: `23`.
- DTU campus OSM way last edited: `2024-07-22T15:42:07Z`.
- Changeset: `154269396`.

This means the OpenStreetMap service queried by the project was current on June 20, 2026, but the main DTU campus boundary feature itself has not been edited since July 22, 2024. If some buildings, paths, or labels look old, update those OpenStreetMap features or adjust `data/campus_graph.json` manually for the project demo.

Official DTU map source:

- DTU Annual Report 2023-24, page 2: https://iqac.dtu.ac.in/ar/pdf/ar23-24_english.pdf
- DTU website Campus Map page: https://dtu.ac.in/Web/About/campusmap.php

## Dijkstra explanation

The algorithm keeps three main structures:

- `distances`: best known time from the source to each node.
- `previous`: predecessor map used to reconstruct the route.
- `heap`: priority queue that always selects the unsettled node with the smallest known time.

For every selected node, the algorithm relaxes its outgoing edges. A relaxation updates a neighbor when the new route time is smaller than its current best known time. When the destination is settled, the shortest-time path is complete.

## Deployment

Render:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn wsgi:app`
- `render.yaml` is included.

Vercel:

- `api/index.py` and `vercel.json` are included for a serverless Flask deployment.
- Keep the graph file read-only in production. Make graph edits locally and redeploy.

## Free map services used

- Leaflet: browser map rendering. See https://leafletjs.com/examples/quick-start/
- OpenStreetMap public tile server: map tiles for a small student demo. See https://operations.osmfoundation.org/policies/tiles/
- Overpass API: used once to seed the sample DTU coordinates. See https://wiki.openstreetmap.org/wiki/Overpass_API
- OSM API: used to audit the DTU campus way metadata. See https://api.openstreetmap.org/api/0.6/way/111212532.json
- DTU official annual report: used as the campus-map label reference. See https://iqac.dtu.ac.in/ar/pdf/ar23-24_english.pdf

For production or heavy usage, use a hosted map provider plan or self-host the relevant OpenStreetMap services. Public OpenStreetMap services have usage policies and attribution requirements.
