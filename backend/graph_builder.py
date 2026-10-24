
import json
from pathlib import Path

import networkx as nx


PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRAPH_DIR = PROJECT_ROOT / "database" / "knowledge_graph"
GRAPH_PATH = GRAPH_DIR / "spotify_graph.json"


def build_knowledge_graph():
    """Build a knowledge graph from relationships in the architecture PDF."""

    graph = nx.MultiDiGraph()

    # Each tuple represents:
    # source entity, relationship, target entity
    relationships = [
        (
            "Analytics & Events Service",
            "feeds listening data to",
            "Recommendation Service",
        ),
        (
            "Catalog Service",
            "manages metadata for",
            "Tracks",
        ),
        (
            "Catalog Service",
            "manages metadata for",
            "Albums",
        ),
        (
            "Catalog Service",
            "manages metadata for",
            "Artists",
        ),
        (
            "Search & Discovery Index Service",
            "indexes",
            "Tracks",
        ),
        (
            "Search & Discovery Index Service",
            "indexes",
            "Playlists",
        ),
        (
            "Library & Playlist Service",
            "manages",
            "Playlists",
        ),
        (
            "Playback & Session Service",
            "manages",
            "Playback Sessions",
        ),
        (
            "Subscription & Billing Service",
            "manages",
            "Subscriptions",
        ),
        (
            "Media Processor Service",
            "writes processed files to",
            "Object Storage",
        ),
        (
            "Streaming / Media Delivery Service",
            "delivers audio through",
            "CDN",
        ),
        (
            "Analytics & Events Service",
            "stores events in",
            "ClickHouse / Data Warehouse",
        ),
    ]

    for source, relation, target in relationships:
        graph.add_node(source, type="entity")
        graph.add_node(target, type="entity")
        graph.add_edge(source, target, relation=relation)

    GRAPH_DIR.mkdir(parents=True, exist_ok=True)

    # Save graph nodes and edges as JSON.
    graph_data = nx.node_link_data(graph)

    with GRAPH_PATH.open("w", encoding="utf-8") as file:
        json.dump(graph_data, file, indent=2, ensure_ascii=False)

    print(f"Nodes created: {graph.number_of_nodes()}")
    print(f"Relationships created: {graph.number_of_edges()}")
    print(f"Graph saved to: {GRAPH_PATH}")


if __name__ == "__main__":
    build_knowledge_graph()
