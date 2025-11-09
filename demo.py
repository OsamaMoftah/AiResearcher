"""
Command-line demo of the research agent system.

Provides an interactive demonstration of the multi-agent pipeline
for generating research insights from academic papers.
"""
from core.research import ResearchAgent
import json

def main():
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                    AiResearcher Demo                              ║
║            4-Agent Research Insight Generator                     ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Configuration
    topic = input("Enter research topic (or press Enter for 'transformer models'): ").strip()
    if not topic:
        topic = "transformer models"

    num_papers = input("Number of papers (default 3): ").strip()
    num_papers = int(num_papers) if num_papers else 3

    print(f"\n{'='*70}")
    print(f"Topic: {topic}")
    print(f"Papers: {num_papers}")
    print(f"{'='*70}\n")

    # Initialize agent
    agent = ResearchAgent()

    # Search papers
    print("📚 Step 1: Searching papers...\n")
    papers = agent.search_papers(topic, num_papers)

    if not papers:
        print("❌ No papers found. Try a different topic.")
        return

    print(f"\n✓ Found {len(papers)} papers:")
    for i, paper in enumerate(papers, 1):
        print(f"  {i}. {paper.title[:80]}...")

    # Generate insights
    print(f"\n{'='*70}")
    print("🤖 Step 2: Running 4-Agent Pipeline...")
    print(f"{'='*70}\n")

    insights = agent.generate_insights(papers)

    # Display results
    print(f"\n{'='*70}")
    print("💡 Results")
    print(f"{'='*70}\n")

    for i, insight in enumerate(insights, 1):
        overall_score = (
            insight.get('novelty_score', 0) +
            insight.get('feasibility_score', 0) +
            insight.get('impact_score', 0)
        ) / 3

        print(f"\n{'─'*70}")
        print(f"Insight #{i}: {insight.get('title', 'Untitled')}")
        print(f"Overall Score: {overall_score:.1f}/10")
        print(f"{'─'*70}")

        print(f"\n🎯 THE GAP:")
        print(f"   {insight.get('gap', 'N/A')}\n")

        print(f"⚠️  SKEPTIC'S CHALLENGE:")
        print(f"   {insight.get('skeptic_challenge', 'N/A')}\n")

        exp = insight.get('experiment_design', {})
        if exp:
            print(f"🔬 3-WEEK EXPERIMENT:")
            print(f"   Week 1: {exp.get('week1', 'N/A')}")
            print(f"   Week 2: {exp.get('week2', 'N/A')}")
            print(f"   Week 3: {exp.get('week3', 'N/A')}\n")

        print(f"💰 IMPACT:")
        print(f"   {insight.get('impact', 'N/A')}\n")

        # Show validation status
        if insight.get('validated'):
            print(f"🛡️  VALIDATION: ✓ VALIDATED (Survival Score: {insight.get('survival_score', 0)}/10)")
            if insight.get('validation_evidence'):
                print(f"   Evidence: {insight.get('validation_evidence', 'N/A')[:100]}...\n")
        else:
            print(f"🛡️  VALIDATION: ⚠️ UNVALIDATED (Survival Score: {insight.get('survival_score', 0)}/10)\n")

        print(f"📊 SCORES:")
        print(f"   Novelty:     {insight.get('novelty_score', 0)}/10")
        print(f"   Feasibility: {insight.get('feasibility_score', 0)}/10")
        print(f"   Impact:      {insight.get('impact_score', 0)}/10")

    # Show agent conversation
    print(f"\n{'='*70}")
    print("🔄 Agent Conversation Log")
    print(f"{'='*70}\n")

    for log in agent.get_conversation_log():
        print(f"🤖 {log['agent']}:")
        print(f"   Action:   {log['action']}")
        print(f"   Result:   {log['output_summary']}")
        print(f"   Duration: {log['duration']:.1f}s\n")

    # Save option
    save = input("\nSave results to JSON? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"demo_results_{topic.replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump({
                "topic": topic,
                "papers": [{"title": p.title, "url": p.url} for p in papers],
                "insights": insights,
                "conversation_log": agent.get_conversation_log()
            }, f, indent=2)
        print(f"✓ Saved to {filename}")

    print("\n✅ Demo complete!")


if __name__ == "__main__":
    main()
