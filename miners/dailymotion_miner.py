"""
Dailymotion Miner - Extract content from Dailymotion videos.
"""

import os
import json
from typing import List, Optional
import urllib.request
import urllib.parse

from models import Evidence, SourceType
from miners.base_miner import BaseMiner


class DailymotionMiner(BaseMiner):
    """
    Miner for extracting content from Dailymotion videos.
    Uses Dailymotion's public API.
    """
    
    def __init__(self):
        """Initialize the Dailymotion miner."""
        super().__init__()
    
    def fetch(self, query: str) -> List[Evidence]:
        """
        Fetch videos from Dailymotion.
        
        Args:
            query: Dailymotion video URL or video ID, or comma-separated list
        
        Returns:
            List of Evidence objects containing video metadata
        """
        # Handle multiple inputs
        inputs = [inp.strip() for inp in query.split(',')]
        
        all_evidence = []
        
        for inp in inputs:
            print(f"\n📹 Fetching Dailymotion video: {inp}")
            
            # Extract video ID if URL provided
            video_id = self._extract_video_id(inp) if inp.startswith('http') else inp
            
            if not video_id:
                print(f"  ✗ Could not extract video ID")
                continue
            
            evidence = self._fetch_video(video_id)
            
            if evidence and self.validate_evidence(evidence):
                all_evidence.append(evidence)
                print(f"  ✓ Extracted: {evidence.title}")
            else:
                print(f"  ✗ Failed to extract video")
        
        print(f"\n  → Collected {len(all_evidence)} Dailymotion videos")
        return all_evidence
    
    def _fetch_video(self, video_id: str) -> Optional[Evidence]:
        """
        Fetch video metadata from Dailymotion.
        
        Args:
            video_id: Dailymotion video ID
        
        Returns:
            Evidence object with video metadata
        """
        try:
            # Dailymotion public API
            api_url = f"https://api.dailymotion.com/video/{video_id}"
            params = {
                'fields': 'title,description,duration,owner,owner.screenname,created_time,url,thumbnail_url,views_total,channel'
            }
            
            url = f"{api_url}?{urllib.parse.urlencode(params)}"
            
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
            
            # Use description as content (Dailymotion doesn't provide transcripts via API)
            content = data.get('description', data.get('title', ''))
            
            # Parse creation date
            from datetime import datetime
            date = None
            if data.get('created_time'):
                try:
                    date = datetime.fromtimestamp(data['created_time'])
                except:
                    pass
            
            return Evidence(
                title=data.get('title', 'Untitled Dailymotion Video'),
                source_url=data.get('url', f"https://www.dailymotion.com/video/{video_id}"),
                raw_content=content,
                source_type=SourceType.VIDEO,
                description=data.get('description'),
                author=data.get('owner.screenname'),
                date=date,
                publisher="Dailymotion",
                metadata={
                    "video_id": video_id,
                    "duration": data.get('duration', 0),
                    "thumbnail": data.get('thumbnail_url'),
                    "views": data.get('views_total', 0),
                    "channel": data.get('channel'),
                    "platform": "dailymotion",
                    "note": "Dailymotion videos don't have automatic transcripts via API. Using description as content."
                }
            )
        
        except Exception as e:
            print(f"  ⚠ Error fetching Dailymotion video: {e}")
            return None
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from Dailymotion URL."""
        import re
        
        # Match patterns like dailymotion.com/video/x8abcde
        match = re.search(r'dailymotion\.com/video/([a-zA-Z0-9]+)', url)
        
        if match:
            return match.group(1)
        
        # Also try dai.ly short URLs
        match = re.search(r'dai\.ly/([a-zA-Z0-9]+)', url)
        
        if match:
            return match.group(1)
        
        return None
