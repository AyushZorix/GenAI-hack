from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import uuid
import datetime

load_dotenv()

from agents.orchestrator import run_orchestrator
from agents.literature_agent import run_literature_agent
from agents.hypothesis_agent import run_hypothesis_agent
from agents.experiment_agent import run_experiment_agent
from agents.critique_agent import run_critique_agent
from agents.synthesizer import run_synthesizer

app = FastAPI(title="GenAI Hackathon Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    question: str
    api_key: str = None  # We rely on .env mostly, but frontend might pass it

@app.post("/api/research")
def run_research_pipeline(req: ResearchRequest):
    print(f"Starting pipeline for: {req.question}")
    
    # 1. Orchestrator
    parsed_query = run_orchestrator(req.question)
    
    # Use only the first keyword to prevent API rejection from overly long strings
    search_keywords = parsed_query.get("keywords_for_search", [req.question])
    search_term = search_keywords[0] if search_keywords else req.question
    literature_state = run_literature_agent(search_term, parsed_query)
    
    # 3. Hypothesis Agent
    hypotheses_raw = run_hypothesis_agent(literature_state, parsed_query)

    # 4. Experiment Agent
    experiments = run_experiment_agent(hypotheses_raw, parsed_query)
    
    # 5. Critique Agent
    critique = run_critique_agent(hypotheses_raw, experiments)
    
    # 6. Synthesizer
    proposal = run_synthesizer(req.question, parsed_query, literature_state.get("synthesis", ""), hypotheses_raw, experiments, critique)
    
    # Assemble GlobalState exactly as frontend expects
    global_state = {
        "session_id": str(uuid.uuid4()),
        "timestamp": datetime.datetime.now().isoformat(),
        "research_question": req.question,
        "parsed_query": parsed_query,
        "literature": literature_state,
        "hypotheses": hypotheses_raw,
        "experiments": experiments,
        "critique": critique,
        "proposal": proposal
    }
    
    print("Pipeline completed successfully!")
    return global_state

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
