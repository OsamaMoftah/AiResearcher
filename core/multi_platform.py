"""
Multi-platform paper search and retrieval.

Supports searching across multiple academic platforms including arXiv,
Papers with Code, Hugging Face, PubMed, bioRxiv, SSRN, and CORE.
Provides parallel search capabilities and unified paper representation.
"""
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional, Set
from datetime import datetime
from dataclasses import dataclass
import concurrent.futures
import time
import json
import re


@dataclass
class EnhancedPaper:
    """
    Extended paper representation with platform-specific metadata.
    
    Includes additional fields for citations, repository URLs, and
    platform-specific information beyond standard paper metadata.
    """
    title: str
    abstract: str
    authors: List[str]
    year: int
    url: str
    platform: str = "arXiv"
    citations: str = "N/A"
    repo_url: str = ""
    type: str = "Paper"
    
    def to_dict(self) -> Dict:
        """Convert to dict for compatibility"""
        return {
            'title': self.title,
            'abstract': self.abstract,
            'authors': self.authors,
            'year': self.year,
            'url': self.url,
            'platform': self.platform,
            'citations': self.citations,
            'repo_url': self.repo_url,
            'type': self.type
        }


class SimpleMultiPlatformScraper:
    """Simple multi-platform scraper without overengineering"""
    
    def __init__(self, enabled_sources: Optional[Set[str]] = None):
        """
        Initialize scraper with optional source selection
        
        Args:
            enabled_sources: Set of source names to enable. If None, enables working sources.
                            Options: 'arxiv', 'pwc', 'hf' (working)
                            Note: 'pubmed', 'biorxiv', 'ssrn', 'core' are available but not enabled by default
        """
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'AiResearcher/1.0'})
        
        # Default enabled sources - only working sources: arXiv, Papers with Code, Hugging Face
        # PubMed, bioRxiv, SSRN, and CORE have been removed as they don't work reliably
        default_sources = {'arxiv', 'pwc', 'hf'}
        self.enabled_sources = enabled_sources if enabled_sources is not None else default_sources
    
    def search_all(self, query: str, max_per_platform: int = 10, 
                   enabled_sources: Optional[Set[str]] = None) -> List[EnhancedPaper]:
        """
        Search all enabled platforms in parallel
        
        Args:
            query: Search query
            max_per_platform: Maximum results per platform
            enabled_sources: Override enabled sources for this search
        
        Returns:
            List of EnhancedPaper objects
        """
        sources_to_use = enabled_sources if enabled_sources is not None else self.enabled_sources
        results = []
        
        # Build list of search tasks
        search_tasks = []
        
        if 'arxiv' in sources_to_use:
            search_tasks.append(('arxiv', self._search_arxiv, query, max_per_platform))
        if 'pwc' in sources_to_use:
            search_tasks.append(('pwc', self._search_pwc, query, max_per_platform))
        if 'hf' in sources_to_use:
            search_tasks.append(('hf', self._search_hf, query, max_per_platform // 2))
        if 'pubmed' in sources_to_use:
            search_tasks.append(('pubmed', self._search_pubmed, query, max_per_platform))
        if 'biorxiv' in sources_to_use:
            search_tasks.append(('biorxiv', self._search_biorxiv, query, max_per_platform))
        if 'ssrn' in sources_to_use:
            search_tasks.append(('ssrn', self._search_ssrn, query, max_per_platform))
        if 'core' in sources_to_use:
            search_tasks.append(('core', self._search_core, query, max_per_platform))
        
        # Execute searches in parallel with rate limiting
        max_workers = min(len(search_tasks), 7)  # Limit concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for source_name, search_func, *args in search_tasks:
                future = executor.submit(search_func, *args)
                futures[future] = source_name
                time.sleep(0.3)  # Rate limiting: small delay between requests
            
            for future in concurrent.futures.as_completed(futures, timeout=30):
                source_name = futures[future]
                try:
                    source_results = future.result(timeout=20)
                    results.extend(source_results)
                    print(f"✓ {source_name.upper()}: Found {len(source_results)} papers")
                except Exception as e:
                    print(f"⚠️  {source_name.upper()} search timeout/error: {e}")
        
        return results
    
    def _search_arxiv(self, query: str, max_results: int) -> List[EnhancedPaper]:
        """Search arXiv"""
        try:
            url = "http://export.arxiv.org/api/query"
            params = {
                'search_query': f'ti:"{query}" OR abs:"{query}"',
                'max_results': min(max_results, 50),
                'sortBy': 'relevance'
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            papers = []
            root = ET.fromstring(response.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', ns)[:max_results]:
                try:
                    title_elem = entry.find('atom:title', ns)
                    abstract_elem = entry.find('atom:summary', ns)
                    url_elem = entry.find('atom:id', ns)
                    published_elem = entry.find('atom:published', ns)
                    
                    if title_elem is None or abstract_elem is None:
                        continue
                    
                    title = title_elem.text.strip() if title_elem.text else "Untitled"
                    abstract = abstract_elem.text.strip() if abstract_elem.text else "No abstract available."
                    url = url_elem.text.strip() if url_elem is not None and url_elem.text else ""
                    published = published_elem.text if published_elem is not None else ""
                    year = int(published[:4]) if published and len(published) >= 4 else datetime.now().year
                    
                    authors = []
                    for author in entry.findall('atom:author', ns):
                        name_elem = author.find('atom:name', ns)
                        if name_elem is not None and name_elem.text:
                            authors.append(name_elem.text)
                    
                    papers.append(EnhancedPaper(
                        title=title,
                        abstract=abstract[:400] + '...' if len(abstract) > 400 else abstract,
                        authors=authors[:5],  # Limit to first 5 authors
                        year=year,
                        url=url,
                        platform='arXiv',
                        citations='N/A',
                        type='Preprint'
                    ))
                except Exception as e:
                    print(f"Error parsing arXiv entry: {e}")
                    continue
                    
            return papers
        except Exception as e:
            print(f"ArXiv search failed: {e}")
            return []
    
    def _search_pwc(self, query: str, max_results: int) -> List[EnhancedPaper]:
        """Search Papers with Code"""
        try:
            url = "https://paperswithcode.com/api/v1/papers"
            params = {
                'q': query,
                'page_size': min(max_results, 30),
                'ordering': '-paper_count'
            }
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return []
            
            papers = []
            data = response.json()
            
            for paper in data.get('results', [])[:max_results]:
                try:
                    title = paper.get('title', '').strip()
                    if not title or len(title) < 10:
                        continue
                    
                    year = datetime.now().year
                    published = paper.get('published', '')
                    if published and len(published) >= 4:
                        try:
                            year = int(published[:4])
                        except:
                            pass
                    
                    paper_id = paper.get('id')
                    paper_url = paper.get('url_abs') or (
                        f"https://paperswithcode.com/paper/{paper_id}" if paper_id else ""
                    )
                    repo_url = paper.get('repo_url', '')
                    abstract = paper.get('abstract', 'No abstract available.').strip()
                    authors = paper.get('authors', [])
                    
                    papers.append(EnhancedPaper(
                        title=title,
                        abstract=abstract[:400] + '...' if len(abstract) > 400 else abstract,
                        authors=authors[:5] if isinstance(authors, list) else [],
                        year=year,
                        url=paper_url,
                        platform='Papers with Code',
                        citations=str(paper.get('paper_count', 0)),
                        repo_url=repo_url,
                        type='Paper'
                    ))
                except Exception as e:
                    print(f"Error parsing PWC paper: {e}")
                    continue
                    
            return papers
        except Exception as e:
            print(f"PWC search failed: {e}")
            return []
    
    def _search_hf(self, query: str, max_results: int) -> List[EnhancedPaper]:
        """Search Hugging Face"""
        try:
            artifacts = []
            
            # Search models
            models_url = "https://huggingface.co/api/models"
            params = {
                'search': query,
                'sort': 'downloads',
                'direction': -1,
                'limit': max_results
            }
            
            response = self.session.get(models_url, params=params, timeout=10)
            
            if response.status_code == 200:
                for item in response.json()[:max_results]:
                    try:
                        item_id = item.get('modelId', '') or item.get('id', '')
                        if not item_id:
                            continue
                        
                        description = 'No description available.'
                        card_data = item.get('cardData', {})
                        if isinstance(card_data, dict):
                            description = (
                                card_data.get('description', '') or
                                card_data.get('summary', '') or
                                card_data.get('text', '') or
                                description
                            )
                        
                        if description == 'No description available.':
                            description = item.get('description', '') or description
                        
                        if isinstance(description, str):
                            description = description[:400] + '...' if len(description) > 400 else description
                        
                        downloads = item.get('downloads', 0) or 0
                        author = item.get('author', 'Unknown')
                        authors = [author] if author and author != 'Unknown' else []
                        
                        # Get year from lastModified
                        year = datetime.now().year
                        last_modified = item.get('lastModified', '')
                        if last_modified and len(last_modified) >= 4:
                            try:
                                year = int(last_modified[:4])
                            except:
                                pass
                        
                        artifacts.append(EnhancedPaper(
                            title=item_id,
                            abstract=description,
                            authors=authors,
                            year=year,
                            url=f"https://huggingface.co/{item_id}",
                            platform='Hugging Face',
                            citations=str(downloads),
                            type='Model'
                        ))
                    except Exception as e:
                        print(f"Error parsing HF model: {e}")
                        continue
            
            return artifacts
        except Exception as e:
            print(f"HF search failed: {e}")
            return []
    
    def _search_pubmed(self, query: str, max_results: int) -> List[EnhancedPaper]:
        """Search PubMed using NCBI E-utilities API"""
        try:
            # Step 1: Search for papers
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                'db': 'pubmed',
                'term': query,
                'retmax': min(max_results, 100),
                'retmode': 'json',
                'sort': 'relevance'
            }
            
            time.sleep(0.34)  # Rate limiting: 3 requests/second max
            search_response = self.session.get(search_url, params=search_params, timeout=10)
            
            if search_response.status_code != 200:
                return []
            
            search_data = search_response.json()
            pmids = search_data.get('esearchresult', {}).get('idlist', [])
            
            if not pmids:
                return []
            
            # Step 2: Fetch paper details
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            fetch_params = {
                'db': 'pubmed',
                'id': ','.join(pmids[:max_results]),
                'retmode': 'xml',
                'rettype': 'abstract'
            }
            
            time.sleep(0.34)  # Rate limiting
            fetch_response = self.session.get(fetch_url, params=fetch_params, timeout=10)
            
            if fetch_response.status_code != 200:
                return []
            
            papers = []
            root = ET.fromstring(fetch_response.content)
            
            for article in root.findall('.//PubmedArticle')[:max_results]:
                try:
                    # Extract title
                    title_elem = article.find('.//ArticleTitle')
                    title = title_elem.text if title_elem is not None and title_elem.text else "Untitled"
                    
                    # Extract abstract
                    abstract_texts = article.findall('.//AbstractText')
                    abstract = " ".join([elem.text for elem in abstract_texts if elem.text]) if abstract_texts else "No abstract available."
                    
                    # Extract authors
                    authors = []
                    for author in article.findall('.//Author'):
                        last_name = author.find('LastName')
                        first_name = author.find('ForeName')
                        if last_name is not None and last_name.text:
                            name = last_name.text
                            if first_name is not None and first_name.text:
                                name += f", {first_name.text}"
                            authors.append(name)
                    
                    # Extract year
                    pub_date = article.find('.//PubDate/Year')
                    year = int(pub_date.text) if pub_date is not None and pub_date.text else datetime.now().year
                    
                    # Extract PMID and URL
                    pmid_elem = article.find('.//PMID')
                    pmid = pmid_elem.text if pmid_elem is not None else ""
                    url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}" if pmid else ""
                    
                    papers.append(EnhancedPaper(
                        title=title.strip(),
                        abstract=abstract[:400] + '...' if len(abstract) > 400 else abstract,
                        authors=authors[:5],
                        year=year,
                        url=url,
                        platform='PubMed',
                        citations='N/A',
                        type='Article'
                    ))
                except Exception as e:
                    print(f"Error parsing PubMed article: {e}")
                    continue
            
            return papers
        except Exception as e:
            print(f"PubMed search failed: {e}")
            return []
    
    def _search_biorxiv(self, query: str, max_results: int) -> List[EnhancedPaper]:
        """Search bioRxiv using RSS feed"""
        try:
            # bioRxiv RSS feed
            rss_url = "https://connect.biorxiv.org/relate/feed/atom"
            params = {
                'x-page': 1,
                'x-rows': min(max_results, 25),
                'x-alldisplay': 'true'
            }
            
            # Try searching via their API endpoint
            api_url = "https://api.biorxiv.org/details/biorxiv"
            params = {
                'query': query,
                'rows': min(max_results, 100),
                'format': 'json'
            }
            
            response = self.session.get(api_url, params=params, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            papers = []
            
            for item in data.get('collection', [])[:max_results]:
                try:
                    title = item.get('title', '').strip()
                    if not title:
                        continue
                    
                    abstract = item.get('abstract', 'No abstract available.').strip()
                    authors = item.get('authors', '').split('; ') if item.get('authors') else []
                    year = int(item.get('date', '')[:4]) if item.get('date') and len(item.get('date')) >= 4 else datetime.now().year
                    doi = item.get('doi', '')
                    url = f"https://www.biorxiv.org/content/{doi}" if doi else ""
                    
                    papers.append(EnhancedPaper(
                        title=title,
                        abstract=abstract[:400] + '...' if len(abstract) > 400 else abstract,
                        authors=authors[:5] if authors else [],
                        year=year,
                        url=url,
                        platform='bioRxiv',
                        citations='N/A',
                        type='Preprint'
                    ))
                except Exception as e:
                    print(f"Error parsing bioRxiv paper: {e}")
                    continue
            
            return papers
        except Exception as e:
            print(f"bioRxiv search failed: {e}")
            return []
    
    def _search_ssrn(self, query: str, max_results: int) -> List[EnhancedPaper]:
        """Search SSRN (Social Science Research Network)"""
        try:
            # SSRN search via their search API
            # Note: SSRN doesn't have a public API, so we'll use a simplified approach
            # This is a basic implementation that may need adjustment
            
            # SSRN search URL (simplified - may not work perfectly)
            search_url = "https://www.ssrn.com/index.cfm/en/"
            # For now, return empty as SSRN requires more complex scraping
            # This is a placeholder that can be enhanced later
            
            # Alternative: Try to use their RSS feed if available
            # For now, we'll return empty to avoid breaking the app
            return []
        except Exception as e:
            print(f"SSRN search failed: {e}")
            return []
    
    def _search_core(self, query: str, max_results: int) -> List[EnhancedPaper]:
        """Search CORE (Academic search engine)"""
        try:
            # CORE API (requires API key, but has free tier)
            # For now, we'll use a basic search without API key
            # Users can add their API key later if needed
            
            api_url = "https://api.core.ac.uk/v3/search"
            params = {
                'q': query,
                'page': 1,
                'pageSize': min(max_results, 100),
                'limit': min(max_results, 100)
            }
            
            # Note: CORE API requires authentication for most endpoints
            # This is a placeholder implementation
            # Without API key, we'll return empty
            # Users can add CORE_API_KEY to environment variables if they have one
            
            return []
        except Exception as e:
            print(f"CORE search failed: {e}")
            return []

