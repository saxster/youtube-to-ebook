"""
Example: Using the Content Funnel Pipeline

This script demonstrates how to use the new modular pipeline
with different content sources.
"""

from models import Evidence, SourceType
from content_brain import ContentBrain
from ghostwriter import GhostWriter
from outputs.epub_creator import create_epub_from_articles


def example_basic_usage():
    """
    Example 1: Basic usage with manually created evidence.
    Useful for testing or custom integrations.
    """
    print("\n" + "="*60)
    print("  EXAMPLE 1: Basic Usage with Manual Evidence")
    print("="*60 + "\n")
    
    # Create ContentBrain
    brain = ContentBrain()
    
    # Create some sample evidence manually
    evidence1 = Evidence(
        title="Understanding Machine Learning",
        source_url="https://example.com/ml-article",
        raw_content="""
        Machine learning has revolutionized how computers learn from data.
        Instead of being explicitly programmed, machine learning algorithms
        use statistical techniques to learn patterns from data. This has
        enabled breakthroughs in computer vision, natural language processing,
        and many other fields. The key insight is that given enough data,
        algorithms can discover patterns that humans might miss.
        """ * 10,  # Repeat to make it longer
        source_type=SourceType.ARTICLE,
        author="Jane Doe",
        publisher="Tech Blog",
        description="An introduction to machine learning concepts"
    )
    
    evidence2 = Evidence(
        title="The Future of AI",
        source_url="https://example.com/ai-future",
        raw_content="""
        Artificial intelligence continues to advance at a rapid pace.
        Recent developments in large language models, computer vision,
        and reinforcement learning are pushing the boundaries of what's
        possible. As these technologies mature, they will transform
        industries from healthcare to transportation to education.
        The key challenges ahead include ensuring AI safety, addressing
        bias, and making AI more accessible to everyone.
        """ * 10,
        source_type=SourceType.ARTICLE,
        author="John Smith",
        publisher="AI Weekly",
        description="Exploring future trends in AI"
    )
    
    # Add to ContentBrain
    brain.add_evidence_batch([evidence1, evidence2])
    
    # Display stats
    stats = brain.get_stats()
    print(f"✓ Added {stats['total_evidence']} pieces of evidence")
    print(f"  Sources: {stats['sources']}")
    print(f"  By type: {stats['by_source_type']}")
    
    # Note: To actually generate articles and create an ebook,
    # you would need valid API keys. Here's how it would work:
    
    print("\n📝 To generate articles, you would:")
    print("   1. Initialize GhostWriter with API key")
    print("   2. Call ghostwriter.transform_batch(brain.evidence_pool)")
    print("   3. Call create_epub_from_articles(articles)")
    print("\n   (Skipping actual generation to avoid API costs)")


def example_filter_by_source():
    """
    Example 2: Working with different source types.
    """
    print("\n" + "="*60)
    print("  EXAMPLE 2: Filtering by Source Type")
    print("="*60 + "\n")
    
    brain = ContentBrain()
    
    # Add different types of evidence
    brain.add_evidence(Evidence(
        title="Video Tutorial",
        source_url="https://youtube.com/watch?v=test",
        raw_content="Video content " * 50,
        source_type=SourceType.VIDEO,
        publisher="Tech Channel"
    ))
    
    brain.add_evidence(Evidence(
        title="Research Paper",
        source_url="https://arxiv.org/abs/2301.00001",
        raw_content="Research content " * 50,
        source_type=SourceType.PAPER,
        publisher="arXiv"
    ))
    
    brain.add_evidence(Evidence(
        title="Podcast Episode",
        source_url="https://podcast.com/ep1",
        raw_content="Podcast transcript " * 50,
        source_type=SourceType.PODCAST,
        publisher="Tech Podcast"
    ))
    
    # Filter by type
    videos = brain.get_by_source_type(SourceType.VIDEO)
    papers = brain.get_by_source_type(SourceType.PAPER)
    podcasts = brain.get_by_source_type(SourceType.PODCAST)
    
    print(f"✓ Total evidence: {len(brain.evidence_pool)}")
    print(f"  Videos: {len(videos)}")
    print(f"  Papers: {len(papers)}")
    print(f"  Podcasts: {len(podcasts)}")
    
    # Filter by publisher
    podcast_items = brain.get_by_publisher("Tech Podcast")
    print(f"\n✓ Items from 'Tech Podcast': {len(podcast_items)}")


def example_save_and_load():
    """
    Example 3: Saving and loading evidence pool.
    """
    print("\n" + "="*60)
    print("  EXAMPLE 3: Saving and Loading Evidence Pool")
    print("="*60 + "\n")
    
    # Create and populate brain
    brain1 = ContentBrain()
    brain1.add_evidence(Evidence(
        title="Saved Evidence",
        source_url="https://example.com",
        raw_content="Content to save " * 50,
        source_type=SourceType.ARTICLE
    ))
    
    # Save to file
    import tempfile
    import os
    
    temp_dir = tempfile.gettempdir()
    save_path = os.path.join(temp_dir, "evidence_pool.json")
    
    brain1.save_to_file(save_path)
    print(f"✓ Saved to: {save_path}")
    
    # Load into new brain
    brain2 = ContentBrain()
    brain2.load_from_file(save_path)
    
    print(f"✓ Loaded {len(brain2.evidence_pool)} items")
    print(f"  Title: {brain2.evidence_pool[0].title}")
    
    # Clean up
    os.remove(save_path)
    print(f"✓ Cleaned up temporary file")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  CONTENT FUNNEL PIPELINE - EXAMPLES")
    print("="*60)
    
    example_basic_usage()
    example_filter_by_source()
    example_save_and_load()
    
    print("\n" + "="*60)
    print("  Examples Complete!")
    print("="*60)
    print("\nFor more information, see CONTENT_FUNNEL.md")
    print()
