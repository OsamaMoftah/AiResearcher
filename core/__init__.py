"""
Core research analysis modules.

Provides research agent system, paper search, and language model interfaces.
"""
from .research import ResearchAgent
from .arxiv import Paper

__all__ = ["ResearchAgent", "Paper"]
