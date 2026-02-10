from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json, random

app = FastAPI()

# Allow frontend (Streamlit) to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# File path to JSON data
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "interview_questions.json"

class AnswerRequest(BaseModel):
    question: str
    answer: str

@app.get("/")
def home():
    return {"message": "AI Interview Coach API is running 🚀"}

@app.get("/random-question/{category}")
def random_question(category: str):
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    qs = data.get(category.lower())
    if not qs:
        return {"error": "No questions found for this category"}

    return {"question": random.choice(qs)}

@app.post("/submit-answer")
def submit_answer(payload: AnswerRequest):
    answer = payload.answer.strip()
    words = answer.split()

    # Simple clarity logic
    if len(words) < 10:
        clarity = "Low"
        clarity_feedback = "Your answer is too short. Try to explain more."
    elif len(words) < 30:
        clarity = "Medium"
        clarity_feedback = "Your answer is fairly clear, but you can add more details."
    else:
        clarity = "High"
        clarity_feedback = "Great clarity! Well explained."

    # Simple keyword scoring
    keywords = ["data", "model", "learn", "algorithm", "api"]
    matched = sum(1 for k in keywords if k in answer.lower())
    score = min(10, max(1, matched * 2))

    return {
        "score": score,
        "clarity": clarity,
        "clarity_feedback": clarity_feedback,
        "keywords_matched": matched
    }
