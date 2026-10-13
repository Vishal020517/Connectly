# Connectly — AI Hiring Platform

## Stack
- **AI / Backend** — Python, LangGraph, FastAPI, MongoDB, ChromaDB
- **Frontend** — React 19, Vite 8, vanilla CSS (glassmorphism)

## Folder structure
```
whisper/
├── backend/               FastAPI server
│   ├── main.py            app entrypoint
│   ├── run.py             uvicorn launcher
│   ├── models.py          request/response schemas
│   ├── state_store.py     in-memory graph state per user
│   └── routers/
│       ├── candidate.py   POST /candidate/chat
│       ├── recruiter.py   POST /recruiter/chat
│       └── sidebar.py     GET  /sidebar/profiles/:id  /sidebar/jobs/:id
├── Candidate_module/      candidate LangGraph
├── Recruiter_module/      recruiter LangGraph
├── Utils/                 embedder, vector store, fetchers
└── frontend/              React app (port 5179)
```

## Running locally

### 1. Activate venv & start backend
```bash
source .venv/bin/activate
python -m backend.run
# → http://localhost:8000
```

### 2. Start frontend (separate terminal)
```bash
cd frontend
npm run dev
# → http://localhost:5179
```

### 3. Seed data (optional)
```bash
python -m Candidate_module.seed_profile_data
python -m Recruiter_module.seed_job_data
```

## How to use
1. Open `http://localhost:5179`
2. Choose **Candidate** or **Recruiter**
3. Enter any ID (e.g. `vishal_dev` or `techcorp_hr`) — created automatically
4. Chat naturally — the AI handles everything
5. Sidebar shows your profiles/jobs with short IDs for easy reference
