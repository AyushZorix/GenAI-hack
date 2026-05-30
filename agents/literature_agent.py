import os
import sys
from groq import Groq

# Adjust path so we can import tools and schema
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.semantic_scholar import search_papers
from schema import Paper

client = Groq(api_key=os.environ.get("GROQ_API_KEY", "dummy"))

def get_key_insight(abstract: str) -> str:
    """Uses Groq to extract a one-sentence key insight from the abstract."""
    if os.environ.get("GROQ_API_KEY") is None or os.environ.get("GROQ_API_KEY") == "dummy":
        return "Insight generation requires a valid GROQ_API_KEY."
        
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a scientific assistant. Extract the single most important key insight from this abstract in one concise sentence."},
                {"role": "user", "content": f"Abstract: {abstract}"}
            ],
            temperature=0.3,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error calling Groq: {e}")
        return "Failed to extract insight."

def run_literature_agent(query: str) -> list[dict]:
    """Finds papers and extracts insights."""
    papers = search_papers(query, limit=5)
    enriched_papers = []
    
    print("Extracting key insights for each paper using Groq...")
    for paper in papers:
        insight = get_key_insight(paper.abstract)
        enriched_papers.append({
            "paper": paper,
            "insight": insight
        })
        print(f"✅ Processed: {paper.title[:50]}...")
        
    return enriched_papers

def get_paper_context_string(enriched_papers: list[dict]) -> str:
    """Helper function used by Member A's hypothesis agent. Do not modify."""
    context = ""
    for idx, item in enumerate(enriched_papers):
        p = item["paper"]
        context += f"[{idx+1}] Title: {p.title}\n"
        context += f"Year: {p.year}\n"
        context += f"Abstract: {p.abstract}\n"
        context += f"Key Insight: {item['insight']}\n\n"
    return context

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv() # Load the .env file locally for testing
    
    test_query = "gut microbiome and depression"
    print(f"Running Literature Agent for query: {test_query}\n")
    results = run_literature_agent(test_query)
    
    print("\n--- Final Output Context String ---\n")
    print(get_paper_context_string(results))
