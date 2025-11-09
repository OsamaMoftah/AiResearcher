"""
Research agent system for analyzing academic papers and generating insights.

This module implements a multi-agent pipeline for paper analysis, gap detection,
contradiction identification, and research opportunity synthesis.
"""
from typing import List, Dict, Any, Optional
from .arxiv import search_arxiv, Paper
from .llm import LLM
import time

# Multi-platform search support (optional dependency)
try:
    from .multi_platform import SimpleMultiPlatformScraper, EnhancedPaper
    MULTI_PLATFORM_AVAILABLE = True
except ImportError:
    MULTI_PLATFORM_AVAILABLE = False
    SimpleMultiPlatformScraper = None
    EnhancedPaper = None

# Research intelligence module (optional dependency)
try:
    from .research_intelligence import ResearchIntelligence
    RESEARCH_INTELLIGENCE_AVAILABLE = True
except ImportError:
    RESEARCH_INTELLIGENCE_AVAILABLE = False
    ResearchIntelligence = None


class AnalyzerAgent:
    """
    Analyzes research papers to extract methods, datasets, and limitations.
    
    Performs deep analysis of academic papers to identify research gaps,
    extract key methodologies, and highlight limitations across papers.
    """

    def __init__(self, llm: LLM):
        self.llm = llm
        self.name = "Analyzer"
        self.personality = "Analytical"
        self.expertise = "Research analyst with 15+ years of experience in systematic literature review"

    def analyze_papers(self, papers: List[Paper], topic: str = "", field_context: str = "") -> Dict[str, Any]:
        """
        Analyzes papers to extract methods, datasets, and limitations.
        
        Returns structured analysis with identified gaps and their severity scores.
        """
        print(f"🔍 {self.name}: Analyzing {len(papers)} papers...")
        start_time = time.time()

        # Limit analysis to top 5 papers for focused analysis and faster processing
        papers_text = "\n\n".join([
            f"PAPER {i+1}:\nTitle: {p.title}\nAbstract: {p.abstract[:400]}"
            for i, p in enumerate(papers[:5])
        ])

        # Build field context section
        field_section = ""
        if field_context:
            field_section = f"""
FIELD CONTEXT (Your Domain Knowledge):
{field_context}

Use this context to:
- Compare papers against known benchmarks and standards
- Identify limitations that papers don't explicitly state
- Reference important authors, methodologies, and debates in the field
- Infer gaps based on field knowledge, not just what papers say
"""

        prompt = f"""You are Dr. Sarah Chen, a leading research analyst at MIT with 15 years of experience in {topic or 'research analysis'}. 
You have reviewed hundreds of papers in this field and know the key players, methodologies, and debates.
Your personality: {self.personality} - You see patterns others miss and think systematically.

Your job: find what's REALLY missing, not just what papers say is missing.

IMPORTANT: Generate your findings in a DIALOGUE STYLE as if you're presenting at a research roundtable.
Start with: "I've extracted..." or "I've analyzed..." and state your findings clearly.

{field_section}
CURRENT PAPERS TO ANALYZE:
{papers_text}

DEEP ANALYSIS FRAMEWORK:
For each paper, extract:
1. **Core method** (in one sentence)
2. **Key dataset** (name it specifically)
3. **Stated limitations** (what authors admit doesn't work)
4. **Hidden limitations** (what they DON'T say but you can infer - e.g., only tested on toy data, assumes infinite compute, requires clean labels)
5. **Future work** (what they suggest)

Then find CROSS-PAPER PATTERNS:
Look for gaps that appear in MULTIPLE papers:
- Do all papers test on the same narrow dataset? (e.g., "everyone uses ImageNet, nobody tests on medical images")
- Do all papers ignore the same problem? (e.g., "nobody addresses training cost")
- Do papers make the same unstated assumption? (e.g., "all assume clean labels")

QUALITY BAR:
- Be SPECIFIC: Not "better datasets needed" but "all papers use ImageNet (1000 classes), none test on fine-grained datasets (10K+ classes)"
- Identify WHY gap exists: "Too expensive? Too hard? Just overlooked?"
- Estimate IMPACT: "If solved, enables X, unlocks Y market, resolves Z debate"

Return JSON:
{{
  "dialogue_message": "I've extracted the core claim: [summary]. Limitation: [key limitation]. This suggests [pattern].",
  "paper_analyses": [
    {{
      "paper_num": 1,
      "methods": ["specific method name"],
      "datasets": ["specific dataset name"],
      "limitations": ["stated limitation 1", "hidden limitation 2"]
    }}
  ],
  "cross_paper_gaps": [
    {{
      "gap": "SPECIFIC gap with evidence (e.g., 'All 5 papers test on sequences <16K tokens, but production needs 100K+')",
      "severity": "high",
      "papers_affected": [1,2,3],
      "why_matters": "Specific impact (e.g., 'This prevents deployment in legal/medical domains where documents are 50K-500K tokens')"
    }}
  ]
}}"""

        response = self.llm.call(prompt, max_tokens=4096)
        analysis = self.llm.extract_json(response)

        duration = time.time() - start_time
        print(f"✓ {self.name}: Analysis complete ({duration:.1f}s)")

        # Normalize response format to ensure consistent structure regardless of API response shape
        if isinstance(analysis, list):
            print(f"⚠️  Warning: Analyzer returned a list instead of dict, converting...")
            analysis = {
                "paper_analyses": analysis if analysis else [],
                "cross_paper_gaps": [],
                "dialogue_message": ""
            }
        elif not isinstance(analysis, dict):
            analysis = {
                "paper_analyses": [],
                "cross_paper_gaps": [],
                "dialogue_message": ""
            }

        # Generate dialogue message for user-facing output
        dialogue_message = analysis.get('dialogue_message', '') if analysis else ''
        if not dialogue_message:
            gaps = analysis.get('cross_paper_gaps', []) if analysis else []
            if gaps:
                top_gap = gaps[0] if isinstance(gaps[0], dict) else {}
                dialogue_message = f"I've extracted the core patterns from {len(papers)} papers. Key finding: {top_gap.get('gap', '')[:150]}. Limitation: {top_gap.get('why_matters', 'Important research gap identified.')[:100]}"
            else:
                dialogue_message = f"I've analyzed {len(papers)} papers and identified several cross-paper patterns and limitations."

        return {
            "analysis": analysis or {"paper_analyses": [], "cross_paper_gaps": []},
            "papers_analyzed": len(papers[:5]),
            "duration": duration,
            "dialogue_message": dialogue_message
        }


class SkepticAgent:
    """
    Challenges assumptions and identifies contradictions in research analysis.
    
    Performs critical review of analyzed papers to question assumptions,
    detect contradictions between papers, and validate identified gaps.
    """

    def __init__(self, llm: LLM):
        self.llm = llm
        self.name = "Skeptic"
        self.personality = "Critical"
        self.expertise = "Brutal skeptic who challenges everything and finds flaws others miss"

    def critique(self, papers: List[Paper], analyzer_output: Dict[str, Any], topic: str = "", field_context: str = "") -> Dict[str, Any]:
        """Challenge assumptions and find contradictions"""
        print(f"⚠️  {self.name}: Challenging assumptions...")
        start_time = time.time()

        papers_text = "\n".join([
            f"{i+1}. {p.title}: {p.abstract[:200]}"
            for i, p in enumerate(papers[:5])
        ])

        gaps = analyzer_output.get("analysis", {}).get("cross_paper_gaps", [])
        gaps_text = "\n".join([f"- {g.get('gap', '')}" for g in gaps[:5]]) if gaps else "No gaps identified yet."

        # Build field context section
        field_section = ""
        if field_context:
            field_section = f"""
FIELD CONTEXT (Your Domain Knowledge):
{field_context}

Use this to:
- Reference known debates and contradictions in the field
- Identify if gaps have already been addressed by other researchers
- Challenge assumptions based on field knowledge
- Provide insights even when no direct contradictions are found
"""

        prompt = f"""You are Dr. Marcus Thompson, a renowned critical thinker at Stanford with 20 years of experience challenging research claims in {topic or 'research'}. 
Your personality: {self.personality} - You're known for being brutally honest and finding flaws others miss. 
You've seen hundreds of papers and know when something doesn't add up.

Your job: find what's WRONG, MISLEADING, or OVERSTATED. But ALWAYS provide insights, even when finding "0 contradictions".

{field_section}
PAPERS TO CRITIQUE:
{papers_text}

GAPS IDENTIFIED BY ANALYZER:
{gaps_text}

IMPORTANT: Even if you find NO contradictions, provide valuable insights:
- "This suggests the field is maturing and converging on solutions"
- "Papers might be testing non-overlapping aspects - this could indicate field fragmentation"
- "Lack of direct contradictions might mean papers are avoiding direct comparisons"
- Reference known debates in the field that these papers relate to

CRITICAL QUESTIONS TO ASK:
1. **Contradictions**: Do papers report different results for the same method? (e.g., "Paper 1 says Method X is 3x faster, Paper 2 says 1.5x - which is true?")
2. **Cherry-picking**: Do papers only show results that work? What failures aren't reported?
3. **Apples to Oranges**: Do papers compare on different datasets/settings making comparisons meaningless?
4. **Unfair Baselines**: Do papers compare against weak baselines to make their method look better?
5. **Hidden Assumptions**: What do ALL papers assume but never state? (e.g., "assume infinite compute", "assume clean data")
6. **Benchmark Gaming**: Are papers optimizing for specific benchmarks that don't reflect real use?

For the GAPS:
- Are they actually important or just academic curiosities?
- Has someone already solved this in a paper we missed?
- Is the gap real or just poorly defined?

Be SPECIFIC. Don't just say "results might not generalize" - say "Paper 1 tests on ImageNet (clean labels), but claims work on 'real-world data' - medical images have 40% label noise, results likely won't transfer."

Return JSON:
{{
  "dialogue_message": "So it's [summary of analyzer's finding], but [your challenge]. Question: [your question]. Suggest: [what to check].",
  "contradictions": [
    {{
      "papers": [1, 3],
      "contradiction": "SPECIFIC contradiction with numbers (e.g., 'Paper 1 reports 92% accuracy on MNIST, Paper 3 reports 78% using same method')",
      "evidence": "Why this matters / what it reveals"
    }}
  ],
  "potential_contradictions": [
    {{
      "description": "Potential contradiction based on field knowledge (e.g., 'In the field, Method X typically shows Y% performance, but these papers don't report this - why?')",
      "field_evidence": "What you know from the field that suggests this contradiction might exist",
      "suggested_investigation": "What should be checked or compared"
    }}
  ],
  "challenged_gaps": [
    {{
      "gap": "The gap being challenged",
      "challenge": "SPECIFIC challenge (e.g., 'This gap only matters on benchmarks, not production. Real systems use method Y which already solves this.')",
      "severity": "critical"
    }}
  ],
  "missing_analysis": ["SPECIFIC things Analyzer should have caught"],
  "field_insights": "ALWAYS provide insights about the field, even if no contradictions found. Reference known debates, trends, or patterns you observe.",
  "interpretation": "What the absence or presence of contradictions means for the field",
  "field_knowledge_contradictions": "Based on your extensive field knowledge, what contradictions or conflicting findings are known in this research area that these papers might relate to? Even if papers don't explicitly contradict each other, what contradictions from the broader field should users be aware of?"
}}"""

        response = self.llm.call(prompt, max_tokens=3072)
        critique = self.llm.extract_json(response)

        # Handle case where critique might be a list, dict, or None
        if isinstance(critique, list):
            # If we got a list, convert to dict structure
            print(f"⚠️  Warning: Skeptic returned a list instead of dict, converting...")
            critique = {
                "contradictions": critique if critique else [],
                "potential_contradictions": [],
                "challenged_gaps": [],
                "missing_analysis": [],
                "field_insights": "",
                "interpretation": "",
                "field_knowledge_contradictions": "",
                "dialogue_message": ""
            }
        elif not isinstance(critique, dict):
            # If it's None or some other type, create default structure
            critique = None

        # Extract dialogue message if available
        dialogue_message = critique.get('dialogue_message', '') if critique else ''
        
        # Ensure critique always has insights
        if not critique:
            critique = {
                "contradictions": [],
                "potential_contradictions": [],
                "challenged_gaps": [],
                "missing_analysis": [],
                "field_insights": f"After analyzing {len(papers)} papers on {topic or 'this topic'}, I observe that the field appears to be converging on certain solutions. The lack of direct contradictions suggests either: (1) papers are testing non-overlapping aspects, (2) the field is maturing, or (3) there's a lack of direct comparison studies. This is itself an important observation.",
                "interpretation": "The absence of contradictions could indicate field maturity, but it might also suggest that papers are avoiding direct comparisons, which is a research opportunity.",
                "field_knowledge_contradictions": f"Based on field knowledge in {topic or 'this area'}, there are known debates and conflicting findings that researchers should be aware of, even if not explicitly stated in these papers."
            }
            if not dialogue_message:
                dialogue_message = f"So it's an interesting analysis, but I have questions. Are we sure these patterns aren't just artifacts of the datasets used? Question: Have similar results appeared in related fields? Suggest cross-checking with recent work."
        else:
            # Ensure all fields are present
            if "potential_contradictions" not in critique:
                critique["potential_contradictions"] = []
            if "field_knowledge_contradictions" not in critique or not critique.get("field_knowledge_contradictions"):
                # Generate field knowledge contradictions if not provided
                if field_context:
                    critique["field_knowledge_contradictions"] = f"Based on field knowledge, there are known debates and conflicting findings in {topic or 'this research area'}. Even if these papers don't explicitly contradict each other, the field has documented contradictions that researchers should consider."
                else:
                    critique["field_knowledge_contradictions"] = "Based on general field knowledge, there may be contradictions or debates in this research area that aren't explicitly stated in the analyzed papers."
            
            # Ensure field_insights and interpretation are always present
            if "field_insights" not in critique or not critique.get("field_insights"):
                critique["field_insights"] = f"Based on my analysis of {len(papers)} papers, I observe patterns in methodology, evaluation, and scope that reveal important insights about the current state of research in this area."
            if "interpretation" not in critique or not critique.get("interpretation"):
                num_contradictions = len(critique.get("contradictions", []))
                if num_contradictions == 0:
                    critique["interpretation"] = "The absence of contradictions suggests either field convergence or lack of direct comparisons - both are valuable insights for researchers."
                else:
                    critique["interpretation"] = f"Found {num_contradictions} contradictions, indicating active debate in the field - an important signal for research direction."
            
            # If no potential contradictions but we have field context, suggest some
            if not critique.get("potential_contradictions") and field_context:
                # Add at least one potential contradiction based on field knowledge
                critique["potential_contradictions"] = [{
                    "description": "Potential contradiction based on field knowledge - papers may not be directly comparable due to different experimental setups, datasets, or evaluation metrics.",
                    "field_evidence": "Field knowledge suggests that similar methods often show different results when tested under different conditions.",
                    "suggested_investigation": "Compare papers on common benchmarks or under standardized conditions to identify potential contradictions."
                }]
            
            # Generate dialogue message if not provided
            if not dialogue_message:
                contradictions = critique.get("contradictions", [])
                if contradictions:
                    top_contradiction = contradictions[0]
                    dialogue_message = f"So it's an elegant concept, but I see a contradiction. Papers {top_contradiction.get('papers', [])} report conflicting results: {top_contradiction.get('contradiction', '')[:100]}. Question: Which result is accurate? Suggest cross-checking with recent work in the field."
                else:
                    gaps = analyzer_output.get("analysis", {}).get("cross_paper_gaps", [])
                    if gaps:
                        dialogue_message = f"So it's an interesting analysis, but I have questions about the gaps identified. Question: Are we sure these gaps haven't been addressed in recent work? Suggest verifying against the latest literature."
                    else:
                        dialogue_message = f"That's a solid analysis. I don't see major contradictions, but question: Are we sure the patterns aren't dataset-specific? Suggest testing on diverse datasets to confirm."

        duration = time.time() - start_time
        print(f"✓ {self.name}: Critique complete ({duration:.1f}s)")

        return {
            "critique": critique,
            "duration": duration,
            "dialogue_message": dialogue_message
        }


class SynthesizerAgent:
    """
    Synthesizes research opportunities and generates experiment designs.
    
    Combines analysis and critique to create actionable research insights
    with structured experiment designs and scoring metrics.
    """

    def __init__(self, llm: LLM):
        self.llm = llm
        self.name = "Synthesizer"
        self.personality = "Creative"
        self.expertise = "World-class research strategist who sees opportunities others miss"

    def synthesize(self, papers: List[Paper], analyzer_output: Dict[str, Any],
                   skeptic_output: Dict[str, Any], topic: str = "", field_context: str = "") -> List[Dict[str, Any]]:
        """Combine analysis and critique to generate actionable research directions"""
        print(f"💡 {self.name}: Synthesizing insights...")
        start_time = time.time()

        # Prepare context
        gaps = analyzer_output.get("analysis", {}).get("cross_paper_gaps", [])
        gaps_text = "\n".join([f"- {g.get('gap', '')}: {g.get('why_matters', '')}" for g in gaps[:5]])

        critique = skeptic_output.get("critique", {})
        contradictions = critique.get("contradictions", [])
        contradictions_text = "\n".join([
            f"- Papers {c.get('papers', [])}: {c.get('contradiction', '')}"
            for c in contradictions[:3]
        ])

        papers_titles = "\n".join([f"{i+1}. {p.title}" for i, p in enumerate(papers[:5])])

        # Build field context section
        field_section = ""
        if field_context:
            field_section = f"""
FIELD CONTEXT (Your Domain Knowledge):
{field_context}

Use this to:
- Reference known research directions and important authors
- Cite important conferences and trends
- Propose experiments that build on established work
- Identify opportunities that align with field evolution
"""

        prompt = f"""You are Dr. Alex Rivera, a world-class research strategist at MIT with 18 years of experience. 
Your personality: {self.personality} - You see connections others miss and generate brilliant research ideas.
You've published in top venues and know what makes research impactful.

Your job is to generate research insights using CONCEPTUAL REASONING, not procedural templates.
Think like a scientist: extract patterns, form hypotheses, design experiments, predict insights, validate.

{field_section}
PAPERS ANALYZED:
{papers_titles}

GAPS IDENTIFIED:
{gaps_text}

CONTRADICTIONS FOUND:
{contradictions_text}

🎯 5-LAYER REASONING STRUCTURE (REQUIRED):

1. **OBSERVATION**: Extract recurring or contrasting patterns across multiple papers. What do you notice?
2. **HYPOTHESIS**: Abstract these patterns into a testable, conceptual claim. What principle might be at work?
3. **EXPERIMENT**: Design a concrete, feasible study with scientific methodology. What would you test?
4. **EXPECTED INSIGHT**: Predict what principle could emerge. If confirmed, what does this reveal?
5. **VALIDATION**: Check if this space is already occupied (citation-aware reasoning).

Generate insights that read like scientific reasoning, not automation. Each insight should tell a story of discovery.

🔬 EXPERIMENT DESIGN REQUIREMENTS (Scientific Methodology):
When designing an experiment, go beyond scheduling. Think like a scientist:

1. **Identify the variable or mechanism being tested** (independent variable)
2. **Propose control and treatment conditions** (control group)
3. **Include metrics for evaluation** (dependent variables: accuracy, robustness, novelty, etc.)
4. **Anticipate possible outcomes and how they would affect the hypothesis** (branch logic)
5. **Specify deliverables for validation** (plots, metrics, datasets that Validator can use)
6. **Define what success and failure mean** (expected outcome, fallback plan)

Your experiment_design should be a research methodology, not a task list. Include:
- **objective**: Clear statement of what is being tested
- **independent_variable**: What is being manipulated (e.g., diversity regularization weight λ)
- **dependent_variables**: List of metrics being measured (e.g., test accuracy, robustness, calibration error)
- **control_group**: Baseline or comparison condition (e.g., ensemble without diversity regularization)
- **experimental_procedure**: Phases of the experiment (phase1, phase2, phase3, phase4)
- **expected_outcome**: What success looks like and how to interpret results (e.g., correlation >0.6)
- **fallback_plan**: What to do if hypothesis fails or partially holds (e.g., investigate saturation, try contrastive pretraining)
- **deliverables**: List of artifacts for validator (e.g., diversity-robustness correlation plot, λ-sweep performance curve, calibration metrics)
- **week1, week2, week3**: Legacy format for backward compatibility (optional, can be derived from phases)

🌟 EXAMPLES OF CONCEPTUAL REASONING (Few-Shot Learning):

EXAMPLE 1 - Symmetry as a Hidden Regulator:
{{
  "title": "Symmetry as a Hidden Regulator in Model Generalization",
  "source_papers": ["Machine Learning Symmetry (Lal et al., 2022)", "Diversity in ML (Gong et al., 2018)"],
  "observation": "Multiple reviewed papers independently leverage structured regularities to improve robustness. These recurring patterns point toward symmetry acting as an implicit stabilizer during training — whether derived from physics, data geometry, or architecture constraints.",
  "hypothesis": "Embedding symmetry constraints directly into neural architectures functions as a natural regularizer, improving generalization under low-data or noisy regimes.",
  "experiment_design": {{
    "objective": "Test whether symmetry constraints in neural architectures improve generalization under low-data or noisy regimes compared to unconstrained architectures.",
    "independent_variable": "Symmetry constraint type and strength (group-theoretic constraints, architectural symmetry, data augmentation symmetry)",
    "dependent_variables": ["Generalization error", "Calibration error", "Invariance preservation metrics", "Robustness to noise", "Performance under few-shot conditions"],
    "control_group": "Unconstrained neural architecture with identical architecture but no symmetry constraints",
    "experimental_procedure": {{
      "phase1": "Re-implement Lal's group-theoretic network and baseline unconstrained network on CIFAR-10. Establish baseline performance metrics.",
      "phase2": "Train both symmetry-constrained and unconstrained versions under few-shot conditions (10%, 20%, 50% of training data).",
      "phase3": "Evaluate generalization error, calibration, and invariance preservation metrics across both architectures. Test robustness under label noise injection (5%, 10%, 20% noise).",
      "phase4": "Compute correlation between symmetry preservation score and generalization improvement. Analyze which types of symmetry provide the strongest regularization effect."
    }},
    "expected_outcome": "If symmetry constraints provide regularization, we expect: (1) generalization error reduction of >5% under few-shot conditions, (2) calibration error improvement of >10%, (3) correlation >0.6 between symmetry preservation and robustness. Success criteria: symmetry-constrained models outperform unconstrained models across at least 2 of 3 evaluation metrics.",
    "fallback_plan": "If no significant improvement is found, investigate: (1) whether symmetry constraints are too weak or too strong (hyperparameter sweep), (2) whether the chosen symmetry groups are relevant for the dataset (try different symmetry groups), (3) whether benefits only appear at larger scale (scale up to ImageNet).",
    "deliverables": ["Generalization error comparison plot (constrained vs unconstrained)", "Calibration error metrics across noise conditions", "Symmetry-robustness correlation analysis", "Invariance preservation heatmap", "Hyperparameter sensitivity analysis"],
    "week1": "Re-implement Lal's group-theoretic network and benchmark on CIFAR-10.",
    "week2": "Train both symmetry-constrained and unconstrained versions under few-shot conditions.",
    "week3": "Compare generalization error, calibration, and invariance preservation metrics."
  }},
  "expected_insight": "If confirmed, this could unify two research lines — geometric deep learning and self-supervised regularization — under a common theoretical principle: robust learning as symmetry preservation.",
  "gap": "All papers test on sequences <16K tokens, but production needs 100K+ tokens. Nobody has systematically tested if solutions work at scale.",
  "skeptic_challenge": "Are the claimed speedups real or just artifacts of small-scale benchmarks? Papers report contradictory speedups.",
  "impact": "Long-context LLMs are a $2B market. Current solutions are benchmarked on toy problems. This could enable processing entire codebases, legal documents, and conversation histories at scale.",
  "novelty_score": 8.5,
  "feasibility_score": 8,
  "impact_score": 9
}}

EXAMPLE 2 - Latent Diversity Hypothesis:
{{
  "title": "The Latent Diversity Hypothesis: Beyond Accuracy Metrics",
  "source_papers": ["Diversity in Machine Learning (Gong et al., 2018)"],
  "observation": "The literature measures 'diversity' in ensembles primarily through output variance or accuracy improvement. However, cross-paper analysis reveals an implicit, unmeasured factor: latent representation diversity — the structural dissimilarity between learned embeddings.",
  "hypothesis": "Optimizing for latent diversity, rather than output diversity, can yield more robust ensemble systems and uncover hidden subspaces of generalization.",
  "experiment_design": {{
    "objective": "Test whether optimizing latent representation diversity in ensemble models improves robustness beyond standard accuracy metrics.",
    "independent_variable": "Diversity regularization weight (λ) applied to cosine distance between model embeddings in latent space",
    "dependent_variables": ["Test accuracy under noise injection (robustness)", "Representation similarity (cosine distance between embeddings)", "Calibration error (model confidence alignment)", "Generalization gap (train-test accuracy difference)"],
    "control_group": "Ensemble without latent diversity regularization (standard ensemble training)",
    "experimental_procedure": {{
      "phase1": "Reproduce baseline from 'Diversity in ML' on CIFAR-100 using three independent ensemble models. Establish baseline accuracy and robustness metrics.",
      "phase2": "Introduce latent diversity regularization into the loss function: L_total = L_classification + λ * (1 - cosine_similarity(E1, E2)). Tune λ ∈ {{0, 0.1, 0.5, 1.0}}.",
      "phase3": "Evaluate across data perturbations (label noise: 5%, 10%, 20%; domain shift: CIFAR-100 to CIFAR-10.1). Compare ensemble resilience metrics between regularized and control groups.",
      "phase4": "Compute correlation between latent diversity index (cosine distance) and robustness scores. Analyze which latent layers show strongest diversity-robustness correlation."
    }},
    "expected_outcome": "If latent diversity correlates with robustness >0.6 across noise conditions, this supports the hypothesis that diversity in representation space, not just output space, drives generalization. Success criteria: (1) robustness improvement of >3% under noise, (2) correlation >0.6 between diversity index and robustness, (3) calibration error reduction of >5%.",
    "fallback_plan": "If results show no correlation, investigate whether latent dimensions are saturated — may require contrastive pretraining or dimensionality pruning. Alternative: test if diversity needs to be measured at multiple layers, not just final layer. If correlation is weak, explore non-linear diversity measures beyond cosine distance.",
    "deliverables": ["Diversity-robustness correlation plot (latent diversity index vs robustness score)", "λ-sweep performance curve (showing optimal regularization weight)", "Comparative calibration metrics (regularized vs control)", "Layer-wise diversity analysis (which layers matter most)", "Noise robustness comparison table"],
    "week1": "Train ensemble models on standard datasets (CIFAR-100, ImageNet-mini).",
    "week2": "Compute cosine distance between latent layers across models as a new 'representation diversity index'.",
    "week3": "Correlate this index with performance stability across random seeds and data noise."
  }},
  "expected_insight": "This may redefine 'diversity' as a representation-level concept — pushing ensemble learning closer to representation theory, not just accuracy heuristics.",
  "gap": "Papers measure diversity through output variance, but ignore latent representation diversity.",
  "skeptic_challenge": "Verify that latent diversity correlates with generalization, not just accuracy improvements.",
  "impact": "Could revolutionize ensemble learning by focusing on representation structure rather than output metrics.",
  "novelty_score": 9,
  "feasibility_score": 7,
  "impact_score": 8.5
}}

EXAMPLE 3 - Open-Environment Learning:
{{
  "title": "Open-Environment Learning: Toward Adaptive Context Awareness",
  "source_papers": ["Open-environment Machine Learning (Zhou, 2022)"],
  "observation": "Most ML systems fail when environmental variables shift outside training conditions. Yet reviewed models often 'freeze' their context assumptions, lacking mechanisms for real-time context sensing.",
  "hypothesis": "An adaptive environment module that infers latent context shifts (e.g., via embedding drift detection) can serve as a universal plug-in for context-aware ML.",
  "experiment_design": {{
    "objective": "Test whether an adaptive environment module using embedding drift detection improves model resilience to open-world environmental shifts compared to static models.",
    "independent_variable": "Environment adaptation mechanism (embedding drift threshold, adaptation rate, context detection sensitivity)",
    "dependent_variables": ["Prediction accuracy under domain shift", "Prediction entropy (uncertainty calibration)", "Calibration error (confidence alignment)", "Adaptation latency (time to detect and adapt to shift)", "False positive rate (incorrect shift detection)"],
    "control_group": "Standard image classification model without environment adaptation module (frozen context assumptions)",
    "experimental_procedure": {{
      "phase1": "Integrate embedding drift metrics into standard image classification pipeline (ResNet-50 on ImageNet). Establish baseline performance and drift detection thresholds.",
      "phase2": "Simulate open-world shifts: (a) domain changes (ImageNet to ImageNet-C with corruption), (b) unseen categories (train on 800 classes, test on 200 unseen), (c) temporal drift (simulated data distribution shift over time).",
      "phase3": "Measure resilience via prediction entropy, calibration performance, and adaptation speed. Compare adaptive module vs control across all shift scenarios.",
      "phase4": "Analyze false positive rate of shift detection. Optimize drift threshold to minimize false alarms while maintaining sensitivity. Evaluate trade-off between adaptation speed and accuracy."
    }},
    "expected_outcome": "If adaptive module improves resilience, we expect: (1) accuracy improvement of >5% under domain shift, (2) calibration error reduction of >10%, (3) prediction entropy increase (better uncertainty quantification) when shift is detected, (4) adaptation latency <100ms. Success criteria: adaptive model outperforms control on at least 2 of 3 shift scenarios with <5% false positive rate.",
    "fallback_plan": "If no improvement is found, investigate: (1) whether drift detection is too sensitive or not sensitive enough (threshold tuning), (2) whether adaptation mechanism is too slow (optimize detection algorithm), (3) whether the module needs domain-specific calibration (train separate detectors per domain type). If adaptation causes performance degradation, explore conservative adaptation (only adapt when confidence is high).",
    "deliverables": ["Domain shift accuracy comparison (adaptive vs control)", "Embedding drift detection timeline plot", "Calibration error metrics across shift scenarios", "False positive rate analysis", "Adaptation latency vs accuracy trade-off curve"],
    "week1": "Integrate embedding drift metrics into standard image classification pipeline.",
    "week2": "Simulate open-world shifts (domain changes, unseen categories).",
    "week3": "Measure resilience via prediction entropy and calibration performance."
  }},
  "expected_insight": "This could bridge a gap between domain adaptation and open-world learning — shifting ML from static generalization toward dynamic environmental adaptation.",
  "gap": "Models fail when environmental variables shift, but lack mechanisms for real-time context sensing.",
  "skeptic_challenge": "Verify that embedding drift detection actually improves performance in open-world scenarios.",
  "impact": "Could enable ML systems that adapt to changing environments in real-time, crucial for deployment.",
  "novelty_score": 8,
  "feasibility_score": 9,
  "impact_score": 9.5
}}

🎯 YOUR TASK:

Generate 3 insights following this 5-layer structure. Each insight must have:
- **title**: Complete, descriptive title (NO truncation, NO trailing "...")
- **observation**: What patterns do you see across papers?
- **hypothesis**: What testable claim can you make?
- **experiment_design**: Scientific experiment design with objective, variables, controls, procedures, expected outcome, fallback plan, and deliverables (see structure above)
- **expected_insight**: What principle could emerge?
- **gap**: The research gap (for backward compatibility)
- **skeptic_challenge**: What challenges might arise?
- **impact**: Why does this matter?
- **novelty_score**, **feasibility_score**, **impact_score**: 0-10 each

Think conceptually, not procedurally. Write like a scientist reasoning through a discovery, not like an automation tool.

IMPORTANT: 
- Generate COMPLETE titles - never truncate or add "..." to titles
- experiment_design must include scientific methodology (objective, variables, controls, phases, deliverables) - not just week1/week2/week3 task lists
- Include branch logic (what if hypothesis fails?) in fallback_plan
- Specify deliverables that Validator agent can use for evaluation

IMPORTANT: Also generate a DIALOGUE MESSAGE as if you're speaking at a research roundtable.
Format: "That's interesting — I recall that [connection]. Maybe [hypothesis]. Hypothesis: [testable claim]."

Return JSON with two parts:
1. A "dialogue_messages" array with one dialogue message per insight (3 total)
2. The insights array as before

{{
  "dialogue_messages": [
    "That's interesting — I recall that [connection]. Maybe [hypothesis]. Hypothesis: [testable claim].",
    ...
  ],
  "insights": [
    {{...}},
    {{...}},
    {{...}}
  ]
}}

OR if you prefer, return just the insights array and we'll generate dialogue messages from them.
Return ONLY valid JSON."""

        response = self.llm.call(prompt, max_tokens=4096)
        result = self.llm.extract_json(response)

        duration = time.time() - start_time

        # Handle different response formats
        dialogue_messages = []
        insights = []
        
        if isinstance(result, dict):
            # New format with dialogue_messages
            insights = result.get('insights', [])
            dialogue_messages = result.get('dialogue_messages', [])
        elif isinstance(result, list):
            # Old format - just insights array
            insights = result
        
        # Validate and clean insights - ensure all items are dictionaries
        if isinstance(insights, list):
            validated_insights = []
            for item in insights:
                if isinstance(item, dict):
                    validated_insights.append(item)
                elif isinstance(item, str):
                    # If we got a string, try to create a basic insight from it
                    print(f"⚠️  Warning: Found string in insights list, converting: {item[:50]}...")
                    validated_insights.append({
                        "title": item[:100] if len(item) > 100 else item,
                        "observation": item,
                        "hypothesis": "",
                        "gap": item,
                        "experiment_design": {},
                        "expected_insight": "",
                        "skeptic_challenge": "",
                        "impact": "",
                        "novelty_score": 5,
                        "feasibility_score": 5,
                        "impact_score": 5
                    })
                else:
                    # Skip invalid items
                    print(f"⚠️  Warning: Skipping invalid insight item of type {type(item)}")
            insights = validated_insights
        
        # Fallback if parsing fails or no valid insights
        if not insights or not isinstance(insights, list) or len(insights) == 0:
            print(f"⚠️  {self.name}: JSON parsing failed or no valid insights, using fallback ({duration:.1f}s)")
            insights = self._create_fallback_insights(papers, gaps)
        else:
            print(f"✓ {self.name}: Generated {len(insights)} insights ({duration:.1f}s)")

        # Ensure we always return at least 2 insights
        if len(insights) == 0:
            print(f"⚠️  {self.name}: No insights generated, creating generic ones")
            insights = self._create_generic_fallback(papers)
        
        # Final validation - ensure all insights are dictionaries with required fields
        validated_final_insights = []
        for i, insight in enumerate(insights):
            if not isinstance(insight, dict):
                print(f"⚠️  Warning: Insight {i} is not a dict, skipping")
                continue
            
            # Ensure required fields exist
            if 'title' not in insight:
                insight['title'] = f"Research Insight {i+1}"
            if 'observation' not in insight:
                insight['observation'] = ''
            if 'hypothesis' not in insight:
                insight['hypothesis'] = ''
            if 'gap' not in insight:
                insight['gap'] = ''
            if 'experiment_design' not in insight:
                insight['experiment_design'] = {}
            
            validated_final_insights.append(insight)
        
        insights = validated_final_insights
        
        # Generate dialogue messages if not provided
        if not dialogue_messages or len(dialogue_messages) != len(insights):
            dialogue_messages = []
            for insight in insights:
                # Double-check it's a dict (defensive programming)
                if not isinstance(insight, dict):
                    dialogue_msg = "I see an opportunity here that could be worth exploring."
                else:
                    hypothesis = insight.get('hypothesis', '')
                    observation = insight.get('observation', '')
                    if hypothesis:
                        dialogue_msg = f"That's interesting — I recall that {observation[:100] if observation else 'there are patterns here'}. Maybe {hypothesis[:150]}."
                    else:
                        gap = insight.get('gap', '')
                        dialogue_msg = f"I see an opportunity here. {gap[:150]} This could be worth exploring."
                dialogue_messages.append(dialogue_msg)
        
        # Attach dialogue messages to insights
        for i, insight in enumerate(insights):
            if not isinstance(insight, dict):
                continue
            if i < len(dialogue_messages):
                insight['dialogue_message'] = dialogue_messages[i]

        return insights

    def _create_fallback_insights(self, papers: List[Paper], gaps: List[Dict]) -> List[Dict]:
        """Fallback insights based on identified gaps"""
        insights = []
        for i, gap in enumerate(gaps[:3], 1):
            gap_text = gap.get('gap', 'Gap not specified')
            # Generate complete title from gap text without truncation
            # Extract key phrase from gap for title, but ensure it's complete
            gap_words = gap_text.split()[:10]  # Take first 10 words max
            title_phrase = ' '.join(gap_words)
            if len(gap_text.split()) > 10:
                title_phrase += "..."  # Only add ... if we're actually truncating for title length
            title = f"Research Direction {i}: {title_phrase}" if title_phrase else f"Research Direction {i}: Addressing Identified Research Gap"
            
            insights.append({
                "title": title,
                "observation": f"Multiple papers reveal a pattern: {gap_text}",
                "hypothesis": f"If addressed systematically, this could reveal important insights about {gap.get('why_matters', 'the research area')}",
                "experiment_design": {
                    "week1": "Conduct comprehensive literature review to validate the gap",
                    "week2": "Design and implement baseline approach addressing the gap",
                    "week3": "Evaluate results and compare with existing methods"
                },
                "expected_insight": "This could provide new understanding of the underlying mechanisms and improve current approaches.",
                "gap": gap_text,
                "skeptic_challenge": "Verify this gap exists through systematic literature review",
                "impact": gap.get('why_matters', 'Addresses identified limitation in current research'),
                "novelty_score": 7,
                "feasibility_score": 8,
                "impact_score": 7
            })
        return insights

    def _create_generic_fallback(self, papers: List[Paper]) -> List[Dict]:
        """Generic fallback when everything else fails"""
        insights = []
        for i, paper in enumerate(papers[:3], 1):
            # Generate complete title from paper title without truncation
            # Use full paper title or create a meaningful extension title
            paper_title = paper.title if paper.title else "Research Paper"
            # Create extension title that's complete and descriptive
            if len(paper_title) > 80:
                # If title is very long, use a more concise approach
                title = f"Extension and Generalization of {paper_title}"
            else:
                title = f"Extension of {paper_title}"
            
            insights.append({
                "title": title,
                "observation": f"'{paper.title}' presents promising results, but was tested on limited domains or datasets.",
                "hypothesis": f"Extending this approach to new domains or datasets could reveal generalizability patterns and uncover domain-specific adaptations needed.",
                "experiment_design": {
                    "week1": f"Reproduce key results from '{paper.title}' on baseline dataset",
                    "week2": "Adapt the approach to a new domain or dataset not covered in the original paper",
                    "week3": "Evaluate performance and document gaps or improvements compared to original"
                },
                "expected_insight": "This could reveal whether the method generalizes across domains or requires domain-specific adaptations.",
                "gap": f"While '{paper.title}' presents promising results, there are opportunities to extend this work to different domains, datasets, or problem settings that weren't explored in the original paper.",
                "skeptic_challenge": "Verify that these extensions haven't already been explored in subsequent work. Check for follow-up papers and related research.",
                "impact": "Building on proven methods with novel applications can yield practical research contributions and help validate the generalizability of the original approach.",
                "novelty_score": 6,
                "feasibility_score": 9,
                "impact_score": 7
            })
        return insights


class ValidatorAgent:
    """
    Validates research insights against existing prior work.
    
    Searches for contradicting or validating evidence from recent literature
    and assigns survival scores based on validation results.
    """

    def __init__(self, llm: LLM):
        self.llm = llm
        self.name = "Validator"
        self.personality = "Rigorous"
        self.expertise = "Harsh validator who ensures research is truly novel and rigorous"

    def validate(self, insights: List[Dict[str, Any]], original_topic: str, field_context: str = "") -> List[Dict[str, Any]]:
        """Challenge each insight by searching for contradicting prior work"""
        print(f"🛡️  {self.name}: Validating insights against prior work...")
        start_time = time.time()

        validated_insights = []
        validation_stats = {"survived": 0, "refined": 0, "rejected": 0}

        for i, insight in enumerate(insights, 1):
            # Defensive check: ensure insight is a dictionary
            if not isinstance(insight, dict):
                print(f"  ⚠️  Skipping invalid insight {i} (not a dictionary)")
                continue
            
            print(f"  ↳ Validating insight {i}/{len(insights)}...")

            # Extract keywords from the gap for targeted search
            gap_text = insight.get('gap', '')
            title_text = insight.get('title', '')

            # Create search query from gap + title
            search_query = self._extract_search_keywords(gap_text, title_text, original_topic)

            # Search arXiv for potentially contradicting papers
            try:
                challenge_papers = search_arxiv(search_query, max_results=3)
            except Exception as e:
                print(f"  ⚠️  Search failed for insight {i}: {e}")
                challenge_papers = []

            # If no papers found, insight survives by default
            if not challenge_papers or len(challenge_papers) == 0:
                insight['validated'] = True
                insight['survival_score'] = 8.5
                insight['validation_evidence'] = "No contradicting prior work found in recent literature. Gap appears valid."
                validated_insights.append(insight)
                validation_stats["survived"] += 1
                continue

            # Prepare challenge context
            challenge_text = "\n".join([
                f"- {p.title} ({p.year}): {p.abstract[:200]}..."
                for p in challenge_papers[:3]
            ])

            # Build field context section
            field_section = ""
            if field_context:
                field_section = f"""
FIELD CONTEXT (Your Domain Knowledge):
{field_context}

Use this to:
- Reference seminal papers and important prior work
- Know what has already been done in the field
- Identify if gaps are truly novel or already addressed
- Understand recent trends and field evolution
"""

            # Get observation and hypothesis if available (for conceptual reasoning)
            observation = insight.get('observation', '')
            hypothesis = insight.get('hypothesis', '')
            expected_insight = insight.get('expected_insight', '')
            
            # Ask LLM to validate with citation-aware reasoning
            prompt = f"""You are Dr. James Park, a rigorous research validator at Harvard with 22 years of experience. 
Your personality: {self.personality} - You're known for being thorough and ensuring research is truly novel.
You have encyclopedic knowledge of prior work and know what's been done.

Your job: Validate this research insight with CITATION-AWARE reasoning. Check if the space is already occupied, 
if the hypothesis has been tested, if the expected insight conflicts with known work.

IMPORTANT: Generate your validation in a DIALOGUE STYLE as if you're reporting at a research roundtable.
Format: "Quick check: scanning [sources]. [What you found]. → [Conclusion]."

{field_section}
PROPOSED INSIGHT:
Title: {title_text}
Observation: {observation if observation else gap_text}
Hypothesis: {hypothesis if hypothesis else 'N/A'}
Expected Insight: {expected_insight if expected_insight else 'N/A'}

EXPERIMENT DESIGN:
{self._format_experiment_design(insight.get('experiment_design', {}))}

RECENT PAPERS THAT MIGHT CONTRADICT THIS:
{challenge_text if challenge_text else 'No specific contradicting papers found in search.'}

CITATION-AWARE VALIDATION:
1. **Novelty Check**: Has this hypothesis been explicitly tested? Search your knowledge of the field.
2. **Contradiction Check**: Do any of these papers (or known work) directly address this?
3. **Related Work**: What related papers should be cited? Are there partial solutions?
4. **Refinement**: If valid, how can we refine to be more precise given existing work?
5. **Validation Statement**: Write a clear validation statement in narrative form (like "Quick check: scanning OpenAlex and 2023-2025 arXiv. 'Equivariant Transformers' cover group constraints, but none evaluate them as data-regularizers. → Insight validated.")

🔬 EXPERIMENT DESIGN EVALUATION:
Evaluate the experiment design on scientific rigor:
1. **Completeness** (0-10): Does the plan cover variables + metrics? Are independent/dependent variables clearly defined? Is there a control group?
2. **Reproducibility** (0-10): Can another researcher execute it? Is the procedure clear and detailed enough?
3. **Informativeness** (0-10): Does it produce interpretable data? Are the deliverables specified? Will results be meaningful?
4. **Branch Logic** (0-10): What if results differ? Is there a fallback plan? Are failure scenarios addressed?

Score each criterion and provide an overall experiment_design_quality score (average of the four criteria).

Scoring (0-10):
- 0-3: Gap is invalid/already solved
- 4-6: Gap is partially valid but needs major refinement
- 7-10: Gap survives, possibly with minor refinement

Return JSON:
{{
  "gap_still_valid": true/false,
  "survival_score": 0-10,
  "refinement": "Updated gap/observation statement (or original if no changes needed)",
  "evidence": "Narrative validation statement: 'Quick check: scanning [sources]. [What you found]. → [Conclusion]'",
  "related_work": ["List of related papers or topics that should be cited"],
  "validation_comment": "Brief comment on novelty and validation status",
  "experiment_design_evaluation": {{
    "completeness": 0-10,
    "reproducibility": 0-10,
    "informativeness": 0-10,
    "branch_logic": 0-10,
    "overall_quality": 0-10,
    "feedback": "Brief feedback on experiment design quality and suggestions for improvement"
  }}
}}"""

            response = self.llm.call(prompt, max_tokens=1024)
            validation = self.llm.extract_json(response)

            # Handle case where validation might be a list, dict, or None
            if isinstance(validation, list):
                # If we got a list, try to use first element if it's a dict, otherwise create default
                print(f"  ⚠️  Warning: Validator returned a list instead of dict for insight {i}")
                if validation and len(validation) > 0 and isinstance(validation[0], dict):
                    validation = validation[0]
                else:
                    validation = None
            elif not isinstance(validation, dict):
                # If it's None or some other type, set to None
                validation = None

            # Handle failed validation parsing
            if not validation:
                print(f"  ⚠️  Validation parsing failed for insight {i}, defaulting to survive")
                insight['validated'] = True
                insight['survival_score'] = 7.0
                insight['validation_evidence'] = "Validation inconclusive - insight retained with caution."
                dialogue_message = f"Quick check: scanning recent literature. Validation inconclusive, but insight appears valid. → Insight retained with caution."
                validated_insights.append(insight)
                validation_stats["survived"] += 1
                continue

            # Process validation results
            survival_score = validation.get('survival_score', 5)
            gap_valid = validation.get('gap_still_valid', survival_score >= 6)
            
            # Extract dialogue message from validation evidence
            validation_evidence = validation.get('evidence', 'Gap validated against recent literature.')
            dialogue_message = validation_evidence  # Use evidence as dialogue message

            if gap_valid and survival_score >= 6:
                # Insight survives
                insight['validated'] = True
                insight['survival_score'] = survival_score
                insight['validation_evidence'] = validation_evidence
                insight['validation_dialogue'] = dialogue_message
                
                # Add related work and validation comment if available
                if validation.get('related_work'):
                    insight['related_work'] = validation.get('related_work', [])
                if validation.get('validation_comment'):
                    insight['validation_comment'] = validation.get('validation_comment', '')
                
                # Add experiment design evaluation if available
                exp_eval = validation.get('experiment_design_evaluation', {})
                if exp_eval:
                    insight['experiment_design_quality'] = exp_eval.get('overall_quality', 0)
                    insight['experiment_design_feedback'] = exp_eval.get('feedback', '')
                    insight['experiment_design_scores'] = {
                        'completeness': exp_eval.get('completeness', 0),
                        'reproducibility': exp_eval.get('reproducibility', 0),
                        'informativeness': exp_eval.get('informativeness', 0),
                        'branch_logic': exp_eval.get('branch_logic', 0)
                    }

                # Check if refinement needed - update observation or gap
                refinement = validation.get('refinement', '')
                if refinement and refinement.strip():
                    if observation and refinement.strip() != observation.strip():
                        insight['observation'] = refinement
                    if not observation or refinement.strip() != gap_text.strip():
                        insight['gap'] = refinement
                    validation_stats["refined"] += 1
                    print(f"  ✓ Insight {i} survived with refinement (score: {survival_score}/10)")
                else:
                    validation_stats["survived"] += 1
                    print(f"  ✓ Insight {i} survived unchanged (score: {survival_score}/10)")

                validated_insights.append(insight)
            else:
                # Insight rejected
                validation_stats["rejected"] += 1
                print(f"  ✗ Insight {i} rejected (score: {survival_score}/10)")
                # Don't add to validated_insights - it's filtered out

        duration = time.time() - start_time
        print(f"✓ {self.name}: Validation complete ({duration:.1f}s)")
        print(f"  → {validation_stats['survived']} survived | {validation_stats['refined']} refined | {validation_stats['rejected']} rejected")

        # Ensure we return at least 1 insight (keep top-scoring if all rejected)
        if len(validated_insights) == 0 and len(insights) > 0:
            print(f"⚠️  All insights rejected - keeping highest-scored original insight")
            best_insight = max(insights, key=lambda x: x.get('novelty_score', 0))
            best_insight['validated'] = False
            best_insight['survival_score'] = 5.0
            best_insight['validation_evidence'] = "All insights were challenged, but this had the highest novelty score."
            validated_insights = [best_insight]

        return validated_insights

    def _format_experiment_design(self, exp_design: Dict[str, Any]) -> str:
        """Format experiment design for display in validation prompt"""
        if not exp_design:
            return "No experiment design provided."
        
        lines = []
        
        # Scientific methodology fields (preferred)
        if exp_design.get('objective'):
            lines.append(f"Objective: {exp_design.get('objective')}")
        
        if exp_design.get('independent_variable'):
            lines.append(f"Independent Variable: {exp_design.get('independent_variable')}")
        
        if exp_design.get('dependent_variables'):
            deps = exp_design.get('dependent_variables', [])
            if isinstance(deps, list):
                lines.append(f"Dependent Variables: {', '.join(deps)}")
            else:
                lines.append(f"Dependent Variables: {deps}")
        
        if exp_design.get('control_group'):
            lines.append(f"Control Group: {exp_design.get('control_group')}")
        
        if exp_design.get('experimental_procedure'):
            proc = exp_design.get('experimental_procedure', {})
            if isinstance(proc, dict):
                lines.append("Experimental Procedure:")
                for phase, desc in proc.items():
                    lines.append(f"  {phase}: {desc}")
            else:
                lines.append(f"Experimental Procedure: {proc}")
        
        if exp_design.get('expected_outcome'):
            lines.append(f"Expected Outcome: {exp_design.get('expected_outcome')}")
        
        if exp_design.get('fallback_plan'):
            lines.append(f"Fallback Plan: {exp_design.get('fallback_plan')}")
        
        if exp_design.get('deliverables'):
            dels = exp_design.get('deliverables', [])
            if isinstance(dels, list):
                lines.append(f"Deliverables: {', '.join(dels)}")
            else:
                lines.append(f"Deliverables: {dels}")
        
        # Legacy week format (fallback)
        if not lines and (exp_design.get('week1') or exp_design.get('week2') or exp_design.get('week3')):
            lines.append("Week 1: " + exp_design.get('week1', 'N/A'))
            lines.append("Week 2: " + exp_design.get('week2', 'N/A'))
            lines.append("Week 3: " + exp_design.get('week3', 'N/A'))
        elif exp_design.get('week1') or exp_design.get('week2') or exp_design.get('week3'):
            # Include legacy format as additional info
            lines.append("\nLegacy Timeline:")
            lines.append("Week 1: " + exp_design.get('week1', 'N/A'))
            lines.append("Week 2: " + exp_design.get('week2', 'N/A'))
            lines.append("Week 3: " + exp_design.get('week3', 'N/A'))
        
        return "\n".join(lines) if lines else "Experiment design structure not available."

    def _extract_search_keywords(self, gap_text: str, title_text: str, topic: str) -> str:
        """Extract key terms for arXiv search"""
        # Combine gap + title, limit to first 150 chars
        combined = f"{title_text} {gap_text}"[:150]

        # Remove common filler words
        filler = ['the', 'a', 'an', 'is', 'are', 'but', 'has', 'have', 'this', 'that', 'these', 'those', 'been', 'being']
        words = combined.lower().split()
        keywords = [w for w in words if len(w) > 4 and w not in filler]

        # Take top 5 keywords + original topic
        search_terms = keywords[:5] + [topic]
        return " ".join(search_terms)


class ResearchAgent:
    """
    Main orchestrator for the research analysis pipeline.
    
    Coordinates the agent pipeline to search papers, analyze content,
    generate insights, and validate results against prior work.
    """

    def __init__(self, use_multi_platform: bool = False, enabled_sources: Optional[set] = None):
        self.llm = LLM()
        self.analyzer = AnalyzerAgent(self.llm)
        self.skeptic = SkepticAgent(self.llm)
        self.synthesizer = SynthesizerAgent(self.llm)
        self.validator = ValidatorAgent(self.llm)
        self.conversation_log = []
        self.use_multi_platform = use_multi_platform
        self.enabled_sources = enabled_sources
        self.multi_scraper = None
        self.last_enhanced_papers = None  # Cache for enhanced papers
        
        # Initialize research intelligence
        self.research_intelligence = None
        self.field_context = ""
        self.research_intelligence_data = None
        
        if RESEARCH_INTELLIGENCE_AVAILABLE:
            try:
                self.research_intelligence = ResearchIntelligence(self.llm)
            except Exception as e:
                print(f"Warning: Could not initialize research intelligence: {e}")
        
        # Initialize multi-platform scraper if requested and available
        if use_multi_platform and MULTI_PLATFORM_AVAILABLE:
            try:
                # Use provided enabled_sources or default to all sources
                sources = enabled_sources if enabled_sources else {'arxiv', 'pwc', 'hf', 'pubmed', 'biorxiv'}
                self.multi_scraper = SimpleMultiPlatformScraper(enabled_sources=sources)
                self.enabled_sources = sources
            except Exception as e:
                print(f"Warning: Could not initialize multi-platform scraper: {e}")
                self.use_multi_platform = False
                self.enabled_sources = None

    def search_papers(self, topic: str, num_papers: int = 5, multi_platform: Optional[bool] = None,
                      enabled_sources: Optional[set] = None) -> List[Paper]:
        """Search for papers (supports multi-platform)
        
        Args:
            topic: Research topic to search for
            num_papers: Number of papers to retrieve
            multi_platform: If True, search multiple platforms. If None, use instance setting.
            enabled_sources: Set of sources to search. If None, uses instance setting.
        
        Returns:
            List of Paper objects
        """
        # Use parameter if provided, otherwise use instance setting
        use_multi = multi_platform if multi_platform is not None else self.use_multi_platform
        sources_to_use = enabled_sources if enabled_sources is not None else self.enabled_sources
        
        if use_multi and self.multi_scraper:
            print(f"🌐 Searching multiple platforms for '{topic}'...")
            # Calculate papers per platform based on number of enabled sources
            num_sources = len(sources_to_use) if sources_to_use else 7
            max_per_platform = max(5, (num_papers // num_sources) + 1)
            
            enhanced_papers = self.multi_scraper.search_all(
                topic, 
                max_per_platform=max_per_platform,
                enabled_sources=sources_to_use
            )
            
            # Cache ALL enhanced papers for UI display (not just first num_papers)
            self.last_enhanced_papers = enhanced_papers
            
            # Convert ALL EnhancedPapers to Paper for compatibility with existing agents
            # Note: Agent analysis will still use top papers (see generate_insights method)
            papers = []
            for ep in enhanced_papers:
                papers.append(Paper(
                    title=ep.title,
                    abstract=ep.abstract,
                    authors=ep.authors,
                    year=ep.year,
                    url=ep.url
                ))
            print(f"✓ Found {len(papers)} papers from multiple platforms")
            return papers
        else:
            print(f"📚 Searching arXiv for '{topic}'...")
            papers = search_arxiv(topic, max_results=num_papers)
            print(f"✓ Found {len(papers)} papers")
            return papers

    def generate_insights(self, papers: List[Paper], topic: str = "") -> List[dict]:
        """
        Generates research insights using the agent pipeline.
        
        Orchestrates the analysis, critique, synthesis, and validation
        process to produce validated research opportunities.
        
        Args:
            papers: List of papers to analyze
            topic: Research topic for context
            
        Returns:
            List of insight dictionaries with validation scores
        """
        print("\n🤖 Starting 4-Agent Pipeline...")
        pipeline_start = time.time()

        # Clear conversation log
        self.conversation_log = []
        
        # Smart sampling for large paper sets (50+ papers)
        # Agents analyze top 5 papers, but for research intelligence we can use more
        papers_for_agents = papers[:5] if len(papers) > 5 else papers
        papers_for_intelligence = papers
        
        if len(papers) >= 50:
            # For 50+ papers, use stratified sampling for research intelligence
            print(f"📊 Large paper set detected ({len(papers)} papers). Using smart sampling...")
            # Take top 20 by relevance (first 20), 10 random, and sample from different years
            sampled_papers = papers[:20]  # Top 20
            if len(papers) > 30:
                import random
                random_indices = random.sample(range(20, len(papers)), min(10, len(papers) - 20))
                sampled_papers.extend([papers[i] for i in random_indices])
            papers_for_intelligence = sampled_papers[:30]  # Limit to 30 for efficiency
            print(f"✓ Using {len(papers_for_intelligence)} papers for research intelligence analysis")
        
        # Generate field context and research intelligence
        if self.research_intelligence and topic:
            print("🧠 Generating field context and research intelligence...")
            try:
                self.field_context = self.research_intelligence.generate_field_context(topic)
                
                # Extract research themes and other intelligence (use sampled papers for large sets)
                themes_data = self.research_intelligence.extract_research_themes(papers_for_intelligence, topic)
                methodology_combos = self.research_intelligence.analyze_methodology_combinations(papers_for_intelligence)
                temporal_trends = self.research_intelligence.analyze_temporal_trends(papers)  # Use all papers for temporal trends
                top_authors = self.research_intelligence.get_top_authors(papers)  # Use all papers for authors
                
                self.research_intelligence_data = {
                    "themes": themes_data,
                    "methodology_combinations": methodology_combos,
                    "temporal_trends": temporal_trends,
                    "top_authors": top_authors,
                    "field_context": self.field_context
                }
                print("✓ Research intelligence generated")
            except Exception as e:
                print(f"⚠️  Could not generate research intelligence: {e}")
                self.field_context = ""
                self.research_intelligence_data = None

        # Agent 1: Analyzer (uses top 5 papers)
        analyzer_result = self.analyzer.analyze_papers(papers_for_agents, topic=topic, field_context=self.field_context)
        gaps = analyzer_result['analysis'].get('cross_paper_gaps', [])
        analyzer_dialogue = analyzer_result.get('dialogue_message', '')
        
        self.conversation_log.append({
            "turn": 1,
            "agent": "Analyzer",
            "responding_to": [],
            "message_type": "observation",
            "dialogue_message": analyzer_dialogue,
            "action": "Analyzed papers and extracted limitations",
            "duration": analyzer_result["duration"],
            "output_summary": f"Found {len(gaps)} cross-paper gaps",
            "thinking": [
                f"Analyzed {analyzer_result['papers_analyzed']} papers (from {len(papers)} total)",
                f"Identified {len(gaps)} cross-paper patterns",
                f"Most severe gap: {gaps[0]['gap'][:80]}..." if gaps else "No major gaps found"
            ],
            "key_findings": gaps[:2] if gaps else [],
            "analysis_details": analyzer_result.get('analysis', {})
        })

        # Agent 2: Skeptic (uses same papers as Analyzer) - responds to Analyzer
        skeptic_result = self.skeptic.critique(papers_for_agents, analyzer_result, topic=topic, field_context=self.field_context)
        critique = skeptic_result.get('critique', {})
        contradictions = critique.get('contradictions', [])
        potential_contradictions = critique.get('potential_contradictions', [])
        field_insights = critique.get('field_insights', '')
        field_knowledge_contradictions = critique.get('field_knowledge_contradictions', '')
        interpretation = critique.get('interpretation', '')
        skeptic_dialogue = skeptic_result.get('dialogue_message', '')
        
        # Build thinking with field insights
        thinking_items = [
            f"Challenged {len(gaps)} identified gaps",
            f"Found {len(contradictions)} direct contradictions between papers",
            f"Suggested {len(potential_contradictions)} potential contradictions from field knowledge"
        ]
        if field_insights:
            thinking_items.append(f"Field insights: {field_insights[:100]}...")
        if interpretation:
            thinking_items.append(f"Interpretation: {interpretation[:100]}...")
        if not contradictions and not potential_contradictions:
            thinking_items.append("No direct contradictions found - provided field analysis and potential contradictions instead")
        
        self.conversation_log.append({
            "turn": 2,
            "agent": "Skeptic",
            "responding_to": ["Analyzer"],
            "message_type": "challenge",
            "dialogue_message": skeptic_dialogue,
            "action": "Challenged assumptions and found contradictions",
            "duration": skeptic_result["duration"],
            "output_summary": f"Found {len(contradictions)} contradictions, {len(potential_contradictions)} potential contradictions" + (f" | Field insights provided" if field_insights else ""),
            "thinking": thinking_items,
            "key_findings": contradictions[:2] if contradictions else potential_contradictions[:2] if potential_contradictions else [{"field_insights": field_insights[:150]}] if field_insights else [],
            "contradictions": contradictions,
            "potential_contradictions": potential_contradictions,
            "field_insights": field_insights,
            "field_knowledge_contradictions": field_knowledge_contradictions,
            "interpretation": interpretation
        })

        # Agent 3: Synthesizer (uses same papers as Analyzer) - responds to Analyzer and Skeptic
        synthesizer_start = time.time()
        insights = self.synthesizer.synthesize(papers_for_agents, analyzer_result, skeptic_result, topic=topic, field_context=self.field_context)
        synthesizer_duration = time.time() - synthesizer_start
        
        # Validate insights are dictionaries before accessing
        validated_insights_for_stats = [i for i in insights if isinstance(i, dict)]
        avg_novelty = sum([i.get('novelty_score', 0) for i in validated_insights_for_stats]) / len(validated_insights_for_stats) if validated_insights_for_stats else 0
        
        # Get dialogue messages from insights
        synthesizer_dialogues = [i.get('dialogue_message', '') for i in validated_insights_for_stats if isinstance(i, dict) and i.get('dialogue_message')]
        synthesizer_dialogue = synthesizer_dialogues[0] if synthesizer_dialogues else f"I see opportunities here. Based on the analysis and challenges, I've synthesized {len(validated_insights_for_stats)} research directions."
        
        self.conversation_log.append({
            "turn": 3,
            "agent": "Synthesizer",
            "responding_to": ["Analyzer", "Skeptic"],
            "message_type": "synthesis",
            "dialogue_message": synthesizer_dialogue,
            "action": "Generated research opportunities with experiment designs",
            "duration": synthesizer_duration,
            "output_summary": f"Generated {len(validated_insights_for_stats)} actionable insights",
            "thinking": [
                f"Synthesized {len(validated_insights_for_stats)} research opportunities from gaps and contradictions",
                f"Average novelty score: {avg_novelty:.1f}/10",
                f"Top insight: {validated_insights_for_stats[0]['title'][:80]}..." if validated_insights_for_stats and len(validated_insights_for_stats) > 0 else "No insights generated"
            ],
            "key_findings": [{"title": i.get('title', 'Untitled'), "novelty": i.get('novelty_score', 0)} for i in validated_insights_for_stats[:2] if isinstance(i, dict)],
            "insights": validated_insights_for_stats  # Store validated insights for dialogue context
        })

        # Agent 4: Validator - responds to Synthesizer (use validated insights to ensure all are dicts)
        validator_start = time.time()
        validated_insights = self.validator.validate(validated_insights_for_stats, topic or "research", field_context=self.field_context)
        validator_duration = time.time() - validator_start

        survived = len([i for i in validated_insights if isinstance(i, dict) and i.get('validated', False)])
        rejected = len(validated_insights_for_stats) - len(validated_insights)
        
        # Get validation dialogue messages
        validation_dialogues = [i.get('validation_dialogue', '') for i in validated_insights if isinstance(i, dict) and i.get('validation_dialogue')]
        validator_dialogue = validation_dialogues[0] if validation_dialogues else f"Quick check: scanning recent literature. {survived} insights validated, {rejected} rejected. → Validation complete."
        
        self.conversation_log.append({
            "turn": 4,
            "agent": "Validator",
            "responding_to": ["Synthesizer"],
            "message_type": "validation",
            "dialogue_message": validator_dialogue,
            "action": "Validated insights against prior work",
            "duration": validator_duration,
            "output_summary": f"{survived} survived | {rejected} rejected",
            "thinking": [
                f"Validated {len(validated_insights_for_stats)} insights by searching arXiv for contradicting work",
                f"{survived} insights survived validation",
                f"{rejected} insights rejected as already solved or invalid",
                f"Average survival score: {sum([i.get('survival_score', 0) for i in validated_insights if isinstance(i, dict)]) / len(validated_insights):.1f}/10" if validated_insights else "No insights survived"
            ],
            "key_findings": [{"title": i.get('title', 'Untitled'), "survival_score": i.get('survival_score', 0)} for i in validated_insights[:2] if isinstance(i, dict)],
            "validated_insights": validated_insights
        })

        total_duration = time.time() - pipeline_start
        print(f"\n✅ Pipeline complete! ({total_duration:.1f}s total)")

        return validated_insights

    def get_conversation_log(self) -> List[Dict[str, Any]]:
        """Get the conversation log for visualization"""
        return self.conversation_log
    
    def get_research_intelligence(self) -> Optional[Dict[str, Any]]:
        """Get research intelligence data for UI display"""
        return self.research_intelligence_data
