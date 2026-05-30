import requests
import xml.etree.ElementTree as ET
import sys
import os

# Adjust path so we can import schema from parent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schema import Paper

def _hardcoded_fallback() -> list[Paper]:
    print("[Fallback] Using hardcoded papers...")
    return [
        Paper(
            title="Gut microbiome and depression: what we know and what we need to know",
            abstract="The gut microbiome has emerged as a key regulator of brain function and behavior. Dysbiosis of the gut microbiota has been implicated in the pathogenesis of psychiatric disorders, including depression.",
            year=2019,
            url="https://example.com/paper1"
        ),
        Paper(
            title="The microbiome-gut-brain axis in health and disease",
            abstract="We review the evidence for the role of the microbiome-gut-brain axis in psychiatric and neurological disorders, highlighting potential mechanisms and therapeutic opportunities.",
            year=2021,
            url="https://example.com/paper2"
        ),
        Paper(
            title="Probiotics for the treatment of depression",
            abstract="Clinical trials have shown mixed results regarding the efficacy of probiotics for treating depressive symptoms. More targeted interventions are needed.",
            year=2022,
            url="https://example.com/paper3"
        )
    ]

def _arxiv_fallback(query: str, limit: int) -> list[Paper]:
    print("[Fallback] Using ArXiv API...")
    url = f"http://export.arxiv.org/api/query?search_query=all:{query.replace(' ', '+')}&start=0&max_results={limit}"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        papers = []
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            title = entry.find("{http://www.w3.org/2005/Atom}title").text.strip().replace('\n', ' ')
            abstract = entry.find("{http://www.w3.org/2005/Atom}summary").text.strip().replace('\n', ' ')
            url_link = entry.find("{http://www.w3.org/2005/Atom}id").text.strip()
            published = entry.find("{http://www.w3.org/2005/Atom}published").text
            year = int(published[:4]) if published else None
            papers.append(Paper(title=title, abstract=abstract, year=year, url=url_link))
        
        if not papers:
            return _hardcoded_fallback()
        return papers
    except Exception as e:
        print(f"ArXiv API failed: {e}")
        return _hardcoded_fallback()

def search_papers(query: str, limit: int = 8) -> list[Paper]:
    """
    Search for papers. Tries Semantic Scholar -> ArXiv -> Hardcoded Fallback
    """
    print(f"Searching for papers related to: '{query}'...")
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,authors,year,url"
    }
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    try:
        r = requests.get(url, params=params, headers=headers, timeout=5)
        r.raise_for_status()
        data = r.json().get("data", [])
        
        papers = []
        for item in data:
            if not item.get("abstract"): # skip papers without abstract
                continue
            papers.append(Paper(
                title=item.get("title", ""),
                abstract=item.get("abstract", ""),
                year=item.get("year"),
                url=item.get("url")
            ))
        
        if not papers:
            return _arxiv_fallback(query, limit)
        return papers
    except Exception as e:
        print(f"Semantic Scholar API failed ({e}). Falling back to ArXiv...")
        return _arxiv_fallback(query, limit)

if __name__ == "__main__":
    results = search_papers("role of gut microbiome in depression", limit=3)
    for p in results:
        print(f"- {p.title} ({p.year})")
