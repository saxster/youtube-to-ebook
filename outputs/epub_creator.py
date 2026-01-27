"""
EPUB Creator - Create EPUB ebooks from articles.
Enhanced version that works with the new article format.
"""

import os
import markdown
from datetime import datetime
from typing import List, Dict, Any
from ebooklib import epub


def create_epub_from_articles(articles: List[Dict[str, Any]], output_dir: str = None) -> str:
    """
    Create an EPUB ebook from articles.
    
    Args:
        articles: List of article dictionaries
        output_dir: Directory to save the ebook (default: current directory)
    
    Returns:
        Path to the created EPUB file
    """
    if not articles:
        raise ValueError("No articles provided")
    
    today = datetime.now().strftime("%B %d, %Y")
    filename = f"content_digest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.epub"
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
    else:
        filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    
    # Create the ebook
    book = epub.EpubBook()
    
    # Set metadata
    book.set_identifier(f"content-digest-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    book.set_title(f"Content Digest - {today}")
    book.set_language("en")
    book.add_author("Content Funnel Pipeline")
    
    # CSS for nice formatting
    style = """
    body {
        font-family: Georgia, serif;
        line-height: 1.6;
        padding: 1em;
    }
    h1 {
        font-size: 1.5em;
        margin-top: 1em;
        border-bottom: 1px solid #ccc;
        padding-bottom: 0.3em;
    }
    h2 {
        font-size: 1.3em;
        margin-top: 1em;
    }
    h3 {
        font-size: 1.1em;
    }
    .intro {
        background: #f5f5f5;
        padding: 1em;
        border-left: 3px solid #666;
        margin-bottom: 1.5em;
        font-size: 0.95em;
    }
    .source-link {
        margin-top: 1.5em;
        padding: 0.5em;
        background: #f0f0f0;
        display: block;
    }
    blockquote {
        border-left: 3px solid #ccc;
        padding-left: 1em;
        margin-left: 0;
        font-style: italic;
        color: #555;
    }
    code {
        background: #f4f4f4;
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-family: monospace;
    }
    """
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style
    )
    book.add_item(nav_css)
    
    chapters = []
    
    # Create a chapter for each article
    for i, article in enumerate(articles):
        # Convert markdown to HTML
        article_html = markdown.markdown(
            article['article'],
            extensions=['extra', 'codehilite']
        )
        
        # Get source info
        source_type = article.get('source_type', 'unknown')
        publisher = article.get('publisher', 'Unknown Source')
        author = article.get('author')
        
        # Build intro text
        intro_parts = [f"<em>This article is based on content from <strong>{publisher}</strong>"]
        if author:
            intro_parts.append(f" by <strong>{author}</strong>")
        intro_parts.append(f" ({source_type}).</em>")
        intro_text = "".join(intro_parts)
        
        chapter_content = f"""
        <html>
        <head>
            <link rel="stylesheet" type="text/css" href="style/nav.css"/>
        </head>
        <body>
            <div class="intro">
                <p>{intro_text}</p>
            </div>
            {article_html}
            <p class="source-link">Source: <a href="{article['source_url']}">{article['source_url']}</a></p>
        </body>
        </html>
        """
        
        chapter = epub.EpubHtml(
            title=article['title'][:50],
            file_name=f"chapter_{i+1}.xhtml",
            lang="en"
        )
        chapter.content = chapter_content
        chapter.add_item(nav_css)
        
        book.add_item(chapter)
        chapters.append(chapter)
    
    # Create table of contents
    book.toc = tuple(chapters)
    
    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Set the reading order
    book.spine = ["nav"] + chapters
    
    # Write the EPUB file
    epub.write_epub(filepath, book)
    
    print(f"\n  ✓ Created EPUB: {filename}")
    print(f"     Location: {filepath}")
    
    return filepath


if __name__ == "__main__":
    # Test with mock articles
    test_articles = [
        {
            "title": "Test Article",
            "source_url": "https://example.com",
            "source_type": "article",
            "publisher": "Example Publisher",
            "author": "John Doe",
            "article": "# Test Headline\n\nThis is a test article with **bold** and *italic* text.\n\n## Section 1\n\nSome content here."
        }
    ]
    
    filepath = create_epub_from_articles(test_articles)
    print(f"Test ebook created: {filepath}")
