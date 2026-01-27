"""
Miners package - modular content extractors for various sources.
"""

# Lazy imports to avoid dependency issues
# Import specific miners only when needed

__all__ = [
    'BaseMiner',
    'YouTubeMiner',
    'ArticleMiner',
    'RSSMiner',
    'PaperMiner',
    'PodcastMiner',
    'VimeoMiner',
    'DailymotionMiner',
]


def __getattr__(name):
    """Lazy load miners to avoid importing dependencies that may not be installed."""
    if name == 'BaseMiner':
        from .base_miner import BaseMiner
        return BaseMiner
    elif name == 'YouTubeMiner':
        from .youtube_miner import YouTubeMiner
        return YouTubeMiner
    elif name == 'ArticleMiner':
        from .article_miner import ArticleMiner
        return ArticleMiner
    elif name == 'RSSMiner':
        from .rss_miner import RSSMiner
        return RSSMiner
    elif name == 'PaperMiner':
        from .paper_miner import PaperMiner
        return PaperMiner
    elif name == 'PodcastMiner':
        from .podcast_miner import PodcastMiner
        return PodcastMiner
    elif name == 'VimeoMiner':
        from .vimeo_miner import VimeoMiner
        return VimeoMiner
    elif name == 'DailymotionMiner':
        from .dailymotion_miner import DailymotionMiner
        return DailymotionMiner
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
