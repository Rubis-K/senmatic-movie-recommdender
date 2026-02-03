from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from semantic_movie_recommendations import retrive_semantic_recommendations
import uvicorn
import os




class MovieQuery(BaseModel):
    query: str
    category: str
    tone: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/recommend")
def recommend(q: MovieQuery):
    recs = retrive_semantic_recommendations(q.query, q.category, q.tone)
    results = []
    for _, row in recs.iterrows():
        results.append({
            "title": row["title"],
            "poster": row["poster"],
            "description": row["description"],
            "category": row["simplified_categories"],
            "tone": max(
                ("Happy", row["joy"]),
                ("Surprising", row["surprise"]),
                ("Angry", row["anger"]),
                ("Suspenseful", row["fear"]),
                ("Sad", row["sadness"]),
                key=lambda x: x[1]
            )[0]
        })
    return results

    

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("movie_recommender_api:app", host="0.0.0.0", port=port)

    #uvicorn movie_recommender_api:app --reload