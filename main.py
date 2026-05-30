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
    
    # 2. Literature Agent
    # For speed, we just use the first keyword or the raw question
    search_term = " ".join(parsed_query.get("keywords_for_search", [req.question]))
    enriched_papers = run_literature_agent(search_term)
    
    # Format papers for the frontend global state
    frontend_papers = []
    for item in enriched_papers:
        p = item["paper"]
        frontend_papers.append({
            "paper_id": p.url, "title": p.title, "authors": ["Unknown"], 
            "year": p.year, "venue": "Journal", "citation_count": 0,
            "relevance_score": 8, "abstract_summary": item["insight"],
            "key_findings": [item["insight"]], "doi_or_url": p.url
        })
    
    lit_synthesis = "Based on the retrieved literature, we observe several patterns..."
    if frontend_papers:
        lit_synthesis = f"Found {len(frontend_papers)} highly relevant papers. " + " ".join([p["abstract_summary"] for p in frontend_papers])
        
    literature_state = {
        "papers": frontend_papers,
        "synthesis": lit_synthesis,
        "knowledge_gaps": ["Gap 1", "Gap 2"],
        "consensus_findings": [],
        "contradictions": []
    }

    # 3. Hypothesis Agent
    hypothesis_list_obj = run_hypothesis_agent(enriched_papers)
    # The frontend expects an array of dicts, not the Pydantic wrapper
    hypotheses_raw = []
    if hypothesis_list_obj and hasattr(hypothesis_list_obj, 'hypotheses'):
        for h in hypothesis_list_obj.hypotheses:
            # We convert our schema back to what the frontend expects
            hypotheses_raw.append({
                "hypothesis_id": h.id, "strategy": "gap-filling", "title": "Hypothesis",
                "statement": {"if_then_because": h.statement, "H0": "Null", "H1": "Alt"},
                "variables": {"independent": "X", "dependent": "Y", "controls": []},
                "predicted_outcome": h.rationale, "falsification_criterion": "...",
                "novelty_score": 8, "testability_score": 9,
                "evidence_map": {"supporting_papers": h.supporting_papers}
            })
    else:
        # Fallback if the agent fails or returns dict instead of Pydantic model
        if isinstance(hypothesis_list_obj, dict) and "hypotheses" in hypothesis_list_obj:
            hypotheses_raw = hypothesis_list_obj["hypotheses"]
        elif isinstance(hypothesis_list_obj, list):
            hypotheses_raw = hypothesis_list_obj

    # 4. Experiment Agent
    experiments = run_experiment_agent(hypotheses_raw, parsed_query)
    
    # 5. Critique Agent
    critique = run_critique_agent(hypotheses_raw, experiments)
    
    # 6. Synthesizer
    proposal = run_synthesizer(req.question, parsed_query, lit_synthesis, hypotheses_raw, experiments, critique)
    
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
