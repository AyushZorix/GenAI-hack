from pydantic import BaseModel, Field
from typing import List, Optional

# --- Literature Agent Output ---
class Paper(BaseModel):
    title: str = Field(description="Title of the paper")
    abstract: str = Field(description="Abstract of the paper")
    year: Optional[int] = Field(description="Publication year")
    url: Optional[str] = Field(description="URL to the paper")

class LiteratureReview(BaseModel):
    query: str = Field(description="The user's original research query")
    papers: List[Paper] = Field(description="List of relevant papers retrieved")
    synthesis: str = Field(description="A brief synthesis of the current state of literature")

# --- Hypothesis Agent Output ---
class Hypothesis(BaseModel):
    id: str = Field(description="Unique identifier for the hypothesis (e.g., H1, H2)")
    statement: str = Field(description="The core scientific hypothesis")
    rationale: str = Field(description="Why this hypothesis is valid based on literature")
    supporting_papers: List[str] = Field(description="Titles of papers supporting this hypothesis")

class HypothesisList(BaseModel):
    hypotheses: List[Hypothesis] = Field(description="List of generated hypotheses")

# --- Experiment Agent Output ---
class ExperimentDesign(BaseModel):
    hypothesis_id: str = Field(description="The ID of the hypothesis being tested")
    independent_variables: List[str] = Field(description="Variables that will be manipulated")
    dependent_variables: List[str] = Field(description="Variables that will be measured")
    controls: List[str] = Field(description="Control variables and groups")
    methodology: str = Field(description="Step-by-step experimental methodology")
    expected_outcomes: str = Field(description="What results would support or falsify the hypothesis")

class FullExperimentPlan(BaseModel):
    experiments: List[ExperimentDesign] = Field(description="Experimental designs for all hypotheses")

# --- Critique Agent Output ---
class Critique(BaseModel):
    hypothesis_id: str = Field(description="The ID of the hypothesis being critiqued")
    novelty_score: float = Field(description="Computed semantic novelty score (0.0 to 1.0)")
    feasibility: str = Field(description="Assessment of how practical the experiment is")
    ethical_concerns: str = Field(description="Any ethical issues with the methodology")
    verdict: str = Field(description="Final recommendation: Pursue, Modify, or Discard")

class FinalReportData(BaseModel):
    research_query: str
    literature_review: LiteratureReview
    hypotheses: HypothesisList
    experiments: FullExperimentPlan
    critiques: List[Critique]
