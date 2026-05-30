import os
import sys
import json
from groq import Groq

# Adjust path so we can import schema
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def run_experiment_agent(hypotheses: list, parsed_query: dict) -> list:
    """Takes hypotheses and parsed query to generate experiments via Groq."""
    if not hypotheses:
        return []

    system_prompt = (
        "You are the Experiment Design Agent. For each of the 3 hypotheses generated, "
        "design a complete, rigorous experimental methodology.\n\n"
        "Return a JSON array of exactly 3 ExperimentObjects, conforming to this exact structure:\n"
        "[\n"
        "  {\n"
        '    "experiment_id": "E1 | E2 | E3",\n'
        '    "hypothesis_id": "H1 | H2 | H3",\n'
        '    "study_design": "string",\n'
        '    "design_justification": "string",\n'
        '    "participants_or_subjects": {\n'
        '      "type": "human | animal | cell line | dataset | simulation",\n'
        '      "inclusion_criteria": ["string"],\n'
        '      "exclusion_criteria": ["string"],\n'
        '      "sample_size": "string",\n'
        '      "sampling_strategy": "string",\n'
        '      "power_analysis": "string"\n'
        '    },\n'
        '    "materials_and_tools": {\n'
        '      "equipment": ["string"],\n'
        '      "reagents_or_stimuli": ["string"],\n'
        '      "software": ["string"],\n'
        '      "datasets_if_computational": ["string"]\n'
        '    },\n'
        '    "procedure": {\n'
        '      "phases": [\n'
        '        { "phase_name": "string", "duration": "string", "steps": ["string"], "measurements": ["string"] }\n'
        '      ],\n'
        '      "blinding": "single-blind | double-blind | open-label | not applicable",\n'
        '      "randomization_method": "string",\n'
        '      "control_group_description": "string"\n'
        '    },\n'
        '    "measurements": {\n'
        '      "primary_outcome": { "measure": "string", "instrument": "string", "timepoints": ["string"], "units": "string" },\n'
        '      "secondary_outcomes": [ { "measure": "string", "instrument": "string", "timepoints": ["string"] } ]\n'
        '    },\n'
        '    "statistical_analysis": {\n'
        '      "primary_test": "string", "significance_threshold": "string", "effect_size_metric": "string",\n'
        '      "correction_for_multiple_comparisons": "string", "software": "string"\n'
        '    },\n'
        '    "timeline": { "total_duration": "string", "milestones": [ { "week": 1, "milestone": "string" } ] },\n'
        '    "budget_estimate": { "personnel": "string", "equipment": "string", "consumables": "string", "total_estimated": "string" },\n'
        '    "potential_confounds": ["string"],\n'
        '    "mitigation_strategies": ["string"],\n'
        '    "replication_strategy": "string"\n'
        "  }\n"
        "]\n"
    )

    try:
        print("Calling Groq to generate 3 experiments...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Hypotheses: {json.dumps(hypotheses)}\nParsed Variables: {json.dumps(parsed_query.get('variables', {}))}"}
            ],
            response_format={"type": "json_object"}, # Groq allows json_object if output is dict. We must wrap array in dict.
            temperature=0.7,
            max_tokens=2500
        )
        
        # Note: Since response_format={"type": "json_object"} requires the prompt to output a dict, 
        # Groq might fail if it just returns an array. Let's fix the prompt just in case.
        # Actually we will parse it directly.
        json_resp = response.choices[0].message.content.strip()
        
        # Handle if Groq wrapped it in a dict like {"experiments": [...]}
        parsed = json.loads(json_resp)
        if isinstance(parsed, dict) and "experiments" in parsed:
            return parsed["experiments"]
        elif isinstance(parsed, dict) and len(parsed.keys()) == 1:
            return list(parsed.values())[0]
            
        return parsed
    except Exception as e:
        print(f"Error calling Groq for experiments: {e}")
        return []
