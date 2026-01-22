"""
YouTube Miner - Extract content from YouTube videos.
Refactored from the original get_videos.py and get_transcripts.py.
"""

import os
import time
import requests
from typing import List, Optional
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

from models import Evidence, SourceType
from miners.base_miner import BaseMiner


# Load environment variables
load_dotenv()


class YouTubeMiner(BaseMiner):
    """
    Miner for extracting content from YouTube videos.
    Fetches videos from channels and extracts transcripts.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the YouTube miner.
        
        Args:
            api_key: YouTube Data API key (optional, will try to load from env)
        """
        super().__init__()
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        
        if not self.api_key:
            raise ValueError("YouTube API key is required. Set YOUTUBE_API_KEY in .env")
        
        self.youtube = build("youtube", "v3", developerKey=self.api_key)
    
    def fetch(self, query: str) -> List[Evidence]:
        """
        Fetch videos from a YouTube channel.
        
        Args:
            query: Channel handle (e.g., "@mkbhd") or comma-separated list of handles
        
        Returns:
            List of Evidence objects containing video transcripts
        """
        # Handle multiple channels
        channels = [ch.strip() for ch in query.split(',')]
        
        all_evidence = []
        
        for channel_handle in channels:
            print(f"\n📺 Fetching from YouTube channel: {channel_handle}")
            
            # Get channel info
            channel_info = self._get_channel_info(channel_handle)
            
            if not channel_info:
                print(f"  ✗ Channel not found: {channel_handle}")
                continue
            
            print(f"  Channel: {channel_info['channel_name']}")
            
            # Get latest video
            video_info = self._get_latest_video(
                channel_info["uploads_playlist_id"],
                channel_info["channel_name"]
            )
            
            if not video_info:
                print(f"  ✗ No long-form videos found")
                continue
            
            print(f"  ✓ Found: {video_info['title']}")
            
            # Get transcript
            transcript = self._get_transcript(video_info["video_id"])
            
            if not transcript:
                print(f"  ✗ No transcript available")
                continue
            
            word_count = len(transcript.split())
            print(f"  ✓ Got transcript ({word_count} words)")
            
            # Create Evidence object
            evidence = Evidence(
                title=video_info["title"],
                source_url=video_info["url"],
                raw_content=transcript,
                source_type=SourceType.VIDEO,
                description=video_info.get("description", ""),
                publisher=channel_info["channel_name"],
                metadata={
                    "video_id": video_info["video_id"],
                    "channel_id": channel_info["channel_id"],
                    "word_count": word_count,
                    "platform": "youtube"
                }
            )
            
            if self.validate_evidence(evidence):
                all_evidence.append(evidence)
        
        print(f"\n  → Collected {len(all_evidence)} videos with transcripts")
        return all_evidence
    
    def _get_channel_info(self, channel_handle: str) -> Optional[dict]:
        """
        Get channel information from a handle.
        
        Args:
            channel_handle: Channel handle (with or without @)
        
        Returns:
            Dictionary with channel info or None if not found
        """
        # Remove @ if present
        handle = channel_handle.lstrip("@")
        
        try:
            request = self.youtube.channels().list(
                part="snippet,contentDetails",
                forHandle=handle
            )
            response = request.execute()
            
            if response.get("items"):
                channel = response["items"][0]
                return {
                    "channel_id": channel["id"],
                    "channel_name": channel["snippet"]["title"],
                    "uploads_playlist_id": channel["contentDetails"]["relatedPlaylists"]["uploads"]
                }
        except Exception as e:
            print(f"  ⚠ Error fetching channel info: {e}")
        
        return None
    
    def _is_youtube_short(self, video_id: str) -> bool:
        """
        Check if a video is a YouTube Short.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            True if it's a Short, False otherwise
        """
        shorts_url = f"https://www.youtube.com/shorts/{video_id}"
        
        try:
            response = requests.head(shorts_url, allow_redirects=True, timeout=5)
            return "/shorts/" in response.url
        except:
            return False
    
    def _get_latest_video(self, uploads_playlist_id: str, channel_name: str) -> Optional[dict]:
        """
        Get the most recent long-form video from a channel.
        
        Args:
            uploads_playlist_id: YouTube playlist ID for channel uploads
            channel_name: Name of the channel
        
        Returns:
            Dictionary with video info or None if not found
        """
        try:
            request = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=15
            )
            response = request.execute()
            
            for item in response.get("items", []):
                video_id = item["snippet"]["resourceId"]["videoId"]
                
                # Skip Shorts
                if self._is_youtube_short(video_id):
                    continue
                
                return {
                    "title": item["snippet"]["title"],
                    "video_id": video_id,
                    "description": item["snippet"]["description"],
                    "channel": channel_name,
                    "url": f"https://www.youtube.com/watch?v={video_id}"
                }
        except Exception as e:
            print(f"  ⚠ Error fetching videos: {e}")
        
        return None
    
    def _get_transcript(self, video_id: str) -> Optional[str]:
        """
        Extract transcript from a YouTube video.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Full transcript text or None if unavailable
        """
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.fetch(video_id)
            
            # Combine all segments
            full_text = " ".join(segment.text for segment in transcript_list)
            return full_text.strip()
        except Exception as e:
            print(f"  ⚠ Error getting transcript: {e}")
            return None
