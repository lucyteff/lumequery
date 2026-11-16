
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.ai.orchestrator import ask_lumequery

app = FastAPI(
    title="LumeQuery API",
    description="AI-powered marketplace data intelligence API",
    version="1.0.0"
)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


@app.get("/health")
def health():
    return {"status": "ok", "service": "LumeQuery API"}


@app.post("/ask")
def ask(request: QuestionRequest):
    try:
        return ask_lumequery(request.question.strip())
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
