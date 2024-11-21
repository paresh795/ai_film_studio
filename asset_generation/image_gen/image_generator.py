import os
import time
import logging
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import replicate
from datetime import datetime
from tqdm import tqdm
import random

class ImageGenerator:
    def __init__(self, output_dir: str = "generated_images"):
        load_dotenv()
        self.api_token = os.getenv("REPLICATE_API_TOKEN")
        if not self.api_token:
            raise ValueError("REPLICATE_API_TOKEN not found in environment variables")
        
        # Generate a random seed for this session
        self.seed = random.randint(0, 2**32 - 1)  # Using 32-bit integer range
        print(f"Using seed: {self.seed}")  # Print to console
        logging.info(f"Initialized with seed: {self.seed}")  # Log to file
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.metadata_store = {}
    
    def generate_with_primary_model(self, prompt: str) -> Optional[bytes]:
        """Try generating with flux-1.1-pro model"""
        try:
            output = replicate.run(
                "black-forest-labs/flux-1.1-pro",
                input={
                    "prompt": prompt,
                    "aspect_ratio": "16:9",
                    "output_format": "png",
                    "output_quality": 95,
                    "safety_tolerance": 5,
                    "seed": self.seed
                }
            )
            
            if output:
                return requests.get(output, timeout=10).content
            return None
            
        except Exception as e:
            if "NSFW content detected" in str(e):
                return None
            raise e
            
    def generate_with_fallback_model(self, prompt: str) -> Optional[bytes]:
        """Try generating with flux-dev model"""
        try:
            output = replicate.run(
                "black-forest-labs/flux-dev",
                input={
                    "prompt": prompt,
                    "go_fast": True,
                    "guidance": 3.5,
                    "megapixels": "1",
                    "num_outputs": 1,
                    "aspect_ratio": "16:9",
                    "output_format": "png",
                    "output_quality": 100,
                    "prompt_strength": 0.8,
                    "num_inference_steps": 50,
                    "seed": self.seed
                }
            )
            
            if isinstance(output, list) and output:
                image_url = output[0]
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    return response.content
                    
            return None
                
        except Exception as e:
            logging.error(f"Fallback model failed: {str(e)}")
            return None

    def generate_single_image(
        self, 
        prompt: str, 
        retries: int = 3,
        retry_delay: int = 5
    ) -> Optional[bytes]:
        """Generate single image with proper versioning and parameters."""
        for attempt in range(retries):
            try:
                output = replicate.run(
                    "black-forest-labs/flux-1.1-pro",
                    input={
                        "prompt": prompt,
                        "aspect_ratio": "16:9",
                        "width": 1024,
                        "height": 576,
                        "output_format": "png",
                        "seed": self.seed
                    }
                )
                
                if isinstance(output, list) and output:
                    image_url = output[0]
                elif isinstance(output, str):
                    image_url = output
                else:
                    raise ValueError(f"Unexpected output format: {type(output)}")
                    
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    return response.content
                    
            except Exception as e:
                if "NSFW content detected" in str(e):
                    try:
                        return self.generate_with_fallback_model(prompt)
                    except Exception as fallback_e:
                        logging.error(f"Fallback model failed: {str(fallback_e)}")
                
                logging.error(f"Attempt {attempt + 1}/{retries} failed: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(retry_delay)
                    
        logging.error(f"All attempts failed for prompt: {prompt}")
        return None

    def batch_generate(self, prompts: List[str]) -> List[str]:
        """Generate multiple images with proper prompt filtering."""
        # Filter out square brackets and empty lines
        filtered_prompts = [
            prompt.strip() 
            for prompt in prompts 
            if prompt.strip() and prompt.strip() not in ['[', ']']
        ]
        
        generated_files = []
        with tqdm(total=len(filtered_prompts), desc="Generating images") as pbar:
            for i, prompt in enumerate(filtered_prompts):
                logging.info(f"Processing prompt {i+1}/{len(filtered_prompts)}: {prompt}")
                
                image_data = self.generate_single_image(prompt)
                if image_data:
                    filename = f"{int(time.time())}_{i:03d}.png"
                    filepath = self.output_dir / filename
                    
                    with open(filepath, "wb") as f:
                        f.write(image_data)
                    
                    generated_files.append(str(filepath))
                
                pbar.update(1)
        
        return generated_files

    def generate_from_scene(self, visual_output: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate images from a scene's visual output"""
        scene_id = visual_output["scene_id"]
        generated_files = []
        
        for prompt_data in visual_output["image_prompts"]:
            # Store metadata for tracking
            metadata_key = f"{scene_id}_{prompt_data['prompt_id']}"
            self.metadata_store[metadata_key] = {
                "scene_id": scene_id,
                "prompt_id": prompt_data["prompt_id"],
                "metadata": prompt_data["metadata"]
            }
            
            # Generate image using just the description
            image_data = self.generate_single_image(prompt_data["description"])
            if image_data:
                filename = f"{metadata_key}.png"
                filepath = self.output_dir / filename
                
                with open(filepath, "wb") as f:
                    f.write(image_data)
                generated_files.append(str(filepath))
                
        return {scene_id: generated_files}

def main():
    # Load prompts from file
    with open("prompts.txt", "r", encoding="utf-8") as f:
        prompts = [line.strip() for line in f if line.strip()]
    
    # Generate images
    generator = ImageGenerator()
    results = generator.batch_generate(prompts)
    
    # Report results
    successful = len(results)
    print(f"\nGeneration complete!")
    print(f"Successfully generated {successful}/{len(prompts)} images")
    print(f"Images saved in: {generator.output_dir}")
    
    return successful == len(prompts)

if __name__ == "__main__":
    main() 