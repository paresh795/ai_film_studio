from typing import Dict, Any, Optional
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from .state import CreativeState
import os
from dotenv import load_dotenv
import json

load_dotenv()

class BaseAgent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = f"""You are part of an AI Film Studio team that uses generative AI tools.
Our team creates videos using:
- AI image generation for visuals
- AI video generation for scenes
- AI audio generation for sound effects and music
- No physical props or traditional filming required

Key Points:
- All visual elements are created through AI
- Production complexity should focus on AI generation challenges
- Cost considerations should relate to AI processing and generation time
- Technical requirements should focus on AI model capabilities

{system_prompt}"""
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OpenAI API key not found in .env file")
        
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo-0125",
            temperature=0.7,
            openai_api_key=openai_api_key
        )

    def _build_context(self, state: CreativeState) -> str:
        """Build rich context from state"""
        context = []
        
        # Add iteration info
        context.append(f"Current Iteration: {state.iteration}")
        
        # Add previous feedback if available
        if state.previous_feedback:
            context.append("\nPrevious Feedback:")
            for feedback in state.previous_feedback:
                if feedback.get("recommendations"):
                    context.append("\nRecommendations:")
                    for key, items in feedback["recommendations"].items():
                        context.append(f"\n{key}:")
                        for item in items:
                            context.append(f"- {item}")
        
        # Add current content
        if state.story_content and self.name != "story_analyst":
            context.append("\nCurrent Story Content:")
            # Handle both dict and model cases
            if hasattr(state.story_content, 'model_dump'):
                context.append(json.dumps(state.story_content.model_dump(), indent=2))
            else:
                context.append(json.dumps(state.story_content, indent=2))
        
        if state.media_direction and self.name == "expert_evaluator":
            context.append("\nMedia Direction:")
            if hasattr(state.media_direction, 'model_dump'):
                context.append(json.dumps(state.media_direction.model_dump(), indent=2))
            else:
                context.append(json.dumps(state.media_direction, indent=2))
        
        return "\n".join(context)

    def _validate_scores(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize scores if present"""
        if self.name == "expert_evaluator" and isinstance(result, dict):
            scores = result.get("scores", {})
            if isinstance(scores, dict):
                # Ensure all scores are valid floats between 0-10
                for key, value in scores.items():
                    try:
                        scores[key] = max(0.0, min(10.0, float(value)))
                    except (ValueError, TypeError):
                        scores[key] = 5.0  # Default to middle score if invalid
                
                # Recalculate overall score as average
                if "overall_score" in scores:
                    score_values = [v for k, v in scores.items() if k != "overall_score"]
                    scores["overall_score"] = round(sum(score_values) / len(score_values), 1)
                
                result["scores"] = scores
        return result

    async def process(self, state: CreativeState) -> Dict[str, Any]:
        """Process state with full context"""
        context = self._build_context(state)
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""
Current Iteration: {state.iteration}
Original Prompt: {state.memory.get('original_prompt', '')}

Context:
{context}

Please process this information according to your role and return a valid JSON response.
""")
        ]
        
        response = await self.llm.ainvoke(messages)
        try:
            content = self._extract_json(response.content)
            result = json.loads(content)
            return self._validate_scores(result)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {str(e)}")
            print(f"Raw Response: {response.content}")
            return {
                "error": "Failed to parse JSON response",
                "raw_response": response.content
            }

    def _extract_json(self, content: str) -> str:
        """Extract JSON from response content"""
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        return content.strip()