import os

from dotenv import load_dotenv
from fastapi import FastAPI ,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
    raise RuntimeError("Supabase environment variables are missing.")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY
)

app = FastAPI(title="San Matias Intramurals Voting API") ######

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
       " https://frontend-cc-refz-m61a38d13-comettrail-s-projects.vercel.app/"
       #test
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def root():
    return {"message": "Voting API is running!"}


@app.get("/api/candidates")
def get_candidates():
    response = supabase.table("candidates").select("*").execute()
    return response.data

@app.post("/api/votes")
def submit_vote(vote: dict):
    response = (
        supabase
        .table("votes")
        .insert({
            "mr_candidate_id": vote["mr_candidate_id"],
            "ms_candidate_id": vote["ms_candidate_id"],
        })
        .execute()
    )

    return {"message": "Vote recorded successfully"}

@app.get("/api/leaderboard")
def get_leaderboard():
    candidates_response = (
        supabase.table("candidates")
        .select("id, name, category")
        .execute()
    )

    votes_response = (
        supabase.table("votes")
        .select("mr_candidate_id, ms_candidate_id")
        .execute()
    )

    candidates = candidates_response.data
    votes = votes_response.data

    counts = {candidate["id"]: 0 for candidate in candidates}

    for vote in votes:
        mr_id = vote["mr_candidate_id"]
        ms_id = vote["ms_candidate_id"]

        if mr_id in counts:
            counts[mr_id] += 1

        if ms_id in counts:
            counts[ms_id] += 1

    mr_counts = [
        counts[candidate["id"]]
        for candidate in candidates
        if candidate["category"] == "Mr"
    ]

    ms_counts = [
        counts[candidate["id"]]
        for candidate in candidates
        if candidate["category"] == "Ms"
    ]

    mr_max = max(mr_counts, default=0)
    ms_max = max(ms_counts, default=0)

    result = []

    for candidate in candidates:
        maximum = mr_max if candidate["category"] == "Mr" else ms_max
        count = counts[candidate["id"]]

        progress = round((count / maximum) * 100) if maximum > 0 else 0

        result.append({
            "id": candidate["id"],
            "name": candidate["name"],
            "category": candidate["category"],
            "progress": progress
        })

    return result

# for admin result
@app.post("/api/admin/results")
def get_admin_results(data: dict):
    if data.get("password") != os.getenv("ADMIN_PASSWORD"):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )

    candidates_response = (
        supabase
        .table("candidates")
        .select("id, name, category")
        .execute()
    )

    votes_response = (
        supabase
        .table("votes")
        .select("id, mr_candidate_id, ms_candidate_id, created_at")
        .execute()
    )

    candidates = candidates_response.data
    votes = votes_response.data

    counts = {
        candidate["id"]: 0
        for candidate in candidates
    }

    for vote in votes:
        mr_id = vote["mr_candidate_id"]
        ms_id = vote["ms_candidate_id"]

        if mr_id in counts:
            counts[mr_id] += 1

        if ms_id in counts:
            counts[ms_id] += 1

    results = []

    for candidate in candidates:
        results.append({
            "id": candidate["id"],
            "name": candidate["name"],
            "category": candidate["category"],
            "votes": counts[candidate["id"]]
        })

    return results

@app.post("/api/admin/reset")
def reset_votes(data: dict):
    if data.get("password") != os.getenv("ADMIN_PASSWORD"):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )

    response = (
        supabase
        .table("votes")
        .delete()
        .gte("id", 1)
        .execute()
    )

    return {"message": "All votes have been reset successfully"}