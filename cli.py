"""
Enhanced CLI for Content Funnel Pipeline
Interactive interface using Rich for better UX.
"""

import os
import sys
from typing import List, Optional

try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.panel import Panel
    from rich.table import Table
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Rich library not available. Install with: pip install rich")
    print("Using basic CLI instead.\n")

from content_brain import ContentBrain
from ghostwriter import GhostWriter
from models import SourceType


if RICH_AVAILABLE:
    console = Console()
else:
    console = None


class ContentFunnelCLI:
    """
    Interactive CLI for the Content Funnel pipeline.
    Provides a user-friendly interface for content aggregation and transformation.
    """
    
    def __init__(self):
        """Initialize the CLI."""
        self.brain = ContentBrain()
        self.ghostwriter = None
        self.use_rich = RICH_AVAILABLE
    
    def run(self):
        """Run the interactive CLI."""
        if self.use_rich:
            self._run_rich()
        else:
            self._run_basic()
    
    def _run_rich(self):
        """Run with Rich formatting."""
        console.clear()
        
        # Display header
        console.print(Panel.fit(
            "[bold cyan]Content Funnel Pipeline[/bold cyan]\n"
            "Transform content from multiple sources into beautiful ebooks",
            border_style="cyan"
        ))
        
        console.print()
        
        # Main menu loop
        while True:
            console.print("[bold]What would you like to do?[/bold]\n")
            
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Option", style="cyan")
            table.add_column("Description")
            
            table.add_row("1", "Add content from sources")
            table.add_row("2", "View evidence pool")
            table.add_row("3", "Generate articles")
            table.add_row("4", "Create ebook")
            table.add_row("5", "Exit")
            
            console.print(table)
            console.print()
            
            choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5"])
            console.print()
            
            if choice == "1":
                self._add_content_rich()
            elif choice == "2":
                self._view_evidence_rich()
            elif choice == "3":
                self._generate_articles_rich()
            elif choice == "4":
                self._create_ebook_rich()
            elif choice == "5":
                console.print("[yellow]Goodbye![/yellow]")
                break
    
    def _add_content_rich(self):
        """Add content from various sources (Rich version)."""
        console.print("[bold]Select content source:[/bold]\n")
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Option", style="cyan")
        table.add_column("Source Type")
        
        table.add_row("1", "YouTube")
        table.add_row("2", "Article (Web)")
        table.add_row("3", "RSS Feed")
        table.add_row("4", "Research Paper (arXiv/PDF)")
        table.add_row("5", "Podcast")
        table.add_row("6", "Vimeo")
        table.add_row("7", "Dailymotion")
        table.add_row("0", "Back")
        
        console.print(table)
        console.print()
        
        choice = Prompt.ask("Choose a source", choices=["0", "1", "2", "3", "4", "5", "6", "7"])
        
        if choice == "0":
            return
        
        console.print()
        
        # Import miners on demand
        from miners import (
            YouTubeMiner, ArticleMiner, RSSMiner, 
            PaperMiner, PodcastMiner, VimeoMiner, DailymotionMiner
        )
        
        miner = None
        query_prompt = ""
        
        if choice == "1":
            query_prompt = "Enter YouTube channel handle(s) (e.g., @mkbhd)"
            miner = YouTubeMiner()
        elif choice == "2":
            query_prompt = "Enter article URL(s)"
            miner = ArticleMiner()
        elif choice == "3":
            query_prompt = "Enter RSS feed URL(s)"
            miner = RSSMiner()
        elif choice == "4":
            query_prompt = "Enter arXiv ID, PDF URL, or search query"
            miner = PaperMiner()
        elif choice == "5":
            query_prompt = "Enter podcast RSS feed URL(s)"
            miner = PodcastMiner()
        elif choice == "6":
            query_prompt = "Enter Vimeo video URL(s)"
            miner = VimeoMiner()
        elif choice == "7":
            query_prompt = "Enter Dailymotion video URL(s)"
            miner = DailymotionMiner()
        
        if miner:
            query = Prompt.ask(query_prompt)
            
            console.print()
            
            with console.status("[bold green]Fetching content...", spinner="dots"):
                try:
                    evidence = miner.fetch(query)
                    self.brain.add_evidence_batch(evidence)
                    
                    console.print(f"\n[green]✓[/green] Added {len(evidence)} item(s) to evidence pool")
                except Exception as e:
                    console.print(f"[red]✗ Error:[/red] {e}")
            
            console.print()
            Prompt.ask("Press Enter to continue")
        
        console.clear()
    
    def _view_evidence_rich(self):
        """View current evidence pool (Rich version)."""
        console.print("[bold]Evidence Pool[/bold]\n")
        
        if not self.brain.evidence_pool:
            console.print("[yellow]No evidence collected yet.[/yellow]\n")
            Prompt.ask("Press Enter to continue")
            console.clear()
            return
        
        stats = self.brain.get_stats()
        
        # Display stats
        table = Table(title="Statistics", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Evidence", str(stats['total_evidence']))
        table.add_row("Unique Sources", str(stats['sources']))
        
        for source_type, count in stats['by_source_type'].items():
            table.add_row(f"  {source_type.title()}", str(count))
        
        console.print(table)
        console.print()
        
        # Display evidence items
        evidence_table = Table(title="Evidence Items", show_header=True)
        evidence_table.add_column("Title", style="cyan", max_width=40)
        evidence_table.add_column("Source", style="yellow")
        evidence_table.add_column("Type", style="green")
        evidence_table.add_column("Words", style="magenta")
        
        for ev in self.brain.evidence_pool:
            word_count = str(ev.metadata.get('word_count', len(ev.raw_content.split())))
            evidence_table.add_row(
                ev.title[:37] + "..." if len(ev.title) > 40 else ev.title,
                ev.publisher or "Unknown",
                ev.source_type.value,
                word_count
            )
        
        console.print(evidence_table)
        console.print()
        
        Prompt.ask("Press Enter to continue")
        console.clear()
    
    def _generate_articles_rich(self):
        """Generate articles from evidence (Rich version)."""
        if not self.brain.evidence_pool:
            console.print("[yellow]No evidence to process. Please add content first.[/yellow]\n")
            Prompt.ask("Press Enter to continue")
            console.clear()
            return
        
        console.print(f"[bold]Generate articles from {len(self.brain.evidence_pool)} evidence items[/bold]\n")
        
        if not Confirm.ask("Proceed with article generation?"):
            console.clear()
            return
        
        console.print()
        
        try:
            if not self.ghostwriter:
                self.ghostwriter = GhostWriter()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console
            ) as progress:
                task = progress.add_task("[cyan]Generating articles...", total=len(self.brain.evidence_pool))
                
                articles = []
                for evidence in self.brain.evidence_pool:
                    article = self.ghostwriter.transform(evidence)
                    if article:
                        articles.append(article)
                    progress.advance(task)
            
            console.print(f"\n[green]✓[/green] Generated {len(articles)} articles")
            
            # Save articles for ebook creation
            self.articles = articles
        
        except Exception as e:
            console.print(f"\n[red]✗ Error:[/red] {e}")
        
        console.print()
        Prompt.ask("Press Enter to continue")
        console.clear()
    
    def _create_ebook_rich(self):
        """Create ebook from articles (Rich version)."""
        if not hasattr(self, 'articles') or not self.articles:
            console.print("[yellow]No articles generated yet. Please generate articles first.[/yellow]\n")
            Prompt.ask("Press Enter to continue")
            console.clear()
            return
        
        console.print(f"[bold]Create ebook from {len(self.articles)} articles[/bold]\n")
        
        # Ask for format
        format_choice = Prompt.ask(
            "Choose output format",
            choices=["epub", "both"],
            default="epub"
        )
        
        console.print()
        
        with console.status("[bold green]Creating ebook...", spinner="dots"):
            try:
                # Import the output module
                from outputs.epub_creator import create_epub_from_articles
                
                filepath = create_epub_from_articles(self.articles)
                
                console.print(f"\n[green]✓[/green] Created ebook: {filepath}")
            
            except Exception as e:
                console.print(f"\n[red]✗ Error:[/red] {e}")
        
        console.print()
        Prompt.ask("Press Enter to continue")
        console.clear()
    
    def _run_basic(self):
        """Run with basic text interface (fallback)."""
        print("=" * 60)
        print("  CONTENT FUNNEL PIPELINE")
        print("=" * 60)
        print("\nBasic mode (install 'rich' for enhanced UI: pip install rich)\n")
        
        # Simple menu
        while True:
            print("\nOptions:")
            print("1. Add content")
            print("2. View evidence")
            print("3. Generate articles")
            print("4. Create ebook")
            print("5. Exit")
            
            choice = input("\nChoose an option (1-5): ").strip()
            
            if choice == "5":
                print("Goodbye!")
                break
            elif choice in ["1", "2", "3", "4"]:
                print(f"\nOption {choice} selected.")
                print("(Full functionality requires Rich library)")
            else:
                print("Invalid choice. Please try again.")


def main():
    """Main entry point for CLI."""
    cli = ContentFunnelCLI()
    cli.run()


if __name__ == "__main__":
    main()
