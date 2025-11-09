"""
AiResearcher web application.

Provides a multi-tab interface for research paper analysis and insight generation
using a specialized agent pipeline.
"""
import streamlit as st
from core.research import ResearchAgent
import json
from datetime import datetime
import html
import time
import re
from typing import Dict, List, Any

# MUST be first Streamlit command
st.set_page_config(
    page_title="AiResearcher",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Elegant Design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600&display=swap');
:root { --p: #D94B2B; --bg: #FAF9F7; --bg2: #F3F1ED; --txt: #2C2B27; --hov: #EBE8E3; --brd: #E0DED9; }
* { font-family: 'Space Grotesk', sans-serif !important; color: var(--txt); }
.stApp { background: var(--bg) !important; }
[data-testid="stSidebar"] { background: var(--bg2) !important; border-right: 1px solid var(--brd) !important; }
h1, h2, h3 { font-weight: 600 !important; letter-spacing: -0.02em; }
button[kind="primary"] { background: var(--p) !important; border-radius: 10px !important; border: none !important; padding: 0.6rem 1.2rem !important; font-weight: 500 !important; transition: all 0.2s; }
button[kind="primary"]:hover { background: #B63D23 !important; transform: scale(1.02); }
div[data-testid="stMetric"] { border-radius: 12px !important; background: white !important; padding: 1rem !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important; transition: transform 0.2s; }
div[data-testid="stMetric"]:hover { transform: translateY(-2px); background: var(--hov) !important; }
.stTextInput > div > div > input { border-radius: 10px !important; border: 1px solid var(--brd) !important; }
.stSlider > div > div > div { color: var(--p) !important; }
div[data-testid="stAlert"] { border-radius: 10px !important; border-left: 4px solid var(--p) !important; }

/* Enhanced insight cards */
.insight-card {
    background: white;
    border: 2px solid #E0DED9;
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.insight-header {
    font-size: 1.3em;
    font-weight: 600;
    color: #2C2B27;
    margin-bottom: 1rem;
    border-bottom: 2px solid #D94B2B;
    padding-bottom: 0.5rem;
}
.insight-section {
    margin: 1rem 0;
    padding: 1rem;
    background: #FAF9F7;
    border-radius: 8px;
}
.insight-section-title {
    font-weight: 600;
    color: #D94B2B;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    font-size: 0.85em;
    letter-spacing: 0.5px;
}
.timeline-item {
    padding: 1rem;
    margin: 0.5rem 0;
    background: white;
    border-left: 4px solid #D94B2B;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Paper card styles (AiResearcher style) */
.paper-card-ar {
    background: white;
    border: 1px solid var(--brd);
    border-radius: 12px;
    padding: 1.2rem;
    margin: 0.8rem 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    font-family: 'Space Grotesk', sans-serif;
}

.paper-badge-ar {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
}

.badge-arxiv-ar { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
.badge-pwc-ar { background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }
.badge-hf-ar { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
.badge-pubmed-ar { background: #e0e7ff; color: #3730a3; border: 1px solid #c7d2fe; }
.badge-biorxiv-ar { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
.badge-ssrn-ar { background: #fce7f3; color: #831843; border: 1px solid #fbcfe8; }
.badge-core-ar { background: #f3e8ff; color: #6b21a8; border: 1px solid #e9d5ff; }

/* Reasoning flow styles - updated for proper alignment with pastel colors */
.reasoning-flow {
    display: flex;
    justify-content: space-between;
    align-items: stretch;
    margin: 1.5rem 0;
    padding: 1rem;
    background: #FAF9F7;
    border-radius: 12px;
    gap: 0.5rem;
}
.reasoning-node {
    flex: 1;
    text-align: center;
    padding: 1rem;
    background: #FAF9F7;
    border: 2px solid #E0DED9;
    border-radius: 10px;
    font-size: 1em;
    color: #2C2B27;
    transition: all 0.2s;
    min-height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.reasoning-node:first-child { margin-left: 0; }
.reasoning-node:last-child { margin-right: 0; }
.reasoning-arrow {
    color: #5B574D;
    font-size: 1.5em;
    font-weight: bold;
    display: flex;
    align-items: center;
    margin: 0 0.25rem;
}

/* Timeline styles */
.timeline-container {
    display: flex;
    justify-content: space-between;
    margin: 1rem 0;
    padding: 1rem;
    background: #FAF9F7;
    border-radius: 12px;
}
.timeline-week {
    flex: 1;
    padding: 0.8rem;
    margin: 0 0.5rem;
    background: white;
    border: 1px solid #E0DED9;
    border-radius: 8px;
    text-align: center;
    font-size: 0.9em;
}
.timeline-deviation {
    border: 2px solid #D94B2B;
    background: #FFF5F3;
}

/* Roundtable styles */
.roundtable-container {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    grid-template-rows: auto auto auto;
    gap: 1rem;
    margin: 2rem 0;
    padding: 2rem;
    background: #FAF9F7;
    border-radius: 16px;
}
.agent-node {
    padding: 1rem;
    background: white;
    border: 2px solid #E0DED9;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.connection-line {
    stroke: #D94B2B;
    stroke-width: 2;
    fill: none;
}

/* Badge styles */
.mini-stat-badge {
    display: inline-block;
    background: #FAF9F7;
    color: #2C2B27;
    padding: 0.3rem 0.7rem;
    border-radius: 8px;
    font-size: 0.85em;
    font-weight: 500;
    border: 1px solid #E0DED9;
    margin-right: 0.5rem;
    transition: all 0.2s;
}
.mini-stat-badge:hover {
    background: #EBE8E3;
    transform: translateY(-1px);
}
.validation-badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 15px;
    font-size: 0.85em;
    font-weight: 600;
    color: white;
}

/* Summary styles */
.collective-summary {
    background: white;
    border: 2px solid #D94B2B;
    border-radius: 16px;
    padding: 1.5rem;
    margin: 2rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.meta-commentary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 2rem 0;
    text-align: center;
}

/* Dashboard Hero Section */
.hero-section {
    background: linear-gradient(135deg, #FAF9F7 0%, #F3F1ED 100%);
    border-radius: 20px;
    padding: 3rem 2rem;
    margin: 2rem 0;
    text-align: center;
    border: 2px solid #E0DED9;
}
.hero-title {
    font-size: 2.5em;
    font-weight: 600;
    color: #2C2B27;
    margin-bottom: 1rem;
    letter-spacing: -0.02em;
}
.hero-subtitle {
    font-size: 1.2em;
    color: #5B574D;
    margin-bottom: 2rem;
    line-height: 1.6;
}
.hero-cta {
    display: inline-block;
    margin: 0.5rem;
    padding: 0.8rem 1.5rem;
    background: #D94B2B;
    color: white;
    border-radius: 10px;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s;
}
.hero-cta:hover {
    background: #B63D23;
    transform: scale(1.05);
}

/* Pulsing animation for agent nodes */
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.85; transform: scale(1.05); }
}
.agent-node-pulse {
    animation: pulse 3s ease-in-out infinite;
}
.user-avatar-center {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 80px;
    height: 80px;
    background: linear-gradient(135deg, #D94B2B 0%, #B63D23 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2em;
    color: white;
    box-shadow: 0 4px 12px rgba(217, 75, 43, 0.3);
    z-index: 20;
    border: 4px solid white;
}

/* Bottleneck comparison */
.bottleneck-comparison {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin: 2rem 0;
}
.bottleneck-card {
    background: white;
    border: 2px solid #E0DED9;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.bottleneck-card.old-way {
    border-color: #9CA3AF;
}
.bottleneck-card.new-way {
    border-color: #D94B2B;
    background: #FFF5F3;
}
.bottleneck-title {
    font-size: 1.5em;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #2C2B27;
}
.bottleneck-item {
    padding: 0.8rem 0;
    border-bottom: 1px solid #E0DED9;
}
.bottleneck-item:last-child {
    border-bottom: none;
}

/* Metrics with context */
.metric-card {
    background: white;
    border: 2px solid #E0DED9;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.metric-value {
    font-size: 2em;
    font-weight: 600;
    color: #D94B2B;
    margin-bottom: 0.5rem;
}
.metric-label {
    font-size: 1.1em;
    font-weight: 500;
    color: #2C2B27;
    margin-bottom: 0.5rem;
}
.metric-context {
    font-size: 0.9em;
    color: #5B574D;
    font-style: italic;
}

/* Pipeline timeline */
.pipeline-timeline {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 2rem 0;
    padding: 1.5rem;
    background: #FAF9F7;
    border-radius: 12px;
}
.pipeline-step {
    flex: 1;
    text-align: center;
    padding: 1rem;
    margin: 0 0.5rem;
    background: white;
    border: 2px solid #E0DED9;
    border-radius: 10px;
    transition: all 0.3s;
}
.pipeline-step.complete {
    border-color: #10B981;
    background: #D1FAE5;
}
.pipeline-step.pending {
    border-color: #9CA3AF;
    opacity: 0.6;
}
.pipeline-arrow {
    color: #D94B2B;
    font-size: 1.5em;
    font-weight: bold;
}

/* Author cards */
.author-card {
    background: white;
    border: 2px solid #E0DED9;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.author-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}
.author-name {
    font-size: 1.3em;
    font-weight: 600;
    color: #2C2B27;
}
.author-paper-count {
    font-size: 0.9em;
    color: #5B574D;
}
.author-theme {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    background: #F0F4F8;
    color: #2C2B27;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 500;
    margin: 0.5rem 0.5rem 0.5rem 0;
    border: 1px solid #E0DED9;
}
.author-insight-link {
    display: inline-block;
    padding: 0.4rem 1rem;
    background: #2C2B27;
    color: white;
    border-radius: 8px;
    text-decoration: none;
    font-size: 0.9em;
    margin-top: 0.5rem;
    transition: all 0.2s;
}
.author-insight-link:hover {
    background: #5B574D;
}

/* Beyond Keywords */
.keywords-section {
    background: white;
    border: 2px solid #E0DED9;
    border-radius: 16px;
    padding: 2rem;
    margin: 2rem 0;
}
.concept-cluster {
    display: inline-block;
    padding: 0.5rem 1rem;
    background: #FAF9F7;
    color: #2C2B27;
    border-radius: 20px;
    margin: 0.5rem;
    font-size: 0.9em;
    border: 1px solid #E0DED9;
}
.field-summary {
    background: #FAF9F7;
    border-left: 3px solid #2C2B27;
    padding: 1.5rem;
    margin: 1.5rem 0;
    border-radius: 8px;
    line-height: 1.8;
    color: #2C2B27;
}

/* Collaboration flow */
.collaboration-flow {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 2rem 0;
    padding: 2rem;
    background: #FAF9F7;
    border-radius: 16px;
}
.flow-agent {
    flex: 1;
    text-align: center;
    padding: 1.5rem;
    margin: 0 0.5rem;
    background: white;
    border: 2px solid #E0DED9;
    border-radius: 12px;
    transition: all 0.2s;
}
.flow-agent:hover {
    border-color: #2C2B27;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.flow-arrow {
    color: #5B574D;
    font-size: 2em;
    font-weight: bold;
}

/* Dialogue bubbles */
.dialogue-bubble {
    background: white;
    border: 2px solid #E0DED9;
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    position: relative;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.dialogue-agent {
    font-weight: 600;
    color: #2C2B27;
    margin-bottom: 0.5rem;
}
.dialogue-text {
    color: #2C2B27;
    line-height: 1.6;
}

/* Use cases */
.use-case-card {
    background: white;
    border: 2px solid #E0DED9;
    border-radius: 12px;
    padding: 2rem;
    margin: 1rem 0;
    text-align: center;
    transition: all 0.2s;
}
.use-case-card:hover {
    border-color: #2C2B27;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.use-case-icon {
    font-size: 3em;
    margin-bottom: 1rem;
}
.use-case-title {
    font-size: 1.3em;
    font-weight: 600;
    color: #2C2B27;
    margin-bottom: 0.5rem;
}
.use-case-outcome {
    color: #5B574D;
    font-size: 0.9em;
    font-style: italic;
    margin-top: 1rem;
}

/* CTA Section */
.cta-section {
    background: #FAF9F7;
    color: #2C2B27;
    border-radius: 20px;
    padding: 3rem 2rem;
    margin: 3rem 0;
    text-align: center;
    border: 2px solid #E0DED9;
}
.cta-title {
    font-size: 2em;
    font-weight: 600;
    margin-bottom: 1rem;
}
.cta-text {
    font-size: 1.1em;
    line-height: 1.8;
    margin-bottom: 2rem;
    opacity: 0.95;
}
.cta-buttons {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
}
.cta-button {
    display: inline-block;
    padding: 1rem 2rem;
    background: white;
    color: #2C2B27;
    border-radius: 10px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.2s;
    border: 2px solid white;
}
.cta-button:hover {
    background: #FAF9F7;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)


def create_enhanced_paper_card(paper, index: int = 0):
    """Create an informative paper card in AiResearcher style"""
    # Handle both Paper dataclass and EnhancedPaper
    if hasattr(paper, 'to_dict'):
        p = paper.to_dict()
    elif hasattr(paper, '__dict__'):
        p = paper.__dict__
    else:
        p = paper if isinstance(paper, dict) else {
            'title': getattr(paper, 'title', 'Unknown'),
            'abstract': getattr(paper, 'abstract', ''),
            'authors': getattr(paper, 'authors', []),
            'year': getattr(paper, 'year', 2024),
            'url': getattr(paper, 'url', '#'),
            'platform': getattr(paper, 'platform', 'arXiv'),
            'citations': getattr(paper, 'citations', 'N/A'),
            'repo_url': getattr(paper, 'repo_url', ''),
            'type': getattr(paper, 'type', 'Paper')
        }
    
    # Get platform
    platform = str(p.get('platform', 'Unknown'))
    is_huggingface = 'Hugging Face' in platform
    
    # Process title - truncate long Hugging Face model names
    raw_title = str(p.get('title', 'Untitled'))
    if is_huggingface and '/' in raw_title:
        # For Hugging Face, show just the model name part
        title_parts = raw_title.split('/')
        if len(title_parts) > 1:
            display_title = title_parts[-1].replace('_', ' ').replace('-', ' ').title()
        else:
            display_title = raw_title
    else:
        display_title = raw_title
    
    # Clean up title
    title_clean = ' '.join(display_title.split())
    title_escaped = html.escape(title_clean)
    
    # Process authors
    authors = p.get('authors', [])
    if not authors or (len(authors) == 1 and str(authors[0]).strip() in ['Unknown', '']):
        if is_huggingface and '/' in raw_title:
            # Extract author from Hugging Face model path
            author_name = raw_title.split('/')[0]
            authors_str = html.escape(author_name)
        else:
            authors_str = "Unknown"
    else:
        authors_list = [str(a) for a in authors[:3] if a and str(a).strip() not in ['Unknown', '']]
        authors_str = ', '.join(authors_list)
        if len(authors) > 3:
            authors_str += ' et al.'
        authors_str = html.escape(authors_str) if authors_str else "Unknown"
    
    # Process abstract
    raw_abstract = str(p.get('abstract', ''))
    if not raw_abstract or raw_abstract.strip() in ['No description available.', '']:
        abstract_short = "No abstract available."
    else:
        abstract_short = raw_abstract[:200] + "..." if len(raw_abstract) > 200 else raw_abstract
    abstract_escaped = html.escape(abstract_short)
    
    year = p.get('year', 'N/A')
    citations = p.get('citations', 'N/A')
    paper_url = p.get('url', '#')
    repo_url = p.get('repo_url', '')
    
    # Platform badge class (AiResearcher style)
    badge_class = 'badge-arxiv-ar'
    platform_lower = platform.lower()
    if 'papers with code' in platform_lower or 'pwc' in platform_lower:
        badge_class = 'badge-pwc-ar'
    elif 'hugging face' in platform_lower or 'hf' in platform_lower:
        badge_class = 'badge-hf-ar'
    elif 'pubmed' in platform_lower:
        badge_class = 'badge-pubmed-ar'
    elif 'biorxiv' in platform_lower:
        badge_class = 'badge-biorxiv-ar'
    elif 'ssrn' in platform_lower:
        badge_class = 'badge-ssrn-ar'
    elif 'core' in platform_lower:
        badge_class = 'badge-core-ar'
    
    # Build metadata string
    metadata_parts = []
    if year != 'N/A':
        metadata_parts.append(f"<strong>Year:</strong> {year}")
    if citations != 'N/A':
        try:
            # Check if it's a number
            int(citations)
            metadata_parts.append(f"<strong>Citations:</strong> {citations}")
        except (ValueError, TypeError):
            if str(citations) != 'N/A':
                metadata_parts.append(f"<strong>Downloads:</strong> {citations}")
    metadata_str = " | ".join(metadata_parts) if metadata_parts else ""
    
    # Build metadata HTML
    metadata_html = ''
    if metadata_str:
        metadata_html = f'<span style="color: #5B574D; font-size: 0.9em;">{metadata_str}</span>'
    
    # Build links (AiResearcher simple style)
    links_html = ''
    if paper_url and paper_url != '#':
        view_text = 'View Model' if is_huggingface else 'View Paper'
        paper_url_escaped = html.escape(paper_url)
        links_html = f'<a href="{paper_url_escaped}" target="_blank" style="color: #D94B2B; text-decoration: none; font-weight: 500;">🔗 {view_text} →</a>'
        if repo_url and repo_url != '#':
            repo_url_escaped = html.escape(repo_url)
            links_html += f' | <a href="{repo_url_escaped}" target="_blank" style="color: #D94B2B; text-decoration: none; font-weight: 500;">💻 Code</a>'
    elif repo_url and repo_url != '#':
        repo_url_escaped = html.escape(repo_url)
        links_html = f'<a href="{repo_url_escaped}" target="_blank" style="color: #D94B2B; text-decoration: none; font-weight: 500;">🔗 View Code →</a>'
    
    # Build links section
    links_section = ''
    if links_html:
        links_section = f'<div style="margin-top: 0.8rem;">{links_html}</div>'
    
    # Create card in AiResearcher style
    card_html = f"""<div class="paper-card-ar">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
            <span class="paper-badge-ar {badge_class}">{html.escape(platform)}</span>
            {metadata_html}
        </div>
        <h4 style="margin-top: 0; margin-bottom: 0.5rem; color: #2C2B27; font-weight: 600;">{index + 1}. {title_escaped}</h4>
        <p style="color: #5B574D; margin: 0.5rem 0; font-size: 0.9em;"><strong>Authors:</strong> {authors_str}</p>
        <p style="color: #666; font-size: 0.9em; line-height: 1.5; margin: 0.8rem 0;">{abstract_escaped}</p>
        {links_section}
    </div>"""
    
    return card_html


def extract_insight_summary(insight: Dict) -> str:
    """Generate one-sentence summary from observation or hypothesis"""
    observation = insight.get('observation', '')
    hypothesis = insight.get('hypothesis', '')
    gap = insight.get('gap', '')
    
    # Prefer observation, then hypothesis, then gap
    source_text = observation or hypothesis or gap
    if not source_text:
        return "A promising research opportunity identified through multi-agent analysis."
    
    # Clean HTML comments from source text
    source_text = clean_html_comments(source_text)
    
    # Extract first sentence or first 150 chars
    sentences = source_text.split('.')
    if sentences and len(sentences[0]) > 20:
        summary = sentences[0].strip()
        if not summary.endswith('.'):
            summary += '.'
        if len(summary) > 150:
            summary = summary[:147] + '...'
        return summary
    else:
        # Fallback: use first 150 chars
        summary = source_text[:150].strip()
        if len(source_text) > 150:
            summary += '...'
        return summary


def extract_evidence_links(insight: Dict) -> List[Dict[str, str]]:
    """Parse validation_evidence and related_work for paper links"""
    links = []
    
    # Extract from validation_evidence
    validation_evidence = insight.get('validation_evidence', '')
    if validation_evidence:
        # Look for paper titles or arXiv IDs in the text
        # Simple pattern matching - can be improved
        # Look for patterns like "Paper Title (arXiv)" or "Paper Title (2024)"
        patterns = re.findall(r'([A-Z][^()]+?)\s*\([^)]*(?:arXiv|arxiv|paper|202[0-9]|202[0-9])[^)]*\)', validation_evidence)
        for pattern in patterns[:3]:  # Limit to 3
            links.append({'title': pattern.strip(), 'source': 'validation'})
    
    # Extract from related_work
    related_work = insight.get('related_work', [])
    if isinstance(related_work, list):
        for work in related_work[:3]:  # Limit to 3
            if isinstance(work, str):
                links.append({'title': work, 'source': 'related_work'})
    
    return links


def clean_html_comments(text: str) -> str:
    """
    Removes HTML comments from text content.
    
    HTML comments can interfere with markdown rendering and should be
    removed before display. Handles both single-line and multiline comments.
    
    Args:
        text: Text content that may contain HTML comments
        
    Returns:
        Text with HTML comments removed and whitespace normalized
    """
    if not text:
        return text
    
    # Remove HTML comment blocks using non-greedy matching for multiline comments
    cleaned = re.sub(r'<!--.*?-->', '', str(text), flags=re.DOTALL)
    
    # Normalize excessive line breaks created by removed comments
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned


def strip_html_tags(text: str) -> str:
    """
    Strip HTML tags from text, leaving only plain text content.
    
    Args:
        text: Text content that may contain HTML tags
    
    Returns:
        Text with HTML tags removed and HTML entities decoded
    """
    if not text:
        return ""
    # Remove HTML tags using regex
    text = re.sub(r'<[^>]+>', '', str(text))
    # Decode HTML entities (e.g., &lt; becomes <, &amp; becomes &)
    text = html.unescape(text)
    return text.strip()


def create_styled_content_box(content: str, box_type: str = "info") -> str:
    """Create a styled content box with AiResearcher pastel design
    
    Args:
        content: The text content to display
        box_type: Type of box - "info", "success", "warning", or "observation"
    
    Returns:
        HTML string for the styled box
    """
    # Pastel colors based on box type
    color_schemes = {
        "info": {
            "bg": "#F0F4F8",  # Analyzer pastel blue
            "border": "#6B8DD6",
            "icon": "ℹ️"
        },
        "success": {
            "bg": "#F5F9F6",  # Synthesizer pastel green
            "border": "#9FC5A8",
            "icon": "✓"
        },
        "warning": {
            "bg": "#FEF9E7",  # Light pastel yellow
            "border": "#F59E0B",
            "icon": "⚠️"
        },
        "observation": {
            "bg": "#FAF5F5",  # Skeptic pastel red
            "border": "#C99A9A",
            "icon": "🔍"
        }
    }
    
    scheme = color_schemes.get(box_type, color_schemes["info"])
    
    # Clean HTML comments before escaping
    content_cleaned = clean_html_comments(str(content))
    content_escaped = html.escape(content_cleaned)
    
    return f"""
    <div style="
        background: {scheme['bg']};
        border: 1px solid {scheme['border']};
        border-left: 3px solid {scheme['border']};
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #2C2B27;
        line-height: 1.8;
        font-size: 1.05em;
        font-weight: 400;
    ">
        {content_escaped}
    </div>
    """


def create_reasoning_flow(insight: Dict) -> str:
    """Generate HTML/CSS for horizontal reasoning flow diagram with AiResearcher pastel colors"""
    observation = insight.get('observation', '')
    hypothesis = insight.get('hypothesis', '')
    exp_design = insight.get('experiment_design', {})
    validation_evidence = insight.get('validation_evidence', '')
    
    # Check if each step is complete
    has_observation = bool(observation or insight.get('gap', ''))
    has_hypothesis = bool(hypothesis)
    has_experiment = bool(exp_design)
    has_validation = bool(validation_evidence)
    
    # Clean HTML comments and get brief text for each node (truncate if too long)
    observation_cleaned = clean_html_comments(observation) if observation else ''
    hypothesis_cleaned = clean_html_comments(hypothesis) if hypothesis else ''
    gap_cleaned = clean_html_comments(insight.get('gap', '')) if insight.get('gap') else ''
    
    obs_text = (observation_cleaned[:50] + '...') if observation_cleaned and len(observation_cleaned) > 50 else (observation_cleaned or (gap_cleaned[:50] if gap_cleaned else 'Observation'))
    hyp_text = (hypothesis_cleaned[:50] + '...') if hypothesis_cleaned and len(hypothesis_cleaned) > 50 else (hypothesis_cleaned or 'Hypothesis')
    exp_text = 'Experiment Designed' if exp_design else 'Experiment'
    val_text = 'Validated' if validation_evidence else 'Validation'
    
    # Use AiResearcher pastel colors from AGENT_STYLES
    # Analyzer (Observation), Synthesizer (Hypothesis), Synthesizer (Experiment), Validator (Validation)
    analyzer_style = AGENT_STYLES.get("Analyzer", {"color": "#6B8DD6", "bg": "#F0F4F8"})
    synthesizer_style = AGENT_STYLES.get("Synthesizer", {"color": "#9FC5A8", "bg": "#F5F9F6"})
    validator_style = AGENT_STYLES.get("Validator", {"color": "#B8A9D9", "bg": "#F7F5FA"})
    
    # Node colors - use pastel colors for active nodes, light gray for inactive
    obs_color = analyzer_style["color"] if has_observation else "#E0DED9"
    obs_bg = analyzer_style["bg"] if has_observation else "#FAF9F7"
    hyp_color = synthesizer_style["color"] if has_hypothesis else "#E0DED9"
    hyp_bg = synthesizer_style["bg"] if has_hypothesis else "#FAF9F7"
    exp_color = synthesizer_style["color"] if has_experiment else "#E0DED9"
    exp_bg = synthesizer_style["bg"] if has_experiment else "#FAF9F7"
    val_color = validator_style["color"] if has_validation else "#E0DED9"
    val_bg = validator_style["bg"] if has_validation else "#FAF9F7"
    
    # Escape text before using in f-string to avoid shadowing html module
    obs_escaped = html.escape(obs_text[:60])
    hyp_escaped = html.escape(hyp_text[:60])
    exp_escaped = html.escape(exp_text[:60])
    val_escaped = html.escape(val_text[:60])
    
    html_str = f"""
    <div class="reasoning-flow" style="display: flex; justify-content: space-between; align-items: stretch; margin: 1.5rem 0; padding: 1rem; background: #FAF9F7; border-radius: 12px; gap: 0.5rem;">
        <div class="reasoning-node" style="flex: 1; text-align: center; padding: 1rem; background: {obs_bg}; border: 2px solid {obs_color}; border-radius: 10px; min-height: 120px; display: flex; flex-direction: column; justify-content: center;">
            <div style="font-weight: 600; color: {obs_color}; margin-bottom: 0.5rem; font-size: 1.1em;">🔍 Observation</div>
            <div style="font-size: 1em; color: #5B574D; line-height: 1.6;">{obs_escaped}</div>
        </div>
        <div class="reasoning-arrow" style="color: #5B574D; font-size: 1.5em; font-weight: bold; display: flex; align-items: center; margin: 0 0.25rem;">→</div>
        <div class="reasoning-node" style="flex: 1; text-align: center; padding: 1rem; background: {hyp_bg}; border: 2px solid {hyp_color}; border-radius: 10px; min-height: 120px; display: flex; flex-direction: column; justify-content: center;">
            <div style="font-weight: 600; color: {hyp_color}; margin-bottom: 0.5rem; font-size: 1.1em;">💡 Hypothesis</div>
            <div style="font-size: 1em; color: #5B574D; line-height: 1.6;">{hyp_escaped}</div>
        </div>
        <div class="reasoning-arrow" style="color: #5B574D; font-size: 1.5em; font-weight: bold; display: flex; align-items: center; margin: 0 0.25rem;">→</div>
        <div class="reasoning-node" style="flex: 1; text-align: center; padding: 1rem; background: {exp_bg}; border: 2px solid {exp_color}; border-radius: 10px; min-height: 120px; display: flex; flex-direction: column; justify-content: center;">
            <div style="font-weight: 600; color: {exp_color}; margin-bottom: 0.5rem; font-size: 1.1em;">🧪 Experiment</div>
            <div style="font-size: 1em; color: #5B574D; line-height: 1.6;">{exp_escaped}</div>
        </div>
        <div class="reasoning-arrow" style="color: #5B574D; font-size: 1.5em; font-weight: bold; display: flex; align-items: center; margin: 0 0.25rem;">→</div>
        <div class="reasoning-node" style="flex: 1; text-align: center; padding: 1rem; background: {val_bg}; border: 2px solid {val_color}; border-radius: 10px; min-height: 120px; display: flex; flex-direction: column; justify-content: center;">
            <div style="font-weight: 600; color: {val_color}; margin-bottom: 0.5rem; font-size: 1.1em;">🛡️ Validation</div>
            <div style="font-size: 1em; color: #5B574D; line-height: 1.6;">{val_escaped}</div>
        </div>
    </div>
    """
    return html_str


def analyze_shared_timeline(insights: List[Dict]) -> Dict[str, Any]:
    """Analyze insights for shared experiment patterns and create unified timeline"""
    if not insights:
        return {"has_shared_timeline": False, "shared_steps": [], "deviations": {}}
    
    # Extract experiment designs
    exp_designs = [insight.get('experiment_design', {}) for insight in insights if insight.get('experiment_design')]
    
    if not exp_designs:
        return {"has_shared_timeline": False, "shared_steps": [], "deviations": {}}
    
    # Check for scientific methodology format (phases)
    has_phases = any(exp.get('experimental_procedure') for exp in exp_designs)
    
    if has_phases:
        # Analyze phases for common patterns
        all_phases = []
        for exp in exp_designs:
            proc = exp.get('experimental_procedure', {})
            if isinstance(proc, dict):
                phases = list(proc.keys())
                all_phases.append(phases)
        
        # Find common phase structure
        if all_phases:
            common_phases = set(all_phases[0])
            for phases in all_phases[1:]:
                common_phases = common_phases.intersection(set(phases))
            
            if len(common_phases) >= 3:  # At least 3 common phases
                return {
                    "has_shared_timeline": True,
                    "shared_steps": sorted(list(common_phases)),
                    "deviations": {},
                    "format": "phases"
                }
    
    # Check for legacy week format
    has_weeks = any(exp.get('week1') or exp.get('week2') or exp.get('week3') for exp in exp_designs)
    
    if has_weeks:
        # Analyze week structures for similarities
        week_patterns = []
        for exp in exp_designs:
            weeks = []
            if exp.get('week1'):
                weeks.append(exp.get('week1', ''))
            if exp.get('week2'):
                weeks.append(exp.get('week2', ''))
            if exp.get('week3'):
                weeks.append(exp.get('week3', ''))
            week_patterns.append(weeks)
        
        # Simple similarity check - if all have 3 weeks with similar keywords
        if len(week_patterns) >= 2:
            # Check if week1 patterns are similar (contain common keywords)
            week1_keywords = set()
            for pattern in week_patterns:
                if pattern and len(pattern) > 0:
                    words = pattern[0].lower().split()
                    week1_keywords.update([w for w in words if len(w) > 4])
            
            # If there are common keywords across multiple insights, consider it shared
            if len(week1_keywords) > 0:
                return {
                    "has_shared_timeline": True,
                    "shared_steps": ["Week 1", "Week 2", "Week 3"],
                    "deviations": {},
                    "format": "weeks"
                }
    
    return {"has_shared_timeline": False, "shared_steps": [], "deviations": {}}


def create_timeline_visualization(insights: List[Dict]) -> str:
    """Create timeline visualization for shared experiment patterns"""
    timeline_analysis = analyze_shared_timeline(insights)
    
    if not timeline_analysis.get('has_shared_timeline'):
        return ""
    
    shared_steps = timeline_analysis.get('shared_steps', [])
    format_type = timeline_analysis.get('format', 'weeks')
    
    # Create timeline HTML
    timeline_html = f"""
    <div class="timeline-container" style="margin: 1.5rem 0;">
    """
    
    for i, step in enumerate(shared_steps):
        timeline_html += f"""
        <div class="timeline-week">
            <div style="font-weight: 600; color: #D94B2B; margin-bottom: 0.5rem;">{step}</div>
            <div style="font-size: 0.85em; color: #5B574D;">Common step across all experiments</div>
        </div>
        """
        if i < len(shared_steps) - 1:
            timeline_html += '<div style="align-self: center; color: #D94B2B; font-size: 1.5em;">→</div>'
    
    timeline_html += "</div>"
    
    return timeline_html


def generate_collective_summary(insights: List[Dict], research_intelligence: Any = None) -> str:
    """Generate collective insight summary from all insights"""
    if not insights:
        return ""
    
    num_papers = len(st.session_state.get('papers', [])) if 'papers' in st.session_state else 0
    validated_count = len([i for i in insights if i.get('validated', False)])
    
    # Extract themes from insights
    themes = []
    for insight in insights:
        observation = insight.get('observation', '')
        hypothesis = insight.get('hypothesis', '')
        if hypothesis:
            # Extract key concepts from hypothesis
            words = hypothesis.split()
            key_words = [w for w in words if w[0].isupper() and len(w) > 5][:2]
            themes.extend(key_words)
        elif observation:
            words = observation.split()
            key_words = [w for w in words if w[0].isupper() and len(w) > 5][:2]
            themes.extend(key_words)
    
    # Get unique themes
    unique_themes = list(set(themes))[:5]
    
    # Try to get themes from research_intelligence if available
    if research_intelligence and research_intelligence.get('themes'):
        themes_data = research_intelligence.get('themes', {})
        if isinstance(themes_data, dict) and 'themes' in themes_data:
            theme_dict = themes_data['themes']
            if isinstance(theme_dict, dict):
                all_themes = []
                for theme_list in theme_dict.values():
                    if isinstance(theme_list, list):
                        all_themes.extend(theme_list[:2])
                if all_themes:
                    unique_themes = list(set(all_themes))[:5] if all_themes else unique_themes
    
    themes_str = ', '.join(unique_themes) if unique_themes else 'key research patterns'
    
    # Generate synthesis
    synthesis = f"Across {num_papers} papers and {validated_count} validated hypotheses, the agents identified {themes_str} as recurring structural principles. Collectively, these suggest that modern research is converging on fundamental insights about how to approach these problems systematically."
    
    return synthesis


# Agent colors and styles (consistent across app) - Pastel colors
AGENT_STYLES = {
    "Analyzer": {"color": "#6B8DD6", "bg": "#F0F4F8", "icon": "🔍"},
    "Skeptic": {"color": "#C99A9A", "bg": "#FAF5F5", "icon": "⚠️"},
    "Synthesizer": {"color": "#9FC5A8", "bg": "#F5F9F6", "icon": "💡"},
    "Validator": {"color": "#B8A9D9", "bg": "#F7F5FA", "icon": "🛡️"}
}


def calculate_consensus_metrics(conversation_log: List[Dict], insights: List[Dict]) -> Dict[str, Any]:
    """Calculate consensus indicators from conversation log and insights"""
    if not conversation_log or not insights:
        return {
            "consensus_reached": "0/4",
            "disagreement_index": 0.0,
            "insight_strength": 0.0
        }
    
    # Count agents that contributed (from conversation log)
    agents_contributed = len(set([entry.get('agent') for entry in conversation_log if entry.get('agent')]))
    
    # Calculate disagreement index from challenges/contradictions
    total_challenges = 0
    resolved_challenges = 0
    for entry in conversation_log:
        if entry.get('agent') == 'Skeptic':
            contradictions = entry.get('contradictions', [])
            potential_contradictions = entry.get('potential_contradictions', [])
            total_challenges = len(contradictions) + len(potential_contradictions)
        if entry.get('agent') == 'Validator':
            # Count validated vs rejected
            validated_insights = entry.get('validated_insights', [])
            if validated_insights:
                survived = len([v for v in validated_insights if v.get('validated', False)])
                resolved_challenges = survived
    
    disagreement_index = 1.0 - (resolved_challenges / max(total_challenges, 1)) if total_challenges > 0 else 0.0
    
    # Calculate insight strength (average survival score)
    survival_scores = [i.get('survival_score', 0) for i in insights if i.get('survival_score')]
    insight_strength = sum(survival_scores) / len(survival_scores) if survival_scores else 0.0
    
    return {
        "consensus_reached": f"{agents_contributed}/4",
        "disagreement_index": round(disagreement_index, 2),
        "insight_strength": round(insight_strength, 1)
    }


def generate_meta_commentary(conversation_log: List[Dict], insights: List[Dict]) -> str:
    """Generate meta-commentary system summary"""
    if not conversation_log or not insights:
        return ""
    
    validated_count = len([i for i in insights if i.get('validated', False)])
    refined_count = 0
    rejected_count = 0
    
    # Count refinements and rejections from conversation log
    for entry in conversation_log:
        if entry.get('agent') == 'Validator':
            validated_insights = entry.get('validated_insights', [])
            if validated_insights:
                rejected_count = len(insights) - len(validated_insights)
    
    # Count contradictions resolved
    contradictions_count = 0
    for entry in conversation_log:
        if entry.get('agent') == 'Skeptic':
            contradictions = entry.get('contradictions', [])
            contradictions_count = len(contradictions)
    
    commentary = f"Through iterative reasoning, agents converged on {validated_count} validated insights, refining {contradictions_count} contradictions and discarding {rejected_count} redundant hypotheses."
    
    return commentary


def create_roundtable_visualization(conversation_log: List[Dict], show_user: bool = False) -> str:
    """Generate HTML/CSS for roundtable visualization with agent nodes and connections"""
    if not conversation_log and not show_user:
        return ""
    
    # Agent positions in diamond layout
    agent_positions = {
        "Analyzer": {"top": "50%", "left": "25%", "transform": "translate(-50%, -50%)"},
        "Skeptic": {"top": "20%", "left": "50%", "transform": "translate(-50%, -50%)"},
        "Synthesizer": {"top": "50%", "left": "75%", "transform": "translate(-50%, -50%)"},
        "Validator": {"top": "80%", "left": "50%", "transform": "translate(-50%, -50%)"}
    }
    
    # Get agent data from conversation log
    agents_data = {}
    if conversation_log:
        for entry in conversation_log:
            agent_name = entry.get('agent', 'Unknown')
            if agent_name not in agents_data:
                agents_data[agent_name] = {
                    'turn': entry.get('turn', 0),
                    'duration': entry.get('duration', 0),
                    'status': 'active'
                }
    
    # Build agent nodes HTML - show all agents
    agent_nodes_html = ""
    for agent_name, style_info in AGENT_STYLES.items():
        pos = agent_positions.get(agent_name, {"top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"})
        if agent_name in agents_data:
            agent_data = agents_data[agent_name]
            turn_info = f"Turn {agent_data['turn']}"
            opacity = "1.0"
            pulse_class = "agent-node-pulse"
        else:
            turn_info = "Pending"
            opacity = "0.6"
            pulse_class = ""
        
        agent_nodes_html += f"""
        <div class="{pulse_class}" style="
            position: absolute;
            top: {pos['top']};
            left: {pos['left']};
            transform: {pos['transform']};
            background: {style_info['bg']};
            border: 3px solid {style_info['color']};
            border-radius: 50%;
            width: 100px;
            height: 100px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            z-index: 10;
            opacity: {opacity};
        ">
            <div style="font-size: 2em; margin-bottom: 0.3rem;">{style_info['icon']}</div>
            <div style="font-weight: 600; font-size: 0.85em; color: {style_info['color']}; text-align: center;">
                {agent_name}
            </div>
            <div style="font-size: 0.7em; color: #6B7280; margin-top: 0.2rem;">
                {turn_info}
            </div>
        </div>
        """
    
    # User avatar in center if requested
    user_avatar = ""
    if show_user:
        user_avatar = '<div class="user-avatar-center">👤</div>'
    
    # Connection arrows (SVG)
    connections_svg = """
    <svg style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; pointer-events: none;">
        <!-- Analyzer to Skeptic -->
        <line x1="25%" y1="50%" x2="50%" y2="20%" stroke="#3B82F6" stroke-width="3" marker-end="url(#arrowhead)" opacity="0.6"/>
        <!-- Skeptic to Synthesizer -->
        <line x1="50%" y1="20%" x2="75%" y2="50%" stroke="#EF4444" stroke-width="3" marker-end="url(#arrowhead)" opacity="0.6"/>
        <!-- Synthesizer to Validator -->
        <line x1="75%" y1="50%" x2="50%" y2="80%" stroke="#10B981" stroke-width="3" marker-end="url(#arrowhead)" opacity="0.6"/>
        <!-- Analyzer to Synthesizer (direct) -->
        <line x1="30%" y1="50%" x2="70%" y2="50%" stroke="#D94B2B" stroke-width="2" stroke-dasharray="5,5" opacity="0.4"/>
        <!-- Connections to center (user) -->
        <line x1="25%" y1="50%" x2="50%" y2="50%" stroke="#D94B2B" stroke-width="2" stroke-dasharray="3,3" opacity="0.3"/>
        <line x1="50%" y1="20%" x2="50%" y2="50%" stroke="#D94B2B" stroke-width="2" stroke-dasharray="3,3" opacity="0.3"/>
        <line x1="75%" y1="50%" x2="50%" y2="50%" stroke="#D94B2B" stroke-width="2" stroke-dasharray="3,3" opacity="0.3"/>
        <line x1="50%" y1="80%" x2="50%" y2="50%" stroke="#D94B2B" stroke-width="2" stroke-dasharray="3,3" opacity="0.3"/>
        <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <polygon points="0 0, 10 3, 0 6" fill="#D94B2B" opacity="0.6"/>
            </marker>
        </defs>
    </svg>
    """
    
    html_str = f"""
    <div style="
        position: relative;
        width: 100%;
        height: 500px;
        background: #FAF9F7;
        border-radius: 16px;
        margin: 2rem 0;
        padding: 2rem;
        border: 2px solid #E0DED9;
    ">
        {connections_svg}
        {agent_nodes_html}
        {user_avatar}
    </div>
    """
    return html_str


# Dashboard helper functions
def create_hero_section_streamlit():
    """Create hero section using Streamlit-native components"""
    st.markdown("""
    <div style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #FAF9F7 0%, #F3F1ED 100%); 
                border-radius: 20px; margin: 2rem 0; border: 2px solid #E0DED9;">
        <h1 style="font-size: 2.5em; font-weight: 600; color: #2C2B27; margin-bottom: 1rem; letter-spacing: -0.02em;">
            Think With AiResearcher
        </h1>
        <p style="font-size: 1.2em; color: #5B574D; margin-bottom: 2rem; line-height: 1.6;">
            Turn scattered research into strategy. AiResearcher transforms complex papers into validated insights — powered by a team of reasoning agents working like your own research lab.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Agent pipeline visualization - minimal, pastel colors, perfectly aligned
    st.markdown("### 🤖 The Agent Pipeline")
    st.markdown("*Four specialized agents work together, with you at the center*")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Use Streamlit columns for reliable layout - equal width, perfectly aligned
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Pastel colors matching AGENT_STYLES
    agents_data = [
        ("🔍", "Analyzer", "#6B8DD6", "#F0F4F8", "Extracts methods & data"),
        ("⚠️", "Skeptic", "#C99A9A", "#FAF5F5", "Challenges gaps & logic"),
        ("💡", "Synthesizer", "#9FC5A8", "#F5F9F6", "Proposes hypotheses"),
        ("🛡️", "Validator", "#B8A9D9", "#F7F5FA", "Tests novelty"),
                ("👤", "You", "#2C2B27", "#F5F5F5", "Guide & refine")
    ]
    
    cols = [col1, col2, col3, col4, col5]
    for col, (icon, name, color, bg, desc) in zip(cols, agents_data):
        is_user = (name == "You")
        # Use subtle styling for user - minimal, elegant
        border_color = "#2C2B27" if is_user else "#E0DED9"
        border_width = "2px" if is_user else "1px"
        text_color = "#2C2B27"  # Same text color for all
        
        with col:
            st.markdown(f"""
            <div style="text-align: center; padding: 1.5rem 1rem; background: {bg}; 
                        border: {border_width} solid {border_color}; border-radius: 12px; 
                        min-height: 160px; max-height: 160px; 
                        display: flex; flex-direction: column; justify-content: center; align-items: center;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
                <div style="font-size: 2em; margin-bottom: 0.6rem;">{icon}</div>
                <div style="font-weight: 600; color: {text_color}; margin-bottom: 0.4rem; font-size: 0.95em;">{name}</div>
                <div style="font-size: 0.8em; color: #5B574D; line-height: 1.4; text-align: center;">
                    {desc}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)


def create_bottleneck_comparison() -> str:
    """Create research bottleneck comparison section - minimal colors, clean design"""
    html_str = """
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin: 2rem 0;">
        <div style="background: white; border: 1px solid #E0DED9; border-radius: 16px; padding: 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="font-size: 1.3em; font-weight: 600; margin-bottom: 1rem; color: #2C2B27;">The Old Way</div>
            <div style="padding: 0.8rem 0; border-bottom: 1px solid #E0DED9; color: #5B574D;">10+ PDFs summarized into pages of unread text</div>
            <div style="padding: 0.8rem 0; border-bottom: 1px solid #E0DED9; color: #5B574D;">Opaque reasoning, black-box outputs</div>
            <div style="padding: 0.8rem 0; color: #5B574D;">Human reviews results after analysis completes</div>
        </div>
        <div style="background: #FAF9F7; border: 2px solid #2C2B27; border-radius: 16px; padding: 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="font-size: 1.3em; font-weight: 600; margin-bottom: 1rem; color: #2C2B27;">The AiResearcher Way</div>
            <div style="padding: 0.8rem 0; border-bottom: 1px solid #E0DED9; color: #5B574D;">10+ papers turned into 3 validated, human-guided insights</div>
            <div style="padding: 0.8rem 0; border-bottom: 1px solid #E0DED9; color: #5B574D;">Transparent debate among agents</div>
            <div style="padding: 0.8rem 0; color: #5B574D;">Human shapes reasoning as it unfolds</div>
        </div>
    </div>
    """
    return html_str


def create_metrics_with_context(papers: List, insights: List[Dict], conversation_log: List[Dict], tab_switches: int = 0) -> str:
    """
    Creates a metrics display section with contextual information.
    
    Calculates and displays key metrics including paper count, insight count,
    validation rates, and engagement metrics for the dashboard.
    """
    num_papers = len(papers) if papers else 0
    num_insights = len(insights) if insights else 0
    validated_count = len([i for i in insights if i.get('validated', False)]) if insights else 0
    
    # Calculate reasoning depth (dialogue turns)
    reasoning_depth = len(conversation_log) if conversation_log else 0
    
    # Calculate pipeline time
    pipeline_time = sum(log.get('duration', 0) for log in conversation_log) if conversation_log else 0
    
    # Calculate engagement index based on tab navigation
    # Normalizes tab switches to a 0-100 scale for display
    max_switches = 4
    engagement_index = min(int((tab_switches / max_switches) * 100), 100) if tab_switches > 0 else 0
    
    html_str = f"""
    <div style="margin: 2rem 0;">
        <h2 style="margin-bottom: 1.5rem; color: #2C2B27;">Live Discovery Dashboard</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.2rem;">
            <div style="background: white; border: 1px solid #E0DED9; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-size: 2em; font-weight: 600; color: #2C2B27; margin-bottom: 0.5rem;">🧩 {num_papers}</div>
                <div style="font-size: 1em; font-weight: 500; color: #2C2B27; margin-bottom: 0.5rem;">Papers Processed</div>
                <div style="font-size: 0.85em; color: #5B574D; font-style: italic;">each read, debated, and mapped by agents</div>
            </div>
            <div style="background: white; border: 1px solid #E0DED9; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-size: 2em; font-weight: 600; color: #2C2B27; margin-bottom: 0.5rem;">💡 {validated_count}</div>
                <div style="font-size: 1em; font-weight: 500; color: #2C2B27; margin-bottom: 0.5rem;">Insights Validated</div>
                <div style="font-size: 0.85em; color: #5B574D; font-style: italic;">ideas that survived critical debate</div>
            </div>
            <div style="background: white; border: 1px solid #E0DED9; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-size: 2em; font-weight: 600; color: #2C2B27; margin-bottom: 0.5rem;">🧠 {reasoning_depth}</div>
                <div style="font-size: 1em; font-weight: 500; color: #2C2B27; margin-bottom: 0.5rem;">Avg Reasoning Depth</div>
                <div style="font-size: 0.85em; color: #5B574D; font-style: italic;">dialogue turns per insight</div>
            </div>
            <div style="background: white; border: 1px solid #E0DED9; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-size: 2em; font-weight: 600; color: #2C2B27; margin-bottom: 0.5rem;">🤝 {engagement_index}%</div>
                <div style="font-size: 1em; font-weight: 500; color: #2C2B27; margin-bottom: 0.5rem;">Human Engagement Index</div>
                <div style="font-size: 0.85em; color: #5B574D; font-style: italic;">clicks, edits, approvals</div>
            </div>
            <div style="background: white; border: 1px solid #E0DED9; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-size: 2em; font-weight: 600; color: #2C2B27; margin-bottom: 0.5rem;">⚙️ {pipeline_time:.1f}s</div>
                <div style="font-size: 1em; font-weight: 500; color: #2C2B27; margin-bottom: 0.5rem;">Pipeline Time</div>
                <div style="font-size: 0.85em; color: #5B574D; font-style: italic;">a complete reasoning cycle</div>
            </div>
        </div>
    </div>
    """
    
    # Add pipeline timeline - simple, aligned
    if conversation_log:
        agents_order = ["Analyzer", "Skeptic", "Synthesizer", "Validator"]
        completed_agents = [log.get('agent') for log in conversation_log if log.get('agent')]
        
        timeline_html = '<div style="display: flex; justify-content: space-between; align-items: center; margin: 2rem 0; padding: 1.5rem; background: #FAF9F7; border-radius: 12px; gap: 0.5rem;">'
        for i, agent in enumerate(agents_order):
            is_complete = agent in completed_agents
            status_icon = "✅" if is_complete else "⏳"
            bg_color = "#F5F9F6" if is_complete else "white"
            border_color = "#9FC5A8" if is_complete else "#E0DED9"
            agent_escaped = html.escape(agent)
            
            timeline_html += f"""<div style="flex: 1; text-align: center; padding: 1rem 0.5rem; background: {bg_color}; border: 1px solid {border_color}; border-radius: 10px; min-height: 80px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <div style="font-size: 1.2em; margin-bottom: 0.3rem;">{status_icon}</div>
                <div style="font-weight: 500; color: #2C2B27; font-size: 0.9em;">{agent_escaped}</div>
            </div>"""
            if i < len(agents_order) - 1:
                timeline_html += '<div style="color: #5B574D; font-size: 1.2em; font-weight: bold;">→</div>'
        timeline_html += """<div style="flex: 1; text-align: center; padding: 1rem 0.5rem; background: white; border: 1px solid #E0DED9; border-radius: 10px; min-height: 80px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <div style="font-size: 1.2em; margin-bottom: 0.3rem;">⏳</div>
            <div style="font-weight: 500; color: #2C2B27; font-size: 0.9em;">You (ready for review)</div>
        </div>"""
        timeline_html += '</div>'
        
        html_str += timeline_html
    
    return html_str


def build_author_insight_mapping(papers: List, insights: List[Dict]) -> Dict[str, List[Dict]]:
    """Build mapping from author names to linked insights"""
    author_insights = {}
    
    if not papers or not insights:
        return author_insights
    
    # Extract author names from papers and map to paper indices
    author_papers = {}  # author_name -> [paper_indices]
    for idx, paper in enumerate(papers):
        # Handle both Paper dataclass and dict
        if hasattr(paper, 'authors'):
            authors = paper.authors
        elif isinstance(paper, dict):
            authors = paper.get('authors', [])
        else:
            continue
        
        for author in authors:
            if author and author.strip():
                if author not in author_papers:
                    author_papers[author] = []
                author_papers[author].append(idx)
    
    # Match insights to authors via paper titles/keywords
    for insight in insights:
        # Extract referenced papers from insight (via gap, observation, or validation_evidence)
        insight_text = (
            insight.get('gap', '') + ' ' +
            insight.get('observation', '') + ' ' +
            insight.get('validation_evidence', '')
        ).lower()
        
        # Try to match paper titles in insight text
        for author, paper_indices in author_papers.items():
            for paper_idx in paper_indices:
                paper = papers[paper_idx]
                paper_title = paper.title if hasattr(paper, 'title') else paper.get('title', '')
                if paper_title and paper_title.lower() in insight_text:
                    if author not in author_insights:
                        author_insights[author] = []
                    if insight not in author_insights[author]:
                        author_insights[author].append(insight)
    
    return author_insights


def create_enhanced_authors_section(papers: List, insights: List[Dict], research_intelligence: Dict = None) -> str:
    """Create enhanced authors section with expandable cards"""
    if not research_intelligence or not research_intelligence.get('top_authors'):
        return ""
    
    authors = research_intelligence['top_authors'][:5]  # Top 5 authors
    author_insights_map = build_author_insight_mapping(papers, insights)
    
    html_str = '<div style="margin: 2rem 0;"><h2 style="margin-bottom: 1.5rem;">Top Authors and Emerging Fields</h2>'
    
    for author_data in authors:
        author_name = author_data.get('name', 'Unknown')
        paper_count = author_data.get('paper_count', 0)
        sample_papers = author_data.get('sample_papers', [])
        
        # Get linked insights
        linked_insights = author_insights_map.get(author_name, [])
        
        # Get first paper by author for abstract
        author_papers = []
        for p in papers:
            paper_authors = p.authors if hasattr(p, 'authors') else (p.get('authors', []) if isinstance(p, dict) else [])
            if author_name in paper_authors:
                author_papers.append(p)
        
        first_paper = author_papers[0] if author_papers else None
        abstract = "No abstract available."
        if first_paper:
            if hasattr(first_paper, 'abstract'):
                paper_abstract = first_paper.abstract or ""
            elif isinstance(first_paper, dict):
                paper_abstract = first_paper.get('abstract', '')
            else:
                paper_abstract = ""
            
            if paper_abstract:
                abstract = paper_abstract[:300] + '...' if len(paper_abstract) > 300 else paper_abstract
        
        # Extract contribution theme from first paper title/abstract (simple keyword extraction)
        theme_keywords = ['symmetry', 'diversity', 'ensemble', 'generalization', 'optimization', 'learning', 'neural', 'network']
        theme = "Research in ML"
        if first_paper:
            if hasattr(first_paper, 'title'):
                paper_title = first_paper.title or ""
            elif isinstance(first_paper, dict):
                paper_title = first_paper.get('title', '')
            else:
                paper_title = ""
            paper_text = (paper_title + ' ' + abstract).lower()
            for keyword in theme_keywords:
                if keyword in paper_text:
                    theme = keyword.capitalize() + " in ML"
                    break
        
        # Get key insight and gap from linked insights
        key_insight = linked_insights[0].get('title', 'No linked insights') if linked_insights else 'No linked insights'
        related_gap_raw = linked_insights[0].get('gap', 'N/A') if linked_insights and linked_insights[0].get('gap') else 'N/A'
        
        # Escape all text before building HTML to avoid issues
        author_name_escaped = html.escape(author_name)
        theme_escaped = html.escape(theme)
        # Truncate key_insight if needed (before escaping)
        if len(key_insight) > 150:
            key_insight_escaped = html.escape(key_insight[:150]) + '...'
        else:
            key_insight_escaped = html.escape(key_insight)
        # Truncate related_gap if needed (before escaping)
        if len(related_gap_raw) > 100:
            related_gap_escaped = html.escape(related_gap_raw[:100]) + '...'
        else:
            related_gap_escaped = html.escape(related_gap_raw)
        abstract_escaped = html.escape(abstract)
        
        # Build insights list HTML
        insights_list_html = ''
        for insight in linked_insights[:3]:
            insight_title = insight.get('title', 'Untitled')
            insights_list_html += f'<li>{html.escape(insight_title)}</li>'
        
        html_str += f"""<div style="background: white; border: 1px solid #E0DED9; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div>
                    <div style="font-size: 1.2em; font-weight: 600; color: #2C2B27; margin-bottom: 0.3rem;">{author_name_escaped}</div>
                    <div style="font-size: 0.9em; color: #5B574D;">{paper_count} papers analyzed</div>
                </div>
                <span style="display: inline-block; padding: 0.3rem 0.8rem; background: #F0F4F8; color: #2C2B27; border-radius: 20px; font-size: 0.85em; font-weight: 500; border: 1px solid #E0DED9;">{theme_escaped}</span>
            </div>
            <div style="margin: 1rem 0; padding: 0.8rem; background: #FAF9F7; border-radius: 8px; border-left: 3px solid #D94B2B;">
                <div style="font-weight: 500; color: #2C2B27; margin-bottom: 0.3rem;">Key Insight:</div>
                <div style="color: #5B574D; font-size: 0.95em;">{key_insight_escaped}</div>
            </div>
            <div style="margin: 1rem 0; padding: 0.8rem; background: #FAF9F7; border-radius: 8px;">
                <div style="font-weight: 500; color: #2C2B27; margin-bottom: 0.3rem;">Related Gap:</div>
                <div style="color: #5B574D; font-size: 0.95em;">{related_gap_escaped}</div>
            </div>
            <details style="margin-top: 1rem;">
                <summary style="cursor: pointer; font-weight: 600; color: #2C2B27; margin-bottom: 1rem; padding: 0.5rem; background: #FAF9F7; border-radius: 6px;">View Details</summary>
                <div style="margin-top: 1rem; padding: 1rem; background: #FAF9F7; border-radius: 8px;">
                    <p style="color: #5B574D;"><strong>Mini Abstract:</strong> {abstract_escaped}</p>
                    <p style="margin-top: 1rem; color: #2C2B27;"><strong>Connected Insights ({len(linked_insights)}):</strong></p>
                    <ul style="color: #5B574D;">{insights_list_html}</ul>
                </div>
            </details>
        </div>"""
    
    html_str += '</div>'
    return html_str


def generate_field_summary_cached(papers: List, topic: str, research_intelligence: Dict = None) -> str:
    """Generate field summary once and cache it in research_intelligence"""
    # Check if already cached
    if research_intelligence and research_intelligence.get('field_summary'):
        return research_intelligence['field_summary']
    
    # Generate summary (simplified - in real implementation, would use LLM)
    if papers:
        num_papers = len(papers)
        years = []
        for p in papers:
            if hasattr(p, 'year') and p.year:
                years.append(p.year)
            elif isinstance(p, dict) and p.get('year'):
                years.append(p.get('year'))
        recent_years = [y for y in years if y and y >= 2022] if years else []
        
        summary = f"The field of {topic} has seen significant activity with {num_papers} recent papers analyzed. "
        if recent_years:
            summary += f"Recent publications (2022-2024) show continued innovation and exploration. "
        summary += "The research landscape is characterized by diverse methodologies, emerging paradigms, and applications across multiple domains. "
        summary += "Key trends include the integration of novel architectures, optimization techniques, and evaluation metrics that push the boundaries of current understanding."
    else:
        summary = f"The field of {topic} represents an active area of research with ongoing developments and emerging opportunities."
    
    # Cache it (would need to update research_intelligence dict)
    return summary


def generate_emerging_subfields_cached(papers: List, research_intelligence: Dict = None) -> List[str]:
    """Generate emerging subfields once and cache them"""
    # Check if already cached
    if research_intelligence and research_intelligence.get('emerging_subfields'):
        return research_intelligence['emerging_subfields']
    
    # Extract from themes if available
    subfields = []
    if research_intelligence and research_intelligence.get('themes'):
        themes_data = research_intelligence['themes']
        if isinstance(themes_data, dict) and 'themes' in themes_data:
            theme_dict = themes_data['themes']
            # Extract trends as emerging subfields
            if 'trends' in theme_dict:
                subfields = theme_dict['trends'][:5]
            elif 'paradigms' in theme_dict:
                subfields = theme_dict['paradigms'][:5]
    
    # Fallback: generate simple subfields
    if not subfields:
        subfields = [
            "Open-environment ML",
            "Geometric learning",
            "Representation bias",
            "Efficient models",
            "Multimodal learning"
        ]
    
    return subfields


def create_beyond_keywords_section(papers: List, research_intelligence: Dict = None, topic: str = "") -> str:
    """Create Beyond Keywords section with concept clusters, subfields, and field summary"""
    if not research_intelligence:
        return ""
    
    # Get concept clusters from themes
    concept_clusters = []
    if research_intelligence.get('themes'):
        themes_data = research_intelligence['themes']
        if isinstance(themes_data, dict) and 'themes' in themes_data:
            theme_dict = themes_data['themes']
            # Collect all themes
            for theme_list in theme_dict.values():
                if isinstance(theme_list, list):
                    concept_clusters.extend(theme_list[:2])
    
    # Get unique clusters (limit to 8)
    concept_clusters = list(set(concept_clusters))[:8]
    
    # Generate emerging subfields (cached)
    emerging_subfields = generate_emerging_subfields_cached(papers, research_intelligence)
    
    # Generate field summary (cached)
    field_summary = generate_field_summary_cached(papers, topic, research_intelligence)
    
    html_str = f"""
    <div class="keywords-section">
        <h2 style="margin-bottom: 1.5rem;">Beyond Keywords</h2>
        
        <div style="margin: 1.5rem 0;">
            <h3 style="margin-bottom: 1rem;">Top Concept Clusters</h3>
            <div>
    """
    
    for cluster in concept_clusters:
        html_str += f'<span class="concept-cluster">{html.escape(cluster)}</span>'
    
    html_str += """
            </div>
        </div>
        
        <div style="margin: 1.5rem 0;">
            <h3 style="margin-bottom: 1rem;">Emerging Subfields</h3>
            <ul>
    """
    
    for subfield in emerging_subfields:
        html_str += f'<li>{html.escape(subfield)}</li>'
    
    html_str += f"""
            </ul>
        </div>
        
        <div style="margin: 1.5rem 0;">
            <h3 style="margin-bottom: 1rem;">Field Summary</h3>
            <div class="field-summary" style="white-space: pre-wrap;">
                {html.escape(field_summary)}
            </div>
        </div>
    </div>
    """
    
    return html_str


def create_collaboration_flow_section(conversation_log: List[Dict] = None) -> str:
    """
    Creates a collaboration flow visualization.
    
    Displays the interaction flow between human users and the analysis
    pipeline to illustrate the collaborative research process.
    """
    html_str = """
    <div style="margin: 2rem 0;">
        <h2 style="margin-bottom: 1.5rem;">Human + Multi-Agent Collaboration</h2>
        <div class="collaboration-flow">
    """
    
    agents_flow = [
        ("Analyzer", "🔍", "extracts key methods & data"),
        ("Skeptic", "⚠️", "challenges gaps, checks logic"),
        ("Synthesizer", "💡", "proposes hypotheses & experiments"),
        ("Validator", "🛡️", "tests novelty & confirms gaps"),
        ("You", "👤", "guide, approve, and refine")
    ]
    
    for i, (agent_name, icon, description) in enumerate(agents_flow):
        style_info = AGENT_STYLES.get(agent_name, {"color": "#2C2B27", "bg": "#FAF9F7"})
        agent_name_escaped = html.escape(agent_name)
        description_escaped = html.escape(description)
        html_str += f"""<div class="flow-agent">
            <div style="font-size: 2em; margin-bottom: 0.5rem;">{icon}</div>
            <div style="font-weight: 600; color: #2C2B27; margin-bottom: 0.5rem;">{agent_name_escaped}</div>
            <div style="font-size: 0.9em; color: #5B574D;">{description_escaped}</div>
        </div>"""
        if i < len(agents_flow) - 1:
            html_str += '<div class="flow-arrow">→</div>'
    
    html_str += """
        </div>
    """
    
    # Add expandable reasoning snippets
    if conversation_log:
        html_str += '<details style="margin-top: 2rem;"><summary style="cursor: pointer; font-weight: 600; color: #2C2B27; margin-bottom: 1rem; padding: 0.5rem; background: #FAF9F7; border-radius: 6px;">View Example Reasoning Snippets</summary>'
        html_str += '<div style="margin-top: 1rem;">'
        
        for log in conversation_log[:3]:  # Show first 3
            agent = log.get('agent', 'Unknown')
            output_summary = log.get('output_summary', '')
            style_info = AGENT_STYLES.get(agent, {"color": "#2C2B27", "bg": "#FAF9F7"})
            agent_escaped = html.escape(agent)
            output_escaped = html.escape(output_summary[:200]) + ('...' if len(output_summary) > 200 else '')
            
            html_str += f"""<div class="dialogue-bubble" style="border-left: 3px solid #2C2B27;">
                <div class="dialogue-agent">{agent_escaped}</div>
                <div class="dialogue-text">{output_escaped}</div>
            </div>"""
        
        html_str += '</div></details>'
    
    html_str += '</div>'
    return html_str


def create_see_thinking_section(conversation_log: List[Dict] = None) -> str:
    """Create See Thinking section with conversation highlights"""
    html_str = """
    <div style="margin: 2rem 0;">
        <h2 style="margin-bottom: 1rem;">See Thinking, Not Just Results</h2>
        <p style="font-size: 1.1em; color: #5B574D; margin-bottom: 2rem; font-style: italic;">
            Every discovery is a conversation — between minds, human and machine.
        </p>
    """
    
    if conversation_log:
        html_str += '<div style="display: grid; gap: 1.5rem;">'
        for log in conversation_log[:4]:  # Show first 4 turns
            agent = log.get('agent', 'Unknown')
            output_summary = log.get('output_summary', '')
            style_info = AGENT_STYLES.get(agent, {"color": "#D94B2B", "bg": "#FAF9F7"})
            agent_escaped = html.escape(agent)
            icon = style_info.get('icon', '')
            output_escaped = html.escape(output_summary)
            bg_color = html.escape(style_info['bg'])
            
            html_str += f"""<div class="dialogue-bubble" style="border-left: 3px solid #2C2B27; background: {bg_color};">
                <div class="dialogue-agent">{agent_escaped} {icon}</div>
                <div class="dialogue-text">{output_escaped}</div>
            </div>"""
        html_str += '</div>'
    else:
        html_str += '<p style="color: #5B574D; font-style: italic;">No conversation data available. Start a discovery session to see agents think together.</p>'
    
    html_str += '</div>'
    return html_str


def create_use_cases_section() -> str:
    """Create Use Cases section with curated examples"""
    use_cases = [
        {
            "icon": "🧪",
            "title": "Researcher",
            "description": "Map literature & derive new hypotheses",
            "outcome": "Generated a validated hypothesis on symmetry-based generalization in under 2 minutes."
        },
        {
            "icon": "💼",
            "title": "Innovation Lead",
            "description": "Monitor emerging tech domains",
            "outcome": "Identified 3 unexplored research directions in ensemble learning with market potential."
        },
        {
            "icon": "📈",
            "title": "Analyst",
            "description": "Identify unexplored white spaces",
            "outcome": "Discovered gaps in representation bias research across 15 analyzed papers."
        },
        {
            "icon": "🧑‍💻",
            "title": "Developer",
            "description": "Build reasoning workflows into apps",
            "outcome": "Integrated multi-agent reasoning pipeline into research tool in 1 hour."
        }
    ]
    
    # Escape text before building HTML to avoid issues
    html_str = '<div style="margin: 2rem 0;"><h2 style="margin-bottom: 1.5rem; color: #2C2B27;">Use Cases: Where Human + Agent Collaboration Shines</h2><div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">'
    
    for use_case in use_cases:
        title_escaped = html.escape(use_case['title'])
        desc_escaped = html.escape(use_case['description'])
        outcome_escaped = html.escape(use_case['outcome'])
        
        html_str += f'<div class="use-case-card"><div class="use-case-icon">{use_case["icon"]}</div><div class="use-case-title">{title_escaped}</div><div style="color: #5B574D; margin-bottom: 1rem;">{desc_escaped}</div><div class="use-case-outcome">{outcome_escaped}</div></div>'
    
    html_str += '</div></div>'
    return html_str


def create_cta_section() -> str:
    """Create Join the Research Renaissance CTA section - minimal, no buttons"""
    html_str = """
    <div class="cta-section">
        <h2 style="font-size: 1.8em; font-weight: 600; margin-bottom: 1rem; color: #2C2B27;">Join the Research Renaissance</h2>
        <p style="font-size: 1.1em; line-height: 1.8; margin-bottom: 1.5rem; color: #5B574D; opacity: 0.95;">
            AiResearcher isn't an assistant. It's a collaborator.<br>
            Built for the new era of Agentic Research Discovery.<br>
            Let's bridge human intuition and machine reasoning.
        </p>
        <p style="font-size: 0.95em; color: #5B574D; font-style: italic; margin: 0;">
            Use the sidebar to start your research discovery journey.
        </p>
    </div>
    """
    return html_str


# Header - Minimal (tabs provide navigation)
st.markdown("""
<div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem; border-bottom: 1px solid #E0DED9;">
    <h1 style="font-size: 1.8em; font-weight: 600; color: #2C2B27; margin: 0;">🔬 AiResearcher</h1>
    <p style="color: #5B574D; margin: 0.3rem 0 0 0; font-size: 0.9em;">Multi-Agent Research Insight Generator</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    topic = st.text_input("Research Topic", value="machine learning")
    num_papers = st.slider("Number of Papers", 2, 100, 5)
    
    # Warning for large paper counts
    if num_papers >= 50:
        st.warning(f"⚠️ Large paper count ({num_papers} papers) may take 2-3 minutes to process.")
    
    # Multi-platform search option
    use_multi_platform = st.checkbox(
        "🌐 Multi-Platform Search",
        value=False,
        help="Search multiple publication sources"
    )
    
    # Source selection (only show if multi-platform is enabled)
    enabled_sources = set()
    if use_multi_platform:
        st.markdown("**Select Sources:**")
        col1, col2 = st.columns(2)
        with col1:
            if st.checkbox("arXiv", value=True):
                enabled_sources.add('arxiv')
            if st.checkbox("Papers with Code", value=True):
                enabled_sources.add('pwc')
            if st.checkbox("Hugging Face", value=True):
                enabled_sources.add('hf')
            if st.checkbox("PubMed", value=True):
                enabled_sources.add('pubmed')
        with col2:
            if st.checkbox("bioRxiv", value=True):
                enabled_sources.add('biorxiv')
            if st.checkbox("SSRN", value=False):
                enabled_sources.add('ssrn')
            if st.checkbox("CORE", value=False):
                enabled_sources.add('core')
        
        # Ensure at least one source is selected
        if not enabled_sources:
            st.error("Please select at least one source.")
            enabled_sources = {'arxiv'}  # Default fallback
    else:
        enabled_sources = None

    st.divider()
    st.subheader("🤖 Agent System")
    st.markdown("""
    **4 Specialized Agents:**
    - 🔍 **Analyzer** - Extracts methods, datasets, limitations
    - ⚠️ **Skeptic** - Challenges assumptions, finds contradictions
    - 💡 **Synthesizer** - Generates experiment designs
    - 🛡️ **Validator** - Validates insights against prior work
    """)

    if st.button("🚀 Generate Insights", type="primary", use_container_width=True):
        st.session_state.run = True
        st.session_state.use_multi_platform = use_multi_platform
        st.session_state.enabled_sources = enabled_sources

# Initialize session state
if "papers" not in st.session_state:
    st.session_state.papers = None
if "insights" not in st.session_state:
    st.session_state.insights = None
if "conversation_log" not in st.session_state:
    st.session_state.conversation_log = None
if "agent" not in st.session_state:
    st.session_state.agent = None
if "enhanced_papers" not in st.session_state:
    st.session_state.enhanced_papers = None
if "use_multi_platform" not in st.session_state:
    st.session_state.use_multi_platform = False
if "enabled_sources" not in st.session_state:
    st.session_state.enabled_sources = None
if "research_intelligence" not in st.session_state:
    st.session_state.research_intelligence = None
if "tab_switches" not in st.session_state:
    st.session_state.tab_switches = 0
if "last_tab" not in st.session_state:
    st.session_state.last_tab = None
if "last_topic" not in st.session_state:
    st.session_state.last_topic = "machine learning"

# Track tab switches for engagement index
def track_tab_switch(tab_name: str):
    """Track tab switches for engagement index"""
    if st.session_state.last_tab != tab_name:
        st.session_state.tab_switches += 1
        st.session_state.last_tab = tab_name

# Multi-tab interface
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Dashboard",
    "📚 Papers",
    "💡 Research Insights",
    "🔄 Agent Conversation",
    "📄 Full Report",
    "🧭 Next Discovery"
])

# Main Content
if st.session_state.get("run", False):
    use_multi = st.session_state.get("use_multi_platform", False)
    enabled_sources = st.session_state.get("enabled_sources", None)
    agent = ResearchAgent(use_multi_platform=use_multi, enabled_sources=enabled_sources)
    st.session_state.agent = agent

    # Search papers with progress
    search_text = "🌐 Searching multiple platforms..." if use_multi else "📚 Searching papers..."
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    with st.spinner(search_text):
        status_text.text("Searching papers...")
        papers = agent.search_papers(topic, num_papers, multi_platform=use_multi, enabled_sources=enabled_sources)
        progress_bar.progress(1.0)
        status_text.text(f"✓ Found {len(papers)} papers")
        st.session_state.papers = papers
        time.sleep(0.5)  # Brief pause to show completion
        progress_bar.empty()
        status_text.empty()
        
        # Store enhanced papers if multi-platform was used (cached in agent)
        if use_multi and hasattr(agent, 'last_enhanced_papers') and agent.last_enhanced_papers:
            st.session_state.enhanced_papers = agent.last_enhanced_papers
        else:
            st.session_state.enhanced_papers = None

    if not papers:
        st.error("❌ No papers found. Try a different topic.")
        st.session_state.run = False
    else:
        # Generate insights with 4-agent pipeline
        agent_progress = st.progress(0)
        agent_status = st.empty()
        
        with st.spinner("🤖 Running 4-agent pipeline..."):
            agent_status.text("Initializing agents...")
            agent_progress.progress(0.1)
            
            insights = agent.generate_insights(papers, topic)
            agent_progress.progress(1.0)
            agent_status.text("✓ Pipeline complete!")
            
            st.session_state.insights = insights
            st.session_state.conversation_log = agent.get_conversation_log()
            st.session_state.research_intelligence = agent.get_research_intelligence()
            st.session_state.last_topic = topic
            
            time.sleep(0.5)
            agent_progress.empty()
            agent_status.empty()

        st.session_state.run = False
        st.rerun()

# TAB 1: Dashboard - Narrative Storytelling
with tab1:
    track_tab_switch("Dashboard")
    
    papers = st.session_state.papers or []
    insights = st.session_state.insights or []
    conversation_log = st.session_state.conversation_log or []
    research_intelligence = st.session_state.research_intelligence
    topic = st.session_state.get('last_topic', 'machine learning')
    
    # Always show hero section and bottleneck comparison
    create_hero_section_streamlit()
    st.markdown(create_bottleneck_comparison(), unsafe_allow_html=True)
    
    # Show data-dependent sections only if we have papers/insights
    if papers and insights:
        # Section 3: Live Discovery Dashboard
        st.markdown(create_metrics_with_context(
            papers, 
            insights, 
            conversation_log or [], 
            st.session_state.tab_switches
        ), unsafe_allow_html=True)
        
        # Section 4: Enhanced Top Authors
        if research_intelligence:
            st.markdown(create_enhanced_authors_section(
                papers, 
                insights, 
                research_intelligence
            ), unsafe_allow_html=True)
        
        # Section 5: Human + Multi-Agent Collaboration
        st.markdown(create_collaboration_flow_section(conversation_log), unsafe_allow_html=True)
        
        # Section 7: See Thinking
        st.markdown(create_see_thinking_section(conversation_log), unsafe_allow_html=True)
    
    # Section 8: Use Cases (always show)
    st.markdown(create_use_cases_section(), unsafe_allow_html=True)
    
    # Section 9: CTA (always show)
    st.markdown(create_cta_section(), unsafe_allow_html=True)

# TAB 2: Papers
with tab2:
    track_tab_switch("Papers")
    if st.session_state.papers:
        papers = st.session_state.papers
        enhanced_papers = st.session_state.get('enhanced_papers', None)
        
        st.subheader(f"📚 {len(papers)} Papers Analyzed")

        # Platform filter if multi-platform
        selected_platform = "All"
        if enhanced_papers:
            platforms = set()
            for ep in enhanced_papers:
                if hasattr(ep, 'platform'):
                    platforms.add(ep.platform)
                elif isinstance(ep, dict):
                    platforms.add(ep.get('platform', 'arXiv'))
            
            if platforms:
                platforms_list = ["All"] + sorted(list(platforms))
                selected_platform = st.selectbox("🔍 Filter by Platform", platforms_list)
        
        # Filter papers by platform if filter is set
        papers_to_show = papers
        enhanced_to_show = enhanced_papers
        
        if selected_platform != "All" and enhanced_papers:
            filtered_indices = []
            for i, ep in enumerate(enhanced_papers):
                platform = ep.platform if hasattr(ep, 'platform') else (ep.get('platform', '') if isinstance(ep, dict) else '')
                if platform == selected_platform:
                    filtered_indices.append(i)
            
            papers_to_show = [papers[i] for i in filtered_indices if i < len(papers)]
            enhanced_to_show = [enhanced_papers[i] for i in filtered_indices]
        
        # Display papers with enhanced cards
        for i, paper in enumerate(papers_to_show):
            # Use enhanced paper if available
            if enhanced_to_show and i < len(enhanced_to_show):
                enhanced = enhanced_to_show[i]
                st.markdown(create_enhanced_paper_card(enhanced, i), unsafe_allow_html=True)
            else:
                # Fallback to enhanced card format with basic paper data
                st.markdown(create_enhanced_paper_card(paper, i), unsafe_allow_html=True)
        
        if not papers_to_show:
            st.info(f"No papers found for platform: {selected_platform}")
    else:
        st.info("No papers loaded yet. Run the analysis first.")

# TAB 3: Research Insights
with tab3:
    track_tab_switch("Research Insights")
    if st.session_state.insights:
        insights = st.session_state.insights
        st.subheader(f"💡 {len(insights)} Research Opportunities")
        
        # Shared Timeline Section (if applicable)
        timeline_analysis = analyze_shared_timeline(insights)
        if timeline_analysis.get('has_shared_timeline'):
            st.markdown("### 📅 Shared Experiment Timeline")
            st.markdown("*Common experimental steps across all insights*")
            timeline_html = create_timeline_visualization(insights)
            if timeline_html:
                st.markdown(timeline_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)

        # Conceptual Reasoning Flow - render once before insights
        st.markdown("### 🧠 Conceptual Reasoning Flow")
        st.markdown("*This flow represents the structured reasoning process applied to each research opportunity*")
        # Create a generic reasoning flow visualization (use first insight as example, or create generic one)
        if insights:
            # Use first insight to show the flow structure
            reasoning_flow_html = create_reasoning_flow(insights[0])
            st.markdown(reasoning_flow_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)

        for i, insight in enumerate(insights, 1):
            # Calculate overall score
            overall = (
                insight.get('novelty_score', 0) +
                insight.get('feasibility_score', 0) +
                insight.get('impact_score', 0)
            ) / 3

            full_title = insight.get('title', 'Untitled')
            summary = extract_insight_summary(insight)
            novelty_score = insight.get('novelty_score', 0)
            feasibility_score = insight.get('feasibility_score', 0)
            impact_score = insight.get('impact_score', 0)
            survival_score = insight.get('survival_score', 0)
            is_validated = insight.get('validated', False)

            # Enhanced card with clear hierarchy
            with st.container():
                # Card container with AiResearcher styling
                st.markdown(f"""
                <div class="insight-card" style="margin-bottom: 2rem;">
                    <!-- Title and Summary Section -->
                    <div style="margin-bottom: 1rem;">
                        <h2 style="font-size: 1.5em; font-weight: 600; color: #2C2B27; margin-bottom: 0.5rem; line-height: 1.3;">
                            {i}. {html.escape(full_title)}
                        </h2>
                        <p style="font-size: 1.05em; color: #5B574D; font-style: italic; margin: 0; line-height: 1.7; font-weight: 400;">
                            {html.escape(summary)}
                        </p>
                        </div>
                    
                    <!-- Mini-Stats Badges and Validation Badge -->
                    <div style="display: flex; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid #E0DED9;">
                        <span class="mini-stat-badge" style="background: #FAF9F7; color: #2C2B27; padding: 0.3rem 0.7rem; border-radius: 8px; font-size: 0.85em; font-weight: 500; border: 1px solid #E0DED9;">
                            🧠 Novelty {novelty_score:.1f}
                        </span>
                        <span class="mini-stat-badge" style="background: #FAF9F7; color: #2C2B27; padding: 0.3rem 0.7rem; border-radius: 8px; font-size: 0.85em; font-weight: 500; border: 1px solid #E0DED9;">
                            ⚙️ Feasibility {feasibility_score:.1f}
                        </span>
                        <span class="mini-stat-badge" style="background: #FAF9F7; color: #2C2B27; padding: 0.3rem 0.7rem; border-radius: 8px; font-size: 0.85em; font-weight: 500; border: 1px solid #E0DED9;">
                            💥 Impact {impact_score:.1f}
                        </span>
                        <div style="margin-left: auto; display: flex; align-items: center; gap: 0.5rem;">
                """, unsafe_allow_html=True)
                
                # Validation badge and overall score - using pastel colors
                validator_style = AGENT_STYLES.get("Validator", {"color": "#B8A9D9", "bg": "#F7F5FA"})
                if is_validated:
                    validation_bg = "#F5F9F6"  # Synthesizer pastel green
                    validation_border = "#9FC5A8"
                    validation_text = "#2C2B27"
                    validation_status_text = "✓ VALIDATED"
                else:
                    validation_bg = "#FAF5F5"  # Skeptic pastel red
                    validation_border = "#C99A9A"
                    validation_text = "#2C2B27"
                    validation_status_text = "⚠️ UNVALIDATED"
                
                st.markdown(f"""
                            <span style="display: inline-block;
                                        background: {validation_bg};
                                        color: {validation_text};
                                        border: 1px solid {validation_border};
                                        padding: 0.3rem 0.8rem;
                                        border-radius: 15px;
                                        font-size: 0.85em;
                                        font-weight: 600;">
                                {validation_status_text} ({survival_score:.1f}/10)
                            </span>
                            <span style="display: inline-block;
                                        background: #FAF9F7;
                                        color: #2C2B27;
                                        border: 1px solid #E0DED9;
                                        padding: 0.4rem 0.9rem;
                                        border-radius: 20px;
                                        font-weight: 600;
                                        font-size: 1em;">
                                {overall:.1f}/10
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.divider()
                
                # Layer 1: Observation
                observation = insight.get('observation', '')
                if observation:
                    st.markdown("#### 1️⃣ Observation")
                    st.markdown(f"*What patterns do we see across papers?*")
                    # HTML comments are cleaned inside create_styled_content_box
                    st.markdown(create_styled_content_box(observation, "observation"), unsafe_allow_html=True)
                else:
                    # Fallback to gap if observation not available (backward compatibility)
                    st.markdown("#### 1️⃣ Observation (The Gap)")
                    st.markdown(f"*What patterns do we see across papers?*")
                    # HTML comments are cleaned inside create_styled_content_box
                    st.markdown(create_styled_content_box(insight.get('gap', 'N/A'), "observation"), unsafe_allow_html=True)

                # Layer 2: Hypothesis
                hypothesis = insight.get('hypothesis', '')
                if hypothesis:
                    st.markdown("#### 2️⃣ Hypothesis")
                    st.markdown(f"*What testable claim can we make?*")
                    # HTML comments are cleaned inside create_styled_content_box
                    st.markdown(create_styled_content_box(hypothesis, "success"), unsafe_allow_html=True)

                # Layer 3: Experiment Design
                exp = insight.get('experiment_design', {})
                if exp:
                    st.markdown("#### 3️⃣ Experiment Design")
                    st.markdown(f"*How would we test this hypothesis?*")
                    
                    # Display scientific experiment design if available
                    if exp.get('objective') or exp.get('independent_variable') or exp.get('dependent_variables'):
                        # Scientific methodology format
                        if exp.get('objective'):
                            # Strip HTML tags from objective text
                            objective_text = strip_html_tags(exp.get('objective', ''))
                            st.markdown(f"**Objective:** {objective_text}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if exp.get('independent_variable'):
                                # Strip HTML tags before creating content box
                                independent_var_text = strip_html_tags(exp.get('independent_variable', ''))
                                st.markdown(f"**Independent Variable:**")
                                st.markdown(create_styled_content_box(independent_var_text, "info"), unsafe_allow_html=True)
                            if exp.get('control_group'):
                                # Strip HTML tags before creating content box
                                control_group_text = strip_html_tags(exp.get('control_group', ''))
                                st.markdown(f"**Control Group:**")
                                st.markdown(create_styled_content_box(control_group_text, "info"), unsafe_allow_html=True)
                        
                        with col2:
                            if exp.get('dependent_variables'):
                                deps = exp.get('dependent_variables', [])
                                if isinstance(deps, list):
                                    # Strip HTML tags from each dependent variable
                                    deps_cleaned = [strip_html_tags(str(dep)) for dep in deps]
                                    st.markdown(f"**Dependent Variables:**")
                                    st.markdown(create_styled_content_box(', '.join(deps_cleaned) if deps_cleaned else 'N/A', "info"), unsafe_allow_html=True)
                                else:
                                    # Strip HTML tags from dependent variables string
                                    deps_text = strip_html_tags(str(deps))
                                    st.markdown(f"**Dependent Variables:**")
                                    st.markdown(create_styled_content_box(deps_text, "info"), unsafe_allow_html=True)
                        
                        # Experimental Procedure (Phases)
                        if exp.get('experimental_procedure'):
                            proc = exp.get('experimental_procedure', {})
                            if isinstance(proc, dict) and proc:
                                st.markdown(f"**Experimental Procedure:**")
                                for phase, desc in proc.items():
                                    # Strip HTML tags from phase description
                                    phase_num = phase.replace('phase', '').upper() if 'phase' in phase.lower() else phase.upper()
                                    desc_cleaned = strip_html_tags(str(desc))
                                    st.markdown(f"- **{phase_num}:** {desc_cleaned}")
                        
                        # Expected Outcome
                        if exp.get('expected_outcome'):
                            # Strip HTML tags before creating content box
                            expected_outcome_text = strip_html_tags(exp.get('expected_outcome', ''))
                            st.markdown(f"**Expected Outcome:**")
                            st.markdown(create_styled_content_box(expected_outcome_text, "success"), unsafe_allow_html=True)
                        
                        # Fallback Plan
                        if exp.get('fallback_plan'):
                            # Strip HTML tags before creating content box
                            fallback_plan_text = strip_html_tags(exp.get('fallback_plan', ''))
                            st.markdown(f"**Fallback Plan:**")
                            st.markdown(create_styled_content_box(fallback_plan_text, "warning"), unsafe_allow_html=True)
                        
                        # Deliverables
                        if exp.get('deliverables'):
                            dels = exp.get('deliverables', [])
                            if isinstance(dels, list) and dels:
                                st.markdown(f"**Deliverables:**")
                                for deliverable in dels:
                                    # Strip HTML tags from each deliverable
                                    deliverable_cleaned = strip_html_tags(str(deliverable))
                                    st.markdown(f"- {deliverable_cleaned}")
                            elif dels:
                                # Strip HTML tags from deliverables string
                                dels_text = strip_html_tags(str(dels))
                                st.markdown(f"**Deliverables:** {dels_text}")
                        
                        # Show experiment design quality score if available
                        if insight.get('experiment_design_quality'):
                            quality_score = insight.get('experiment_design_quality', 0)
                            st.markdown(f"**Experiment Design Quality:** {quality_score:.1f}/10")
                            if insight.get('experiment_design_feedback'):
                                st.caption(f"*{insight.get('experiment_design_feedback')}*")
                    
                    # Legacy format (week1/week2/week3) - show if scientific format not available or as additional info
                    if exp.get('week1') or exp.get('week2') or exp.get('week3'):
                        # Strip any HTML tags from week text to prevent raw HTML from showing
                        week1_text = strip_html_tags(exp.get('week1', 'N/A')) if exp.get('week1') else 'N/A'
                        week2_text = strip_html_tags(exp.get('week2', 'N/A')) if exp.get('week2') else 'N/A'
                        week3_text = strip_html_tags(exp.get('week3', 'N/A')) if exp.get('week3') else 'N/A'
                        
                        if not exp.get('objective') and not exp.get('independent_variable'):
                            # Only show legacy format if scientific format not available
                            st.markdown(f"**Week 1:** {week1_text}")
                            st.markdown(f"**Week 2:** {week2_text}")
                            st.markdown(f"**Week 3:** {week3_text}")
                        else:
                            # Show as timeline summary if scientific format is also present
                            st.markdown("**Timeline Summary:**")
                            if exp.get('week1'):
                                st.markdown(f"- **Week 1:** {week1_text}")
                            if exp.get('week2'):
                                st.markdown(f"- **Week 2:** {week2_text}")
                            if exp.get('week3'):
                                st.markdown(f"- **Week 3:** {week3_text}")

                # Layer 4: Expected Insight
                expected_insight = insight.get('expected_insight', '')
                if expected_insight:
                    st.markdown("#### 4️⃣ Expected Insight")
                    st.markdown(f"*What principle could emerge if confirmed?*")
                    st.markdown(create_styled_content_box(expected_insight, "warning"), unsafe_allow_html=True)

                # Layer 5: Validation
                if insight.get('validation_evidence'):
                    st.markdown("#### 5️⃣ Validation")
                    st.markdown(f"*Is this space already occupied?*")
                    validation_status = "✓ VALIDATED" if insight.get('validated') else "⚠️ UNVALIDATED"
                    survival_score = insight.get('survival_score', 0)
                    st.markdown(f"**Status:** {validation_status} | **Survival Score:** {survival_score}/10")
                    if insight.get('validated'):
                        st.markdown(create_styled_content_box(insight['validation_evidence'], "success"), unsafe_allow_html=True)
                    else:
                        st.markdown(create_styled_content_box(insight['validation_evidence'], "warning"), unsafe_allow_html=True)
                    
                    # Show evidence links
                    evidence_links = extract_evidence_links(insight)
                    if evidence_links:
                        st.markdown("**✅ Validated against:**")
                        links_text = " | ".join([link['title'] for link in evidence_links[:3]])
                        st.markdown(f'<p style="color: #D94B2B; font-size: 0.9em;">{html.escape(links_text)}</p>', unsafe_allow_html=True)
                    
                    # Show related work if available
                    if insight.get('related_work'):
                        st.markdown("**Related Work:**")
                        for work in insight['related_work'][:3]:
                            st.markdown(f"- {work}")

                st.divider()

                # Additional details (backward compatibility)
                if not observation and not hypothesis:
                    # Show gap and challenge if 5-layer structure not available
                    st.markdown("#### 🎯 The Gap (What's Missing)")
                    st.write(insight.get('gap', 'N/A'))

                    # Skeptic's Challenge
                    st.markdown("#### ⚠️ Skeptic's Challenge")
                    st.markdown(create_styled_content_box(insight.get('skeptic_challenge', 'N/A'), "info"), unsafe_allow_html=True)

                # Impact
                st.markdown("#### 💰 Why This Matters")
                st.markdown(create_styled_content_box(insight.get('impact', 'N/A'), "success"), unsafe_allow_html=True)

                # Separator between insights
                if i < len(insights):
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.divider()
                    st.markdown("<br>", unsafe_allow_html=True)
        
        # Collective Insight Summary
        if insights:
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<br>", unsafe_allow_html=True)
            
            collective_summary = generate_collective_summary(
                insights, 
                st.session_state.get('research_intelligence')
            )
            
            if collective_summary:
                st.markdown("### 🎯 Collective Insight Summary")
                st.markdown(f"""
                <div style="
                    background: #FAF9F7;
                    border: 2px solid #E0DED9;
                    border-left: 3px solid #9FC5A8;
                    border-radius: 16px;
                    padding: 1.5rem;
                    margin: 2rem 0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                ">
                    <p style="font-size: 1.1em; line-height: 1.7; color: #2C2B27; margin: 0;">
                        {html.escape(collective_summary)}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No insights generated yet. Run the analysis first.")

# TAB 4: Agent Conversation
with tab4:
    track_tab_switch("Agent Conversation")
    if st.session_state.conversation_log:
        st.subheader("🧠 Research Roundtable: Agent Conversation")
        st.markdown("*Watch how agents reason together in a Socratic dialogue*")

        log = st.session_state.conversation_log
        insights = st.session_state.get('insights', [])
        
        # Use global agent styles
        agent_styles = AGENT_STYLES

        st.markdown("### 💬 Dialogue Sequence")

        # Display conversation as roundtable dialogue
        for entry in log:
            agent_name = entry.get('agent', 'Unknown')
            turn = entry.get('turn', 0)
            message_type = entry.get('message_type', 'observation')
            responding_to = entry.get('responding_to', [])
            dialogue_message = entry.get('dialogue_message', '')
            style = agent_styles.get(agent_name, {"color": "#6B7280", "bg": "#F3F4F6", "icon": "🤖"})
            
            # Conversation bubble
            with st.container():
                # Turn indicator and responding to
                turn_info = f"**Turn {turn}**"
                if responding_to:
                    turn_info += f" → Responding to: {', '.join(responding_to)}"
                
                col_icon, col_content = st.columns([1, 15])
                with col_icon:
                    st.markdown(f"""
                    <div style="
                        background: {style['bg']};
                        color: {style['color']};
                        width: 50px;
                        height: 50px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 1.5em;
                        border: 2px solid {style['color']};
                    ">
                        {style['icon']}
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_content:
                    # Turn-level summary (visible) - properly escaped
                    output_summary = entry.get('output_summary', '')
                    if output_summary:
                        summary_escaped = html.escape(str(output_summary))
                        agent_name_escaped = html.escape(agent_name)
                        st.markdown(f"""
                        <div style="
                            background: {style['bg']};
                            border-left: 3px solid {style['color']};
                            padding: 0.6rem 0.8rem;
                            border-radius: 6px;
                            margin-bottom: 0.5rem;
                            font-weight: 500;
                            font-size: 0.95em;
                            color: #2C2B27;
                        ">
                            <strong>{agent_name_escaped}:</strong> {summary_escaped}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Agent name and turn - properly escaped
                    if 'agent_name_escaped' not in locals():
                        agent_name_escaped = html.escape(agent_name)
                    turn_info_escaped = html.escape(turn_info)
                    st.markdown(f"""
                    <div style="margin-bottom: 0.5rem;">
                        <span style="color: {style['color']}; font-weight: 600; font-size: 1.1em;">{style['icon']} {agent_name_escaped}</span>
                        <span style="color: #6B7280; font-size: 0.85em; margin-left: 1rem;">{turn_info_escaped}</span>
                        <span style="color: #9CA3AF; font-size: 0.8em; margin-left: 1rem;">⏱️ {entry.get('duration', 0):.1f}s</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Dialogue message (main content - details) - properly escaped
                    if dialogue_message:
                        dialogue_escaped = html.escape(str(dialogue_message))
                        st.markdown(f"""
                        <div style="
                            background: {style['bg']};
                            border-left: 4px solid {style['color']};
                            padding: 1rem;
                            border-radius: 8px;
                            margin-bottom: 0.5rem;
                            font-size: 1.05em;
                            line-height: 1.6;
                            color: #2C2B27;
                        ">
                            {dialogue_escaped}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Additional details (thinking, findings, etc.) - styled box instead of expander
                    if entry.get('thinking'):
                        thoughts_html = ""
                        for thought in entry['thinking']:
                            thought_escaped = html.escape(str(thought))
                            thoughts_html += f"<li style='margin: 0.5rem 0; color: #5B574D;'>{thought_escaped}</li>"
                        
                        st.markdown(f"""
                        <div style="
                            background: {style['bg']};
                            border: 1px solid {style['color']};
                            border-left: 3px solid {style['color']};
                            border-radius: 8px;
                            padding: 1rem;
                            margin: 1rem 0;
                        ">
                            <div style="font-weight: 600; color: {style['color']}; margin-bottom: 0.8rem; font-size: 0.95em;">
                                💭 Detailed Reasoning
                            </div>
                            <ul style="margin: 0; padding-left: 1.5rem; color: #2C2B27;">
                                {thoughts_html}
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Show specific agent outputs - styled boxes instead of st.info/st.success
                    if agent_name == "Skeptic":
                        if entry.get('field_insights'):
                            field_insights_text = str(entry['field_insights'])
                            field_insights_escaped = html.escape(field_insights_text[:300] + ('...' if len(field_insights_text) > 300 else ''))
                            st.markdown(f"""
                            <div style="
                                background: {style['bg']};
                                border: 1px solid {style['color']};
                                border-left: 3px solid {style['color']};
                                border-radius: 8px;
                                padding: 1rem;
                                margin: 1rem 0;
                            ">
                                <div style="font-weight: 600; color: {style['color']}; margin-bottom: 0.5rem; font-size: 0.95em;">
                                    Field Insights
                                </div>
                                <div style="color: #2C2B27; line-height: 1.6; font-size: 0.95em;">
                                    {field_insights_escaped}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        if entry.get('potential_contradictions'):
                            contradictions_html = ""
                            for pc in entry['potential_contradictions'][:2]:
                                desc = str(pc.get('description', ''))[:150]
                                if desc:
                                    desc_escaped = html.escape(desc) + '...'
                                    contradictions_html += f"<li style='margin: 0.5rem 0; color: #5B574D;'>{desc_escaped}</li>"
                            
                            if contradictions_html:
                                st.markdown(f"""
                                <div style="
                                    background: {style['bg']};
                                    border: 1px solid {style['color']};
                                    border-left: 3px solid {style['color']};
                                    border-radius: 8px;
                                    padding: 1rem;
                                    margin: 1rem 0;
                                ">
                                    <div style="font-weight: 600; color: {style['color']}; margin-bottom: 0.5rem; font-size: 0.95em;">
                                        🔍 Potential Contradictions
                                    </div>
                                    <ul style="margin: 0; padding-left: 1.5rem; color: #2C2B27;">
                                        {contradictions_html}
                                    </ul>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    if agent_name == "Synthesizer" and entry.get('insights'):
                        insights_list = entry.get('insights', [])
                        insights_html = ""
                        for i, insight in enumerate(insights_list[:2], 1):
                            if isinstance(insight, dict):
                                title = str(insight.get('title', 'Untitled'))[:80]
                                title_escaped = html.escape(title) + ('...' if len(str(insight.get('title', ''))) > 80 else '')
                                insights_html += f"<li style='margin: 0.5rem 0; color: #5B574D;'>{i}. {title_escaped}</li>"
                        
                        if insights_html:
                            st.markdown(f"""
                            <div style="
                                background: {style['bg']};
                                border: 1px solid {style['color']};
                                border-left: 3px solid {style['color']};
                                border-radius: 8px;
                                padding: 1rem;
                                margin: 1rem 0;
                            ">
                                <div style="font-weight: 600; color: {style['color']}; margin-bottom: 0.5rem; font-size: 0.95em;">
                                    Generated {len(insights_list)} insights:
                                </div>
                                <ul style="margin: 0; padding-left: 1.5rem; color: #2C2B27;">
                                    {insights_html}
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    if agent_name == "Validator" and entry.get('validated_insights'):
                        validated_list = entry.get('validated_insights', [])
                        survived = len([v for v in validated_list if isinstance(v, dict) and v.get('validated', False)])
                        st.markdown(f"""
                        <div style="
                            background: {style['bg']};
                            border: 1px solid {style['color']};
                            border-left: 3px solid {style['color']};
                            border-radius: 8px;
                            padding: 1rem;
                            margin: 1rem 0;
                        ">
                            <div style="font-weight: 600; color: {style['color']}; margin-bottom: 0.5rem; font-size: 0.95em;">
                                Validation Result
                            </div>
                            <div style="color: #2C2B27; font-size: 0.95em;">
                                {survived}/{len(validated_list)} insights validated
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.divider()
                st.markdown("<br>", unsafe_allow_html=True)

        # Consensus Indicators
        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()
        st.markdown("### 📊 Consensus Metrics")
        
        consensus_metrics = calculate_consensus_metrics(log, insights)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🤝 Consensus Reached", consensus_metrics['consensus_reached'])
        with col2:
            st.metric("⚔️ Disagreement Index", f"{consensus_metrics['disagreement_index']:.2f}")
        with col3:
            st.metric("🧩 Insight Strength", f"{consensus_metrics['insight_strength']:.1f}/10")
        
        # Meta-Commentary - AiResearcher design (no purple gradient)
        st.markdown("<br>", unsafe_allow_html=True)
        meta_commentary = generate_meta_commentary(log, insights)
        if meta_commentary:
            meta_escaped = html.escape(meta_commentary)
        st.markdown(f"""
        <div style="
                background: #FAF9F7;
                border: 2px solid #D94B2B;
                border-radius: 12px;
            padding: 1.5rem;
                margin: 2rem 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            ">
                <h3 style="color: #2C2B27; margin: 0 0 0.5rem 0; font-size: 1.2em; font-weight: 600;">🧠 System Summary</h3>
                <p style="color: #2C2B27; margin: 0; font-size: 1.05em; line-height: 1.6;">
                    {meta_escaped}
                </p>
            </div>
            """, unsafe_allow_html=True)

        # Summary - AiResearcher design (no purple gradient)
        total_duration = sum([e.get('duration', 0) for e in log])
        st.markdown(f"""
        <div style="
            background: #F5F9F6;
            border: 2px solid #9FC5A8;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            margin-top: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        ">
            <h3 style="color: #2C2B27; margin: 0; font-size: 1.2em; font-weight: 600;">✅ Roundtable Complete</h3>
            <p style="color: #5B574D; margin: 0.5rem 0 0 0; font-size: 1em;">Pipeline completed successfully in {total_duration:.1f}s</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No conversation log available. Run the analysis first.")

# TAB 5: Full Report
with tab5:
    track_tab_switch("Full Report")
    if st.session_state.insights and st.session_state.papers:
        st.subheader("📄 Full Report")

        insights = st.session_state.insights
        papers = st.session_state.papers
        topic = st.session_state.get('last_topic', 'machine learning')

        # Generate Markdown Report
        report_lines = [
            f"# Research Analysis Report",
            f"\n**Topic:** {topic}",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Papers Analyzed:** {len(papers)}",
            f"**Insights Generated:** {len(insights)}",
            f"\n---\n",
            f"\n## 💡 Research Opportunities\n"
        ]

        for i, insight in enumerate(insights, 1):
            overall = (
                insight.get('novelty_score', 0) +
                insight.get('feasibility_score', 0) +
                insight.get('impact_score', 0)
            ) / 3

            report_lines.append(f"\n### {i}. {insight.get('title', 'Untitled')} (Score: {overall:.1f}/10)\n")
            
            # 5-Layer Conceptual Reasoning Structure
            observation = insight.get('observation', '')
            hypothesis = insight.get('hypothesis', '')
            expected_insight = insight.get('expected_insight', '')
            
            if observation or hypothesis:
                report_lines.append(f"\n## Conceptual Reasoning Flow\n")
                
                if observation:
                    report_lines.append(f"\n**1. Observation:**\n{observation}\n")
                else:
                    report_lines.append(f"\n**1. Observation (The Gap):**\n{insight.get('gap', 'N/A')}\n")
                
                if hypothesis:
                    report_lines.append(f"\n**2. Hypothesis:**\n{hypothesis}\n")
                
                exp = insight.get('experiment_design', {})
                if exp:
                    report_lines.append(f"\n**3. Experiment Design:**")
                    # Scientific methodology format
                    if exp.get('objective'):
                        report_lines.append(f"\n**Objective:** {exp.get('objective')}")
                    if exp.get('independent_variable'):
                        report_lines.append(f"\n**Independent Variable:** {exp.get('independent_variable')}")
                    if exp.get('dependent_variables'):
                        deps = exp.get('dependent_variables', [])
                        if isinstance(deps, list):
                            report_lines.append(f"\n**Dependent Variables:** {', '.join(deps)}")
                        else:
                            report_lines.append(f"\n**Dependent Variables:** {deps}")
                    if exp.get('control_group'):
                        report_lines.append(f"\n**Control Group:** {exp.get('control_group')}")
                    if exp.get('experimental_procedure'):
                        proc = exp.get('experimental_procedure', {})
                        if isinstance(proc, dict):
                            report_lines.append(f"\n**Experimental Procedure:**")
                            for phase, desc in proc.items():
                                report_lines.append(f"- **{phase}:** {desc}")
                    if exp.get('expected_outcome'):
                        report_lines.append(f"\n**Expected Outcome:** {exp.get('expected_outcome')}")
                    if exp.get('fallback_plan'):
                        report_lines.append(f"\n**Fallback Plan:** {exp.get('fallback_plan')}")
                    if exp.get('deliverables'):
                        dels = exp.get('deliverables', [])
                        if isinstance(dels, list):
                            report_lines.append(f"\n**Deliverables:** {', '.join(dels)}")
                        else:
                            report_lines.append(f"\n**Deliverables:** {dels}")
                    # Legacy format
                    if exp.get('week1') or exp.get('week2') or exp.get('week3'):
                        report_lines.append(f"\n**Timeline:**")
                        report_lines.append(f"- **Week 1:** {exp.get('week1', 'N/A')}")
                        report_lines.append(f"- **Week 2:** {exp.get('week2', 'N/A')}")
                        report_lines.append(f"- **Week 3:** {exp.get('week3', 'N/A')}")
                        report_lines.append("")
                
                if expected_insight:
                    report_lines.append(f"\n**4. Expected Insight:**\n{expected_insight}\n")
                
                # Validation
                if insight.get('validation_evidence'):
                    validation_status = "✓ VALIDATED" if insight.get('validated') else "⚠️ UNVALIDATED"
                    report_lines.append(f"\n**5. Validation:** {validation_status} (Survival Score: {insight.get('survival_score', 0)}/10)")
                    report_lines.append(f"\n**Validation Evidence:**\n{insight.get('validation_evidence')}\n")
                    if insight.get('related_work'):
                        report_lines.append(f"\n**Related Work:**")
                        for work in insight.get('related_work', [])[:5]:
                            report_lines.append(f"- {work}")
                        report_lines.append("")
            else:
                # Fallback to old format (backward compatibility)
                report_lines.append(f"\n**The Gap:**\n{insight.get('gap', 'N/A')}\n")
                report_lines.append(f"\n**Skeptic's Challenge:**\n{insight.get('skeptic_challenge', 'N/A')}\n")

                exp = insight.get('experiment_design', {})
                if exp:
                    report_lines.append(f"\n**3-Week Experiment:**")
                    report_lines.append(f"- **Week 1:** {exp.get('week1', 'N/A')}")
                    report_lines.append(f"- **Week 2:** {exp.get('week2', 'N/A')}")
                    report_lines.append(f"- **Week 3:** {exp.get('week3', 'N/A')}\n")
                
                # Add validation information
                if insight.get('validated'):
                    report_lines.append(f"\n**Validation:** ✓ VALIDATED (Survival Score: {insight.get('survival_score', 0)}/10)")
                    if insight.get('validation_evidence'):
                        report_lines.append(f"\n**Validation Evidence:**\n{insight.get('validation_evidence')}\n")
                else:
                    report_lines.append(f"\n**Validation:** ⚠️ UNVALIDATED (Survival Score: {insight.get('survival_score', 0)}/10)")
                    if insight.get('validation_evidence'):
                        report_lines.append(f"\n**Validation Evidence:**\n{insight.get('validation_evidence')}\n")
            
            report_lines.append(f"\n**Impact:**\n{insight.get('impact', 'N/A')}\n")
            report_lines.append(f"\n**Scores:**\n")
            report_lines.append(f"- **Novelty:** {insight.get('novelty_score', 0)}/10")
            report_lines.append(f"- **Feasibility:** {insight.get('feasibility_score', 0)}/10")
            report_lines.append(f"- **Impact:** {insight.get('impact_score', 0)}/10")
            report_lines.append("")

        report_lines.append(f"\n---\n\n## 📚 Papers Analyzed\n")

        for i, paper in enumerate(papers, 1):
            report_lines.append(f"\n### {i}. {paper.title}")
            report_lines.append(f"**Authors:** {', '.join(paper.authors[:3])}")
            report_lines.append(f"**Year:** {paper.year}")
            report_lines.append(f"**URL:** {paper.url}\n")

        report_lines.append(f"\n---\n\n*Generated by AiResearcher - Multi-Agent Research System*")

        markdown_report = "\n".join(report_lines)

        # JSON Export
        json_data = {
            "topic": topic,
            "date": datetime.now().isoformat(),
            "papers": [
                {
                    "title": p.title,
                    "authors": p.authors,
                    "year": p.year,
                    "url": p.url,
                    "abstract": p.abstract[:500]
                }
                for p in papers
            ],
            "insights": insights,
            "conversation_log": st.session_state.conversation_log
        }

        # Download buttons
        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="📄 Download Markdown Report",
                data=markdown_report,
                file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col2:
            st.download_button(
                label="📊 Download JSON Data",
                data=json.dumps(json_data, indent=2),
                file_name=f"research_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True
            )

        st.divider()

        # Preview - styled HTML box instead of expander
        st.subheader("📄 Report Preview")
        # Render markdown report in a styled container
        # Use st.markdown with custom CSS class for styling
        st.markdown(f"""
        <div style="
            background: #FAF9F7;
            border: 2px solid #E0DED9;
            border-left: 3px solid #9FC5A8;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            max-height: 700px;
            overflow-y: auto;
        ">
        <div style="
            font-family: 'Space Grotesk', sans-serif;
            line-height: 1.7;
            color: #2C2B27;
        ">
        """, unsafe_allow_html=True)
        
        # Render the markdown report - Streamlit will render it as markdown
        st.markdown(markdown_report)
        
        # Close the styled container
        st.markdown("""
        </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No data to export. Run the analysis first.")

# TAB 6: Next Discovery
with tab6:
    track_tab_switch("Next Discovery")
    
    st.markdown("""
    <div style="
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem 0;
    ">
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("## 🧭 Next Discovery — From Insight to Ideation")
    
    st.markdown("""
    Every discovery is just the beginning. This space helps you transform validated insights into new hypotheses, creative experiments, or publishable ideas. It draws from scientific creativity, design thinking, and the BMAD method — a structured approach to innovation used in advanced research labs.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # The Purpose
    st.markdown("### The Purpose")
    st.markdown("""
    After generating and validating insights with AiResearcher, the next step is exploration — questioning assumptions, remixing methods, and expanding what's possible. This guide helps you move from insight to ideation using frameworks that blend creativity with analytical depth.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # The BMAD Method
    st.markdown("### The BMAD Method (Break down, Map, Analyze, Develop)")
    st.markdown("""
    Begin by breaking down your validated insight into its essential components: data sources, methods, results, and assumptions. Then map the relationships between them — note where they depend, where they overlap, and where gaps appear. Analyze these relationships for tensions or weak points that invite further exploration. Finally, develop the most promising paths into hypotheses, pilot experiments, or collaborative projects.
    
    BMAD encourages iterative curiosity: each "Develop" step becomes the next "Break down." Over time, it forms a continuous loop of creative reasoning.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # SCAMPER Thinking
    st.markdown("### SCAMPER Thinking")
    st.markdown("""
    Once you have a research direction, reimagine it through transformation. Substitute methods, combine approaches, adapt concepts from other domains, modify the structure, put ideas to new uses, eliminate what's unnecessary, and reverse assumptions. SCAMPER works best when you challenge conventions that appear settled.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Cross-Domain Transfer
    st.markdown("### Cross-Domain Transfer")
    st.markdown("""
    Many breakthroughs come from analogy. Translate your idea into another discipline's language — what would a biologist, architect, or sociologist do with this concept? Seeing your idea through another field's framework can expose missing variables, new metaphors, or entirely fresh models.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Constraint-Driven Creativity
    st.markdown("### Constraint-Driven Creativity")
    st.markdown("""
    Imagination thrives under pressure. Try limiting your dataset, computing resources, or time frame. Ask: what would the smallest possible version of this idea look like? Constraints force simplification and often lead to elegant, efficient designs that scale later.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Future Backcasting
    st.markdown("### Future Backcasting")
    st.markdown("""
    Picture success five years ahead — your work cited, your method standardized, your dataset reused. Now work backward. What milestones or collaborations must happen for that vision to exist? Backcasting translates idealism into an actionable roadmap.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Divergent and Convergent Flow
    st.markdown("### Divergent and Convergent Flow")
    st.markdown("""
    Alternate between creative expansion and critical focus. Spend one session generating as many ideas as possible — even absurd ones. Then switch gears and narrow them down to one or two feasible projects. Repeating this rhythm produces both novelty and rigor.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Systems Mapping and Concept Networks
    st.markdown("### Systems Mapping and Concept Networks")
    st.markdown("""
    Represent your research as an ecosystem. Draw connections among methods, data, and outcomes — each link is a potential discovery. Systemic mapping reveals leverage points where a small shift can lead to large conceptual gains.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Analogy and Metaphor Storming
    st.markdown("### Analogy and Metaphor Storming")
    st.markdown("""
    Transform abstract problems into vivid metaphors. If your algorithm were a living organism, what would it eat, breathe, or compete with? If your research were a city, where would the traffic jams occur? These metaphorical translations spark lateral thinking — often yielding insights no linear analysis could reach.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Extended BMAD Prompting
    st.markdown("### Extended BMAD Prompting")
    st.markdown("""
    You can run BMAD interactively with language models:
    
    Begin by describing your validated insight. Request the model to break it down into parts. Then ask for a map of relationships. Have it analyze where tensions, gaps, or contradictions lie. Finally, prompt it to develop new hypotheses or projects based on those discoveries.
    
    This creates an iterative ideation process — reasoning through exploration beyond summarization.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Creative Reflection
    st.markdown("### Creative Reflection")
    st.markdown("""
    What surprised you in your last analysis? Which assumptions proved weakest? Which ideas recur across unrelated papers? Reflection transforms noise into new structure — it's where intuition refines evidence.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # From Insight to Impact
    st.markdown("### From Insight to Impact")
    st.markdown("""
    Every validated finding is an invitation — to explore, write, prototype, or collaborate. The discovery process doesn't end with validation; it begins with it. Use this space to reimagine what your insight could become when extended, shared, or challenged.
    """)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("*Validated Insight → Brainstorm → Prototype → Test → Publish*")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Placeholder buttons
    col1, col2 = st.columns(2)
    with col1:
        st.button("🧠 Start Brainstorming Session", use_container_width=True, disabled=True)
    with col2:
        st.button("📝 Export Ideas", use_container_width=True, disabled=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
