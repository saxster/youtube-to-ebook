"""
Unit tests for the Evidence data model.
"""

import pytest
from datetime import datetime
from models import Evidence, SourceType


def test_evidence_creation():
    """Test basic Evidence object creation."""
    evidence = Evidence(
        title="Test Title",
        source_url="https://example.com",
        raw_content="This is test content with enough words to pass validation.",
        source_type=SourceType.ARTICLE
    )
    
    assert evidence.title == "Test Title"
    assert evidence.source_url == "https://example.com"
    assert evidence.source_type == SourceType.ARTICLE


def test_evidence_with_metadata():
    """Test Evidence with metadata."""
    evidence = Evidence(
        title="Test",
        source_url="https://example.com",
        raw_content="Test content " * 20,
        source_type=SourceType.VIDEO,
        metadata={"video_id": "12345", "duration": 300}
    )
    
    assert evidence.metadata["video_id"] == "12345"
    assert evidence.metadata["duration"] == 300


def test_evidence_validation():
    """Test Evidence validation."""
    with pytest.raises(ValueError):
        Evidence(
            title="",  # Empty title should fail
            source_url="https://example.com",
            raw_content="Content",
            source_type=SourceType.ARTICLE
        )


def test_evidence_to_dict():
    """Test Evidence serialization to dictionary."""
    evidence = Evidence(
        title="Test",
        source_url="https://example.com",
        raw_content="Content " * 20,
        source_type=SourceType.PAPER,
        author="John Doe"
    )
    
    data = evidence.to_dict()
    
    assert data["title"] == "Test"
    assert data["source_type"] == "paper"
    assert data["author"] == "John Doe"


def test_evidence_from_dict():
    """Test Evidence deserialization from dictionary."""
    data = {
        "title": "Test",
        "source_url": "https://example.com",
        "raw_content": "Content " * 20,
        "source_type": "article",
        "metadata": {},
        "description": None,
        "author": "Jane Doe",
        "date": None,
        "publisher": "Test Publisher"
    }
    
    evidence = Evidence.from_dict(data)
    
    assert evidence.title == "Test"
    assert evidence.source_type == SourceType.ARTICLE
    assert evidence.author == "Jane Doe"


def test_source_type_enum():
    """Test SourceType enum values."""
    assert SourceType.VIDEO.value == "video"
    assert SourceType.ARTICLE.value == "article"
    assert SourceType.PAPER.value == "paper"
    assert SourceType.PODCAST.value == "podcast"
    assert SourceType.RSS.value == "rss"
