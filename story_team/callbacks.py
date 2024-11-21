from typing import Dict, Any, Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
import json

class EnhancedStoryTeamCallback:
    def __init__(self):
        self.console = Console(force_terminal=True)
        
    def _format_feedback_history(self, feedback_list: List[Dict[str, Any]]) -> str:
        """Format feedback history into readable markdown"""
        if not feedback_list:
            return "No previous feedback"
            
        formatted = []
        for feedback in feedback_list:
            iteration = feedback.get("iteration", 0)
            recommendations = feedback.get("recommendations", {})
            
            formatted.append(f"\n### Iteration {iteration} Feedback:")
            for category, items in recommendations.items():
                formatted.append(f"\n**{category.replace('_', ' ').title()}:**")
                for item in items:
                    formatted.append(f"- {item}")
                    
        return "\n".join(formatted)

    def _create_scores_table(self, scores: Dict[str, float]) -> Table:
        """Create a rich table for scores"""
        table = Table(title="Quality Scores", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Score", justify="right", style="green")
        
        for metric, score in scores.items():
            table.add_row(
                metric.replace('_', ' ').title(),
                f"{score:.1f}/10"
            )
        return table

    def on_chain_start(self, state: Dict[str, Any]) -> None:
        """Called when the workflow chain starts"""
        self.console.print("\n[bold yellow]🎬 Content Generation Pipeline Started[/bold yellow]")
        self.console.print(Panel(
            f"Initial Prompt: {state.get('memory', {}).get('original_prompt', '')}",
            title="[bold]Input[/bold]",
            width=100
        ))
        
    def on_agent_start(self, agent: str, state: Dict[str, Any]) -> None:
        """Called when an agent starts processing"""
        self.console.print(f"\n[bold blue]🔄 {agent.upper()} Starting[/bold blue]")
        
        # Display state information
        info = [
            f"Iteration: {state.get('iteration', 0)}",
            f"Current Phase: {agent}",
        ]
        
        # Add previous feedback if available
        if state.get("previous_feedback"):
            self.console.print("\n[bold cyan]Previous Feedback:[/bold cyan]")
            feedback_md = self._format_feedback_history(state["previous_feedback"])
            self.console.print(Markdown(feedback_md))
        
        # Display scores if available
        evaluation_result = state.get('evaluation_result') or {}
        if isinstance(evaluation_result, dict):
            scores = evaluation_result.get('scores', {})
            if isinstance(scores, dict) and scores:
                self.console.print(self._create_scores_table(scores))
        
        self.console.print(Panel(
            "\n".join(info),
            title="[bold]Current State[/bold]",
            width=100
        ))
        
    def on_agent_finish(self, agent: str, result: Dict[str, Any]) -> None:
        """Called when an agent finishes processing"""
        self.console.print(f"\n[bold green]✅ {agent.upper()} Output[/bold green]")
        
        # Format output based on agent type
        if agent == "expert_evaluator":
            if "scores" in result:
                self.console.print(self._create_scores_table(result["scores"]))
            
            if "analysis" in result:
                analysis_md = "### Analysis:\n"
                for key, value in result["analysis"].items():
                    analysis_md += f"\n**{key.replace('_', ' ').title()}:**\n"
                    if isinstance(value, list):
                        for item in value:
                            analysis_md += f"- {item}\n"
                    else:
                        analysis_md += f"{value}\n"
                self.console.print(Markdown(analysis_md))
        
        # Show feedback addressed if available
        if "feedback_addressed" in result:
            self.console.print("\n[bold cyan]Feedback Addressed:[/bold cyan]")
            for item in result["feedback_addressed"]:
                self.console.print(f"✓ {item}")
        
        # Display full output in panel
        self.console.print(Panel(
            json.dumps(result, indent=2, ensure_ascii=False),
            width=100,
            padding=(1, 2)
        ))
