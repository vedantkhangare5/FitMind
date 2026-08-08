# FitMind AI

An evidence-based fitness and nutrition intelligence agent for Indian users.

Built with FastAPI (Python) + Next.js (TypeScript) + Tailwind CSS.

## Project Structure

```
Fitmind AI/
├── backend/          # FastAPI server (Python)
│   ├── app/          # Application code
│   └── tests/        # Backend tests
└── frontend/         # Next.js app (TypeScript + Tailwind v4)
    └── src/app/      # Pages and components
```

## Prerequisites

- **Python 3.11+** — [python.org](https://www.python.org/downloads/)
- **Node.js 18+** — [nodejs.org](https://nodejs.org/)
- **Git** — [git-scm.com](https://git-scm.com/)

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd "Fitmind AI"
```

### 2. Backend setup

```bash
# Navigate to backend folder
cd backend

# Create a Python virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS/Linux:
# source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Create your .env file from the template
cp ../.env.example .env
# Then edit .env and fill in your values

# Start the backend server
uvicorn app.main:app --reload
```

The backend will be running at **http://localhost:8000**

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

### 3. Frontend setup

```bash
# Navigate to frontend folder (from project root)
cd frontend

# Install dependencies
npm install

# Create your .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start the development server
npm run dev
```

The frontend will be running at **http://localhost:3000**

## Development

### Running tests

```bash
# Backend tests
cd backend
python -m pytest tests/ -v
```

### Running linters

```bash
# Frontend lint + type checks
cd frontend
npm run lint
```

## Current Status

- [x] Phase 1: Project Foundation
- [ ] Phase 2: Deterministic Fitness Calculations
- [ ] Phase 3: Knowledge Base + RAG
- [ ] Phase 4: RAG Evaluation
- [ ] Phase 5: Tool Calling / Basic Agent
- [ ] Phase 6: Meal & Workout Recommendations
- [ ] Phase 7: Progress Tracking + Memory
- [ ] Phase 8: Authentication + Polish + Deployment
