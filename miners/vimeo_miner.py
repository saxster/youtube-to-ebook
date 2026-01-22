"""
Vimeo Miner - Extract content from Vimeo videos.
"""

import os
import json
from typing import List, Optional
import urllib.request
import urllib.parse

from models import Evidence, SourceType
from miners.base_miner import BaseMiner


class VimeoMiner(BaseMiner):
    """
    Miner for extracting content from Vimeo videos.
    Uses Vimeo's oEmbed API for metadata.
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the Vimeo miner.
        
        Args:
            access_token: Vimeo API access token (optional)
        """
        super().__init__()
        self.access_token = access_token or os.getenv("VIMEO_ACCESS_TOKEN")
    
    def fetch(self, query: str) -> List[Evidence]:
        """
        Fetch videos from Vimeo.
        
        Args:
            query: Vimeo video URL or comma-separated list of URLs
        
        Returns:
            List of Evidence objects containing video metadata
        """
        # Handle multiple URLs
        urls = [url.strip() for url in query.split(',')]
        
        all_evidence = []
        
        for url in urls:
            print(f"\n🎬 Fetching Vimeo video: {url}")
            
            evidence = self._fetch_video(url)
            
            if evidence and self.validate_evidence(evidence):
                all_evidence.append(evidence)
                print(f"  ✓ Extracted: {evidence.title}")
            else:
                print(f"  ✗ Failed to extract video")
        
        print(f"\n  → Collected {len(all_evidence)} Vimeo videos")
        return all_evidence
    
    def _fetch_video(self, url: str) -> Optional[Evidence]:
        """
        Fetch video metadata from Vimeo.
        
        Args:
            url: Vimeo video URL
        
        Returns:
            Evidence object with video metadata
        """
        try:
            # Use oEmbed API for basic metadata
            oembed_url = f"https://vimeo.com/api/oembed.json?url={urllib.parse.quote(url)}"
            
            with urllib.request.urlopen(oembed_url) as response:
                data = json.loads(response.read())
            
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            
            # Try to get more details if we have an access token
            description = data.get('description', '')
            
            if self.access_token and video_id:
                details = self._fetch_video_details(video_id)
                if details:
                    description = details.get('description', description)
            
            # Use description as content (Vimeo doesn't have automatic transcripts)
            content = description if description else data.get('title', '')
            
            return Evidence(
                title=data.get('title', 'Untitled Vimeo Video'),
                source_url=url,
                raw_content=content,
                source_type=SourceType.VIDEO,
                description=description,
                author=data.get('author_name'),
                publisher="Vimeo",
                metadata={
                    "video_id": video_id,
                    "duration": data.get('duration', 0),
                    "thumbnail": data.get('thumbnail_url'),
                    "width": data.get('width'),
                    "height": data.get('height'),
                    "author_url": data.get('author_url'),
                    "platform": "vimeo",
                    "note": "Vimeo videos don't have automatic transcripts. Using description as content."
                }
            )
        
        except Exception as e:
            print(f"  ⚠ Error fetching Vimeo video: {e}")
            return None
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from Vimeo URL."""
        import re
        
        # Match patterns like vimeo.com/123456 or vimeo.com/channels/stuff/123456
        match = re.search(r'vimeo\.com/(?:channels/[^/]+/|groups/[^/]+/videos/|video/|)(\d+)', url)
        
        if match:
            return match.group(1)
        
        return None
    
    def _fetch_video_details(self, video_id: str) -> Optional[dict]:
        """
        Fetch detailed video information using Vimeo API.
        
        Args:
            video_id: Vimeo video ID
        
        Returns:
            Dictionary with video details
        """
        if not self.access_token:
            return None
        
        try:
            api_url = f"https://api.vimeo.com/videos/{video_id}"
            
            request = urllib.request.Request(api_url)
            request.add_header('Authorization', f'Bearer {self.access_token}')
            
            with urllib.request.urlopen(request) as response:
                return json.loads(response.read())
        
        except Exception as e:
            print(f"    ⚠ Error fetching video details: {e}")
            return None
