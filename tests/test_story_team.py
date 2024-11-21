import pytest
from story_team.coordinator import EnhancedStoryTeamCoordinator
import json

@pytest.mark.asyncio
async def test_content_generation(capsys):
    coordinator = EnhancedStoryTeamCoordinator()
    
    prompt = """Create a short story about a robot discovering emotions for the first time.
    The story should be visually interesting and suitable for a 1-minute video."""
    
    result = await coordinator.generate_content(prompt)
    
    # Print the final result for visibility
    print("\nFinal Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Regular assertions
    assert "story" in result
    assert "media_direction" in result
    assert "evaluation" in result
    assert "iterations" in result
    
    # Verify feedback incorporation
    if result["iterations"] > 1:
        assert "previous_feedback" in result, "Should track feedback history"
        assert "feedback_addressed" in result["story_content"], "Story should address feedback"
        assert "feedback_addressed" in result["media_direction"], "Media direction should address feedback"
    
    # Verify score improvement
    if "previous_scores" in result and len(result["previous_scores"]) > 1:
        assert result["previous_scores"][-1] >= result["previous_scores"][0], "Score should improve or stay same"