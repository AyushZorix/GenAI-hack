import os
import sys
import json
from groq import Groq

# Adjust path so we can import tools and schema
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.literature_agent import run_literature_agent, get_paper_context_string
from tools.hypothesisbank_loader import load_few_shot_examples
from schema import HypothesisList

client = Groq(api_key=os.environ.get("GROQ_API_KEY", "dummy"))

def run_hypothesis_agent(enriched_papers: list[dict]) -> HypothesisList:
    """Takes enriched papers and asks Groq to generate 3 novel hypotheses in JSON."""
    if not enriched_papers:
        print("No papers provided to hypothesis agent.")
        return HypothesisList(hypotheses=[])

    if os.environ.get("GROQ_API_KEY") is None or os.environ.get("GROQ_API_KEY") == "dummy":
        print("Valid GROQ_API_KEY required. Returning empty hypotheses.")
        return HypothesisList(hypotheses=[])

    context_str = get_paper_context_string(enriched_papers)
    few_shot_examples = load_few_shot_examples() # currently returns empty list, but wired up
    
    system_prompt = (
        "You are an expert scientific researcher. Given the following literature context, "
        "identify 3 distinct research gaps and propose 3 novel, testable scientific hypotheses.\n"
        "You MUST output ONLY a valid JSON object adhering to this exact schema:\n"
        "{\n"
        '  "hypotheses": [\n'
        '    {\n'
        '      "id": "H1",\n'
        '      "statement": "...",\n'
        '      "rationale": "...",\n'
        '      "supporting_papers": ["Title 1", "Title 2"]\n'
        '    }\n'
        "  ]\n"
        "}\n"
    )

    try:
        print("Calling Groq to generate 3 hypotheses...")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", # or llama-3.3-70b-versatile
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Literature Context:\n{context_str}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1000
        )
        
        json_response = response.choices[0].message.content.strip()
        parsed_data = json.loads(json_response)
        
        # Validate against our Pydantic schema
        hypothesis_list = HypothesisList(**parsed_data)
        
        # Simple retry mechanism if not exactly 3
        if len(hypothesis_list.hypotheses) < 3:
            print(f"Warning: Only generated {len(hypothesis_list.hypotheses)} hypotheses. A real implementation would retry here.")
            
        return hypothesis_list

    except Exception as e:
        print(f"Error calling Groq for hypotheses: {e}")
        return HypothesisList(hypotheses=[])

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("--- Running Member A Integration Test ---")
    
    # 1. Run literature agent (which calls semantic scholar)
    papers_with_insights = run_literature_agent("sleep and alzheimer's disease")
    
    # 2. Run hypothesis agent
    final_hypotheses = run_hypothesis_agent(papers_with_insights)
    
    print("\n--- Final Generated Hypotheses ---")
    print(final_hypotheses.model_dump_json(indent=2))
