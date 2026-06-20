import json
import os
import time
from functools import lru_cache
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class NominatimError(RuntimeError):
    pass


_last_request_at = 0.0


def search_places(query: str, limit: int = 5) -> list[dict]:
    normalized = " ".join(query.split())
    if not normalized:
        return []
    return list(_search_places_cached(normalized, limit))


@lru_cache(maxsize=128)
def _search_places_cached(query: str, limit: int) -> tuple[dict, ...]:
    global _last_request_at

    elapsed = time.monotonic() - _last_request_at
    if elapsed < 1.1:
        time.sleep(1.1 - elapsed)

    params = urlencode(
        {
            "format": "jsonv2",
            "q": query,
            "limit": max(1, min(limit, 10)),
            "addressdetails": 1,
        }
    )
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    user_agent = os.getenv(
        "NOMINATIM_USER_AGENT",
        "CampusRouteDijkstra/1.0 student-project local-demo",
    )

    request = Request(url, headers={"User-Agent": user_agent})

    try:
        with urlopen(request, timeout=8) as response:
            _last_request_at = time.monotonic()
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise NominatimError("Map search is temporarily unavailable") from exc

    results = []
    for item in payload:
        results.append(
            {
                "name": item.get("name") or item.get("display_name", "").split(",")[0],
                "display_name": item.get("display_name"),
                "lat": float(item["lat"]),
                "lng": float(item["lon"]),
                "category": item.get("category"),
                "type": item.get("type"),
            }
        )

    return tuple(results)
