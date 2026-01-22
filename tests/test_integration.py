"""
Integration tests for the full Content Funnel pipeline.
"""

import pytest
from unittest.mock import Mock, patch
from models import Evidence, SourceType
from content_brain import ContentBrain
from ghostwriter import GhostWriter


@pytest.fixture
def mock_evidence_list():
    """Create a list of mock evidence for testing."""
    return [
        Evidence(
            title="Test Video",
            source_url="https://youtube.com/watch?v=test",
            raw_content="Video transcript content. " * 50,
            source_type=SourceType.VIDEO,
            publisher="Test Channel"
        ),
        Evidence(
            title="Test Article",
            source_url="https://example.com/article",
            raw_content="Article content goes here. " * 50,
            source_type=SourceType.ARTICLE,
            publisher="Test Publisher"
        )
    ]


def test_content_brain_integration(mock_evidence_list):
    """Test ContentBrain with multiple evidence types."""
    brain = ContentBrain()
    
    # Add evidence
    brain.add_evidence_batch(mock_evidence_list)
    
    # Verify evidence was added
    assert len(brain.evidence_pool) == 2
    
    # Test filtering
    videos = brain.get_by_source_type(SourceType.VIDEO)
    articles = brain.get_by_source_type(SourceType.ARTICLE)
    
    assert len(videos) == 1
    assert len(articles) == 1
    
    # Test stats
    stats = brain.get_stats()
    assert stats["total_evidence"] == 2
    assert stats["by_source_type"]["video"] == 1
    assert stats["by_source_type"]["article"] == 1


def test_ghostwriter_transform_mock(mock_evidence_list):
    """Test GhostWriter with mocked API calls."""
    # Mock the Anthropic API
    with patch('anthropic.Anthropic') as mock_anthropic:
        # Setup mock response
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock(text="# Transformed Article\n\nThis is the transformed content.")]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client
        
        # Create GhostWriter with mocked client
        ghostwriter = GhostWriter(api_key="test_key")
        ghostwriter.client = mock_client
        
        # Transform evidence
        result = ghostwriter.transform(mock_evidence_list[0])
        
        # Verify result
        assert result is not None
        assert "article" in result
        assert result["title"] == "Test Video"
        assert result["source_type"] == "video"


def test_pipeline_integration_mock():
    """Test the full pipeline with mocked components."""
    # Create ContentBrain
    brain = ContentBrain()
    
    # Add mock evidence
    evidence = Evidence(
        title="Integration Test",
        source_url="https://example.com/test",
        raw_content="Integration test content. " * 50,
        source_type=SourceType.ARTICLE,
        publisher="Test Source"
    )
    brain.add_evidence(evidence)
    
    # Verify evidence is in brain
    assert len(brain.evidence_pool) == 1
    
    # Mock GhostWriter transformation
    with patch('anthropic.Anthropic') as mock_anthropic:
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock(text="# Test Article\n\nTransformed content.")]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client
        
        ghostwriter = GhostWriter(api_key="test_key")
        ghostwriter.client = mock_client
        
        articles = ghostwriter.transform_batch(brain.evidence_pool)
        
        # Verify articles were created
        assert len(articles) == 1
        assert articles[0]["title"] == "Integration Test"
