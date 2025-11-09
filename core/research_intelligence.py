"""
Research intelligence and field analysis.

Extracts themes, trends, and field context from research papers to provide
domain-specific knowledge for enhanced analysis.
"""
from typing import List, Dict, Any, Optional
from .arxiv import Paper
from .llm import LLM
import re
import json
from collections import Counter, defaultdict
from datetime import datetime


class ResearchIntelligence:
    """
    Extracts research themes, methodology combinations, and temporal trends.
    
    Analyzes papers to identify common themes, methodology patterns, and
    temporal trends that provide context for research analysis.
    """
    
    def __init__(self, llm: Optional[LLM] = None):
        self.llm = llm or LLM()
    
    def extract_research_themes(self, papers: List[Paper], topic: str) -> Dict[str, Any]:
        """Extract 8 research dimensions/themes from papers"""
        if not papers:
            return {"themes": [], "methodologies": [], "applications": []}
        
        # For large paper sets, use batch processing
        papers_to_analyze = papers[:20] if len(papers) > 20 else papers
        
        # Prepare paper summaries
        papers_text = "\n\n".join([
            f"PAPER {i+1}:\nTitle: {p.title}\nAbstract: {p.abstract[:500]}\nAuthors: {', '.join(p.authors[:3])}\nYear: {p.year}"
            for i, p in enumerate(papers_to_analyze)
        ])
        
        prompt = f"""You are a research analyst extracting key themes from papers on "{topic}".

PAPERS:
{papers_text}

Extract research themes across 8 dimensions:
1. **Architectures** - Model architectures, network designs (e.g., "Transformer variants", "CNN architectures")
2. **Paradigms** - Learning paradigms, approaches (e.g., "Self-supervised learning", "Few-shot learning")
3. **Applications** - Real-world applications, domains (e.g., "Computer vision", "NLP", "Healthcare")
4. **Datasets** - Key datasets used (e.g., "ImageNet", "COCO", "GLUE")
5. **Optimization** - Training methods, optimization techniques (e.g., "Adam variants", "Learning rate schedules")
6. **Evaluation** - Metrics, benchmarks (e.g., "Accuracy", "BLEU", "F1-score")
7. **Challenges** - Problems addressed (e.g., "Overfitting", "Scalability", "Interpretability")
8. **Trends** - Emerging directions (e.g., "Efficient models", "Multimodal learning")

For each dimension, list 3-5 specific themes found in these papers.

Return JSON:
{{
  "themes": {{
    "architectures": ["theme1", "theme2", "theme3"],
    "paradigms": ["theme1", "theme2"],
    "applications": ["theme1", "theme2", "theme3"],
    "datasets": ["dataset1", "dataset2"],
    "optimization": ["method1", "method2"],
    "evaluation": ["metric1", "metric2"],
    "challenges": ["challenge1", "challenge2"],
    "trends": ["trend1", "trend2"]
  }},
  "methodologies": ["method1", "method2", "method3"],
  "applications": ["app1", "app2", "app3"]
}}"""
        
        response = self.llm.call(prompt, max_tokens=2048)
        themes_data = self.llm.extract_json(response)
        
        # Handle case where themes_data might be a list or None
        if isinstance(themes_data, list):
            # If we got a list, convert to expected dict structure
            print("⚠️  Warning: Research intelligence returned a list instead of dict for themes, using fallback")
            themes_data = None
        elif not isinstance(themes_data, dict):
            themes_data = None
        
        if not themes_data:
            # Fallback: extract from titles/abstracts
            themes_data = self._extract_themes_fallback(papers, topic)
        
        return themes_data
    
    def _extract_themes_fallback(self, papers: List[Paper], topic: str) -> Dict[str, Any]:
        """Fallback theme extraction using keyword matching"""
        all_text = " ".join([p.title + " " + p.abstract[:200] for p in papers])
        words = re.findall(r'\b[a-z]{4,}\b', all_text.lower())
        common_words = [w for w, count in Counter(words).most_common(20) if count >= 2]
        
        return {
            "themes": {
                "architectures": common_words[:3],
                "paradigms": common_words[3:6],
                "applications": [topic],
                "datasets": [],
                "optimization": [],
                "evaluation": [],
                "challenges": [],
                "trends": []
            },
            "methodologies": common_words[:5],
            "applications": [topic]
        }
    
    def analyze_methodology_combinations(self, papers: List[Paper]) -> List[Dict[str, Any]]:
        """Find intersection opportunities between methodologies"""
        if not papers:
            return []
        
        # For large paper sets, limit to top papers
        papers_to_analyze = papers[:15] if len(papers) > 15 else papers
        
        papers_text = "\n".join([
            f"{i+1}. {p.title}: {p.abstract[:300]}"
            for i, p in enumerate(papers_to_analyze)
        ])
        
        prompt = f"""Analyze these papers and identify methodology combinations that could be promising:

PAPERS:
{papers_text}

Look for:
1. Methods from different papers that could be combined
2. Techniques that complement each other
3. Unexplored intersections

Return JSON array:
[
  {{
    "combination": "Method A from Paper 1 + Method B from Paper 2",
    "rationale": "Why this combination is promising",
    "papers_involved": [1, 2],
    "opportunity_score": 8
  }}
]"""
        
        response = self.llm.call(prompt, max_tokens=1536)
        combinations = self.llm.extract_json(response)
        
        if not combinations or not isinstance(combinations, list):
            return []
        
        return combinations
    
    def analyze_temporal_trends(self, papers: List[Paper]) -> Dict[str, Any]:
        """Analyze year-over-year patterns"""
        if not papers:
            return {"trends": [], "year_distribution": {}}
        
        # Group by year
        year_counts = Counter(p.year for p in papers if p.year)
        years = sorted(year_counts.keys())
        
        # Extract trends from abstracts/titles
        recent_papers = [p for p in papers if p.year and p.year >= max(years) - 2] if years else []
        older_papers = [p for p in papers if p.year and p.year < max(years) - 2] if years else []
        
        if not recent_papers:
            return {
                "trends": ["Insufficient data for trend analysis"],
                "year_distribution": dict(year_counts),
                "recent_focus": [],
                "evolution": "Cannot determine evolution with available data"
            }
        
        recent_text = " ".join([p.title + " " + p.abstract[:200] for p in recent_papers[:5]])
        older_text = " ".join([p.title + " " + p.abstract[:200] for p in older_papers[:5]]) if older_papers else ""
        
        prompt = f"""Analyze temporal trends in this research area:

RECENT PAPERS (last 2 years):
{recent_text}

OLDER PAPERS:
{older_text if older_text else "No older papers for comparison"}

Identify:
1. What's NEW in recent papers vs older ones?
2. What trends are emerging?
3. What's declining or being replaced?

Return JSON:
{{
  "trends": ["trend1", "trend2", "trend3"],
  "recent_focus": ["focus1", "focus2"],
  "evolution": "How the field has evolved"
}}"""
        
        response = self.llm.call(prompt, max_tokens=1024)
        trends_data = self.llm.extract_json(response)
        
        # Handle case where trends_data might be a list or None
        if isinstance(trends_data, list):
            # If we got a list, convert to expected dict structure
            print("⚠️  Warning: Research intelligence returned a list instead of dict for trends, using default")
            trends_data = None
        elif not isinstance(trends_data, dict):
            trends_data = None
        
        if not trends_data:
            trends_data = {
                "trends": ["Insufficient data"],
                "recent_focus": [],
                "evolution": "Cannot determine"
            }
        
        trends_data["year_distribution"] = dict(year_counts)
        return trends_data
    
    def identify_research_gaps(self, papers: List[Paper], themes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific, scored research gaps"""
        if not papers:
            return []
        
        themes_text = json.dumps(themes, indent=2)
        papers_text = "\n".join([
            f"{i+1}. {p.title}: {p.abstract[:300]}"
            for i, p in enumerate(papers[:8])
        ])
        
        prompt = f"""Based on these papers and themes, identify SPECIFIC research gaps:

THEMES IDENTIFIED:
{themes_text}

PAPERS:
{papers_text}

Find gaps that are:
1. SPECIFIC (not vague like "better methods needed")
2. ACTIONABLE (can be addressed with experiments)
3. IMPORTANT (high impact if solved)

For each gap, provide:
- Specific description
- Why it matters
- Opportunity score (0-10)
- Which themes it relates to

Return JSON array:
[
  {{
    "gap": "SPECIFIC gap description",
    "why_matters": "Why this gap is important",
    "opportunity_score": 8,
    "related_themes": ["theme1", "theme2"],
    "papers_affected": [1, 2]
  }}
]"""
        
        response = self.llm.call(prompt, max_tokens=2048)
        gaps = self.llm.extract_json(response)
        
        if not gaps or not isinstance(gaps, list):
            return []
        
        return gaps
    
    def generate_field_context(self, topic: str) -> str:
        """Generate domain knowledge context for agents"""
        prompt = f"""You are a domain expert in "{topic}". Provide a comprehensive field context including:

1. **Key Players**: Important researchers, labs, institutions in this field
2. **Seminal Papers**: Foundational papers everyone references
3. **Current Debates**: Active debates and open questions
4. **Common Methodologies**: Standard approaches used
5. **Known Limitations**: Well-known problems in the field
6. **Recent Trends**: What's hot right now
7. **Important Conferences/Journals**: Where this research is published

Be specific and reference real names, papers, and institutions when possible.

Format as a structured field context document."""
        
        response = self.llm.call(prompt, max_tokens=1536)
        
        # If response is too short, enhance it
        if len(response) < 200:
            enhanced_prompt = f"""Provide detailed field context for "{topic}". Include:
- 5-10 key researchers/labs
- 3-5 seminal papers
- 2-3 current debates
- Common methodologies
- Known limitations
- Recent trends (2023-2024)

Be specific with names and details."""
            response = self.llm.call(enhanced_prompt, max_tokens=1536)
        
        return response if response else f"Field context for {topic}: Active research area with ongoing developments."
    
    def get_top_authors(self, papers: List[Paper], top_n: int = 5) -> List[Dict[str, Any]]:
        """Extract top authors by paper count"""
        author_counts = Counter()
        author_papers = defaultdict(list)
        
        for paper in papers:
            for author in paper.authors:
                if author and author.strip():
                    author_counts[author] += 1
                    author_papers[author].append(paper.title)
        
        top_authors = []
        for author, count in author_counts.most_common(top_n):
            top_authors.append({
                "name": author,
                "paper_count": count,
                "sample_papers": author_papers[author][:3]
            })
        
        return top_authors

