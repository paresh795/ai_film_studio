#!/bin/bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Create necessary directories if they don't exist
mkdir -p assembly/output
mkdir -p asset_generation/audio_gen
mkdir -p asset_generation/image_gen
mkdir -p asset_generation/video_gen
mkdir -p asset_generation/music_gen
mkdir -p story_team
mkdir -p tests
mkdir -p utils

# Create a .env file template if it doesn't exist
if [ ! -f .env ]; then
    echo "# API Keys" > .env
    echo "OPENAI_API_KEY=" >> .env
    echo "REPLICATE_API_TOKEN=" >> .env
fi

echo "Setup complete! Don't forget to:"
echo "1. Activate the virtual environment with 'source venv/bin/activate'"
echo "2. Add your API keys to the .env file" 