
import os


def evaluate_evidence(
    vector_results: list[dict],
    graph_results: list[dict],
) -> dict:
    """
    Basic retrieval evaluation and abstention guardrail.

    For FAISS L2 distance, lower is generally better.
    Tune the threshold using representative test questions.
    """
    max_distance = float(
        os.getenv("FAISS_MAX_DISTANCE", "1.0")
    )

    relevant_vectors = [
        result
        for result in vector_results
        if result.get("content", "").strip()
        and result.get("score") is not None
        and result["score"] <= max_distance
    ]

    relevant_graph = [
        result
        for result in graph_results
        if result.get("source")
        and result.get("relationship")
        and result.get("target")
    ]

    if not relevant_vectors and not relevant_graph:
        return {
            "decision": "needs_clarification",
            "sufficient_evidence": False,
            "relevant_vector_count": 0,
            "relevant_graph_count": 0,
            "message": (
                "I couldn't find sufficient supporting evidence. "
                "Could you clarify your question or provide more details?"
            ),
        }

    return {
        "decision": "evidence_found",
        "sufficient_evidence": True,
        "relevant_vector_count": len(relevant_vectors),
        "relevant_graph_count": len(relevant_graph),
        "message": (
            "Evidence retrieved. The answer must still be checked "
            "against the retrieved content."
        ),
    }
