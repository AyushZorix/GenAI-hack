import os
import json
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def run_orchestrator(question: str) -> dict:
    """Parses the user's research question into structured variables."""
    system_prompt = (
        "You are the Master Orchestrator of a scientific research pipeline.\n"
        "Analyze the following research question and extract its domain, subdomain, key concepts, "
        "independent/dependent/confounding variables, research type, and construct 3 distinct search keywords.\n\n"
        "Return a JSON object conforming exactly to this structure:\n"
        "{\n"
        '  "domain": "string",\n'
        '  "subdomain": "string",\n'
        '  "key_concepts": ["string"],\n'
        '  "variables": {\n'
        '    "independent": ["string"],\n'
        '    "dependent": ["string"],\n'
        '    "confounding": ["string"]\n'
        '  },\n'
        '  "research_type": "exploratory | confirmatory | mechanistic | applied",\n'
        '  "keywords_for_search": ["string"]\n'
        "}\n"
    )

    try:
        print("Calling Groq to parse the research question...")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Research Question: \"{question}\""}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=800
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"Error calling Groq for orchestrator: {e}")
        return {
            "domain": "Unknown", "subdomain": "Unknown", "key_concepts": [],
            "variables": {"independent": [], "dependent": [], "confounding": []},
            "research_type": "exploratory", "keywords_for_search": [question]
        }
