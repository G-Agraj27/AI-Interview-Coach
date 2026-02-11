from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json, random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "interview_questions.json"

IDEAL_ANSWERS = {
    "what is machine learning?": "Machine learning is a field of artificial intelligence where models learn from data to make predictions and improve over time.",
    "what is rest api?": "A REST API is an interface that allows communication between client and server using standard HTTP methods."
}

class AnswerRequest(BaseModel):
    question: str
    answer: str

@app.get("/")
def home():
    return {"message": "AI Interview Coach API is running 🚀"}

@app.get("/random-question/{category}")
def random_question(category: str):
    try:
        if not DATA_PATH.exists():
            return {"error": f"Data file not found at {DATA_PATH}"}

        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        qs = data.get(category.lower())
        if not qs:
            return {"error": "No questions found for this category"}

        return {"question": random.choice(qs)}
    except Exception as e:
        return {"error": str(e)}


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

    # NLP similarity scoring (safe)
    ideal = IDEAL_ANSWERS.get(payload.question.lower())
    similarity_score = None

    if ideal and payload.answer.strip():
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([payload.answer, ideal])
        similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        similarity_score = round(similarity * 100, 2)

    return {
        "score": score,
        "clarity": clarity,
        "clarity_feedback": clarity_feedback,
        "keywords_matched": matched,
        "similarity_score_percent": similarity_score
    }
