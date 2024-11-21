from typing import Dict, Any, Callable
from langgraph.graph import StateGraph, END
from .agents import StoryAnalyst, MediaDirector, ExpertEvaluator
from .state import CreativeState
from .callbacks import EnhancedStoryTeamCallback
from .models import StoryContent, MediaDirection, EvaluationResult

class EnhancedStoryTeamCoordinator:
    def __init__(self):
        self.story_analyst = StoryAnalyst()
        self.media_director = MediaDirector()
        self.expert_evaluator = ExpertEvaluator()
        self.callback = EnhancedStoryTeamCallback()
        self.workflow = self._create_workflow()
        
    def _create_workflow(self) -> StateGraph:
        workflow = StateGraph(Dict)
        
        # Add nodes for each agent
        workflow.add_node("story_analysis", 
            self._wrap_with_callbacks("story_analyst", self.story_analyst.process))
        workflow.add_node("media_direction", 
            self._wrap_with_callbacks("media_director", self.media_director.process))
        workflow.add_node("expert_evaluation", 
            self._wrap_with_callbacks("expert_evaluator", self.expert_evaluator.process))
        
        # Add conditional edges based on quality score
        workflow.add_conditional_edges(
            "expert_evaluation",
            self.should_continue,
            {
                "continue": "story_analysis",
                "end": END
            }
        )
        
        # Add main workflow edges
        workflow.add_edge("story_analysis", "media_direction")
        workflow.add_edge("media_direction", "expert_evaluation")
        
        workflow.set_entry_point("story_analysis")
        
        return workflow.compile()

    def should_continue(self, state: Dict[str, Any]) -> str:
        """Determine if workflow should continue based on evaluation scores"""
        if isinstance(state, dict):
            evaluation_result = state.get("evaluation_result", {})
            iteration = state.get("iteration", 0)
            previous_scores = state.get("previous_scores", [])
            
            # Get overall score
            overall_score = 0.0
            if isinstance(evaluation_result, dict):
                scores = evaluation_result.get("scores", {})
                if isinstance(scores, dict):
                    overall_score = float(scores.get("overall_score", 0.0))
            
            # Store score history
            previous_scores.append(overall_score)
            state["previous_scores"] = previous_scores
            
            # Check for score improvement
            score_improving = len(previous_scores) >= 2 and overall_score > previous_scores[-2]
            
            # Termination conditions
            if iteration == 0:
                return "continue"
            elif overall_score >= 8.0:
                return "end"
            elif iteration >= 3 and not score_improving:
                return "end"
            elif iteration >= 5:  # Hard limit
                return "end"
            return "continue"
        return "continue"

    def _wrap_with_callbacks(self, agent_name: str, process_func: Callable) -> Callable:
        """Wrap an agent's process function with callbacks"""
        async def wrapped_process(state: Dict[str, Any]) -> Dict[str, Any]:
            if isinstance(state, dict):
                state = CreativeState(**state)
            
            self.callback.on_agent_start(agent_name, state.model_dump())
            result = await process_func(state)
            self.callback.on_agent_finish(agent_name, result)
            
            # Update state with result based on agent type
            state_dict = state.model_dump()
            if agent_name == "story_analyst":
                state_dict["story_content"] = result
            elif agent_name == "media_director":
                state_dict["media_direction"] = result
            elif agent_name == "expert_evaluator":
                state_dict["evaluation_result"] = result
                if result.get("recommendations"):
                    state_dict["previous_feedback"] = state_dict.get("previous_feedback", [])
                    state_dict["previous_feedback"].append({
                        "iteration": state.iteration,
                        "recommendations": result["recommendations"]
                    })
                if result.get("scores", {}).get("overall_score"):
                    state_dict["previous_scores"] = state_dict.get("previous_scores", [])
                    state_dict["previous_scores"].append(
                        float(result["scores"]["overall_score"])
                    )
                state_dict["iteration"] = state.iteration + 1
            
            return state_dict
        return wrapped_process

    async def generate_content(self, prompt: str) -> Dict[str, Any]:
        """Generate content from prompt"""
        initial_state = CreativeState(
            memory={"original_prompt": prompt}
        )
        
        self.callback.on_chain_start(initial_state.model_dump())
        final_state = await self.workflow.ainvoke(initial_state.model_dump())
        
        # Ensure we return a dictionary
        if isinstance(final_state, CreativeState):
            final_state = final_state.model_dump()
        
        return {
            "story": final_state.get("story_content", {}),
            "media_direction": final_state.get("media_direction", {}),
            "evaluation": final_state.get("evaluation_result", {}),
            "iterations": final_state.get("iteration", 0),
            "previous_feedback": final_state.get("previous_feedback", []),
            "previous_scores": final_state.get("previous_scores", [])
        } 