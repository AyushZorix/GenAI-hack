import os
import json
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def run_synthesizer(question: str, parsed_query: dict, lit_synthesis: str, hypotheses: list, experiments: list, critique: dict) -> dict:
    """Synthesizes the final research proposal."""
    system_prompt = (
        "You are the Research Proposal Synthesizer.\n"
        "Assemble the proposal into 10 structured sections. Write rich, academic-style content.\n"
        "Return a JSON object conforming exactly to this structure:\n"
        "{\n"
        '  "title": "string",\n'
        '  "abstract": "string (250-word abstract)",\n'
        '  "sections": {\n'
        '    "1_introduction": { "background": "string", "problem_statement": "string", "research_question": "string", "significance": "string" },\n'
        '    "2_literature_review": { "content": "string", "citations": ["string"] },\n'
        '    "3_hypotheses": {\n'
        '      "hypothesis_1": { "title": "string", "statement": "string", "null_hyp": "string", "alt_hyp": "string" },\n'
        '      "hypothesis_2": { "title": "string", "statement": "string", "null_hyp": "string", "alt_hyp": "string" },\n'
        '      "hypothesis_3": { "title": "string", "statement": "string", "null_hyp": "string", "alt_hyp": "string" }\n'
        '    },\n'
        '    "4_methodology": { "overview": "string", "primary_experiment": {}, "alternative_experiments": [] },\n'
        '    "5_ethical_considerations": "string",\n'
        '    "6_timeline_and_budget": "string",\n'
        '    "7_expected_outcomes": "string",\n'
        '    "8_limitations": "string",\n'
        '    "9_future_directions": "string",\n'
        '    "10_references": ["string"]\n'
        '  }\n'
        "}\n"
    )

    try:
        print("Calling Groq to synthesize the final proposal...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {question}\nLiterature: {lit_synthesis}\nHypotheses: {json.dumps(hypotheses)}\nExperiments: {json.dumps(experiments)}\nCritique: {json.dumps(critique)}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.5,
            max_tokens=3000
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"Error calling Groq for synthesizer: {e}")
        return {}
