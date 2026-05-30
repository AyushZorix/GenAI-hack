# Multi-Agent Scientific Hypothesis Generator and Experiment Designer

We are building a multi-agent system that takes a research topic or dataset as input, retrieves relevant scientific literature, generates novel hypotheses, designs experiments, critiques the hypotheses (including a novelty score), and outputs a downloadable research proposal in DOCX format.

## User Review Required

> [!IMPORTANT]
> Please review the architecture and timeline. Since we have a strict 12-hour timeline, we need to ensure our environment is correctly set up with the necessary API keys (Groq, Semantic Scholar).

## Open Questions

> [!CAUTION]
> 1. **Team Constraints:** You mentioned asking about team members and their strengths. Is it just you and me (the AI) working on this, or do you have other human teammates we should split the tasks with? 
> 2. **API Keys:** Do you have your **Groq API key** and **Semantic Scholar API key** ready? (If not, we can use a free tier or fallback mocks for testing).
> 3. **LLM Orchestration:** The plan mentions `CrewAI`. Are we aligned on using `CrewAI` and `Groq`, or would you prefer a different stack?

## Proposed Changes

We will create a structured Python project with CrewAI agents, tools, and a Streamlit frontend.

### Project Setup and Configuration
#### [NEW] [requirements.txt](file:///d:/Academics/GenAI/Hacky/requirements.txt)
Will include `crewai`, `streamlit`, `groq`, `sentence-transformers`, `faiss-cpu`, `python-docx`, `requests`, etc.
#### [NEW] [.env](file:///d:/Academics/GenAI/Hacky/.env)
To hold API keys securely.

---

### Core Pipeline (Agents and Orchestration)
#### [NEW] [agents/literature_agent.py](file:///d:/Academics/GenAI/Hacky/agents/literature_agent.py)
Agent responsible for retrieving 5-10 relevant papers with abstracts.
#### [NEW] [agents/hypothesis_agent.py](file:///d:/Academics/GenAI/Hacky/agents/hypothesis_agent.py)
Agent responsible for generating 3 novel, testable hypotheses based on literature.
#### [NEW] [agents/experiment_agent.py](file:///d:/Academics/GenAI/Hacky/agents/experiment_agent.py)
Agent responsible for designing experimental methodology per hypothesis.
#### [NEW] [agents/critique_agent.py](file:///d:/Academics/GenAI/Hacky/agents/critique_agent.py)
Agent responsible for scoring novelty, feasibility, and ethics.
#### [NEW] [crew.py](file:///d:/Academics/GenAI/Hacky/crew.py)
CrewAI orchestration to wire the agents together into a sequential pipeline.

---

### Tools
#### [NEW] [tools/semantic_scholar.py](file:///d:/Academics/GenAI/Hacky/tools/semantic_scholar.py)
API wrapper for Semantic Scholar to fetch papers.
#### [NEW] [tools/novelty_scorer.py](file:///d:/Academics/GenAI/Hacky/tools/novelty_scorer.py)
Uses FAISS + `sentence-transformers` (`all-MiniLM`) to compute cosine similarity between generated hypotheses and retrieved abstracts.
#### [NEW] [tools/docx_generator.py](file:///d:/Academics/GenAI/Hacky/tools/docx_generator.py)
Uses `python-docx` to generate the final downloadable research proposal.

---

### Frontend
#### [NEW] [app.py](file:///d:/Academics/GenAI/Hacky/app.py)
Streamlit UI to capture user input, display live progress, show novelty scores, and provide the DOCX download link.

## Verification Plan

### Automated Tests
- We can write a simple test script to run the CrewAI pipeline headlessly to verify LLM outputs and data passing between agents.
- Verify `novelty_scorer.py` locally with dummy data.

### Manual Verification
- Run `streamlit run app.py` and input a sample query (e.g., *"What is the role of gut microbiome in depression?"*).
- Observe the live paper retrieval, hypotheses generation, and critique.
- Download the generated DOCX and verify the formatting is clean and professional.
