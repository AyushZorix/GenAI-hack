import os
import sys
import json
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def run_critique_agent(hypotheses: list, experiments: list) -> dict:
    """Evaluates the hypotheses and experiments using Groq."""
    if not hypotheses or not experiments:
        return {}

    system_prompt = (
        "You are the Critique Agent, a senior peer reviewer. Evaluate the provided hypotheses and experiments.\n\n"
        "Return a JSON object conforming exactly to this structure:\n"
        "{\n"
        '  "overall_score": 8.5,\n'
        '  "summary": "string",\n'
        '  "best_hypothesis": "H1",\n'
        '  "recommended_sequence": ["H1", "H2", "H3"],\n'
        '  "synergy_opportunities": ["string"],\n'
        '  "fatal_flaws": ["string"],\n'
        '  "cross_cutting_recommendations": ["string"],\n'
        '  "per_hypothesis": [\n'
        '    {\n'
        '      "hypothesis_id": "H1",\n'
        '      "experiment_id": "E1",\n'
        '      "novelty_assessment": { "score": 8, "max_score": 10, "verdict": "highly novel", "rationale": "string", "prior_art_concerns": "string", "recommendation": "string" },\n'
        '      "feasibility_assessment": { "score": 7, "max_score": 10, "verdict": "feasible", "rationale": "string", "resource_requirements": "low", "technical_barriers": ["string"], "expertise_required": ["string"], "timeline_realism": "realistic", "recommendation": "string" },\n'
        '      "ethical_assessment": { "concerns_identified": false, "severity": "none", "concern_list": [], "irb_required": false, "animal_welfare_issues": false, "data_privacy_issues": false, "informed_consent_required": false, "dual_use_risk": false, "recommendation": "string" },\n'
        '      "scientific_rigor_assessment": { "score": 9, "max_score": 10, "internal_validity": "high", "external_validity": "high", "construct_validity": "high", "statistical_power": "adequate", "confound_control": "thorough", "measurement_validity": "validated instruments", "weaknesses": ["string"], "strengths": ["string"], "recommendation": "string" },\n'
        '      "overall_score": 8.5,\n'
        '      "overall_verdict": "recommend with revisions",\n'
        '      "priority_ranking": 1,\n'
        '      "summary_for_researcher": "string"\n'
        '    }\n'
        '  ]\n'
        "}\n"
    )

    try:
        print("Calling Groq to critique the research...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Hypotheses: {json.dumps(hypotheses)}\nExperiments: {json.dumps(experiments)}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=2500
        )
        
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"Error calling Groq for critique: {e}")
        return {}
