
import json
import re
from pathlib import Path

import networkx as nx

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRAPH_PATH = (
    PROJECT_ROOT
    / "database"
    / "knowledge_graph"
    / "spotify_graph.json"
)

STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were",
    "what", "which", "who", "where", "when", "how",
    "does", "do", "did", "can", "could", "would",
    "should", "please", "tell", "me", "about", "for",
    "to", "of", "in", "on", "and", "or", "with",
    "from", "it", "its", "this", "that", "i",
    "we", "you", "they", "their", "has", "have",
}


def tokenize(text: str) -> set[str]:
    words = set(re.findall(r"[a-z0-9]+", text.lower()))
    return words - STOP_WORDS


def load_knowledge_graph() -> nx.MultiDiGraph:
    if not GRAPH_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge graph not found: {GRAPH_PATH}"
        )

    with GRAPH_PATH.open("r", encoding="utf-8") as file:
        graph_data = json.load(file)

    return nx.node_link_graph(
        graph_data,
        directed=True,
        multigraph=True,
    )


def search_graph(
    question: str,
    max_results: int = 5,
    min_score: float = 0.35,
) -> list[dict]:
    graph = load_knowledge_graph()
    query_tokens = tokenize(question)

    if not query_tokens:
        return []

    ranked_results = []

    for source, target, data in graph.edges(data=True):
        relation = data.get("relation", "")

        triple_text = f"{source} {relation} {target}"
        triple_tokens = tokenize(triple_text)

        if not triple_tokens:
            continue

        overlap = query_tokens & triple_tokens
        overlap_score = len(overlap) / len(query_tokens)

        source_exact = source.lower() in question.lower()
        target_exact = target.lower() in question.lower()

        # Entity matches strengthen a result, but do not guarantee
        # that the relationship answers the question.
        score = overlap_score

        if source_exact:
            score += 0.20

        if target_exact:
            score += 0.20

        score = min(score, 1.0)

        if score >= min_score:
            ranked_results.append({
                "source": source,
                "relationship": relation,
                "target": target,
                "relevance_score": round(score, 3),
            })

    ranked_results.sort(
        key=lambda item: item["relevance_score"],
        reverse=True,
    )

    return ranked_results[:max_results]


if __name__ == "__main__":
    questions = [
        "Which service provides listening data to the Recommendation Service?",
        "Which service manages playlists?",
        "Where does the Media Processor Service write processed files?",
        "What is the capital of Mars?",
    ]

    for question in questions:
        print(f"\nQuestion: {question}")

        for result in search_graph(question):
            print(
                f"{result['source']} "
                f"--[{result['relationship']}]--> "
                f"{result['target']} "
                f"(score={result['relevance_score']})"
            )
