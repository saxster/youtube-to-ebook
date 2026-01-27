# Content Funnel Pipeline - Enhanced Features

This document describes the new modular Content Funnel pipeline that extends the original YouTube-to-ebook functionality.

## 🎯 Overview

The Content Funnel pipeline is a sophisticated, modular system for aggregating content from multiple sources, transforming it into polished articles, and creating beautiful ebooks. It maintains backward compatibility with the original YouTube-only functionality while adding support for many new content sources.

## ✨ New Features

### Multiple Content Sources

The pipeline now supports:

1. **YouTube Videos** - Original functionality, enhanced with modular design
2. **Vimeo & Dailymotion** - Additional video platforms
3. **Web Articles** - Using newspaper3k and trafilatura for robust extraction
4. **RSS Feeds** - Aggregate content from any RSS feed
5. **Research Papers** - arXiv API integration and PDF parsing
6. **Podcasts** - RSS-based with optional Whisper transcription

### Modular Architecture

```
Content Sources → Miners → ContentBrain → GhostWriter → Output Formats
```

- **Miners**: Pluggable content extractors (BaseMiner interface)
- **Evidence**: Unified data model for all content types
- **ContentBrain**: Central repository for aggregated content
- **GhostWriter**: AI-powered content transformation
- **Output**: Multiple format support (EPUB, with more coming)

### Enhanced UI/UX

- **Interactive CLI**: Built with Rich library for beautiful terminal interfaces
- **Progress Indicators**: Real-time feedback on long-running operations
- **Better Error Handling**: Detailed logging and error messages
- **Legacy Mode**: Full backward compatibility with original pipeline

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/saxster/youtube-to-ebook.git
cd youtube-to-ebook

# Install dependencies
pip install -r requirements.txt

# Set up API keys
cp .env.example .env
# Edit .env with your API keys
```

### Basic Usage

#### Interactive CLI (Recommended)

```bash
python main_pipeline.py --cli
```

This launches an interactive menu where you can:
1. Select content sources
2. Add content from various platforms
3. Generate articles with AI
4. Create ebooks

#### Legacy Mode (YouTube Only)

```bash
python main_pipeline.py --legacy
```

Runs the original YouTube-to-ebook pipeline with backward compatibility.

#### Programmatic Usage

```python
from main_pipeline import run_pipeline

# Define your content sources
sources = {
    "youtube": "@mkbhd,@veritasium",
    "article": "https://example.com/article1,https://example.com/article2",
    "rss": "https://example.com/feed.xml",
    "paper": "machine learning transformers"  # arXiv search
}

# Run the pipeline
output_file = run_pipeline(sources, output_format="epub")
print(f"Created: {output_file}")
```

## 📚 Content Source Examples

### YouTube

```python
from miners import YouTubeMiner

miner = YouTubeMiner()
evidence = miner.fetch("@mkbhd,@veritasium")  # Multiple channels
```

### Web Articles

```python
from miners import ArticleMiner

miner = ArticleMiner()
evidence = miner.fetch("https://example.com/article1,https://example.com/article2")
```

### RSS Feeds

```python
from miners import RSSMiner

miner = RSSMiner(fetch_full_content=True)  # Fetches full articles, not just RSS descriptions
evidence = miner.fetch("https://example.com/feed.xml")
```

### Research Papers

```python
from miners import PaperMiner

miner = PaperMiner()

# Search arXiv
evidence = miner.fetch("machine learning", max_results=5)

# Specific arXiv paper
evidence = miner.fetch("arxiv:2301.00001")

# Local PDF
evidence = miner.fetch("/path/to/paper.pdf")

# PDF URL
evidence = miner.fetch("https://example.com/paper.pdf")
```

### Podcasts

```python
from miners import PodcastMiner

# Note: Whisper transcription requires significant compute
miner = PodcastMiner(model_size="base")  # Options: tiny, base, small, medium, large
evidence = miner.fetch("https://example.com/podcast/feed.xml", max_episodes=3)
```

### Vimeo & Dailymotion

```python
from miners import VimeoMiner, DailymotionMiner

vimeo = VimeoMiner()
evidence = vimeo.fetch("https://vimeo.com/123456789")

daily = DailymotionMiner()
evidence = daily.fetch("https://www.dailymotion.com/video/x8abcde")
```

## 🧪 Testing

The project includes comprehensive tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run integration tests
pytest tests/test_integration.py
```

Test categories:
- **Unit Tests**: Individual components (models, miners, brain)
- **Integration Tests**: Full pipeline workflows
- **Performance Tests**: (Coming soon) Load and stress testing

## 🏗️ Architecture

### Data Flow

1. **Input**: Users specify content sources (URLs, channels, queries)
2. **Mining**: Appropriate miners fetch and normalize content into Evidence objects
3. **Aggregation**: ContentBrain collects all Evidence in a unified pool
4. **Transformation**: GhostWriter uses Claude AI to transform content into articles
5. **Output**: Articles are formatted into ebooks (EPUB, PDF, etc.)

### Key Components

#### Evidence Model

```python
@dataclass
class Evidence:
    title: str
    source_url: str
    raw_content: str
    source_type: SourceType
    metadata: Dict[str, Any]
    description: Optional[str]
    author: Optional[str]
    date: Optional[datetime]
    publisher: Optional[str]
```

#### BaseMiner Interface

```python
class BaseMiner(ABC):
    @abstractmethod
    def fetch(self, query: str) -> List[Evidence]:
        pass
```

All miners implement this interface, ensuring consistency.

#### ContentBrain

```python
brain = ContentBrain()
brain.add_evidence(evidence)
brain.add_evidence_batch(evidence_list)
stats = brain.get_stats()
videos = brain.get_by_source_type(SourceType.VIDEO)
```

## 📝 API Keys Required

- **YouTube Data API**: Required for YouTube miner
- **Anthropic API**: Required for article generation (Claude)
- **Vimeo API** (Optional): For enhanced Vimeo metadata
- **Gmail** (Optional): For email delivery

All keys are configured in `.env` file (see `.env.example`).

## 🔧 Advanced Configuration

### Custom Miners

Create your own miner by extending BaseMiner:

```python
from miners.base_miner import BaseMiner
from models import Evidence, SourceType

class CustomMiner(BaseMiner):
    def fetch(self, query: str) -> List[Evidence]:
        # Your custom logic here
        evidence = Evidence(
            title="Custom Content",
            source_url="https://example.com",
            raw_content="Content here",
            source_type=SourceType.ARTICLE
        )
        return [evidence]
```

### Custom Output Formats

The system is designed to support multiple output formats. Currently EPUB is implemented, but the architecture supports adding PDF, HTML, Audiobook, and more.

## 🐛 Troubleshooting

### Dependency Issues

Some optional dependencies may not install on all systems:

- `openai-whisper`: Requires FFmpeg and can be resource-intensive
- `newspaper3k`: May have conflicts with some Python versions
- `trafilatura`: Alternative to newspaper3k if issues arise

You can use the system without these optional dependencies - the relevant features will be disabled gracefully.

### API Rate Limits

- YouTube API: 10,000 units/day (free tier)
- Anthropic API: Pay-per-use, monitor usage in console
- arXiv: No authentication required, but respect rate limits

## 📄 License

MIT - See LICENSE file for details.

## 🤝 Contributing

Contributions welcome! The modular design makes it easy to add new miners for additional content sources.

### Adding a New Miner

1. Create a new file in `miners/` directory
2. Extend `BaseMiner` class
3. Implement the `fetch()` method
4. Return a list of `Evidence` objects
5. Add to `miners/__init__.py`
6. Write tests in `tests/`

## 🔮 Future Enhancements

- [ ] Web dashboard (Flask/Django)
- [ ] PDF output format
- [ ] Audiobook generation
- [ ] Database persistence
- [ ] Batch processing improvements
- [ ] More video platforms (Twitch, etc.)
- [ ] Social media sources (Twitter threads, LinkedIn posts)
- [ ] Performance optimizations
