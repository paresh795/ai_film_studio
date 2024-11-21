import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON
from .coordinator import EnhancedStoryTeamCoordinator
import json

async def main():
    console = Console()
    coordinator = EnhancedStoryTeamCoordinator()
    
    prompt = """Create a short story about a robot discovering emotions for the first time.
    The story should be visually interesting and suitable for a 1-minute video."""
    
    console.print("[bold]🎥 Starting Content Generation Pipeline[/bold]")
    
    result = await coordinator.generate_content(prompt)
    
    formatted_result = json.dumps(result, indent=2, ensure_ascii=False)
    console.print("\n[bold]Final Output:[/bold]")
    console.print(Panel(
        formatted_result,
        title="[bold]Generated Content[/bold]",
        width=100,
        padding=(1, 2),
        border_style="bold green"
    ))

if __name__ == "__main__":
    asyncio.run(main()) 