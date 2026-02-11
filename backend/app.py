from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json
import random

app = FastAPI(title="AI Interview Coach API")

# Path to data file
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "interview_questions.json"

# --------- Models ---------
class AnswerRequest(BaseModel):
    question: str
    answer: str

# --------- Utils ---------
def load_data():
    if not DATA_PATH.exists():
        raise HTTPException(status_code=500, detail=f"Data file not found at {DATA_PATH}")
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON format: {e}")

# --------- Routes ---------
@app.get("/")
def root():
    return {"message": "AI Interview Coach API is running"}

# HR questions
@app.get("/questions/hr")
def get_hr_questions():
    data = load_data()
    return {"questions": data.get("hr", [])}

# Technical questions by topic (python, dsa, ml, ai, cn, os)
@app.get("/questions/technical/{topic}")
def get_technical_questions(topic: str):
    data = load_data()
    technical = data.get("technical", {})
    if topic not in technical:
        raise HTTPException(status_code=404, detail=f"Topic '{topic}' not found")
    return {"questions": technical.get(topic, [])}

# Random question by category/topic
@app.get("/random-question/{category}")
def random_question(category: str):
    data = load_data()

    if category == "hr":
        pool = data.get("hr", [])
    else:
        technical = data.get("technical", {})
        pool = technical.get(category, [])

    if not pool:
        raise HTTPException(status_code=404, detail=f"No questions found for '{category}'")

    q = random.choice(pool)
    return {"question": q.get("question"), "answer": q.get("answer")}

# Submit answer (simple scoring placeholder)
@app.post("/submit-answer")
def submit_answer(payload: AnswerRequest):
    # Dummy scoring logic (replace later with NLP/LLM scoring)
    score = min(10, max(1, len(payload.answer.strip()) // 30))
    clarity = "Good" if len(payload.answer.split()) > 20 else "Needs improvement"

    return {
        "score": score,
        "clarity": clarity,
        "clarity_feedback": "Try to be more concise and structured." if clarity == "Needs improvement" else "Well explained.",
        "keywords_matched": [],
        "similarity_score_percent": min(100, len(payload.answer) * 2)
    }

# Search questions
@app.get("/search")
def search_questions(q: str):
    data = load_data()
    results = []

    # HR
    for item in data.get("hr", []):
        if q.lower() in item.get("question", "").lower():
            results.append({"category": "hr", **item})

    # Technical
    technical = data.get("technical", {})
    for topic, items in technical.items():
        for item in items:
            if q.lower() in item.get("question", "").lower():
                results.append({"category": topic, **item})

    return {"results": results}
