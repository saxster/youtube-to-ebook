"""
Podcast Miner - Extract content from podcasts via RSS and audio transcription.
"""

import os
from typing import List, Optional
from datetime import datetime
import urllib.request

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

from models import Evidence, SourceType
from miners.base_miner import BaseMiner


class PodcastMiner(BaseMiner):
    """
    Miner for extracting content from podcasts.
    Combines RSS feed parsing with audio transcription using Whisper.
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize the Podcast miner.
        
        Args:
            model_size: Whisper model size ("tiny", "base", "small", "medium", "large")
        """
        super().__init__()
        
        if not FEEDPARSER_AVAILABLE:
            raise ImportError("feedparser is required. Install with: pip install feedparser")
        
        self.transcribe_audio = WHISPER_AVAILABLE
        
        if WHISPER_AVAILABLE:
            print(f"  Loading Whisper model ({model_size})...")
            self.whisper_model = whisper.load_model(model_size)
        else:
            print("  ⚠ Whisper not available. Install with: pip install openai-whisper")
            print("  ⚠ Will extract only podcast descriptions from RSS")
    
    def fetch(self, query: str, max_episodes: int = 3) -> List[Evidence]:
        """
        Fetch podcast episodes from RSS feed.
        
        Args:
            query: Podcast RSS feed URL or comma-separated list of URLs
            max_episodes: Maximum number of episodes to process per podcast
        
        Returns:
            List of Evidence objects containing podcast transcripts
        """
        # Handle multiple feeds
        feeds = [feed.strip() for feed in query.split(',')]
        
        all_evidence = []
        
        for feed_url in feeds:
            print(f"\n🎙️ Fetching podcast feed: {feed_url}")
            
            try:
                feed = feedparser.parse(feed_url)
                
                if feed.bozo:
                    print(f"  ⚠ Error parsing feed: {feed.bozo_exception}")
                    continue
                
                podcast_title = feed.feed.get('title', 'Unknown Podcast')
                print(f"  Podcast: {podcast_title}")
                print(f"  Found {len(feed.entries)} episodes")
                
                # Process episodes
                for i, entry in enumerate(feed.entries[:max_episodes]):
                    print(f"\n  Episode {i+1}/{max_episodes}: {entry.get('title', 'Untitled')[:50]}...")
                    
                    evidence = self._process_episode(entry, podcast_title)
                    
                    if evidence and self.validate_evidence(evidence):
                        all_evidence.append(evidence)
                        print(f"    ✓ Processed successfully")
                    else:
                        print(f"    ✗ Failed to process episode")
            
            except Exception as e:
                print(f"  ✗ Error fetching podcast feed: {e}")
        
        print(f"\n  → Collected {len(all_evidence)} podcast episodes")
        return all_evidence
    
    def _process_episode(self, entry: dict, podcast_title: str) -> Optional[Evidence]:
        """
        Process a podcast episode.
        
        Args:
            entry: RSS feed entry for the episode
            podcast_title: Title of the podcast
        
        Returns:
            Evidence object with transcript or description
        """
        # Find audio enclosure
        audio_url = None
        
        for enclosure in entry.get('enclosures', []):
            if enclosure.get('type', '').startswith('audio/'):
                audio_url = enclosure.get('href')
                break
        
        # Try alternate audio link methods
        if not audio_url:
            for link in entry.get('links', []):
                if link.get('type', '').startswith('audio/'):
                    audio_url = link.get('href')
                    break
        
        # Get transcript
        content = None
        
        if audio_url and self.transcribe_audio:
            print(f"    Transcribing audio...")
            content = self._transcribe_audio(audio_url)
        
        # Fallback to description if no transcript
        if not content:
            content = entry.get('description') or entry.get('summary') or ""
            
            # Remove HTML tags
            import re
            content = re.sub('<[^<]+?>', '', content)
            
            if audio_url:
                print(f"    Using episode description (transcription unavailable)")
        
        if not content or len(content) < 50:
            return None
        
        # Parse date
        date = None
        if entry.get('published_parsed'):
            try:
                import time
                date = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            except:
                pass
        
        return Evidence(
            title=entry.get('title', 'Untitled Episode'),
            source_url=entry.get('link', audio_url or ''),
            raw_content=content,
            source_type=SourceType.PODCAST,
            description=entry.get('summary', '')[:200] if entry.get('summary') else None,
            author=entry.get('author') or podcast_title,
            date=date,
            publisher=podcast_title,
            metadata={
                "word_count": len(content.split()),
                "audio_url": audio_url,
                "duration": entry.get('itunes_duration', 'Unknown'),
                "transcribed": audio_url and self.transcribe_audio and content,
                "podcast_feed": podcast_title,
            }
        )
    
    def _transcribe_audio(self, audio_url: str) -> Optional[str]:
        """
        Download and transcribe audio using Whisper.
        
        Args:
            audio_url: URL to audio file
        
        Returns:
            Transcribed text or None
        """
        if not self.transcribe_audio:
            return None
        
        try:
            # Download audio file
            audio_path = "/tmp/podcast_audio.mp3"
            print(f"      Downloading audio...")
            urllib.request.urlretrieve(audio_url, audio_path)
            
            # Transcribe
            print(f"      Transcribing (this may take a while)...")
            result = self.whisper_model.transcribe(audio_path)
            
            # Clean up
            os.remove(audio_path)
            
            return result["text"]
        
        except Exception as e:
            print(f"      ⚠ Transcription error: {e}")
            return None
