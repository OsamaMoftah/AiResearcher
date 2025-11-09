"""
arXiv paper search and data retrieval.

Provides functionality to search and retrieve academic papers
from the arXiv preprint repository.
"""
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Paper:
    """Represents an academic paper with metadata."""
    title: str
    abstract: str
    authors: List[str]
    year: int
    url: str

def search_arxiv(query: str, max_results: int = 5) -> List[Paper]:
    """
    Search arXiv for papers matching the query.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of Paper objects
    """
    url = "http://export.arxiv.org/api/query"
    # Limit to 100 papers to balance response time and completeness
    params = {
        "search_query": f'all:"{query}"',
        "max_results": min(max_results, 100),
        "sortBy": "relevance"
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        papers = []
        
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            try:
                title_elem = entry.find("{http://www.w3.org/2005/Atom}title")
                summary_elem = entry.find("{http://www.w3.org/2005/Atom}summary")
                link_elem = entry.find("{http://www.w3.org/2005/Atom}id")
                published_elem = entry.find("{http://www.w3.org/2005/Atom}published")
                
                if title_elem is None or summary_elem is None:
                    continue
                
                title = title_elem.text.strip() if title_elem.text else "Untitled"
                summary = summary_elem.text.strip() if summary_elem.text else "No abstract available."
                link = link_elem.text if link_elem is not None else ""
                authors = [a.find("{http://www.w3.org/2005/Atom}name").text 
                          for a in entry.findall("{http://www.w3.org/2005/Atom}author")
                          if a.find("{http://www.w3.org/2005/Atom}name") is not None and a.find("{http://www.w3.org/2005/Atom}name").text]
                published = published_elem.text if published_elem is not None else ""
                year = int(published[:4]) if published and len(published) >= 4 else 2024
                
                papers.append(Paper(
                    title=title,
                    abstract=summary,
                    authors=authors,
                    year=year,
                    url=link
                ))
            except Exception as e:
                print(f"Error parsing arXiv entry: {e}")
                continue
        
        return papers[:max_results]  # Ensure we don't return more than requested
    except Exception as e:
        print(f"Error searching arXiv: {e}")
        return []

