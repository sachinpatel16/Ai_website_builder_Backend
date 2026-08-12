"""
Image generation node for website generation workflow.
Generates images using DALL-E 3 based on descriptions.
"""
import asyncio
import logging
import os
from typing import Dict

from dotenv import load_dotenv

from app.workflow_state import WorkflowState
from app.utils import call_dalle

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


async def image_generation_node(state: WorkflowState) -> WorkflowState:
    """
    Step 2b: Generate images using DALL-E 3 based on descriptions.
    Uses call_dalle function from utils. Falls back to static images if API fails.
    """
    logger.info("Starting image generation node...")
    
    try:
        image_descriptions = state["image_descriptions"]
        image_urls = {}
        
        # Get base URL from environment (default to localhost)
        base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
        
        # Static image mapping for fallback
        static_images = {
            "hero": "hero_1766668485.png",
            "features": "features_1766668478.png",
            "testimonials": "testimonials_1766668479.png"
        }
        
        # Create tasks for parallel execution
        tasks = []
        sections_to_process = []
        
        for section, description in image_descriptions.items():
            logger.info(f"Queuing image generation for {section}")
            sections_to_process.append(section)
            tasks.append(
                call_dalle(
                    section=section,
                    prompt=description,
                    size="1792x1024",
                    quality="standard"
                )
            )
            
        # Execute in parallel
        if tasks:
            logger.info(f"Starting parallel generation of {len(tasks)} images...")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                section = sections_to_process[i]
                
                if isinstance(result, Exception):
                    logger.error(f"Image generation failed for {section}: {str(result)}")
                    logger.info(f"Using static fallback image for {section}")
                    fallback_filename = static_images.get(section, "placeholder.png")
                    image_urls[section] = f"{base_url}/uploads/{fallback_filename}"
                else:
                    # Success - result is local_url
                    local_url = result
                    image_urls[section] = f"{base_url}{local_url}"
                    logger.info(f"✓ Image generated and saved for {section}: {image_urls[section]}")
        else:
            logger.warning("No image descriptions found to process")
        
        logger.info(f"Generated {len(image_urls)} images")
        logger.info(f"Image URLs: {image_urls}")
        
        # Update state
        return {
            **state,
            "image_urls": image_urls,
            "current_step": "html_generation",
            "progress": 65,
            "progress_message": f"✓ {len(image_urls)} images generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Image generation node error: {str(e)}")
        return {
            **state,
            "current_step": "failed",
            "status": "failed",
            "error": f"Image generation failed: {str(e)}",
            "progress": 40,
            "progress_message": f"✗ Image generation failed: {str(e)}"
        }
