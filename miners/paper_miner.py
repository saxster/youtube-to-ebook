"""
Paper Miner - Extract content from academic papers (arXiv, PDFs).
"""

import os
from typing import List, Optional
from datetime import datetime
import urllib.request
import urllib.parse

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import arxiv
    ARXIV_AVAILABLE = True
except ImportError:
    ARXIV_AVAILABLE = False

from models import Evidence, SourceType
from miners.base_miner import BaseMiner


class PaperMiner(BaseMiner):
    """
    Miner for extracting content from academic papers.
    Supports arXiv API and direct PDF parsing.
    """
    
    def __init__(self):
        """Initialize the Paper miner."""
        super().__init__()
        
        if not ARXIV_AVAILABLE:
            print("  ⚠ arxiv package not available. Install with: pip install arxiv")
        
        if not PYPDF2_AVAILABLE:
            print("  ⚠ PyPDF2 not available. Install with: pip install PyPDF2")
    
    def fetch(self, query: str, max_results: int = 5) -> List[Evidence]:
        """
        Fetch academic papers.
        
        Args:
            query: arXiv query, arXiv ID, PDF URL, or local PDF path
            max_results: Maximum number of results for searches
        
        Returns:
            List of Evidence objects containing paper content
        """
        all_evidence = []
        
        # Detect query type
        if query.startswith("http") and query.endswith(".pdf"):
            # PDF URL
            print(f"\n📄 Fetching PDF from URL: {query}")
            evidence = self._fetch_pdf_from_url(query)
            if evidence and self.validate_evidence(evidence):
                all_evidence.append(evidence)
        
        elif os.path.isfile(query) and query.endswith(".pdf"):
            # Local PDF file
            print(f"\n📄 Reading local PDF: {query}")
            evidence = self._fetch_local_pdf(query)
            if evidence and self.validate_evidence(evidence):
                all_evidence.append(evidence)
        
        elif query.startswith("arxiv:") or "/" in query and any(c.isdigit() for c in query):
            # arXiv ID (e.g., "2301.00001" or "arxiv:2301.00001")
            arxiv_id = query.replace("arxiv:", "").strip()
            print(f"\n📚 Fetching arXiv paper: {arxiv_id}")
            evidence = self._fetch_arxiv_by_id(arxiv_id)
            if evidence and self.validate_evidence(evidence):
                all_evidence.append(evidence)
        
        else:
            # arXiv search query
            print(f"\n🔍 Searching arXiv for: {query}")
            all_evidence = self._search_arxiv(query, max_results)
        
        print(f"\n  → Collected {len(all_evidence)} papers")
        return all_evidence
    
    def _search_arxiv(self, query: str, max_results: int) -> List[Evidence]:
        """Search arXiv and return papers."""
        if not ARXIV_AVAILABLE:
            print("  ✗ arxiv package required for searches")
            return []
        
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            evidence_list = []
            
            for i, result in enumerate(search.results()):
                print(f"  {i+1}. {result.title}")
                
                # Download PDF and extract text
                pdf_path = f"/tmp/arxiv_{result.entry_id.split('/')[-1]}.pdf"
                result.download_pdf(filename=pdf_path)
                
                # Extract text from PDF
                content = self._extract_text_from_pdf(pdf_path)
                
                # Clean up
                os.remove(pdf_path)
                
                if content:
                    evidence = Evidence(
                        title=result.title,
                        source_url=result.entry_id,
                        raw_content=content,
                        source_type=SourceType.PAPER,
                        description=result.summary,
                        author=", ".join(author.name for author in result.authors),
                        date=result.published,
                        publisher="arXiv",
                        metadata={
                            "word_count": len(content.split()),
                            "arxiv_id": result.entry_id.split('/')[-1],
                            "categories": result.categories,
                            "pdf_url": result.pdf_url,
                            "doi": result.doi if result.doi else None,
                        }
                    )
                    
                    if self.validate_evidence(evidence):
                        evidence_list.append(evidence)
            
            return evidence_list
        
        except Exception as e:
            print(f"  ✗ Error searching arXiv: {e}")
            return []
    
    def _fetch_arxiv_by_id(self, arxiv_id: str) -> Optional[Evidence]:
        """Fetch a specific arXiv paper by ID."""
        if not ARXIV_AVAILABLE:
            print("  ✗ arxiv package required")
            return None
        
        try:
            search = arxiv.Search(id_list=[arxiv_id])
            result = next(search.results())
            
            # Download PDF
            pdf_path = f"/tmp/arxiv_{arxiv_id}.pdf"
            result.download_pdf(filename=pdf_path)
            
            # Extract text
            content = self._extract_text_from_pdf(pdf_path)
            
            # Clean up
            os.remove(pdf_path)
            
            if not content:
                return None
            
            print(f"  ✓ Extracted {len(content.split())} words")
            
            return Evidence(
                title=result.title,
                source_url=result.entry_id,
                raw_content=content,
                source_type=SourceType.PAPER,
                description=result.summary,
                author=", ".join(author.name for author in result.authors),
                date=result.published,
                publisher="arXiv",
                metadata={
                    "word_count": len(content.split()),
                    "arxiv_id": arxiv_id,
                    "categories": result.categories,
                    "pdf_url": result.pdf_url,
                }
            )
        
        except Exception as e:
            print(f"  ✗ Error fetching arXiv paper: {e}")
            return None
    
    def _fetch_pdf_from_url(self, url: str) -> Optional[Evidence]:
        """Download and parse a PDF from URL."""
        try:
            # Download PDF
            pdf_path = "/tmp/downloaded_paper.pdf"
            urllib.request.urlretrieve(url, pdf_path)
            
            # Extract text
            content = self._extract_text_from_pdf(pdf_path)
            
            # Clean up
            os.remove(pdf_path)
            
            if not content:
                return None
            
            print(f"  ✓ Extracted {len(content.split())} words")
            
            return Evidence(
                title=os.path.basename(url).replace('.pdf', ''),
                source_url=url,
                raw_content=content,
                source_type=SourceType.PAPER,
                publisher="PDF",
                metadata={
                    "word_count": len(content.split()),
                    "source": "pdf_url",
                }
            )
        
        except Exception as e:
            print(f"  ✗ Error fetching PDF: {e}")
            return None
    
    def _fetch_local_pdf(self, filepath: str) -> Optional[Evidence]:
        """Parse a local PDF file."""
        try:
            content = self._extract_text_from_pdf(filepath)
            
            if not content:
                return None
            
            print(f"  ✓ Extracted {len(content.split())} words")
            
            return Evidence(
                title=os.path.basename(filepath).replace('.pdf', ''),
                source_url=f"file://{os.path.abspath(filepath)}",
                raw_content=content,
                source_type=SourceType.PAPER,
                publisher="Local PDF",
                metadata={
                    "word_count": len(content.split()),
                    "source": "local_file",
                    "filepath": filepath,
                }
            )
        
        except Exception as e:
            print(f"  ✗ Error reading PDF: {e}")
            return None
    
    def _extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """Extract text content from a PDF file."""
        if not PYPDF2_AVAILABLE:
            print("  ✗ PyPDF2 required for PDF parsing")
            return None
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return text.strip()
        
        except Exception as e:
            print(f"  ✗ Error extracting text from PDF: {e}")
            return None
