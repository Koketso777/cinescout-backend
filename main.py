from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

TMDB_API_KEY = os.environ.get("TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"

app = FastAPI(title="CineScout API", version="1.0.0")

# Allow your local dev + GitHub Pages
# IMPORTANT: origin must match exactly, including port.
origins = [
    "http://localhost:5174",             # your Vite dev server port (per your screenshot)
    "http://localhost:5173",             # keep this too in case Vite uses default on other machines
    "https://koketso777.github.io",
    "https://koketso777.github.io/cinescout",
    "https://koketso777.github.io/cinescout-backend"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,     # fine to keep True; use specific origins (not "*") when True
    allow_methods=["*"],        # allow GET/OPTIONS/etc during dev
    allow_headers=["*"],        # allow all headers during dev
)

def auth_params():
    if not TMDB_API_KEY:
        raise HTTPException(status_code=500, detail="TMDB_API_KEY not configured")
    return {"api_key": TMDB_API_KEY, "language": "en-US"}

@app.get("/")
def root():
    return {"service": "CineScout API", "ok": True}

@app.get("/search")
async def search_movies(q: str, page: int = 1):
    url = f"{TMDB_BASE}/search/movie"
    params = auth_params() | {"query": q, "page": page, "include_adult": "false"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url, params=params)
    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    data = r.json()
    results = []
    for m in data.get("results", []):
        results.append({
            "id": m.get("id"),
            "title": m.get("title"),
            "year": (m.get("release_date") or "")[:4],
            "overview": m.get("overview"),
            "poster": m.get("poster_path"),
            "rating": m.get("vote_average"),
        })
    return {"page": data.get("page", 1), "total_pages": data.get("total_pages", 1), "results": results}

@app.get("/movie/{movie_id}")
async def movie_detail(movie_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        detail = await client.get(f"{TMDB_BASE}/movie/{movie_id}", params=auth_params())
        credits = await client.get(f"{TMDB_BASE}/movie/{movie_id}/credits", params=auth_params())
    if detail.status_code != 200:
        raise HTTPException(status_code=detail.status_code, detail=detail.text)
    d = detail.json()
    c = credits.json() if credits.status_code == 200 else {}
    top_cast = [p.get("name") for p in (c.get("cast") or [])[:5]]
    return {
        "id": d.get("id"),
        "title": d.get("title"),
        "year": (d.get("release_date") or "")[:4],
        "overview": d.get("overview"),
        "poster": d.get("poster_path"),
        "rating": d.get("vote_average"),
        "genres": [g["name"] for g in d.get("genres", [])],
        "runtime": d.get("runtime"),
        "cast": top_cast,
    }
