"""
Enhanced Main Pipeline - Content Funnel
Modular pipeline supporting multiple content sources.
"""

import os
import sys
from typing import List, Dict, Any, Optional

from content_brain import ContentBrain
from ghostwriter import GhostWriter
from outputs.epub_creator import create_epub_from_articles
from models import Evidence


def run_pipeline(
    sources: Dict[str, str],
    output_format: str = "epub",
    output_dir: str = None
) -> Optional[str]:
    """
    Run the complete Content Funnel pipeline.
    
    Args:
        sources: Dictionary mapping source type to query
                 Example: {"youtube": "@mkbhd", "article": "https://example.com/article"}
        output_format: Output format ("epub" for now, more formats coming)
        output_dir: Directory to save output files
    
    Returns:
        Path to generated output file or None on failure
    """
    print("=" * 60)
    print("  CONTENT FUNNEL PIPELINE")
    print("=" * 60)
    
    # Initialize components
    brain = ContentBrain()
    
    # Step 1: Gather evidence from all sources
    print("\n📥 STEP 1: Gathering evidence from sources...")
    print("=" * 60)
    
    for source_type, query in sources.items():
        print(f"\n  Source: {source_type}")
        
        try:
            # Import and initialize appropriate miner
            miner = _get_miner(source_type)
            
            if not miner:
                print(f"  ✗ Unknown source type: {source_type}")
                continue
            
            # Fetch evidence
            evidence = miner.fetch(query)
            
            # Add to brain
            brain.add_evidence_batch(evidence)
            
        except Exception as e:
            print(f"  ✗ Error with {source_type}: {e}")
    
    # Check if we have any evidence
    if not brain.evidence_pool:
        print("\n✗ No evidence collected. Exiting.")
        return None
    
    # Display stats
    stats = brain.get_stats()
    print(f"\n{'='*60}")
    print(f"  Collected {stats['total_evidence']} pieces of evidence")
    print(f"  From {stats['sources']} unique sources")
    print(f"{'='*60}")
    
    # Step 2: Transform evidence into articles
    print("\n✍️  STEP 2: Transforming evidence into articles...")
    print("=" * 60)
    
    try:
        ghostwriter = GhostWriter()
        articles = ghostwriter.transform_batch(brain.evidence_pool)
    except Exception as e:
        print(f"\n✗ Error generating articles: {e}")
        return None
    
    if not articles:
        print("\n✗ No articles generated. Exiting.")
        return None
    
    # Step 3: Create output
    print("\n📚 STEP 3: Creating output...")
    print("=" * 60)
    
    try:
        if output_format == "epub":
            filepath = create_epub_from_articles(articles, output_dir)
        else:
            print(f"  ✗ Unsupported output format: {output_format}")
            return None
        
        print("\n" + "=" * 60)
        print("  ✓ PIPELINE COMPLETE!")
        print("=" * 60)
        
        return filepath
    
    except Exception as e:
        print(f"\n✗ Error creating output: {e}")
        return None


def _get_miner(source_type: str):
    """Get the appropriate miner for a source type."""
    from miners import (
        YouTubeMiner, ArticleMiner, RSSMiner,
        PaperMiner, PodcastMiner, VimeoMiner, DailymotionMiner
    )
    
    miners = {
        "youtube": YouTubeMiner,
        "article": ArticleMiner,
        "rss": RSSMiner,
        "paper": PaperMiner,
        "podcast": PodcastMiner,
        "vimeo": VimeoMiner,
        "dailymotion": DailymotionMiner,
    }
    
    miner_class = miners.get(source_type.lower())
    
    if miner_class:
        return miner_class()
    
    return None


def run_legacy_mode():
    """
    Run the original YouTube-only pipeline for backward compatibility.
    """
    print("=" * 60)
    print("  YOUTUBE NEWSLETTER GENERATOR (Legacy Mode)")
    print("=" * 60)
    
    # Import legacy functions
    from get_videos import main as fetch_videos
    from get_transcripts import get_transcripts_for_videos
    from write_articles import write_articles_for_videos
    from send_email import send_newsletter
    from video_tracker import filter_new_videos, mark_videos_processed, get_processed_count
    
    print(f"  Previously processed: {get_processed_count()} videos")
    
    # Step 1: Fetch videos
    print("\n📺 STEP 1: Fetching latest videos...\n")
    videos = fetch_videos()
    
    if not videos:
        print("No videos found. Check your channel list.")
        return
    
    # Filter new videos
    print("\n🔍 Checking for new videos...\n")
    new_videos = filter_new_videos(videos)
    
    if not new_videos:
        print("No new videos to process.")
        print("=" * 60)
        return
    
    print(f"\n  → {len(new_videos)} new video(s) to process\n")
    
    # Step 2: Get transcripts
    print("\n📝 STEP 2: Extracting transcripts...\n")
    videos_with_transcripts = get_transcripts_for_videos(new_videos)
    
    if not videos_with_transcripts:
        print("No transcripts available.")
        return
    
    # Step 3: Generate articles
    print("\n✍️ STEP 3: Writing articles with Claude AI...\n")
    articles = write_articles_for_videos(videos_with_transcripts)
    
    if not articles:
        print("No articles generated.")
        return
    
    # Step 4: Send newsletter
    print("\n📧 STEP 4: Sending newsletter...\n")
    success = send_newsletter(articles)
    
    # Mark as processed
    if success:
        mark_videos_processed(videos_with_transcripts)
        print(f"\n  ✓ Marked {len(videos_with_transcripts)} video(s) as processed")
    
    print("\n" + "=" * 60)
    print("  DONE!")
    print("=" * 60)


if __name__ == "__main__":
    # Check if running in interactive mode or with arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--legacy":
            # Run original YouTube-only pipeline
            run_legacy_mode()
        elif sys.argv[1] == "--cli":
            # Run interactive CLI
            from cli import main as cli_main
            cli_main()
        else:
            print("Usage:")
            print("  python main_pipeline.py --cli       # Interactive CLI")
            print("  python main_pipeline.py --legacy    # Legacy YouTube-only mode")
            print("  python main_pipeline.py             # Example multi-source demo")
    else:
        # Demo: Run with example sources
        print("\nRunning demo with example sources...")
        print("(Use --cli for interactive mode or --legacy for YouTube-only mode)\n")
        
        example_sources = {
            "youtube": "@ycombinator",  # Example: Y Combinator channel
        }
        
        run_pipeline(example_sources)
