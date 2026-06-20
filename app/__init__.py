from pathlib import Path

from flask import Flask, jsonify, render_template, request

from .campus_graph import CampusGraph, GraphError
from .nominatim import NominatimError, search_places


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        DATA_PATH=Path(__file__).resolve().parent.parent / "data" / "campus_graph.json",
        JSON_SORT_KEYS=False,
    )

    if test_config:
        app.config.update(test_config)

    graph = CampusGraph.from_json(app.config["DATA_PATH"])
    app.config["CAMPUS_GRAPH"] = graph

    @app.get("/")
    def index():
        return render_template("index.html", campus=graph.metadata)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "campus": graph.metadata.get("campus_name")})

    @app.get("/api/locations")
    def locations():
        return jsonify({"locations": [node.to_dict() for node in graph.nodes.values()]})

    @app.get("/api/graph")
    def graph_payload():
        return jsonify(graph.to_dict())

    @app.post("/api/route")
    def route():
        payload = request.get_json(silent=True) or {}
        source = payload.get("source")
        target = payload.get("target")
        profile = payload.get("profile", "walk")

        if not source or not target:
            return jsonify({"error": "source and target are required"}), 400

        try:
            result = graph.shortest_path(source, target, profile=profile)
        except GraphError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify(result)

    @app.get("/api/search")
    def search():
        query = request.args.get("q", "").strip()
        if len(query) < 3:
            return jsonify({"results": []})

        try:
            results = search_places(query)
        except NominatimError as exc:
            return jsonify({"error": str(exc)}), 502

        return jsonify({"results": results})

    return app
