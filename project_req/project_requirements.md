# AI Film Production Studio
## Project Overview & Vision

### Purpose
An AI-powered film production system that automates the creation of visual stories through coordinated AI agents. The system combines story development, visual asset generation, audio creation, and production assembly into a cohesive pipeline.

### Current Status
- Existing image generation system using Replicate API
- Basic prompt handling and error management
- Local file system storage

### Target Architecture

#### 1. Story Development Team (LangGraph-based)
- **Basic Version (Phase 1)**
  - Story Developer Agent: Creates basic narrative
  - Visual Director Agent: Generates image/video prompts
  - Production Manager Agent: Coordinates asset requirements

- **Advanced Version (Future)**
  - Additional specialized agents
  - Critic/Quality Control Agent
  - Enhanced feedback loops
  - More sophisticated story development

#### 2. Asset Generation Services
- **Image Generation (Current)**
  - Existing service to be modified for JSON input
  - Enhanced error handling
  - Better retry mechanisms

- **Planned Services (Future)**
  - Video Generation
  - Sound Effects
  - Music Generation

#### 3. Integration Layer
- JSON-based communication between components
- Standardized input/output formats
- Local file system management

### Technology Stack
- Python 3.9+
- LangGraph for agent orchestration
- OpenAI API for agent intelligence
- Replicate API for image generation
- Local file system for asset storage

### Implementation Phases

#### Phase 1 (Current Focus)
1. Setup basic story development team
   - Implement minimal agent structure
   - Basic story-to-prompt conversion
   - Simple coordination logic

2. Adapt Image Generator
   - Modify for JSON input
   - Improve error handling
   - Integrate with agent output

3. Basic Integration
   - Story team → Image generation pipeline
   - Asset storage and organization
   - Simple validation

#### Phase 2 (Future)
1. Enhanced Agent Team
   - Add specialized agents
   - Implement feedback loops
   - Quality control mechanisms

2. Additional Asset Services
   - Video generation integration
   - Audio generation setup
   - Music creation system

### Immediate Tasks
1. Modify existing image generator:
   ```python
   class ImageGenerator:
       def __init__(self):
           # Existing initialization
           pass
           
       async def generate_from_json(self, prompt_data: dict) -> dict:
           # New method for JSON input
           pass
   ```

2. Create basic agent structure:
   ```python
   class StoryTeam:
       def __init__(self):
           self.story_developer = Agent("story_developer")
           self.visual_director = Agent("visual_director")
           self.production_manager = Agent("production_manager")
   ```

### Testing Strategy
- Unit tests for each component
- Integration tests between agents
- End-to-end story creation tests
- Asset generation validation

### Development Guidelines
1. Implement incrementally
2. Test each component thoroughly
3. Document all agent interactions
4. Use standardized JSON formats
5. Implement proper error handling

### Current Limitations & Considerations
1. Running locally (no cloud deployment yet)
2. Limited to basic story structures initially
3. Focus on image generation first
4. Simple agent interactions to start

### Next Steps
1. Setup project structure
2. Modify image generator for JSON
3. Implement basic agent team
4. Create integration tests
5. Document API formats