"""
Unit tests for ContentBrain.
"""

import pytest
from content_brain import ContentBrain
from models import Evidence, SourceType


@pytest.fixture
def sample_evidence():
    """Create sample evidence for testing."""
    return Evidence(
        title="Sample Article",
        source_url="https://example.com/article",
        raw_content="This is sample content. " * 20,
        source_type=SourceType.ARTICLE,
        publisher="Example Publisher"
    )


@pytest.fixture
def content_brain():
    """Create a fresh ContentBrain instance."""
    return ContentBrain()


def test_content_brain_initialization(content_brain):
    """Test ContentBrain initialization."""
    assert len(content_brain.evidence_pool) == 0
    assert content_brain.metadata["total_evidence"] == 0


def test_add_evidence(content_brain, sample_evidence):
    """Test adding single evidence."""
    content_brain.add_evidence(sample_evidence)
    
    assert len(content_brain.evidence_pool) == 1
    assert content_brain.metadata["total_evidence"] == 1


def test_add_evidence_batch(content_brain):
    """Test adding multiple evidence items."""
    evidence_list = [
        Evidence(
            title=f"Article {i}",
            source_url=f"https://example.com/{i}",
            raw_content="Content " * 20,
            source_type=SourceType.ARTICLE
        )
        for i in range(5)
    ]
    
    content_brain.add_evidence_batch(evidence_list)
    
    assert len(content_brain.evidence_pool) == 5
    assert content_brain.metadata["total_evidence"] == 5


def test_get_by_source_type(content_brain):
    """Test filtering evidence by source type."""
    # Add different types
    content_brain.add_evidence(Evidence(
        title="Video",
        source_url="https://youtube.com/watch?v=test",
        raw_content="Video transcript " * 20,
        source_type=SourceType.VIDEO
    ))
    
    content_brain.add_evidence(Evidence(
        title="Article",
        source_url="https://example.com/article",
        raw_content="Article content " * 20,
        source_type=SourceType.ARTICLE
    ))
    
    videos = content_brain.get_by_source_type(SourceType.VIDEO)
    articles = content_brain.get_by_source_type(SourceType.ARTICLE)
    
    assert len(videos) == 1
    assert len(articles) == 1
    assert videos[0].source_type == SourceType.VIDEO


def test_get_by_publisher(content_brain):
    """Test filtering evidence by publisher."""
    content_brain.add_evidence(Evidence(
        title="Article 1",
        source_url="https://example.com/1",
        raw_content="Content " * 20,
        source_type=SourceType.ARTICLE,
        publisher="Publisher A"
    ))
    
    content_brain.add_evidence(Evidence(
        title="Article 2",
        source_url="https://example.com/2",
        raw_content="Content " * 20,
        source_type=SourceType.ARTICLE,
        publisher="Publisher B"
    ))
    
    publisher_a_items = content_brain.get_by_publisher("Publisher A")
    
    assert len(publisher_a_items) == 1
    assert publisher_a_items[0].publisher == "Publisher A"


def test_clear(content_brain, sample_evidence):
    """Test clearing evidence pool."""
    content_brain.add_evidence(sample_evidence)
    assert len(content_brain.evidence_pool) == 1
    
    content_brain.clear()
    assert len(content_brain.evidence_pool) == 0
    assert content_brain.metadata["total_evidence"] == 0


def test_get_stats(content_brain):
    """Test getting statistics."""
    content_brain.add_evidence(Evidence(
        title="Video",
        source_url="https://youtube.com/watch?v=test",
        raw_content="Content " * 20,
        source_type=SourceType.VIDEO,
        publisher="YouTube Channel"
    ))
    
    content_brain.add_evidence(Evidence(
        title="Article",
        source_url="https://example.com/article",
        raw_content="Content " * 20,
        source_type=SourceType.ARTICLE,
        publisher="News Site"
    ))
    
    stats = content_brain.get_stats()
    
    assert stats["total_evidence"] == 2
    assert stats["sources"] == 2
    assert "video" in stats["by_source_type"]
    assert "article" in stats["by_source_type"]
