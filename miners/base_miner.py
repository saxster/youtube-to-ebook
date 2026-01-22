"""
Base Miner interface for all content extractors.
"""

from abc import ABC, abstractmethod
from typing import List
from models import Evidence


class BaseMiner(ABC):
    """
    Abstract base class for all content miners.
    Each miner fetches content from a specific source and normalizes it into Evidence objects.
    """
    
    def __init__(self):
        """Initialize the miner."""
        self.name = self.__class__.__name__
    
    @abstractmethod
    def fetch(self, query: str) -> List[Evidence]:
        """
        Fetch content from the source based on a query.
        
        Args:
            query: The search query or source identifier (e.g., channel handle, URL, RSS feed URL)
        
        Returns:
            List of Evidence objects containing the fetched content
        """
        pass
    
    def validate_evidence(self, evidence: Evidence) -> bool:
        """
        Validate an Evidence object before returning it.
        
        Args:
            evidence: The Evidence object to validate
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required fields
            if not evidence.title or not evidence.source_url or not evidence.raw_content:
                return False
            
            # Check content length
            if len(evidence.raw_content) < 100:
                print(f"  ⚠ Warning: Content too short for '{evidence.title}'")
                return False
            
            return True
        except Exception as e:
            print(f"  ⚠ Validation error: {e}")
            return False
