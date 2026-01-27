"""
Article Miner - Extract content from web articles and news sites.
Uses newspaper3k and trafilatura for robust article extraction.
"""

import os
from typing import List, Optional
from datetime import datetime

try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False

try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False

from models import Evidence, SourceType
from miners.base_miner import BaseMiner


class ArticleMiner(BaseMiner):
    """
    Miner for extracting content from web articles.
    Supports both newspaper3k and trafilatura backends.
    """
    
    def __init__(self, backend: str = "auto"):
        """
        Initialize the Article miner.
        
        Args:
            backend: Which backend to use ("newspaper", "trafilatura", or "auto")
        """
        super().__init__()
        
        if backend == "auto":
            if NEWSPAPER_AVAILABLE:
                self.backend = "newspaper"
            elif TRAFILATURA_AVAILABLE:
                self.backend = "trafilatura"
            else:
                raise ImportError(
                    "Neither newspaper3k nor trafilatura is installed. "
                    "Install one with: pip install newspaper3k OR pip install trafilatura"
                )
        else:
            self.backend = backend
            
            if backend == "newspaper" and not NEWSPAPER_AVAILABLE:
                raise ImportError("newspaper3k is not installed. Install with: pip install newspaper3k")
            if backend == "trafilatura" and not TRAFILATURA_AVAILABLE:
                raise ImportError("trafilatura is not installed. Install with: pip install trafilatura")
    
    def fetch(self, query: str) -> List[Evidence]:
        """
        Fetch article content from URLs.
        
        Args:
            query: Article URL or comma-separated list of URLs
        
        Returns:
            List of Evidence objects containing article content
        """
        # Handle multiple URLs
        urls = [url.strip() for url in query.split(',')]
        
        all_evidence = []
        
        for url in urls:
            print(f"\n📰 Fetching article: {url}")
            
            if self.backend == "newspaper":
                evidence = self._fetch_with_newspaper(url)
            else:
                evidence = self._fetch_with_trafilatura(url)
            
            if evidence and self.validate_evidence(evidence):
                all_evidence.append(evidence)
                print(f"  ✓ Extracted: {evidence.title}")
            else:
                print(f"  ✗ Failed to extract article")
        
        print(f"\n  → Collected {len(all_evidence)} articles")
        return all_evidence
    
    def _fetch_with_newspaper(self, url: str) -> Optional[Evidence]:
        """Fetch article using newspaper3k."""
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            # Try to get publish date
            try:
                article.nlp()  # This enables date extraction
            except:
                pass
            
            return Evidence(
                title=article.title or "Untitled Article",
                source_url=url,
                raw_content=article.text,
                source_type=SourceType.ARTICLE,
                description=article.meta_description or "",
                author=", ".join(article.authors) if article.authors else None,
                date=article.publish_date,
                publisher=article.source_url or url.split('/')[2] if '/' in url else None,
                metadata={
                    "word_count": len(article.text.split()),
                    "backend": "newspaper3k",
                    "top_image": article.top_image,
                    "keywords": article.keywords if hasattr(article, 'keywords') else []
                }
            )
        except Exception as e:
            print(f"  ⚠ Error with newspaper3k: {e}")
            return None
    
    def _fetch_with_trafilatura(self, url: str) -> Optional[Evidence]:
        """Fetch article using trafilatura."""
        try:
            downloaded = trafilatura.fetch_url(url)
            
            if not downloaded:
                return None
            
            # Extract metadata
            metadata = trafilatura.extract_metadata(downloaded)
            
            # Extract main content
            content = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=True,
                no_fallback=False
            )
            
            if not content:
                return None
            
            # Parse date if available
            date = None
            if metadata and metadata.date:
                try:
                    date = datetime.fromisoformat(metadata.date)
                except:
                    pass
            
            return Evidence(
                title=metadata.title if metadata else "Untitled Article",
                source_url=url,
                raw_content=content,
                source_type=SourceType.ARTICLE,
                description=metadata.description if metadata else "",
                author=metadata.author if metadata else None,
                date=date,
                publisher=metadata.sitename if metadata else None,
                metadata={
                    "word_count": len(content.split()),
                    "backend": "trafilatura",
                    "categories": metadata.categories if metadata and metadata.categories else [],
                    "tags": metadata.tags if metadata and metadata.tags else []
                }
            )
        except Exception as e:
            print(f"  ⚠ Error with trafilatura: {e}")
            return None
