# AiResearcher

A multi-agent research system that transforms academic papers into validated research insights with actionable experiment designs.

## 🎥 Demo Video

<video src="https://github.com/OsamaMoftah/AiResearcher/raw/main/AiResearcher.mp4" controls width="100%"></video>

*Watch the demo to see AiResearcher in action!*

## Overview

AiResearcher analyzes research papers using a specialized agent pipeline to identify gaps, challenge assumptions, and generate validated research opportunities. The system searches across multiple academic platforms, performs deep analysis, and provides experiment designs with validation against prior work.

## Features

- Multi-platform search across arXiv, Papers with Code, and Hugging Face
- Four-agent pipeline: Analyzer, Skeptic, Synthesizer, and Validator
- Validated research insights with survival scores
- Actionable experiment designs with timelines
- Full reasoning chains and exportable reports

## Requirements

- Python 3.10+
- Google Gemini API key

## Installation

```bash
pip install -r requirements.txt
```

Set your API key in a `.env` file:
```
GOOGLE_API_KEY=your_key_here
```

## Usage

```bash
streamlit run app.py
```

Open the web interface at `http://localhost:8501`, enter a research topic, and generate insights.

## Architecture

The system uses a sequential agent pipeline:
1. **Analyzer**: Extracts methods, datasets, and limitations from papers
2. **Skeptic**: Challenges assumptions and finds contradictions
3. **Synthesizer**: Generates research opportunities with experiment designs
4. **Validator**: Validates insights against prior work

## License

MIT License
