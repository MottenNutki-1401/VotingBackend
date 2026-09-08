import os

from dotenv import load_dotenv
from fastapi import FastAPI
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

app = FastAPI(title="San Matias Intramurals Voting API")


@app.get("/")
def root():
    return {"message": "Voting API is running!"}


@app.get("/api/candidates")
def get_candidates():
    response = supabase.table("candidates").select("*").execute()
    return response.data