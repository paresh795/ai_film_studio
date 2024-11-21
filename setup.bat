@echo off
REM Create and activate virtual environment
python -m venv venv
call venv\Scripts\activate

REM Install requirements
pip install -r requirements.txt

REM Create necessary directories if they don't exist
mkdir assembly\output
mkdir asset_generation\audio_gen
mkdir asset_generation\image_gen
mkdir asset_generation\video_gen
mkdir asset_generation\music_gen
mkdir story_team
mkdir tests
mkdir utils

REM Create a .env file template if it doesn't exist
if not exist .env (
    echo # API Keys > .env
    echo OPENAI_API_KEY= >> .env
    echo REPLICATE_API_TOKEN= >> .env
)

echo Setup complete! Don't forget to:
echo 1. Activate the virtual environment with 'venv\Scripts\activate'
echo 2. Add your API keys to the .env file 