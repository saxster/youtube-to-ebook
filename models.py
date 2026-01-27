"""
Data models for the Content Funnel pipeline.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class SourceType(Enum):
    """Types of content sources."""
    VIDEO = "video"
    ARTICLE = "article"
    PAPER = "paper"
    PODCAST = "podcast"
    RSS = "rss"


@dataclass
class Evidence:
    """
    Unified data structure for all content sources.
    All miners normalize their data into this schema.
    """
    title: str
    source_url: str
    raw_content: str
    source_type: SourceType
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Optional fields
    description: Optional[str] = None
    author: Optional[str] = None
    date: Optional[datetime] = None
    publisher: Optional[str] = None
    
    def __post_init__(self):
        """Validate and normalize data after initialization."""
        if not self.title:
            raise ValueError("Evidence must have a title")
        if not self.source_url:
            raise ValueError("Evidence must have a source_url")
        if not self.raw_content:
            raise ValueError("Evidence must have raw_content")
        
        # Ensure source_type is a SourceType enum
        if isinstance(self.source_type, str):
            self.source_type = SourceType(self.source_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Evidence to dictionary."""
        return {
            "title": self.title,
            "source_url": self.source_url,
            "raw_content": self.raw_content,
            "source_type": self.source_type.value,
            "metadata": self.metadata,
            "description": self.description,
            "author": self.author,
            "date": self.date.isoformat() if self.date else None,
            "publisher": self.publisher,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Evidence':
        """Create Evidence from dictionary."""
        # Convert date string back to datetime if present
        if data.get("date") and isinstance(data["date"], str):
            data["date"] = datetime.fromisoformat(data["date"])
        
        return cls(**data)
