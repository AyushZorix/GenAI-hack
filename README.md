# GenAI-hack

Multi-Agent Scientific Hypothesis Generator and Experiment Designer

## Backend Setup (Python)
1. `pip install -r requirements.txt`
2. `cp .env.example .env` and add your GROQ_API_KEY
3. `python tools/semantic_scholar.py` to test
4. `uvicorn main:app --reload` to run the backend API (coming soon)

## Frontend Setup (React/Vite)
1. `npm install`
2. `npm run dev`
