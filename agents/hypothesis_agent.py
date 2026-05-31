import os
import sys
import json
import google.generativeai as genai

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

genai.configure(api_key=os.environ.get("GEMINI_API_KEY_1", "dummy"))
model = genai.GenerativeModel("gemini-2.5-flash")

def run_hypothesis_agent(literature_results: dict, parsed_query: dict) -> list:
    """Takes literature synthesis and parsed query to generate hypotheses via Gemini."""
    
    if not literature_results or not literature_results.get("papers"):
        return []

    system_prompt = (
        "You are the Hypothesis Agent. Generate exactly 3 distinct hypotheses based on the literature synthesis and gaps.\n"
        "Strategy:\n"
        "- H1 (Gap-filling): Directly addresses a gap.\n"
        "- H2 (Mechanistic): Proposes a causal mechanism.\n"
        "- H3 (Contrarian/Novel): Challenges a consensus or proposes a new angle.\n\n"
        "Return a JSON object conforming exactly to this structure:\n"
        "{\n"
        '  "hypotheses": [\n'
        '    {\n'
        '      "hypothesis_id": "H1 | H2 | H3",\n'
        '      "strategy": "gap-filling | mechanistic | contrarian",\n'
        '      "title": "string",\n'
        '      "statement": {\n'
        '        "if_then_because": "If [manipulation], then [expected outcome], because [mechanistic rationale]",\n'
        '        "H0": "string",\n'
        '        "H1": "string"\n'
        '      },\n'
        '      "variables": {\n'
        '        "independent": "string",\n'
        '        "dependent": "string",\n'
        '        "controls": ["string"]\n'
        '      },\n'
        '      "predicted_outcome": "string",\n'
        '      "falsification_criterion": "string",\n'
        '      "novelty_score": 9,\n'
        '      "novelty_justification": "string",\n'
        '      "testability_score": 8,\n'
        '      "testability_justification": "string",\n'
        '      "evidence_map": {\n'
        '        "supporting_papers": ["paper_id"],\n'
        '        "supporting_reasoning": "string",\n'
        '        "contradicting_papers": ["paper_id"],\n'
        '        "contradicting_reasoning": "string",\n'
        '        "gap_being_addressed": "string"\n'
        '      },\n'
        '      "theoretical_framework": "string"\n'
        '    }\n'
        '  ]\n'
        "}\n"
    )

    try:
        print("Calling Gemini to generate 3 hypotheses...")
        response = model.generate_content(
            f"{system_prompt}\n\nParsed Query Variables: {json.dumps(parsed_query.get('variables', {}))}\n\nLiterature Synthesis: {literature_results.get('synthesis')}\n\nGaps: {json.dumps(literature_results.get('knowledge_gaps'))}",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.7,
            )
        )
        
        json_response = response.text.strip()
        parsed_data = json.loads(json_response)
        
        if "hypotheses" in parsed_data:
            return parsed_data["hypotheses"]
        elif isinstance(parsed_data, list):
            return parsed_data
        return list(parsed_data.values())[0]

    except Exception as e:
        print(f"Error calling Gemini for hypotheses: {e}")
        return []
