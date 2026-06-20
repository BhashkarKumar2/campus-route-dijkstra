import argparse
import json
import re
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "location"


def geocode(query: str) -> dict | None:
    params = urlencode({"format": "jsonv2", "q": query, "limit": 1})
    request = Request(
        f"https://nominatim.openstreetmap.org/search?{params}",
        headers={"User-Agent": "CampusRouteDijkstra/1.0 student-project geocoder"},
    )
    with urlopen(request, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if not payload:
        return None

    item = payload[0]
    name = item.get("name") or query
    return {
        "id": slugify(name),
        "name": name,
        "lat": float(item["lat"]),
        "lng": float(item["lon"]),
        "category": "place",
    }


def main():
    parser = argparse.ArgumentParser(description="Geocode campus places with Nominatim.")
    parser.add_argument("queries", nargs="+", help="Place names to geocode")
    args = parser.parse_args()

    nodes = []
    for index, query in enumerate(args.queries):
        result = geocode(query)
        if result:
            nodes.append(result)
        if index != len(args.queries) - 1:
            time.sleep(1.1)

    print(json.dumps(nodes, indent=2))


if __name__ == "__main__":
    main()
