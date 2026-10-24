
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from backend.graph_retriever import search_graph
from backend.vector_retriever import search_vectors
from backend.evaluation import evaluate_evidence
from backend.llm_service import generate_answer

app = FastAPI(
    title="Hybrid RAG API",
    description="FAISS + Knowledge Graph + GPT-4o-mini",
    version="1.0.0",
)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Hybrid RAG API"}


@app.post("/retrieve")
def retrieve(request: QuestionRequest):
    question = request.question.strip()

    if len(question) < 3:
        raise HTTPException(
            status_code=400,
            detail="Please enter a meaningful question.",
        )

    try:
        vector_results = search_vectors(question, k=4)
        graph_results = search_graph(question)

        evaluation = evaluate_evidence(
            vector_results=vector_results,
            graph_results=graph_results,
        )

        max_distance = float(
            os.getenv("FAISS_MAX_DISTANCE", "1.0")
        )

        relevant_vectors = [
            item for item in vector_results
            if item.get("content", "").strip()
            and item.get("score") is not None
            and item["score"] <= max_distance
        ]

        if not evaluation["sufficient_evidence"]:
            return {
                "question": question,
                "status": "needs_clarification",
                "answer": evaluation["message"],
                "sources": [],
                "evaluation": evaluation,
            }

        result = generate_answer(
            question=question,
            vector_results=relevant_vectors,
            graph_results=graph_results,
        )

        return {
            "question": question,
            "status": result["status"],
            "answer": result["answer"],
            "sources": result["sources"],
            "evaluation": evaluation,
        }

    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Request failed: {type(exc).__name__}: {exc}",
        )
