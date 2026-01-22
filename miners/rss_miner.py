"""
RSS Miner - Extract content from RSS feeds.
"""

import os
from typing import List, Optional
from datetime import datetime

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False

from models import Evidence, SourceType
from miners.base_miner import BaseMiner


class RSSMiner(BaseMiner):
    """
    Miner for extracting content from RSS feeds.
    Combines RSS feed parsing with article extraction.
    """
    
    def __init__(self, fetch_full_content: bool = True):
        """
        Initialize the RSS miner.
        
        Args:
            fetch_full_content: Whether to fetch full article content (vs just RSS description)
        """
        super().__init__()
        
        if not FEEDPARSER_AVAILABLE:
            raise ImportError("feedparser is not installed. Install with: pip install feedparser")
        
        self.fetch_full_content = fetch_full_content
        
        # Lazy import ArticleMiner only if needed
        self.article_miner = None
        if fetch_full_content:
            try:
                from miners.article_miner import ArticleMiner
                self.article_miner = ArticleMiner()
            except ImportError:
                print("  ⚠ Article extraction not available, will use RSS descriptions only")
                self.fetch_full_content = False
    
    def fetch(self, query: str, max_entries: int = 5) -> List[Evidence]:
        """
        Fetch content from RSS feeds.
        
        Args:
            query: RSS feed URL or comma-separated list of feed URLs
            max_entries: Maximum number of entries to fetch per feed
        
        Returns:
            List of Evidence objects containing feed content
        """
        # Handle multiple feeds
        feeds = [feed.strip() for feed in query.split(',')]
        
        all_evidence = []
        
        for feed_url in feeds:
            print(f"\n📡 Fetching RSS feed: {feed_url}")
            
            try:
                feed = feedparser.parse(feed_url)
                
                if feed.bozo:  # Error parsing feed
                    print(f"  ⚠ Error parsing feed: {feed.bozo_exception}")
                    continue
                
                feed_title = feed.feed.get('title', 'Unknown Feed')
                print(f"  Feed: {feed_title}")
                print(f"  Found {len(feed.entries)} entries")
                
                # Process entries
                for i, entry in enumerate(feed.entries[:max_entries]):
                    if self.fetch_full_content and entry.get('link'):
                        # Fetch full article content
                        article_evidence = self._fetch_full_article(entry, feed_title)
                        if article_evidence:
                            all_evidence.append(article_evidence)
                    else:
                        # Use RSS description
                        rss_evidence = self._create_from_rss_entry(entry, feed_title)
                        if rss_evidence and self.validate_evidence(rss_evidence):
                            all_evidence.append(rss_evidence)
                    
                    print(f"  ✓ {i+1}/{max_entries}: {entry.get('title', 'Untitled')[:50]}...")
            
            except Exception as e:
                print(f"  ✗ Error fetching feed: {e}")
        
        print(f"\n  → Collected {len(all_evidence)} items from RSS feeds")
        return all_evidence
    
    def _fetch_full_article(self, entry: dict, feed_title: str) -> Optional[Evidence]:
        """
        Fetch full article content for an RSS entry.
        
        Args:
            entry: RSS feed entry
            feed_title: Title of the RSS feed
        
        Returns:
            Evidence object with full article content
        """
        try:
            # Use ArticleMiner to fetch full content
            articles = self.article_miner.fetch(entry['link'])
            
            if articles:
                evidence = articles[0]
                # Update metadata to indicate RSS source
                evidence.metadata['rss_feed'] = feed_title
                evidence.metadata['published'] = entry.get('published', '')
                evidence.source_type = SourceType.RSS
                return evidence
        except Exception as e:
            print(f"    ⚠ Could not fetch full article, using RSS description: {e}")
        
        return None
    
    def _create_from_rss_entry(self, entry: dict, feed_title: str) -> Optional[Evidence]:
        """
        Create Evidence from RSS entry (without fetching full article).
        
        Args:
            entry: RSS feed entry
            feed_title: Title of the RSS feed
        
        Returns:
            Evidence object from RSS data
        """
        try:
            # Get content from description or summary
            content = entry.get('description') or entry.get('summary') or ""
            
            # Remove HTML tags if present
            import re
            content = re.sub('<[^<]+?>', '', content)
            
            # Parse date
            date = None
            if entry.get('published_parsed'):
                try:
                    import time
                    date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                except:
                    pass
            
            return Evidence(
                title=entry.get('title', 'Untitled'),
                source_url=entry.get('link', ''),
                raw_content=content,
                source_type=SourceType.RSS,
                description=content[:200] + "..." if len(content) > 200 else content,
                author=entry.get('author'),
                date=date,
                publisher=feed_title,
                metadata={
                    "word_count": len(content.split()),
                    "rss_feed": feed_title,
                    "published": entry.get('published', ''),
                    "tags": [tag.term for tag in entry.get('tags', [])] if entry.get('tags') else []
                }
            )
        except Exception as e:
            print(f"  ⚠ Error creating evidence from RSS entry: {e}")
            return None
