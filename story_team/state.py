from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field

class StoryContent(BaseModel):
    """Story content structure"""
    title: str = ""
    synopsis: str = ""
    target_audience: str = ""
    estimated_duration: str = ""
    scenes: List[Dict[str, Any]] = Field(default_factory=list)
    feedback_addressed: List[str] = Field(default_factory=list)

class MediaDirection(BaseModel):
    """Media direction structure"""
    visual_style: str = ""
    audio_style: str = ""
    shot_list: List[Dict[str, Any]] = Field(default_factory=list)
    technical_requirements: Dict[str, List[str]] = Field(default_factory=dict)
    feedback_addressed: List[str] = Field(default_factory=list)

class EvaluationResult(BaseModel):
    scores: Dict[str, float] = Field(default_factory=dict)
    analysis: Dict[str, Any] = Field(default_factory=dict)
    recommendations: Dict[str, List[str]] = Field(default_factory=dict)
    iteration_notes: str = ""

class CreativeState(BaseModel):
    """Main state container"""
    iteration: int = 0
    memory: Dict[str, Any] = Field(default_factory=dict)
    story_content: Optional[Dict[str, Any]] = None
    media_direction: Optional[Dict[str, Any]] = None
    evaluation_result: Optional[Dict[str, Any]] = None
    previous_feedback: List[Dict[str, Any]] = Field(default_factory=list)
    previous_scores: List[float] = Field(default_factory=list) 