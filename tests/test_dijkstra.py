import pytest

from app.dijkstra import NoPathError, dijkstra


def test_dijkstra_prefers_lowest_total_weight():
    nodes = {"a", "b", "c", "d"}
    adjacency = {
        "a": [{"to": "b", "weight": 2}, {"to": "c", "weight": 10}],
        "b": [{"to": "c", "weight": 2}, {"to": "d", "weight": 2}],
        "c": [{"to": "d", "weight": 1}],
        "d": [],
    }

    result = dijkstra(nodes, adjacency, "a", "d")

    assert result["path"] == ["a", "b", "d"]
    assert result["distances"]["d"] == 4
    assert result["visited_order"][:2] == ["a", "b"]


def test_dijkstra_raises_when_target_is_unreachable():
    nodes = {"a", "b", "c"}
    adjacency = {"a": [{"to": "b", "weight": 1}], "b": [], "c": []}

    with pytest.raises(NoPathError):
        dijkstra(nodes, adjacency, "a", "c")
