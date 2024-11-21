from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class StoryContent(BaseModel):
    title: str
    synopsis: str
    target_audience: str
    estimated_duration: str
    scenes: List[Dict[str, Any]]
    feedback_addressed: List[str] = []

class MediaDirection(BaseModel):
    visual_style: str
    audio_style: str
    shot_list: List[Dict[str, Any]]
    technical_requirements: Dict[str, List[str]]
    feedback_addressed: List[str] = []

class EvaluationResult(BaseModel):
    scores: Dict[str, float]
    analysis: Dict[str, Any]
    recommendations: Dict[str, List[str]]
    iteration_notes: str

class CreativeState(BaseModel):
    iteration: int = 0
    memory: Dict[str, Any] = {}
    story_content: Optional[StoryContent] = None
    media_direction: Optional[MediaDirection] = None
    evaluation_result: Optional[EvaluationResult] = None
    previous_feedback: List[Dict[str, Any]] = []
    previous_scores: List[float] = []