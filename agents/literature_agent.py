import os
import sys
import json
from groq import Groq

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.semantic_scholar import search_papers

client = Groq(api_key=os.environ.get("GROQ_API_KEY_2", "dummy"))

def run_literature_agent(query: str, parsed_query: dict = None) -> dict:
    """Finds papers and uses Groq to extract the full literature synthesis schema."""
    if not parsed_query:
        parsed_query = {}
        
    papers = search_papers(query, limit=8)
    if not papers:
        return {"papers": [], "synthesis": "No papers found.", "knowledge_gaps": [], "consensus_findings": [], "contradictions": []}
    
    print(f"\n📚 Successfully retrieved {len(papers)} papers:")
    
    # Prepare paper data for LLM processing
    papers_for_llm = []
    for idx, p in enumerate(papers):
        print(f"  ✅ {p.title[:80]}..." if len(p.title) > 80 else f"  ✅ {p.title}")
        papers_for_llm.append({
            "paper_id": p.url or f"paper_{idx}",
            "title": p.title or "Untitled Paper",
            "abstract": p.abstract or "No abstract available",
            "authors": getattr(p, "authors", ["Unknown"]),
            "year": p.year or 2024,
            "venue": getattr(p, "venue", "Academic Journal"),
            "citationCount": getattr(p, "citationCount", 0),
            "doi_or_url": p.url or ""
        })

    system_prompt = (
        "You are the Literature Agent, an expert in academic research synthesis.\n"
        "Analyze the retrieved papers and generate a comprehensive synthesis.\n"
        "Return a JSON object conforming exactly to this structure:\n"
        "{\n"
        '  "papers": [\n'
        '    {\n'
        '      "paper_id": "string",\n'
        '      "title": "string",\n'
        '      "authors": ["LastName, FirstInitial"],\n'
        '      "year": 2024,\n'
        '      "venue": "string",\n'
        '      "citation_count": 0,\n'
        '      "relevance_score": 9,\n'
        '      "abstract_summary": "2-3 sentence summary",\n'
        '      "key_findings": ["string"],\n'
        '      "methodology_used": "string",\n'
        '      "variables_studied": { "independent": ["string"], "dependent": ["string"] },\n'
        '      "limitations_stated": ["string"],\n'
        '      "supports_direction": "supports | contradicts | neutral | mixed",\n'
        '      "doi_or_url": "string"\n'
        '    }\n'
        '  ],\n'
        '  "synthesis": "string (narrative synthesis)",\n'
        '  "knowledge_gaps": ["string"],\n'
        '  "consensus_findings": ["string"],\n'
        '  "contradictions": [\n'
        '    {\n'
        '      "topic": "string",\n'
        '      "contradiction_description": "string",\n'
        '      "paper_ids_side_a": ["string"],\n'
        '      "paper_ids_side_b": ["string"]\n'
        '    }\n'
        '  ]\n'
        "}\n"
    )

    try:
        print("Calling Groq to generate full literature synthesis...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Parsed query context: {json.dumps(parsed_query)}\n\nRetrieved papers:\n{json.dumps(papers_for_llm, indent=2)}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=3000
        )
        
        json_resp = response.choices[0].message.content.strip()
        parsed = json.loads(json_resp)
        return parsed
    except Exception as e:
        print(f"Error calling Groq for literature synthesis: {e}")
        # Return fallback mock schema if Groq fails
        return {
            "papers": [], "synthesis": f"Failed to synthesize: {str(e)}",
            "knowledge_gaps": [], "consensus_findings": [], "contradictions": []
        }
