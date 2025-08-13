# CineScout Backend (FastAPI)
Simple proxy to TMDB for the CineScout frontend.

## Local run
export TMDB_API_KEY=your_key_here
pip install -r requirements.txt
uvicorn main:app --reload

## Endpoints
GET /search?q=...&page=1
GET /movie/{id}
