# Content Funnel - Multi-Source Content Aggregator

Transform content from **YouTube, articles, podcasts, research papers, and more** into beautifully formatted EPUB ebooks.

> **🆕 New!** This project has been enhanced with a modular Content Funnel pipeline that supports multiple content sources beyond just YouTube. See [CONTENT_FUNNEL.md](CONTENT_FUNNEL.md) for details.

## ✨ Features

### Original YouTube Features
- Fetches latest videos from YouTube channels (automatically filters out Shorts)
- Extracts transcripts from videos
- Uses Claude AI to transform transcripts into polished magazine-style articles
- Generates EPUB ebooks readable on any device
- Optional: Email delivery with ebook attachment
- Optional: Web dashboard for easy management

### 🆕 New Content Funnel Features
- **Multiple Content Sources**: YouTube, Vimeo, Dailymotion, articles, RSS feeds, podcasts, and research papers
- **Modular Architecture**: Pluggable miners for easy extension
- **Unified Evidence Pool**: ContentBrain aggregates all content types
- **Enhanced CLI**: Interactive interface with Rich library
- **Comprehensive Testing**: Unit, integration, and performance tests
- **Backward Compatible**: Original YouTube-only pipeline still works

## 🚀 Quick Start

### Original YouTube Mode (Simple)

1. **Clone and install:**
   ```bash
   git clone https://github.com/saxster/youtube-to-ebook.git
   cd youtube-to-ebook
   pip install -r requirements.txt
   ```

2. **Set up API keys:**
   ```bash
   cp .env.example .env
   # Edit .env with your keys
   ```

3. **Add your channels:**
   ```bash
   # Edit channels.txt with YouTube channel handles
   @mkbhd
   @veritasium
   @3blue1brown
   ```

4. **Generate your ebook:**
   ```bash
   python main.py
   ```

### 🆕 Enhanced Content Funnel Mode

#### Interactive CLI (Recommended)
```bash
python main_pipeline.py --cli
```

This launches an interactive menu where you can:
- Select from multiple content sources (YouTube, articles, podcasts, etc.)
- Add content dynamically
- Generate articles with AI
- Create ebooks

#### Programmatic Usage
```python
from main_pipeline import run_pipeline

sources = {
    "youtube": "@mkbhd,@veritasium",
    "article": "https://example.com/article",
    "rss": "https://example.com/feed.xml"
}

run_pipeline(sources, output_format="epub")
```

#### Examples
```bash
python examples.py  # Run demonstration scripts
```

## 📚 Supported Content Sources

| Source Type | Description | Example |
|------------|-------------|---------|
| **YouTube** | Video transcripts | `@mkbhd` |
| **Vimeo** | Video metadata | `https://vimeo.com/123456` |
| **Dailymotion** | Video metadata | `https://dailymotion.com/video/x8abc` |
| **Articles** | Web articles | `https://example.com/article` |
| **RSS Feeds** | Blog/news feeds | `https://blog.com/feed.xml` |
| **Papers** | arXiv/PDF | `machine learning` or `arxiv:2301.00001` |
| **Podcasts** | Audio transcripts | `https://podcast.com/feed.xml` |

## Getting API Keys

### YouTube Data API (Free)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create credentials → API Key
5. Copy to `.env`

### Anthropic API
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an API key
3. Copy to `.env`

## Web Dashboard

Launch a friendly web interface:
```bash
pip install streamlit
python -m streamlit run dashboard.py
```

## Automation (Mac)

Run automatically every week:
```bash
# Copy the plist to LaunchAgents
cp com.youtube.newsletter.plist ~/Library/LaunchAgents/

# Load it
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.youtube.newsletter.plist
```

## Known Issues & Solutions

This project documents several YouTube API quirks:

| Problem | Solution |
|---------|----------|
| Shorts not filtered by duration | Check `/shorts/` URL pattern |
| Search API not chronological | Use uploads playlist instead |
| Transcript API syntax changed | Use instance method `ytt_api.fetch()` |
| Cloud servers blocked | Run locally, not GitHub Actions |
| Names misspelled in transcripts | Include video description in Claude context |

See [SKILL.md](SKILL.md) for detailed explanations.

## Project Structure

```
├── main.py              # Original YouTube pipeline (backward compatible)
├── main_pipeline.py     # 🆕 Enhanced multi-source pipeline
├── cli.py               # 🆕 Interactive CLI interface
├── examples.py          # 🆕 Usage examples
│
├── models.py            # 🆕 Evidence data model
├── content_brain.py     # 🆕 Unified evidence pool
├── ghostwriter.py       # 🆕 Enhanced AI article writer
│
├── miners/              # 🆕 Modular content extractors
│   ├── base_miner.py
│   ├── youtube_miner.py
│   ├── article_miner.py
│   ├── rss_miner.py
│   ├── paper_miner.py
│   ├── podcast_miner.py
│   ├── vimeo_miner.py
│   └── dailymotion_miner.py
│
├── outputs/             # 🆕 Output format creators
│   └── epub_creator.py
│
├── tests/               # 🆕 Comprehensive test suite
│   ├── test_models.py
│   ├── test_content_brain.py
│   └── test_integration.py
│
├── get_videos.py        # Legacy: Fetch YouTube videos
├── get_transcripts.py   # Legacy: Extract transcripts
├── write_articles.py    # Legacy: Transform with Claude
├── send_email.py        # Legacy: Create EPUB & send email
├── dashboard.py         # Streamlit web dashboard
├── video_tracker.py     # Track processed videos
├── channels.txt         # Your channel list
├── .env                 # Your API keys (not committed)
└── newsletters/         # Archive of generated ebooks
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific tests
pytest tests/test_models.py
```

## 📖 Documentation

- **[CONTENT_FUNNEL.md](CONTENT_FUNNEL.md)** - Comprehensive guide to the new modular pipeline
- **[SKILL.md](SKILL.md)** - Original YouTube API documentation and quirks
- **examples.py** - Working code examples

## License

MIT - Use freely, modify as needed.

---

Built with Claude AI
