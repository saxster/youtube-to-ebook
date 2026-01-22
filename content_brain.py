"""
ContentBrain - Unified Evidence Pool
Aggregates content from all miners for processing.
"""

from typing import List, Dict, Any
from models import Evidence, SourceType
import json
import os
from datetime import datetime


class ContentBrain:
    """
    Central repository for all evidence collected from various sources.
    Manages the unified evidence pool and provides methods for filtering and retrieval.
    """
    
    def __init__(self):
        """Initialize the ContentBrain with an empty evidence pool."""
        self.evidence_pool: List[Evidence] = []
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now().isoformat(),
            "total_evidence": 0,
            "by_source_type": {},
        }
    
    def add_evidence(self, evidence: Evidence) -> None:
        """
        Add a single Evidence object to the pool.
        
        Args:
            evidence: The Evidence object to add
        """
        self.evidence_pool.append(evidence)
        self._update_metadata()
    
    def add_evidence_batch(self, evidence_list: List[Evidence]) -> None:
        """
        Add multiple Evidence objects to the pool.
        
        Args:
            evidence_list: List of Evidence objects to add
        """
        self.evidence_pool.extend(evidence_list)
        self._update_metadata()
    
    def get_all_evidence(self) -> List[Evidence]:
        """Get all evidence from the pool."""
        return self.evidence_pool
    
    def get_by_source_type(self, source_type: SourceType) -> List[Evidence]:
        """
        Get all evidence of a specific source type.
        
        Args:
            source_type: The SourceType to filter by
        
        Returns:
            List of Evidence objects matching the source type
        """
        return [e for e in self.evidence_pool if e.source_type == source_type]
    
    def get_by_publisher(self, publisher: str) -> List[Evidence]:
        """
        Get all evidence from a specific publisher/channel.
        
        Args:
            publisher: The publisher/channel name to filter by
        
        Returns:
            List of Evidence objects from that publisher
        """
        return [e for e in self.evidence_pool if e.publisher == publisher]
    
    def clear(self) -> None:
        """Clear all evidence from the pool."""
        self.evidence_pool = []
        self._update_metadata()
    
    def _update_metadata(self) -> None:
        """Update metadata about the evidence pool."""
        self.metadata["total_evidence"] = len(self.evidence_pool)
        self.metadata["updated_at"] = datetime.now().isoformat()
        
        # Count by source type
        by_type = {}
        for evidence in self.evidence_pool:
            type_name = evidence.source_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
        
        self.metadata["by_source_type"] = by_type
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the evidence pool."""
        return {
            "total_evidence": len(self.evidence_pool),
            "by_source_type": self.metadata.get("by_source_type", {}),
            "sources": len(set(e.publisher for e in self.evidence_pool if e.publisher)),
        }
    
    def save_to_file(self, filepath: str) -> None:
        """
        Save the evidence pool to a JSON file.
        
        Args:
            filepath: Path to save the file
        """
        data = {
            "metadata": self.metadata,
            "evidence": [e.to_dict() for e in self.evidence_pool]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"  ✓ Saved {len(self.evidence_pool)} evidence items to {filepath}")
    
    def load_from_file(self, filepath: str) -> None:
        """
        Load evidence pool from a JSON file.
        
        Args:
            filepath: Path to load from
        """
        if not os.path.exists(filepath):
            print(f"  ⚠ File not found: {filepath}")
            return
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.metadata = data.get("metadata", {})
        self.evidence_pool = [Evidence.from_dict(e) for e in data.get("evidence", [])]
        
        print(f"  ✓ Loaded {len(self.evidence_pool)} evidence items from {filepath}")
