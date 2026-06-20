import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .dijkstra import dijkstra


class GraphError(ValueError):
    pass


@dataclass(frozen=True)
class Node:
    id: str
    name: str
    lat: float
    lng: float
    category: str = "place"
    official_map_no: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "lat": self.lat,
            "lng": self.lng,
            "category": self.category,
            "official_map_no": self.official_map_no,
        }


@dataclass(frozen=True)
class Edge:
    from_id: str
    to_id: str
    distance_m: float
    walk_factor: float = 1.0
    label: str = ""
    bidirectional: bool = True

    def cost_minutes(self, speed_m_per_min: float) -> float:
        return (self.distance_m / speed_m_per_min) * self.walk_factor

    def to_dict(self) -> dict[str, Any]:
        return {
            "from": self.from_id,
            "to": self.to_id,
            "distance_m": round(self.distance_m, 1),
            "walk_factor": self.walk_factor,
            "label": self.label,
            "bidirectional": self.bidirectional,
        }


class CampusGraph:
    def __init__(self, metadata: dict[str, Any], nodes: dict[str, Node], edges: list[Edge]):
        self.metadata = metadata
        self.nodes = nodes
        self.edges = edges
        self.speed_profiles = metadata.get(
            "speed_profiles",
            {
                "walk": {"label": "Walk", "speed_m_per_min": 80},
                "fast_walk": {"label": "Fast walk", "speed_m_per_min": 95},
                "cycle": {"label": "Cycle", "speed_m_per_min": 180},
            },
        )

        self._adjacency = self._build_adjacency()
        self._edge_lookup = self._build_edge_lookup()

    @classmethod
    def from_json(cls, path: str | Path):
        path = Path(path)
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        nodes = {}
        for raw in payload.get("nodes", []):
            node = Node(
                id=raw["id"],
                name=raw["name"],
                lat=float(raw["lat"]),
                lng=float(raw["lng"]),
                category=raw.get("category", "place"),
                official_map_no=raw.get("official_map_no"),
            )
            if node.id in nodes:
                raise GraphError(f"Duplicate node id: {node.id}")
            nodes[node.id] = node

        if not nodes:
            raise GraphError("Graph must contain at least one node")

        edges = []
        for raw in payload.get("edges", []):
            from_id = raw["from"]
            to_id = raw["to"]

            if from_id not in nodes or to_id not in nodes:
                raise GraphError(f"Edge references missing node: {from_id} -> {to_id}")

            distance_m = float(raw.get("distance_m") or haversine_m(nodes[from_id], nodes[to_id]))
            edges.append(
                Edge(
                    from_id=from_id,
                    to_id=to_id,
                    distance_m=distance_m,
                    walk_factor=float(raw.get("walk_factor", 1.0)),
                    label=raw.get("label", ""),
                    bidirectional=bool(raw.get("bidirectional", True)),
                )
            )

        if not edges:
            raise GraphError("Graph must contain at least one edge")

        return cls(metadata=payload.get("metadata", {}), nodes=nodes, edges=edges)

    def shortest_path(self, source: str, target: str, profile: str = "walk") -> dict[str, Any]:
        if source not in self.nodes:
            raise GraphError(f"Unknown source: {source}")
        if target not in self.nodes:
            raise GraphError(f"Unknown destination: {target}")
        if source == target:
            raise GraphError("Source and destination must be different")
        if profile not in self.speed_profiles:
            raise GraphError(f"Unknown speed profile: {profile}")

        speed = float(self.speed_profiles[profile]["speed_m_per_min"])
        weighted_adjacency = {
            node_id: [
                {
                    "to": item["to"],
                    "weight": item["edge"].cost_minutes(speed),
                    "distance_m": item["edge"].distance_m,
                    "label": item["edge"].label,
                }
                for item in neighbors
            ]
            for node_id, neighbors in self._adjacency.items()
        }

        route = dijkstra(set(self.nodes), weighted_adjacency, source, target)
        path_ids = route["path"]
        route_edges = self._route_edges(path_ids, speed)
        coordinates = [[self.nodes[node_id].lat, self.nodes[node_id].lng] for node_id in path_ids]
        total_distance = sum(edge["distance_m"] for edge in route_edges)
        total_time = sum(edge["time_min"] for edge in route_edges)

        return {
            "source": self.nodes[source].to_dict(),
            "target": self.nodes[target].to_dict(),
            "profile": profile,
            "profile_label": self.speed_profiles[profile].get("label", profile),
            "path": [self.nodes[node_id].to_dict() for node_id in path_ids],
            "path_ids": path_ids,
            "coordinates": coordinates,
            "edges": route_edges,
            "total_distance_m": round(total_distance, 1),
            "total_time_min": round(total_time, 2),
            "visited_order": [
                {"id": node_id, "name": self.nodes[node_id].name}
                for node_id in route["visited_order"]
            ],
            "distance_table": [
                {
                    "id": node_id,
                    "name": self.nodes[node_id].name,
                    "time_min": None if math.isinf(distance) else round(distance, 2),
                    "previous": route["previous"].get(node_id),
                    "previous_name": (
                        self.nodes[route["previous"][node_id]].name
                        if node_id in route["previous"]
                        else None
                    ),
                }
                for node_id, distance in sorted(route["distances"].items())
            ],
            "trace": [
                {
                    "current": step["current"],
                    "current_name": self.nodes[step["current"]].name,
                    "settled_time_min": round(step["settled_weight"], 2),
                    "relaxations": [
                        {
                            "from": item["from"],
                            "from_name": self.nodes[item["from"]].name,
                            "to": item["to"],
                            "to_name": self.nodes[item["to"]].name,
                            "old_time_min": (
                                None
                                if math.isinf(item["old_weight"])
                                else round(item["old_weight"], 2)
                            ),
                            "new_time_min": round(item["new_weight"], 2),
                        }
                        for item in step["relaxations"]
                    ],
                }
                for step in route["trace"]
            ],
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": self.metadata,
            "speed_profiles": self.speed_profiles,
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": self._edge_lines(),
        }

    def _build_adjacency(self):
        adjacency = {node_id: [] for node_id in self.nodes}
        for edge in self.edges:
            adjacency[edge.from_id].append({"to": edge.to_id, "edge": edge})
            if edge.bidirectional:
                reverse = Edge(
                    from_id=edge.to_id,
                    to_id=edge.from_id,
                    distance_m=edge.distance_m,
                    walk_factor=edge.walk_factor,
                    label=edge.label,
                    bidirectional=edge.bidirectional,
                )
                adjacency[edge.to_id].append({"to": edge.from_id, "edge": reverse})
        return adjacency

    def _build_edge_lookup(self):
        lookup = {}
        for edge in self.edges:
            lookup[(edge.from_id, edge.to_id)] = edge
            if edge.bidirectional:
                lookup[(edge.to_id, edge.from_id)] = Edge(
                    from_id=edge.to_id,
                    to_id=edge.from_id,
                    distance_m=edge.distance_m,
                    walk_factor=edge.walk_factor,
                    label=edge.label,
                    bidirectional=edge.bidirectional,
                )
        return lookup

    def _route_edges(self, path_ids: list[str], speed_m_per_min: float) -> list[dict[str, Any]]:
        route_edges = []
        for from_id, to_id in zip(path_ids, path_ids[1:]):
            edge = self._edge_lookup[(from_id, to_id)]
            route_edges.append(
                {
                    "from": from_id,
                    "from_name": self.nodes[from_id].name,
                    "to": to_id,
                    "to_name": self.nodes[to_id].name,
                    "distance_m": round(edge.distance_m, 1),
                    "time_min": round(edge.cost_minutes(speed_m_per_min), 2),
                    "label": edge.label,
                }
            )
        return route_edges

    def _edge_lines(self) -> list[dict[str, Any]]:
        lines = []
        for edge in self.edges:
            start = self.nodes[edge.from_id]
            end = self.nodes[edge.to_id]
            payload = edge.to_dict()
            payload["coordinates"] = [[start.lat, start.lng], [end.lat, end.lng]]
            lines.append(payload)
        return lines


def haversine_m(first: Node, second: Node) -> float:
    radius_m = 6_371_000
    lat1 = math.radians(first.lat)
    lat2 = math.radians(second.lat)
    delta_lat = math.radians(second.lat - first.lat)
    delta_lng = math.radians(second.lng - first.lng)

    hav = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lng / 2) ** 2
    )
    return 2 * radius_m * math.atan2(math.sqrt(hav), math.sqrt(1 - hav))
