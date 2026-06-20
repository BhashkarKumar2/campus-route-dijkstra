from heapq import heappop, heappush
from math import inf
from typing import Any


class NoPathError(ValueError):
    pass


def dijkstra(
    nodes: set[str],
    adjacency: dict[str, list[dict[str, Any]]],
    source: str,
    target: str,
) -> dict[str, Any]:
    distances = {node: inf for node in nodes}
    previous: dict[str, str] = {}
    visited: set[str] = set()
    visited_order: list[str] = []
    trace: list[dict[str, Any]] = []

    distances[source] = 0.0
    heap: list[tuple[float, str]] = [(0.0, source)]

    while heap:
        current_weight, current = heappop(heap)

        if current in visited:
            continue

        visited.add(current)
        visited_order.append(current)
        step = {
            "current": current,
            "settled_weight": current_weight,
            "relaxations": [],
        }

        if current == target:
            trace.append(step)
            break

        for edge in adjacency.get(current, []):
            neighbor = edge["to"]
            if neighbor in visited:
                continue

            candidate = current_weight + float(edge["weight"])
            if candidate < distances[neighbor]:
                old_weight = distances[neighbor]
                distances[neighbor] = candidate
                previous[neighbor] = current
                heappush(heap, (candidate, neighbor))
                step["relaxations"].append(
                    {
                        "from": current,
                        "to": neighbor,
                        "old_weight": old_weight,
                        "new_weight": candidate,
                    }
                )

        trace.append(step)

    if target not in visited:
        raise NoPathError(f"No route found from {source} to {target}")

    return {
        "path": reconstruct_path(previous, source, target),
        "distances": distances,
        "previous": previous,
        "visited_order": visited_order,
        "trace": trace,
    }


def reconstruct_path(previous: dict[str, str], source: str, target: str) -> list[str]:
    path = [target]
    current = target

    while current != source:
        current = previous[current]
        path.append(current)

    path.reverse()
    return path
