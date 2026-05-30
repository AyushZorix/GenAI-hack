import requests
import json

def search_papers(query: str, limit: int = 10) -> list:
    """
    Search for papers on Semantic Scholar.
    No API key needed for basic usage.
    """
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,authors,year,url"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    return r.json().get("data", [])

if __name__ == "__main__":
    # Test the function if run directly
    sample_query = "role of gut microbiome in depression"
    print(f"Searching for papers related to: '{sample_query}'...\n")
    
    try:
        results = search_papers(sample_query, limit=3)
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error occurred: {e}")
