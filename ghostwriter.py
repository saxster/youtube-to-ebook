"""
GhostWriter - Transform evidence into polished articles.
Enhanced to work with ContentBrain and multiple output formats.
"""

import os
from typing import List, Dict, Any, Optional
import anthropic
from dotenv import load_dotenv

from models import Evidence, SourceType


load_dotenv()


class GhostWriter:
    """
    Transform raw content from Evidence into polished, readable articles.
    Works with any source type from ContentBrain.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize the GhostWriter.
        
        Args:
            api_key: Anthropic API key (optional, will try to load from env)
            model: Claude model to use
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY in .env")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model
    
    def transform(self, evidence: Evidence) -> Optional[Dict[str, Any]]:
        """
        Transform a single Evidence object into a polished article.
        
        Args:
            evidence: The Evidence object to transform
        
        Returns:
            Dictionary with transformed article or None on failure
        """
        print(f"\n✍️  Writing article: {evidence.title[:50]}...")
        
        # Generate prompt based on source type
        prompt = self._create_prompt(evidence)
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            article_text = message.content[0].text
            
            print(f"  ✓ Article generated!")
            
            return {
                "title": evidence.title,
                "source_url": evidence.source_url,
                "source_type": evidence.source_type.value,
                "publisher": evidence.publisher,
                "author": evidence.author,
                "article": article_text,
                "metadata": evidence.metadata,
            }
        
        except Exception as e:
            print(f"  ✗ Error generating article: {e}")
            return None
    
    def transform_batch(self, evidence_list: List[Evidence]) -> List[Dict[str, Any]]:
        """
        Transform multiple Evidence objects into articles.
        
        Args:
            evidence_list: List of Evidence objects
        
        Returns:
            List of transformed articles
        """
        print(f"\n{'='*60}")
        print(f"  GHOSTWRITER: Transforming {len(evidence_list)} pieces of evidence")
        print(f"{'='*60}")
        
        articles = []
        
        for evidence in evidence_list:
            article = self.transform(evidence)
            
            if article:
                articles.append(article)
        
        print(f"\n{'='*60}")
        print(f"  Generated {len(articles)} articles")
        print(f"{'='*60}\n")
        
        return articles
    
    def _create_prompt(self, evidence: Evidence) -> str:
        """
        Create an appropriate prompt based on the evidence source type.
        
        Args:
            evidence: The Evidence object
        
        Returns:
            Prompt string for Claude
        """
        # Base instructions that apply to all types
        base_instructions = """You are a skilled magazine writer. Transform this content into a well-written, engaging article.

Guidelines:
- Start with an engaging headline (different from the original title)
- The audience is a curious individual who is generally smart but not a specialist or expert in the area
- Highly engaging and readable. Wherever jargon or obscure references appear, explain them
- Extremely well-written; think New Yorker or the Atlantic
- Capture the key insights, especially contrarian viewpoints, memorable anecdotes, and surprising insights
- There's no fixed length requirement; it depends on the original content and insight density
- Make your own judgment on what makes a satisfying long-read
- Write as a standalone article. Assume the reader has not seen the original source
- Format the article in clean markdown
"""
        
        # Source-specific instructions
        if evidence.source_type == SourceType.VIDEO:
            specific_instructions = f"""
SOURCE: Video from {evidence.publisher or 'a video platform'}
TITLE: {evidence.title}
URL: {evidence.source_url}

DESCRIPTION:
{evidence.description or 'N/A'}

TRANSCRIPT:
{evidence.raw_content}

---

Transform this video transcript into a magazine article.
- Use the video description to correct any transcription errors, especially names of people, companies, or technical terms
- Preserve key quotes (clean up filler words or transcription errors)
- Do NOT include phrases like "In this video" - write it as a standalone article
"""
        
        elif evidence.source_type == SourceType.ARTICLE:
            specific_instructions = f"""
SOURCE: Article from {evidence.publisher or 'a news website'}
TITLE: {evidence.title}
URL: {evidence.source_url}
AUTHOR: {evidence.author or 'Unknown'}

CONTENT:
{evidence.raw_content}

---

Transform this article into a polished magazine piece.
- Synthesize and restructure for better flow
- Maintain the author's voice and key insights
- Add explanations for technical terms or niche references
"""
        
        elif evidence.source_type == SourceType.PAPER:
            specific_instructions = f"""
SOURCE: Academic paper from {evidence.publisher or 'a research repository'}
TITLE: {evidence.title}
URL: {evidence.source_url}
AUTHOR: {evidence.author or 'Unknown'}

ABSTRACT:
{evidence.description or 'N/A'}

FULL TEXT:
{evidence.raw_content}

---

Transform this academic paper into an accessible magazine article.
- Explain technical concepts in plain language
- Focus on key findings, methodology, and implications
- Make it accessible to intelligent non-specialists
- Highlight practical applications and significance
"""
        
        elif evidence.source_type == SourceType.PODCAST:
            specific_instructions = f"""
SOURCE: Podcast episode from {evidence.publisher or 'a podcast'}
TITLE: {evidence.title}
URL: {evidence.source_url}
HOST/GUEST: {evidence.author or 'Unknown'}

DESCRIPTION:
{evidence.description or 'N/A'}

TRANSCRIPT:
{evidence.raw_content}

---

Transform this podcast transcript into a magazine article.
- Clean up conversational filler words
- Preserve the conversational tone where it adds value
- Capture key insights from the discussion
- Structure it for reading, not listening
"""
        
        elif evidence.source_type == SourceType.RSS:
            specific_instructions = f"""
SOURCE: RSS feed item from {evidence.publisher or 'a feed'}
TITLE: {evidence.title}
URL: {evidence.source_url}

CONTENT:
{evidence.raw_content}

---

Transform this feed content into a polished article.
- Expand and enhance where appropriate
- Ensure it reads as a complete, standalone piece
"""
        
        else:
            # Generic fallback
            specific_instructions = f"""
TITLE: {evidence.title}
SOURCE: {evidence.publisher or evidence.source_url}

CONTENT:
{evidence.raw_content}

---

Transform this content into a magazine-quality article.
"""
        
        return base_instructions + "\n" + specific_instructions
