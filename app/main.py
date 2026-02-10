# Standard library imports
import os
import time
import logging
import asyncio
import json
import re
from typing import Tuple

# Third-party imports
from dotenv import load_dotenv # type: ignore
from fastapi import FastAPI, HTTPException, Request # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse, RedirectResponse # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
import dspy # type: ignore - Used for DSPy configuration and LM settings
import uvicorn # type: ignore - Used for running the FastAPI server

# Local application imports
from app.schema import (
    GeneratePromptsRequest, PromptsResponse,
    GenerateImagesRequest, ImagesResponse,
    GenerateHTMLRequest, HTMLResponse,
    EditHTMLRequest, EditHTMLResponse,
    GenerateWebsiteRequest, WebsitePlanResponse, WebsiteGenerationResponse,
    UpdateWebsiteRequest, UpdateWebsiteResponse
)
from app.utils import call_dalle, find_local_images
from app.const import fallback_html, fallback_css, edit_fallback_html, edit_fallback_css
import app.config  # Import config to configure DSPy
from app.dspy_modules import (
    ImagePromptGenerator,
    LandingPageGenerator,
    TemplateModifier,
    HTMLEditor,
)
from app.workflow_graph import website_workflow
from app.workflow_state import WorkflowState
from app.rate_limiter import init_rate_limiter, get_rate_limiter

# Import litellm for error handling (optional dependency)
try:
    import litellm # type: ignore
except ImportError:
    litellm = None

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Landing Page Generator API",
    version="1.0.0",
    debug=False
)

# Initialize rate limiter with simple config
init_rate_limiter({
    'requests_per_minute': 60,
    'requests_per_hour': 1000,
    'burst_size': 10
})

logger.info("Starting AI Landing Page Generator API v1.0.0")





# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables (OPENAI_API_KEY is used in dspy_modules.py)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
WEBTEMPLATES_DIR = os.path.join(BASE_DIR, "webtemplates")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(WEBTEMPLATES_DIR, exist_ok=True)

# Mount static directories
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.get("/test")
async def serve_test_page():
    """Serve the test page for /api/generate-website endpoint"""
    index_path = os.path.join(BASE_DIR, "index.html")
    return FileResponse(index_path)

@app.get("/api/serve-website/{folder_name}/{file_path:path}")
async def serve_website_file(folder_name: str, file_path: str):
    """
    Serve static files from a generated website folder.
    
    Args:
        folder_name: Name of the website folder (e.g., 'website_20260107_120500')
        file_path: Path to the file within the folder (e.g., 'index.html', 'style.css', 'home.html')
    
    Returns:
        FileResponse with the requested file
    """
    # Sanitize folder_name to prevent directory traversal
    folder_name = os.path.basename(folder_name)
    
    # Construct full path
    website_folder = os.path.join(WEBTEMPLATES_DIR, folder_name)
    full_path = os.path.join(website_folder, file_path)
    
    # Security check: ensure the resolved path is within webtemplates
    try:
        real_path = os.path.realpath(full_path)
        real_webtemplates = os.path.realpath(WEBTEMPLATES_DIR)
        
        if not real_path.startswith(real_webtemplates):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        logger.error(f"Security check failed: {str(e)}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if file exists
    if not os.path.exists(full_path):
        logger.warning(f"File not found: {full_path}")
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    
    # Determine MIME type
    if full_path.endswith('.html'):
        media_type = 'text/html'
    elif full_path.endswith('.css'):
        media_type = 'text/css'
    elif full_path.endswith('.js'):
        media_type = 'application/javascript'
    elif full_path.endswith('.json'):
        media_type = 'application/json'
    elif full_path.endswith('.png'):
        media_type = 'image/png'
    elif full_path.endswith('.jpg') or full_path.endswith('.jpeg'):
        media_type = 'image/jpeg'
    else:
        media_type = None
    
    logger.info(f"Serving file: {full_path}")
    return FileResponse(full_path, media_type=media_type)

@app.get("/api/serve-website/{folder_name}")
async def serve_website_index(folder_name: str, request: Request):
    """
    Redirect to the folder URL with a trailing slash.
    This ensures relative URLs in index.html work correctly.
    
    Args:
        folder_name: Name of the website folder
        request: FastAPI Request object
    
    Returns:
        RedirectResponse to the folder with trailing slash
    """
    # Redirect to the same URL with a trailing slash
    redirect_url = f"/api/serve-website/{folder_name}/index.html"
    return RedirectResponse(url=redirect_url, status_code=307)

@app.get("/api/serve-website/{folder_name}/")
async def serve_website_index_with_slash(folder_name: str):
    """
    Serve the index.html file from a generated website folder.
    The trailing slash ensures relative URLs in the HTML work correctly.
    
    Args:
        folder_name: Name of the website folder
    
    Returns:
        FileResponse with index.html
    """
    # Sanitize folder_name to prevent directory traversal
    folder_name = os.path.basename(folder_name)
    
    # Construct full path to index.html
    website_folder = os.path.join(WEBTEMPLATES_DIR, folder_name)
    index_path = os.path.join(website_folder, "index.html")
    
    # Security check: ensure the resolved path is within webtemplates
    try:
        real_path = os.path.realpath(index_path)
        real_webtemplates = os.path.realpath(WEBTEMPLATES_DIR)
        
        if not real_path.startswith(real_webtemplates):
            raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        logger.error(f"Security check failed: {str(e)}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if file exists
    if not os.path.exists(index_path):
        logger.warning(f"File not found: {index_path}")
        raise HTTPException(status_code=404, detail="index.html not found")
    
    # Check if it's actually a file
    if not os.path.isfile(index_path):
        logger.error(f"Path is not a file: {index_path}")
        raise HTTPException(status_code=500, detail="Invalid file path")
    
    logger.info(f"Serving index.html from: {index_path}")
    return FileResponse(index_path, media_type='text/html')


def extract_css_and_replace_style_tags(html: str) -> Tuple[str, str]:
    """
    Extract CSS from <style> tags and replace them with external stylesheet link.
    
    Args:
        html: HTML string containing <style> tags
        
    Returns:
        tuple: (html_with_link_tag, extracted_css)
    """
    # Pattern to match <style> tags with optional attributes
    style_pattern = r'<style[^>]*>(.*?)</style>'
    
    # Extract all CSS content from style tags
    css_matches = re.findall(style_pattern, html, re.DOTALL | re.IGNORECASE)
    extracted_css = '\n\n'.join(css_matches).strip()
    
    # Remove all style tags from HTML
    html_without_style = re.sub(style_pattern, '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Insert <link> tag before </head> if head tag exists
    link_tag = '<link rel="stylesheet" href="style.css">'
    
    # Check if </head> exists
    if '</head>' in html_without_style.lower():
        # Insert link tag before </head> (case-insensitive)
        html_with_link = re.sub(
            r'(</head>)',
            f'{link_tag}\n    \\1',
            html_without_style,
            flags=re.IGNORECASE
        )
    else:
        # If no </head> tag, try to insert before </html> or at the beginning
        if '</html>' in html_without_style.lower():
            html_with_link = re.sub(
                r'(</html>)',
                f'    {link_tag}\n\\1',
                html_without_style,
                flags=re.IGNORECASE
            )
        else:
            # Fallback: prepend link tag to HTML
            html_with_link = f'{link_tag}\n{html_without_style}'
    
    return html_with_link, extracted_css


@app.get("/")
async def root():
    """Root endpoint."""
    logger.info("Root endpoint accessed")
    return {
        "message": "AI Landing Page Generator API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


@app.get("/api/websites")
async def list_websites():
    """
    List all generated websites by scanning the webtemplates directory.
    Returns metadata for each website if available.
    """
    logger.info("Listing all generated websites...")
    websites = []
    
    if not os.path.exists(WEBTEMPLATES_DIR):
        logger.warning(f"Webtemplates directory not found: {WEBTEMPLATES_DIR}")
        return {"websites": []}
        
    try:
        # List all directories in webtemplates
        for folder_name in os.listdir(WEBTEMPLATES_DIR):
            folder_path = os.path.join(WEBTEMPLATES_DIR, folder_name)
            
            if os.path.isdir(folder_path):
                # Try to find metadata.json
                metadata_path = os.path.join(folder_path, "metadata.json")
                website_info = {
                    "folder_name": folder_name,
                    "created_at": None,
                    "description": folder_name,  # Use folder name as title fallback
                    "pages": []
                }
                
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            website_info.update({
                                "created_at": metadata.get("created_at"),
                                "description": metadata.get("description", folder_name),
                                "pages": metadata.get("pages", []),
                                "plan": metadata.get("plan"),
                                "business_plan": metadata.get("business_plan")
                            })
                    except Exception as e:
                        logger.error(f"Error reading metadata for {folder_name}: {str(e)}")
                
                websites.append(website_info)
        
        # Sort by creation date (newest first)
        websites.sort(key=lambda x: x.get("created_at") or "", reverse=True)
        
        logger.info(f"Found {len(websites)} websites")
        return {"websites": websites}
        
    except Exception as e:
        logger.error(f"Error listing websites: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing websites: {str(e)}")


@app.get("/health/ready")
async def readiness_check():
    """Readiness probe - checks if app can serve traffic."""
    try:
        # Check if DSPy is configured (dspy imported at top)
        if not hasattr(dspy.settings, 'lm') or dspy.settings.lm is None:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "reason": "DSPy LM not configured"
                }
            )
        
        return {
            "status": "ready",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "error": str(e)
            }
        )


@app.get("/health/live")
async def liveness_check():
    """Liveness probe - checks if app is running."""
    return {
        "status": "alive",
        "timestamp": time.time()
    }


# User For OpenAi 
@app.post("/api/generate-prompts", response_model=PromptsResponse)
async def generate_prompts(request: GeneratePromptsRequest):
    """
    Stage 1: Generate image prompts for hero, features, and testimonials sections
    """
    logger.info("=" * 60)
    logger.info("STAGE 1: Generate Image Prompts - Request Received")
    logger.info(f"Description length: {len(request.description) if request.description else 0}")
    logger.info(f"Description preview: {request.description[:100] if request.description else 'None'}...")
    
    if not request.description or len(request.description.strip()) < 10:
        logger.warning("Invalid request: Description too short")
        raise HTTPException(status_code=400, detail="Description must be at least 10 characters long")

    section_configs = {
        "hero": {
            "focus": "main hero banner background",
            "details": "wide aspect ratio, eye-catching, professional, suitable for large header area with text overlay space"
        },
        "features": {
            "focus": "features section background or icon illustration",
            "details": "clean, minimal, supports multiple feature cards, subtle and professional"
        },
        "testimonials": {
            "focus": "testimonials section background",
            "details": "trustworthy, professional atmosphere, subtle patterns or gradients, warm and inviting"
        }
    }
    
    prompt_generator = ImagePromptGenerator()
    stage1_prompt_tokens = 0
    stage1_completion_tokens = 0
    stage1_total_tokens = 0
    
    async def generate_single_prompt(section: str, config: dict) -> tuple:
        """Generate a single prompt for a section"""
        logger.info(f"Generating prompt for section: {section}")
        
        try:
            logger.info(f"Calling DSPy module for {section} prompt generation...")
            loop = asyncio.get_event_loop()
            prompt = await loop.run_in_executor(
                None,
                lambda: prompt_generator(
                    business_description=request.description,
                    section_type=section,
                    section_focus=config['focus'],
                    section_details=config['details']
                )
            )
            logger.info(f"✓ Generated {section} prompt successfully")
            return (section, prompt)
            
        except HTTPException as e:
            logger.error(f"HTTPException for {section}: {e.detail}")
            raise HTTPException(
                status_code=e.status_code,
                detail=f"FALLBACK:{e.detail}"
            )
        except Exception as e:
            logger.error(f"Exception generating {section} prompt: {str(e)}", exc_info=True)
            
            is_rate_limit_error = (
                (litellm and isinstance(e, litellm.RateLimitError)) or
                "RateLimitError" in str(type(e).__name__) or
                "rate limit" in str(e).lower() or
                "quota" in str(e).lower() or
                "exceeded" in str(e).lower()
            )
            
            is_api_key_error = (
                "OPENAI_API_KEY" in str(e) or 
                "api key" in str(e).lower()
            )
            
            if is_rate_limit_error or is_api_key_error:
                logger.warning(f"Error in Stage 1 for {section}, flagging for fallback")
                # Re-raise with special flag for outer handler
                raise HTTPException(
                    status_code=500,
                    detail=f"FALLBACK:Error generating {section} prompt: {str(e)}"
                )
            raise HTTPException(status_code=500, detail=f"Error generating {section} prompt: {str(e)}")
    
    # Create tasks for parallel prompt generation
    tasks = [
        generate_single_prompt(section, config)
        for section, config in section_configs.items()
    ]
    
    try:
        logger.info("Starting parallel prompt generation for all 3 sections...")
        # Generate all prompts in parallel
        results = await asyncio.gather(*tasks)
        prompts = {section: prompt for section, prompt in results}
        logger.info(f"✓ Generated all {len(prompts)} prompts in parallel")
        
    except HTTPException as e:
        logger.error(f"HTTPException in prompt generation: {e.detail}")
        error_detail = str(e.detail)
        error_detail_lower = error_detail.lower()
        
        is_fallback = "FALLBACK:" in error_detail
        is_api_key_error = (
            "OPENAI_API_KEY" in error_detail or
            "api key" in error_detail_lower
        )
        
        if is_fallback or is_api_key_error:
            logger.warning("Error in Stage 1, returning dummy prompts")
            dummy_prompts = {
                "hero": "Wide hero background with abstract gradient shapes and soft lighting, modern SaaS style.",
                "features": "Minimal feature section backdrop with subtle geometric accents and light gradients.",
                "testimonials": "Warm testimonial backdrop with soft gradients and subtle textures for trust."
            }
            return PromptsResponse(prompts=dummy_prompts)
        raise
    except Exception as e:
        logger.error(f"Exception in prompt generation: {str(e)}", exc_info=True)
        error_str = str(e).lower()
        
        is_rate_limit_error = (
            (litellm and isinstance(e, litellm.RateLimitError)) or
            "RateLimitError" in str(type(e).__name__) or
            "rate limit" in error_str or
            "quota" in error_str or
            "exceeded" in error_str
        )
        
        is_api_key_error = (
            "OPENAI_API_KEY" in str(e) or 
            "api key" in error_str
        )
        
        if is_rate_limit_error or is_api_key_error:
            logger.warning("Error in Stage 1, returning static prompts")
            static_prompts = {
                "hero": "Wide hero background with abstract gradient shapes and soft lighting, modern SaaS style.",
                "features": "Minimal feature section backdrop with subtle geometric accents and light gradients.",
                "testimonials": "Warm testimonial backdrop with soft gradients and subtle textures for trust."
            }
            return PromptsResponse(prompts=static_prompts)
        
        raise HTTPException(status_code=500, detail=f"Error generating prompts: {str(e)}")
    
    logger.info(f"STAGE 1 Complete: Generated {len(prompts)} prompts")
    logger.info("=" * 60)
    logger.info("STAGE 1 TOKEN USAGE SUMMARY:")
    logger.info(f"  Prompt tokens: {stage1_prompt_tokens}")
    logger.info(f"  Completion tokens: {stage1_completion_tokens}")
    logger.info(f"  Total tokens: {stage1_total_tokens}")
    logger.info("=" * 60)
    return PromptsResponse(prompts=prompts)


@app.post("/api/generate-images", response_model=ImagesResponse)
async def generate_images(request: GenerateImagesRequest = GenerateImagesRequest()):
    """
    Stage 2: Generate images using DALL-E 3 for each prompt, or use local images if generation fails
    """
    logger.info("=" * 60)
    logger.info("STAGE 2: Generate Images - Request Received")
    logger.info(f"Prompts provided: {bool(request.prompts)}")
    if request.prompts:
        logger.info(f"Prompt sections: {list(request.prompts.keys())}")
        for section, prompt in request.prompts.items():
            logger.info(f"  {section} prompt length: {len(prompt)} chars")
    
    required_sections = ["hero", "features", "testimonials"]
    
    # If no prompts provided, try to use local images as fallback
    if not request.prompts:
        logger.info("No prompts provided, attempting to use local images...")
        images = find_local_images()
        missing_sections = [section for section in required_sections if section not in images]
        if missing_sections:
            logger.warning(f"Missing local images for sections: {missing_sections}")
            raise HTTPException(
                status_code=400,
                detail=f"Prompts are required. Missing prompts for sections: {', '.join(missing_sections)}"
            )
        logger.info(f"Using local images: {list(images.keys())}")
        return ImagesResponse(images=images)
    
    # Verify all required prompts are provided
    for section in required_sections:
        if section not in request.prompts:
            logger.warning(f"Missing prompt for section: {section}")
            raise HTTPException(status_code=400, detail=f"Missing prompt for {section} section")
    
    # Generate images using DALL-E 3
    async def generate_single_image(section: str, prompt: str) -> tuple:
        try:
            logger.info(f"Generating {section} image with DALL-E 3...")
            # Use larger size for hero images
            size = "1792x1024" if section == "hero" else "1024x1024"
            logger.info(f"  Size: {size}, Quality: standard")
            local_url = await call_dalle(section, prompt, size=size, quality="standard")
            
            # Verify file exists
            filename = local_url.split("/")[-1]
            filepath = os.path.join(UPLOAD_DIR, filename)
            if not os.path.exists(filepath):
                logger.error(f"Image file not found: {filepath}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Image file not properly saved for {section} section"
                )
            file_size = os.path.getsize(filepath)
            if file_size == 0:
                logger.error(f"Image file is empty: {filepath}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Image file not properly saved for {section} section"
                )
            logger.info(f"✓ {section} image saved: {filename} ({file_size} bytes)")
            return (section, local_url)
        except HTTPException as e:
            logger.error(f"HTTPException for {section}: {e.detail}")
            # Check for billing/API key errors in HTTPException
            error_detail_lower = str(e.detail).lower()
            is_billing_error = (
                "billing" in error_detail_lower or
                "hard limit" in error_detail_lower or
                "quota" in error_detail_lower or
                "exceeded" in error_detail_lower
            )
            is_api_key_error = (
                "OPENAI_API_KEY" in str(e.detail) or
                "api key" in error_detail_lower or
                "unauthorized" in error_detail_lower
            )
            if is_billing_error or is_api_key_error:
                # Re-raise with a special flag so outer handler can catch it
                raise HTTPException(
                    status_code=e.status_code,
                    detail=f"STATIC_FALLBACK:{e.detail}"
                )
            raise
        except Exception as e:
            logger.error(f"Exception generating {section} image: {str(e)}", exc_info=True)
            error_str = str(e).lower()
            # Check for billing/API key/rate limit errors
            is_billing_error = (
                "billing" in error_str or
                "hard limit" in error_str or
                "quota" in error_str or
                "exceeded" in error_str
            )
            is_api_key_error = (
                "OPENAI_API_KEY" in str(e) or
                "api key" in error_str or
                "unauthorized" in error_str
            )
            is_rate_limit_error = (
                (litellm and isinstance(e, litellm.RateLimitError)) or
                "RateLimitError" in str(type(e).__name__) or
                "rate limit" in error_str
            )
            if is_billing_error or is_api_key_error or is_rate_limit_error:
                # Re-raise with a special flag so outer handler can catch it
                raise HTTPException(
                    status_code=500,
                    detail=f"STATIC_FALLBACK:Error generating {section} image: {str(e)}"
                )
            raise HTTPException(status_code=500, detail=f"Error generating {section} image: {str(e)}")
    
    def get_static_images() -> dict:
        """Get static fallback images - try local images first, then use default URLs"""
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        static_images = {}
        
        # First try to find local images
        try:
            logger.info("Attempting to use local images as fallback...")
            local_images = find_local_images()
            for section in required_sections:
                if section in local_images:
                    # Convert to full URL if it's a relative path
                    img_path = local_images[section]
                    if img_path.startswith("/uploads/"):
                        static_images[section] = f"{base_url}{img_path}"
                    elif img_path.startswith("http"):
                        static_images[section] = img_path
                    else:
                        static_images[section] = f"{base_url}/uploads/{img_path}"
                else:
                    # Use default static image URL
                    static_images[section] = f"{base_url}/uploads/{section}_1766490617.png"
            
            if len(static_images) == len(required_sections):
                logger.info(f"Using local images: {list(static_images.keys())}")
                return static_images
        except Exception as fallback_error:
            logger.warning(f"Could not find local images: {str(fallback_error)}")
        
        # Fallback to default static image URLs
        logger.info("Using default static image URLs")
        for section in required_sections:
            static_images[section] = f"{base_url}/uploads/{section}_1766490617.png"
        
        return static_images
    
    # Create tasks for parallel execution
    tasks = [
        generate_single_image(section, request.prompts[section])
        for section in required_sections
    ]
    
    try:
        logger.info("Starting parallel image generation...")
        results = await asyncio.gather(*tasks)
        images = {section: url for section, url in results}
        logger.info(f"STAGE 2 Complete: Generated {len(images)} images")
        logger.info(f"Image URLs: {images}")
        logger.info("=" * 60)
        logger.info("STAGE 2 API USAGE NOTE:")
        logger.info("  DALL-E 3 image generation does not use tokens")
        logger.info("  Images are billed per image based on size and quality")
        logger.info(f"  Generated {len(images)} images (3 images total)")
        logger.info("=" * 60)
        return ImagesResponse(images=images)
    except HTTPException as e:
        logger.error(f"HTTPException in image generation: {e.detail}")
        error_detail = str(e.detail)
        error_detail_lower = error_detail.lower()
        
        # Check for static fallback flag or specific error types
        is_static_fallback = "STATIC_FALLBACK:" in error_detail
        is_billing_error = (
            "billing" in error_detail_lower or
            "hard limit" in error_detail_lower or
            "quota" in error_detail_lower or
            "exceeded" in error_detail_lower
        )
        is_api_key_error = (
            "OPENAI_API_KEY" in error_detail or
            "api key" in error_detail_lower or
            "unauthorized" in error_detail_lower
        )
        
        if is_static_fallback or is_billing_error or is_api_key_error:
            logger.warning("Billing/API key error in Stage 2, returning static image URLs")
            static_images = get_static_images()
            return ImagesResponse(images=static_images)
        raise
    except Exception as e:
        logger.error(f"Exception in image generation: {str(e)}", exc_info=True)
        error_str = str(e).lower()
        
        # Check for billing/API key/rate limit errors
        is_billing_error = (
            "billing" in error_str or
            "hard limit" in error_str or
            "quota" in error_str or
            "exceeded" in error_str
        )
        is_api_key_error = (
            "OPENAI_API_KEY" in str(e) or
            "api key" in error_str or
            "unauthorized" in error_str
        )
        is_rate_limit_error = (
            (litellm and isinstance(e, litellm.RateLimitError)) or
            "RateLimitError" in str(type(e).__name__) or
            "rate limit" in error_str
        )
        
        if is_billing_error or is_api_key_error or is_rate_limit_error:
            logger.warning("Billing/API key/rate limit error in Stage 2, returning static image URLs")
            static_images = get_static_images()
            return ImagesResponse(images=static_images)
        
        # Try fallback to local images for other errors
        try:
            logger.info("Attempting fallback to local images...")
            images = find_local_images()
            missing_sections = [section for section in required_sections if section not in images]
            if not missing_sections:
                logger.info("Fallback successful: Using local images")
                # Convert to full URLs
                base_url = os.getenv("BASE_URL", "http://localhost:8000")
                full_url_images = {}
                for section, img_path in images.items():
                    if img_path.startswith("/uploads/"):
                        full_url_images[section] = f"{base_url}{img_path}"
                    elif img_path.startswith("http"):
                        full_url_images[section] = img_path
                    else:
                        full_url_images[section] = f"{base_url}/uploads/{img_path}"
                return ImagesResponse(images=full_url_images)
        except Exception as fallback_error:
            logger.error(f"Fallback failed: {str(fallback_error)}")
        
        raise HTTPException(status_code=500, detail=f"Error generating images: {str(e)}")

@app.post("/api/generate-html", response_model=HTMLResponse)
async def generate_html(request: GenerateHTMLRequest):
    """
    Stage 3: Generate HTML landing page using Azure OpenAI GPT-5
    If template is provided, modify the template according to the description.
    If no template, generate HTML from scratch.
    """
    logger.info("=" * 60)
    logger.info("STAGE 3: Generate HTML - Request Received")
    logger.info(f"Description length: {len(request.description) if request.description else 0}")
    logger.info(f"Template provided: {bool(request.template)}")
    if request.template:
        logger.info(f"Template length: {len(request.template)} chars")
    logger.info(f"Images provided: {bool(request.images)}")
    if request.images:
        logger.info(f"Image sections: {list(request.images.keys())}")
        for section, url in request.images.items():
            logger.info(f"  {section}: {url}")
    
    if not request.description or len(request.description.strip()) < 10:
        logger.warning("Invalid request: Description too short")
        raise HTTPException(status_code=400, detail="Description must be at least 10 characters long")
    
    if not request.images:
        logger.warning("Invalid request: No images provided")
        raise HTTPException(status_code=400, detail="Images are required")
    
    required_images = ["hero", "features", "testimonials"]
    for section in required_images:
        if section not in request.images:
            logger.warning(f"Missing image URL for section: {section}")
            raise HTTPException(status_code=400, detail=f"Missing image URL for {section} section")
    
    # Build enhanced user prompt with detailed instructions
    # Convert local paths to full URLs for iframe compatibility
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    logger.info(f"Base URL: {base_url}")
    image_urls = {}
    for section in required_images:
        image_path = request.images[section]
        # If it's a local path starting with /uploads, convert to full URL
        if image_path.startswith("/uploads/"):
            image_urls[section] = f"{base_url}{image_path}"
        elif image_path.startswith("http"):
            image_urls[section] = image_path  # Already a full URL
        else:
            image_urls[section] = image_path  # Keep as-is
        logger.info(f"Converted {section} URL: {image_urls[section]}")
    
    image_urls_text = "\n".join([f"- {section.capitalize()}: {image_urls[section]}" for section in required_images])
    logger.info(f"Image URLs text: {image_urls_text}")

    # Check if template is provided
    try:
        if request.template and request.template.strip():
            logger.info("Using template-based generation with DSPy")
            # Use DSPy TemplateModifier module
            template_modifier = TemplateModifier()
            logger.info("Calling DSPy TemplateModifier module...")
            html = template_modifier(
                template_html=request.template,
                description=request.description,
                image_urls_text=image_urls_text
            )
        else:
            logger.info("Generating HTML from scratch with DSPy")
            # Use DSPy LandingPageGenerator module
            landing_page_generator = LandingPageGenerator()
            logger.info("Calling DSPy LandingPageGenerator module...")
            html = landing_page_generator(
                description=request.description,
                image_urls_text=image_urls_text
            )
        
        logger.info(f"Received HTML response (length: {len(html)} chars)")
        
        # Enhanced cleanup
        html = html.strip()
        
        # Remove markdown code blocks if present
        if html.startswith("```html"):
            logger.info("Removing ```html markdown wrapper")
            html = html[7:]
        elif html.startswith("```"):
            logger.info("Removing ``` markdown wrapper")
            html = html[3:]
            
        if html.endswith("```"):
            logger.info("Removing trailing ``` markdown wrapper")
            html = html[:-3]
            
        html = html.strip()
        logger.info(f"Cleaned HTML length: {len(html)} chars")
        
        # Validate HTML structure
        if not html.startswith("<!DOCTYPE") and not html.startswith("<html"):
            logger.error(f"Invalid HTML structure. First 100 chars: {html[:100]}")
            raise HTTPException(
                status_code=500,
                detail="Generated content is not valid HTML"
            )
        
        # Extract CSS from style tags and replace with external link
        html_with_link, extracted_css = extract_css_and_replace_style_tags(html)
        logger.info(f"Extracted CSS length: {len(extracted_css)} chars")
        
        logger.info("✓ STAGE 3 Complete: HTML generated successfully")
        logger.info("=" * 60)
        logger.info("STAGE 3 TOKEN USAGE SUMMARY:")
        # logger.info(f"  Prompt tokens: {stage3_prompt_tokens}")
        # logger.info(f"  Completion tokens: {stage3_completion_tokens}")
        # logger.info(f"  Total tokens: {stage3_total_tokens}")
        logger.info("=" * 60)
        logger.info("=" * 60)
        logger.info("COMPLETE PROCESS TOKEN USAGE SUMMARY")
        logger.info("=" * 60)
        logger.info("STAGE 1 (Generate Prompts):")
        logger.info("  - Check logs above for Stage 1 token usage")
        logger.info("  - Generated 3 image prompts (hero, features, testimonials)")
        logger.info("STAGE 2 (Generate Images):")
        logger.info("  - DALL-E 3 API (does not use tokens)")
        logger.info("  - Generated 3 images")
        logger.info("STAGE 3 (Generate HTML):")
        # logger.info(f"  Prompt tokens: {stage3_prompt_tokens}")
        # logger.info(f"  Completion tokens: {stage3_completion_tokens}")
        # logger.info(f"  Total tokens: {stage3_total_tokens}")
        logger.info("=" * 60)
        logger.info("NOTE: For complete token usage across all stages,")
        logger.info("      check Stage 1 logs above for prompt generation tokens.")
        logger.info("=" * 60)
        return HTMLResponse(html=html_with_link, css=extracted_css)
        
    except HTTPException as e:
        logger.error(f"HTTPException in HTML generation: {e.detail}")
        # Fallback when OpenAI key is invalid or missing
        if "OPENAI_API_KEY" in str(e.detail) or "api key" in str(e.detail).lower():
            logger.warning("OpenAI API key error encountered, returning fallback HTML/CSS")
            return HTMLResponse(html=fallback_html, css=fallback_css)
        raise
    except Exception as e:
        logger.error(f"Exception in HTML generation: {str(e)}", exc_info=True)
        
        # Check for rate limit or quota errors
        is_rate_limit_error = (
            (litellm and isinstance(e, litellm.RateLimitError)) or
            "RateLimitError" in str(type(e).__name__) or
            "rate limit" in str(e).lower() or
            "quota" in str(e).lower() or
            "exceeded" in str(e).lower()
        )
        
        if is_rate_limit_error:
            logger.warning("Rate limit/quota error in Stage 3, returning static HTML/CSS")
            return HTMLResponse(html=fallback_html, css=fallback_css)
        
        # Fallback when OpenAI key is invalid or missing
        if "OPENAI_API_KEY" in str(e) or "api key" in str(e).lower():
            logger.warning("OpenAI API key error encountered, returning fallback HTML/CSS")
            return HTMLResponse(html=fallback_html, css=fallback_css)
        raise HTTPException(status_code=500, detail=f"Error generating HTML: {str(e)}")


@app.post("/api/edit-html", response_model=EditHTMLResponse)
async def edit_html(request: EditHTMLRequest):
    """
    Stage 4: Edit existing HTML/CSS content based on user's edit request
    """
    logger.info("=" * 60)
    logger.info("STAGE 4: Edit HTML - Request Received")
    logger.info(f"HTML content length: {len(request.html) if request.html else 0}")
    logger.info(f"CSS content length: {len(request.css) if request.css else 0}")
    logger.info(f"Edit request: {request.edit_request[:100] if request.edit_request else 'None'}...")
    
    if not request.html or not request.html.strip():
        logger.warning("Invalid request: HTML content is required")
        raise HTTPException(status_code=400, detail="HTML content is required")
    
    # CSS can be empty if HTML has link tag, but we'll extract it from HTML if needed
    css_content = request.css or ''
    
    # If CSS is empty, try to extract from HTML style tags
    if not css_content.strip():
        logger.info("CSS not provided, attempting to extract from HTML style tags...")
        style_pattern = r'<style[^>]*>(.*?)</style>'
        css_matches = re.findall(style_pattern, request.html, re.DOTALL | re.IGNORECASE)
        if css_matches:
            css_content = '\n\n'.join(css_matches).strip()
            logger.info(f"Extracted CSS from HTML (length: {len(css_content)} chars)")
    
    # If still no CSS and HTML has link tag, that's okay - we'll work with HTML only
    # But for the AI prompt, we need some CSS content, so use empty string
    if not css_content.strip():
        css_content = ''  # Allow empty CSS if HTML uses external stylesheet
        logger.info("No CSS found, proceeding with HTML only")
    
    if not request.edit_request or len(request.edit_request.strip()) < 5:
        logger.warning("Invalid request: Edit request too short")
        raise HTTPException(status_code=400, detail="Edit request must be at least 5 characters long")
    
    try:
        logger.info("Calling DSPy HTMLEditor module for HTML edit...")
        # Use DSPy HTMLEditor module
        html_editor = HTMLEditor()
        modified_html = html_editor(
            html=request.html,
            css=css_content,
            edit_request=request.edit_request
        )
        
        # Extract token usage from DSPy LM history
        # edit_prompt_tokens = 0
        # edit_completion_tokens = 0
        # edit_total_tokens = 0
        
        # if hasattr(dspy_llm, 'history') and dspy_llm.history:
        #     last_call = dspy_llm.history[-1]
        #     if hasattr(last_call, 'usage'):
        #         usage = last_call.usage
        #         edit_prompt_tokens = getattr(usage, 'prompt_tokens', 0)
        #         edit_completion_tokens = getattr(usage, 'completion_tokens', 0)
        #         edit_total_tokens = getattr(usage, 'total_tokens', 0)
        #     elif isinstance(last_call, dict):
        #         edit_prompt_tokens = last_call.get('prompt_tokens', 0)
        #         edit_completion_tokens = last_call.get('completion_tokens', 0)
        #         edit_total_tokens = last_call.get('total_tokens', edit_prompt_tokens + edit_completion_tokens)
        #     else:
        #         edit_prompt_tokens = getattr(last_call, 'prompt_tokens', 0)
        #         edit_completion_tokens = getattr(last_call, 'completion_tokens', 0)
        #         edit_total_tokens = edit_prompt_tokens + edit_completion_tokens
        
        logger.info(f"Received modified HTML response (length: {len(modified_html)} chars)")
        
        # Enhanced cleanup
        modified_html = modified_html.strip()
        
        # Remove markdown code blocks if present
        if modified_html.startswith("```html"):
            logger.info("Removing ```html markdown wrapper")
            modified_html = modified_html[7:]
        elif modified_html.startswith("```"):
            logger.info("Removing ``` markdown wrapper")
            modified_html = modified_html[3:]
            
        if modified_html.endswith("```"):
            logger.info("Removing trailing ``` markdown wrapper")
            modified_html = modified_html[:-3]
            
        modified_html = modified_html.strip()
        logger.info(f"Cleaned modified HTML length: {len(modified_html)} chars")
        
        # Validate HTML structure
        if not modified_html.startswith("<!DOCTYPE") and not modified_html.startswith("<html"):
            logger.error(f"Invalid HTML structure. First 100 chars: {modified_html[:100]}")
            raise HTTPException(
                status_code=500,
                detail="Modified content is not valid HTML"
            )
        
        # Extract CSS from style tags and replace with external link
        html_with_link, extracted_css = extract_css_and_replace_style_tags(modified_html)
        logger.info(f"Extracted CSS length: {len(extracted_css)} chars")
        
        logger.info("✓ STAGE 4 Complete: HTML edited successfully")
        logger.info("=" * 60)
        logger.info("STAGE 4 (EDIT) TOKEN USAGE SUMMARY:")
        # logger.info(f"  Prompt tokens: {edit_prompt_tokens}")
        # logger.info(f"  Completion tokens: {edit_completion_tokens}")
        # logger.info(f"  Total tokens: {edit_total_tokens}")
        logger.info("=" * 60)
        return EditHTMLResponse(html=html_with_link, css=extracted_css)
        
    except HTTPException as e:
        logger.error(f"HTTPException in HTML edit: {e.detail}")
        # Fallback when OpenAI key is invalid or missing
        if "OPENAI_API_KEY" in str(e.detail) or "api key" in str(e.detail).lower():
            logger.warning("OpenAI API key error encountered, returning fallback HTML/CSS")
            return EditHTMLResponse(html=edit_fallback_html, css=edit_fallback_css)
        raise
    except Exception as e:
        logger.error(f"Exception in HTML edit: {str(e)}", exc_info=True)
        
        # Check for rate limit or quota errors
        is_rate_limit_error = (
            (litellm and isinstance(e, litellm.RateLimitError)) or
            "RateLimitError" in str(type(e).__name__) or
            "rate limit" in str(e).lower() or
            "quota" in str(e).lower() or
            "exceeded" in str(e).lower()
        )
        
        if is_rate_limit_error:
            logger.warning("Rate limit/quota error in Stage 4, returning fallback HTML/CSS")
            return EditHTMLResponse(html=edit_fallback_html, css=edit_fallback_css)
        
        # Fallback when OpenAI key is invalid or missing
        if "OPENAI_API_KEY" in str(e) or "api key" in str(e).lower():
            logger.warning("OpenAI API key error encountered, returning fallback HTML/CSS")
            return EditHTMLResponse(html=edit_fallback_html, css=edit_fallback_css)
        
        raise HTTPException(status_code=500, detail=f"Error editing HTML: {str(e)}")


@app.post("/api/update-website", response_model=UpdateWebsiteResponse)
async def update_website(request: UpdateWebsiteRequest):
    """
    Smart Website Update: Update multi-page websites based on natural language instructions.
    
    This endpoint intelligently determines what to update based on the user's request:
    - Global styling (colors, fonts, spacing in style.css)
    - Individual page content (HTML)
    - Multiple pages at once
    - Combination of styling + content
    
    The API analyzes the request and applies updates accordingly, returning only the
    modified files.
    
    Optionally, if folder_path is provided, saves the updates directly to the website folder.
    """
    logger.info("=" * 60)
    logger.info("SMART WEBSITE UPDATE - Request Received")
    logger.info(f"Edit request: {request.edit_request[:100]}...")
    logger.info(f"Number of pages provided: {len(request.pages)}")
    logger.info(f"Pages: {list(request.pages.keys())}")
    logger.info(f"Global CSS provided: {bool(request.global_css)}")
    logger.info(f"Folder path provided: {bool(request.folder_path)}")
    logger.info(f"🔍 FOLDER PATH VALUE: {repr(request.folder_path)}")
    logger.info("=" * 60)
    
    # Validation
    if not request.edit_request or len(request.edit_request.strip()) < 5:
        logger.warning("Invalid request: Edit request too short")
        raise HTTPException(
            status_code=400,
            detail="Edit request must be at least 5 characters long"
        )
    
    if not request.pages or len(request.pages) == 0:
        logger.warning("Invalid request: No pages provided")
        raise HTTPException(
            status_code=400,
            detail="At least one page must be provided"
        )
    
    try:
        # Import WebsiteUpdater module
        from app.dspy_modules import WebsiteUpdater
        
        logger.info("Initializing WebsiteUpdater module...")
        updater = WebsiteUpdater()
        
        # Apply smart updates
        logger.info("Analyzing and applying updates...")
        result = updater(
            pages=request.pages,
            global_css=request.global_css or "",
            edit_request=request.edit_request
        )
          
        updated_pages = result.get("updated_pages", {})
        updated_global_css = result.get("updated_global_css")
        changes_summary = result.get("changes_summary", "Updates applied")
        
        logger.info(f"Updates complete: {changes_summary}")
        logger.info(f"Updated pages: {list(updated_pages.keys())}")
        logger.info(f"Global CSS updated: {bool(updated_global_css)}")
        
        # Optional: Save to folder if path provided
        saved_folder_path = None
        
        logger.info("🔍 FILE SAVE CHECK:")
        logger.info(f"  folder_path exists: {bool(request.folder_path)}")
        logger.info(f"  folder_path value: {repr(request.folder_path)}")
        logger.info(f"  updated_pages exists: {bool(updated_pages)}")
        logger.info(f"  updated_global_css exists: {bool(updated_global_css)}")
        logger.info(f"  Will save: {bool(request.folder_path and (updated_pages or updated_global_css))}")
        
        if request.folder_path and (updated_pages or updated_global_css):
            try:
                logger.info(f"Saving updates to folder: {request.folder_path}")
                from app.file_manager import WebsiteFileManager
                
                file_manager = WebsiteFileManager()
                
                # Verify folder exists
                if not os.path.exists(request.folder_path):
                    logger.warning(f"Folder does not exist: {request.folder_path}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Folder path does not exist: {request.folder_path}"
                    )
                
                # Save updated pages
                if updated_pages:
                    for page_name, page_content in updated_pages.items():
                        html = page_content.get('html', '')
                        css = page_content.get('css', '')
                        
                        # Clean HTML and extract CSS
                        html_clean, extracted_css = file_manager.extract_css_from_html(html)
                        
                        # If global CSS is being used, link to it
                        if updated_global_css:
                            html_final = file_manager.add_css_link_to_html(html_clean, "style.css")
                        else:
                            html_final = html_clean
                        
                        # Save HTML file
                        html_path = os.path.join(request.folder_path, f"{page_name}.html")
                        with open(html_path, 'w', encoding='utf-8') as f:
                            f.write(html_final)
                        logger.info(f"✓ Saved updated HTML: {html_path}")
                
                # Save updated global CSS
                if updated_global_css:
                    css_path = os.path.join(request.folder_path, "style.css")
                    with open(css_path, 'w', encoding='utf-8') as f:
                        f.write(updated_global_css)
                    logger.info(f"✓ Saved updated global CSS: {css_path}")
                
                saved_folder_path = request.folder_path
                logger.info(f"✓ All updates saved to: {saved_folder_path}")
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error saving to folder: {str(e)}", exc_info=True)
                # Don't fail the request, just log the error
                logger.warning("File saving failed, but updates are still returned in response")
        
        logger.info("✓ SMART WEBSITE UPDATE Complete")
        logger.info("=" * 60)
        
        return UpdateWebsiteResponse(
            updated_pages=updated_pages,
            updated_global_css=updated_global_css,
            changes_summary=changes_summary,
            folder_path=saved_folder_path,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in smart website update: {str(e)}", exc_info=True)
        
        # Check for rate limit or quota errors
        is_rate_limit_error = (
            (litellm and isinstance(e, litellm.RateLimitError)) or
            "RateLimitError" in str(type(e).__name__) or
            "rate limit" in str(e).lower() or
            "quota" in str(e).lower() or
            "exceeded" in str(e).lower()
        )
        
        if is_rate_limit_error:
            logger.warning("Rate limit/quota error in website update")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error updating website: {str(e)}"
        )


def _convert_messages_to_langchain(messages_dicts):
    """Convert message dictionaries from frontend to LangChain message objects."""
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    
    if not messages_dicts:
        return []
    
    langchain_messages = []
    for msg_dict in messages_dicts:
        role = msg_dict.get("role", "human")
        content = msg_dict.get("content", "")
        
        # Map role to appropriate message class
        if role in ["human", "user"]:
            langchain_messages.append(HumanMessage(content=content))
        elif role in ["ai", "assistant"]:
            langchain_messages.append(AIMessage(content=content))
        elif role == "system":
            langchain_messages.append(SystemMessage(content=content))
        else:
            # Default to human message
            langchain_messages.append(HumanMessage(content=content))
    
    return langchain_messages


# New LangGraph workflow endpoint
@app.post("/api/generate-website")
async def generate_website(request: GenerateWebsiteRequest):
    """
    Generate complete multi-page website using LangGraph workflow.
    
    Workflow steps:
    1. Planning: Generate website structure and strategy
    2. Image Description: Create targeted image descriptions
    3. Image Generation: Generate images with DALL-E 3
    4. HTML Generation: Create multi-page HTML/CSS
    
    Returns streaming response with progress updates.
    """
    logger.info("=" * 60)
    logger.info("LangGraph Website Generation - Request Received")
    logger.info(f"Description: {request.description[:100]}...")
    template_provided = hasattr(request, 'template') and request.template
    logger.info(f"Template provided: {bool(template_provided)}")
    if template_provided:
        logger.info(f"Template length: {len(request.template)} chars")
    logger.info("=" * 60)
    
    if not request.description or len(request.description.strip()) < 10:
        logger.warning("Invalid request: Description too short")
        raise HTTPException(
            status_code=400,
            detail="Description must be at least 10 characters long"
        )
    
    async def event_stream():
        """Stream workflow progress as Server-Sent Events."""
        try:
            # Use provided thread_id or generate new one for conversation continuity
            thread_id_str = request.thread_id or str(int(time.time()))
            thread_id = {"configurable": {"thread_id": thread_id_str}}
            logger.info(f"Using thread_id: {thread_id_str}")
            
            # Initialize workflow state with business gathering support
            initial_state: WorkflowState = {
                "description": request.description,
                "template": request.template if hasattr(request, 'template') else None,
                
                # Business gathering fields (NEW)
                "ready": False,
                "business_plan": None,
                "clarification_questions": None,
                
                # Planning fields
                "plan": None,
                "plan_json": None,
                "template_styling": None,
                "css_theme": None,
                
                # Image fields
                "image_descriptions": None,
                "image_urls": None,
                
                # HTML generation fields
                "pages": None,
                "folder_path": None,
                "saved_files": None,
                
                # Status tracking
                "current_step": "business_gathering",
                "status": "in_progress",
                "error": None,
                "progress": 0,
                "progress_message": "Starting website generation...",
                
                # Conversation messages - convert from dict format to LangChain messages
                "messages": _convert_messages_to_langchain(request.messages) if request.messages else []
            }
            
            # Stream workflow execution
            logger.info("Starting LangGraph workflow execution...")
            
            async for event in website_workflow.astream(initial_state, thread_id):
                # Extract state from event
                if isinstance(event, dict):
                    # Get the latest node's state
                    for node_name, node_state in event.items():
                        if isinstance(node_state, dict):
                            logger.info(f"Node '{node_name}' completed")
                            
                            # Skip sending intermediate "awaiting_input" events from business_gathering
                            # We'll send the complete event with questions after streaming finishes
                            if (node_name == "business_gathering" and 
                                node_state.get("status") == "awaiting_input" and 
                                not node_state.get("ready", True)):
                                logger.info("Skipping intermediate business gathering event (will send complete event with questions)")
                                continue
                            
                            # Send progress update
                            progress_data = {
                                "step": node_state.get("current_step", "unknown"),
                                "status": node_state.get("status", "in_progress"),
                                "progress": node_state.get("progress", 0),
                                "message": node_state.get("progress_message", ""),
                                "error": node_state.get("error")
                            }
                            
                            # Send as SSE
                            yield f"data: {json.dumps(progress_data)}\n\n"
                            
                            # Check for errors
                            if node_state.get("status") == "failed":
                                logger.error(f"Workflow failed: {node_state.get('error')}")
                                return
            
            # Get final state
            final_state = website_workflow.get_state(thread_id).values
            
            # Check if business gathering needs more information
            if not final_state.get("ready") and final_state.get("clarification_questions"):
                logger.info("Business gathering needs more information")
                
                # Convert LangChain messages to JSON-serializable format
                messages = final_state.get("messages", [])
                serializable_messages = []
                for msg in messages:
                    if hasattr(msg, 'content'):
                        # Get content and ensure it's a string
                        content = str(msg.content) if msg.content else ""
                        
                        # Truncate very long messages and remove problematic characters
                        # Convert newlines to spaces to avoid JSON issues
                        content = content.replace('\n', ' ').replace('\r', ' ')
                        
                        # Limit length to prevent huge payloads
                        if len(content) > 500:
                            content = content[:497] + "..."
                        
                        # Map message class names to LangChain-compatible role names
                        role_mapping = {
                            'HumanMessage': 'human',
                            'AIMessage': 'ai',
                            'SystemMessage': 'system',
                            'FunctionMessage': 'function',
                            'ToolMessage': 'tool'
                        }
                        
                        class_name = msg.__class__.__name__
                        role = role_mapping.get(class_name, 'human')  # Default to 'human' if unknown
                        
                        serializable_messages.append({
                            "role": role,
                            "content": content
                        })
                
                questions_result = {
                    "step": "business_gathering",
                    "status": "awaiting_input",
                    "progress": 5,
                    "ready": False,
                    "questions": final_state.get("clarification_questions", []),
                    "business_plan": final_state.get("business_plan"),
                    "thread_id": thread_id_str,  # Return thread_id for next request
                    "message": "Please provide more information",
                    "messages": serializable_messages  # Converted to JSON-serializable format
                }
                yield f"data: {json.dumps(questions_result)}\n\n"
                return
            
            # Check if workflow completed successfully
            if final_state.get("status") == "completed":
                logger.info("✓ Website generation completed successfully")
                
                # Send final result
                result = {
                    "step": "complete",
                    "status": "completed",
                    "progress": 100,
                    "ready": True,
                    "thread_id": thread_id_str,
                    "message": "✓ Website generation complete",
                    "data": {
                        "pages": final_state.get("pages", {}),
                        "image_urls": final_state.get("image_urls", {}),
                        "plan": final_state.get("plan", {}),
                        "business_plan": final_state.get("business_plan"),
                        "folder_path": final_state.get("folder_path"),
                        "saved_files": final_state.get("saved_files", {})
                    }
                }
                yield f"data: {json.dumps(result)}\n\n"
            else:
                logger.error("Workflow did not complete successfully")
                error_data = {
                    "step": "failed",
                    "status": "failed",
                    "progress": final_state.get("progress", 0),
                    "thread_id": thread_id_str,
                    "message": final_state.get("error", "Unknown error"),
                    "error": final_state.get("error")
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                
        except Exception as e:
            logger.error(f"Error in workflow execution: {str(e)}", exc_info=True)
            error_data = {
                "step": "failed",
                "status": "failed",
                "progress": 0,
                "message": f"Error: {str(e)}",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    # Return streaming response
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Access-Control-Allow-Origin": "*",  # CORS for streaming
        }
    )


# Run the application (uvicorn imported at top)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
