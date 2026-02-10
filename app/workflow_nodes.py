"""
LangGraph workflow nodes for website generation.
"""
import json
import logging
import os
import httpx
import time
from typing import Dict, List, Optional
from app.workflow_state import WorkflowState
from app.dspy_modules import WebsitePlanner, ImageDescriptionGenerator, MultiPageGenerator, TemplateAnalyzer
from app.file_manager import WebsiteFileManager
import asyncio
from app.utils import call_dalle
from openai import AzureOpenAI
from dotenv import load_dotenv
import re
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure OpenAI client for DALL-E 3
azure_client = AzureOpenAI(
    api_key=os.getenv("AZURE_AI_TOKEN"),
    api_version=os.getenv("AZURE_AI_APP_VERSION"),
    azure_endpoint=os.getenv("AZURE_AI_ENDPOINT_URL")
)
api_key = os.getenv("OPENAI_API_KEY_PLAN")

# Business gathering LLM (Claude Sonnet for intelligent questioning)
# business_gathering_llm = init_chat_model(model="anthropic:claude-sonnet-4-5-20250929")
# business_gathering_llm = init_chat_model(model="gemini:gemini-2.5-flash")
business_gathering_llm = init_chat_model(model="openai:gpt-4o", api_key=api_key)

# System prompt for business gathering
BUSINESS_GATHERING_SYSTEM_PROMPT = SystemMessage(content="""
You are a senior website planner AI with strong industry experience.
Your goal is to gather sufficient information through iterative conversation before developing a website.

CRITICAL WORKFLOW - PROGRESSIVE PLAN REFINEMENT:

**EVERY ITERATION, YOU MUST:**
1. Analyze the current conversation (all user messages)
2. Generate a business_plan (draft or refined) based on what you know so far
3. Decide if you need more information (ready=false) or if you can proceed (ready=true)
4. If ready=false, ask 2-3 specific questions to refine the plan further

**ITERATION 1 (First user message):**
- User provides initial description: "generate website for cloud kitchen"
- You analyze and create DRAFT business_plan based on what you know
- You MUST ask questions to refine the plan (ready=false)
- Return: {ready: false, questions: [...], business_plan: "draft plan based on cloud kitchen"}

**ITERATION 2 (User answers questions):**
- User provides more details: "I need home, menu, contact for busy professionals"
- You REFINE the business_plan with new information
- Decide: Do I need more details? Or is this sufficient?
- If need more: ready=false, ask specific questions
- If sufficient: ready=true, finalized plan
- Return: {ready: false/true, questions: [...], business_plan: "refined plan with pages and audience"}

**ITERATION 3+ (If needed):**
- User provides more answers
- You FURTHER REFINE the business_plan
- Continue asking questions OR set ready=true when satisfied

**STOPPING CONDITIONS (ready=true):**
- User explicitly says: "ready to generate", "go ahead", "this is sufficient", "you decide"
- OR you have gathered enough information (pages, audience, goal clearly defined)

**BUSINESS PLAN FORMAT (Always generate, even when asking questions):**
The business_plan should include:
- Business type and description
- Target audience
- Required pages/sections (if known, otherwise "to be determined")
- Main website goal
- Any specific features or requirements mentioned
- Current assumptions (mark what needs clarification)

Example business_plan at different stages:
- Draft (Iteration 1): "Cloud kitchen business. Need website. Pages TBD, audience TBD, goal: likely online ordering and info."
- Refined (Iteration 2): "Cloud kitchen targeting busy professionals. Pages: home, menu, contact. Goal: showcase menu and enable orders. Design: modern, clean."
- Finalized (Iteration 3): "Cloud kitchen 'QuickBite' for busy urban professionals aged 25-40. Pages: home (hero, features, CTA), menu (categories, items), contact (form, location). Goal: drive online orders. Design: modern, vibrant food imagery."

FIRST INTERACTION QUESTIONS (Always ask 2-3 questions):
- What specific pages or sections do you need? (e.g., home, about, services, blog, contact)
- Who is your target audience?
- What is the main goal of this website? (e.g., lead generation, portfolio, e-commerce, information)
- Any specific features or functionality required?

FOLLOW-UP QUESTIONS (Ask to refine unclear points):
- Clarify specific page requirements if vague
- Confirm business details if unclear
- Ask about design preferences, brand colors, specific features

Rules:
- ALWAYS generate business_plan in EVERY response (even when ready=false)
- Progressively refine the plan with each user answer
- Ask 2-3 relevant questions when ready=false
- Set ready=true only when you have sufficient details OR user says "go ahead"

CRITICAL OUTPUT RULES:
- Respond with ONLY valid JSON
- Output must start with { and end with }
- NO markdown code fences (no ```json)
- NO extra text before or after the JSON
- ONLY the raw JSON object

JSON FORMAT when asking questions (ready=false):
{
  "ready": false,
  "questions": ["What specific pages do you need?", "Who is your target audience?"],
  "business_plan": "Current understanding: Cloud kitchen business. Website needed. [Details about what's known so far, what's TBD]"
}

JSON FORMAT when ready to proceed (ready=true):
{
  "ready": true,
  "questions": [],
  "business_plan": "Finalized plan: [Complete detailed understanding including pages, audience, goals, features]"
}

Business description 
""")


def extract_json(text) -> dict:
    """Extract JSON from text, handling markdown code fences and extra whitespace."""
    # Handle non-string inputs (like empty lists from Claude)
    if not isinstance(text, str):
        logger.warning(f"extract_json received non-string input: {type(text)} = {text}")
        if isinstance(text, list) and len(text) == 0:
            # Empty list - return "not ready" without questions
            # The business_gathering_node will handle asking for more info
            return {
                "ready": False,
                "questions": [],
                "business_plan": ""
            }
        # Try to convert to string
        text = str(text)
    
    text = text.strip()
    
    # Handle malformed/truncated responses
    if len(text) < 10 or not any(c in text for c in ['{', 'ready', 'questions']):
        logger.error(f"Malformed LLM response (too short or missing JSON markers): {text}")
        return {
            "ready": False,
            "questions": ["Please provide more details about your business and website requirements."],
            "business_plan": ""
        }
    
    # Try to extract JSON from markdown code fence
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        text = json_match.group(1)
    
    # Try to extract JSON object directly
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        text = json_match.group(0)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {text[:200]}")
        logger.error(f"JSON decode error: {e}")
        # Return a safe fallback instead of crashing
        return {
            "ready": False,
            "questions": ["I had trouble processing that. Please describe your business and website needs in more detail."],
            "business_plan": ""
        }


async def business_gathering_node(state: WorkflowState) -> WorkflowState:
    """
    Step 0: Gather and validate business information.
    Asks clarifying questions if needed, or proceeds if sufficient information is provided.
    """
    logger.info("Starting business gathering node...")
    
    try:
        # Get conversation messages from state
        messages = state.get("messages", [])
        description = state.get("description", "")
        
        logger.info(f"Existing messages: {len(messages)}")
        logger.info(f"New description: {description[:100] if description else 'None'}...")
        
        # Build message history
        if not messages:
            # First time - create initial message from description
            if description:
                messages = [HumanMessage(content=description)]
                logger.info("Created initial message from description")
            else:
                # No description at all - create a message asking for information
                logger.info("No description provided, creating initial request message")
                messages = [HumanMessage(content="I want to create a website but I need help figuring out what I need.")]
        else:
            # Subsequent calls - append new user input to message history
            if description:
                # Check if this is a new message (not already in history)
                if not messages or not isinstance(messages[-1], HumanMessage) or messages[-1].content != description:
                    messages = messages + [HumanMessage(content=description)]
                    logger.info("Appended new user message to conversation history")
        
        # Call LLM to analyze business information with full conversation context
        logger.info(f"Analyzing business information with {len(messages)} messages...")
        
        # FIXED: Changed from .invoke() to .ainvoke() for async operation
        response = await business_gathering_llm.ainvoke(
            [BUSINESS_GATHERING_SYSTEM_PROMPT] + messages
        )
        
        # Debug: Log response details
        logger.info(f"LLM Response type: {type(response)}")
        logger.info(f"LLM Response content preview: {response.content[:200] if isinstance(response.content, str) else response.content}")
        
        # Extract and parse JSON from response
        data = extract_json(response.content)
        
        # Check if we're ready to proceed
        if not data.get("ready"):
            # Need more information - ask questions
            questions = data.get("questions", [])
            
            # Note: extract_json already provides fallback questions for error cases
            # If we get here with empty questions, it's from extract_json's error handling
            
            questions_text = "\n".join(f"- {q}" for q in questions)
            content = f"I need more information:\n{questions_text}"
            
            logger.info(f"Business information insufficient. Asking {len(questions)} questions.")
            
            business_plan = data.get("business_plan", "")
            
            return {
                **state,
                "ready": False,
                "business_plan": business_plan,
                "clarification_questions": questions,
                "current_step": "business_gathering",
                "status": "awaiting_input",
                "progress": 5,
                "progress_message": "Waiting for additional business information",
                "messages": messages + [AIMessage(content=content)]
            }
        
        # We have enough information - proceed
        business_plan = data.get("business_plan", "")
        logger.info(f"✓ Business information gathered successfully")
        logger.info(f"Business plan: {business_plan[:200]}...")
        
        return {
            **state,
            "ready": True,
            "business_plan": business_plan,
            "clarification_questions": [],
            "current_step": "planning",
            "status": "in_progress",
            "progress": 10,
            "progress_message": "✓ Business information gathered, proceeding to planning",
            "messages": messages + [AIMessage(content=f"Great! I have enough information to proceed. Here's my understanding:\n\n{business_plan}")]
        }
        
    except Exception as e:
        logger.error(f"Business gathering node error: {str(e)}")
        return {
            **state,
            "current_step": "failed",
            "status": "failed",
            "error": f"Business gathering failed: {str(e)}",
            "progress": 0,
            "progress_message": f"✗ Business gathering failed: {str(e)}"
        }



def planning_node(state: WorkflowState) -> WorkflowState:
    """
    Step 1: Generate comprehensive website plan.
    PRIMARY: Analyze business requirements
    SECONDARY: Extract template styling as reference (if template provided)
    BALANCE: Generate plan prioritizing business needs with template design consistency
    """
    logger.info("Starting planning node...")
    
    try:
        # import pdb
        # pdb.set_trace()
        # PRIMARY: Use business_plan from gathering phase (with fallback to description)
        # The business_plan contains the analyzed and validated business requirements
        business_description = state.get("business_plan", state.get("description", ""))
        
        if state.get("business_plan"):
            logger.info("Using business_plan from gathering phase...")
            logger.info(f"Business plan preview: {business_description[:200]}...")
        else:
            logger.info("No business_plan found, falling back to raw description...")
            logger.info(f"Description preview: {business_description[:200]}...")
        
        # SECONDARY: Analyze template if provided
        template_styling = None
        css_theme = None
        template = state.get("template")
        
        if template and template.strip():
            logger.info("Template provided - extracting styling patterns as design reference...")
            try:
                # Initialize TemplateAnalyzer
                template_analyzer = TemplateAnalyzer()
                
                # Extract styling patterns from template
                template_styling = template_analyzer(template_html=template)
                logger.info(f"✓ Extracted template styling patterns: {list(template_styling.keys())}")
                
                # Extract CSS theme from template
                css_theme = extract_css_theme_from_template(template)
                if css_theme:
                    logger.info(f"✓ Extracted CSS theme ({len(css_theme)} chars)")
                else:
                    logger.info("No CSS found in template")
                    
            except Exception as e:
                logger.warning(f"Template analysis failed: {str(e)}, continuing without template styling")
                template_styling = None
                css_theme = None
        else:
            logger.info("No template provided - generating plan based on business requirements only")
        
        # BALANCE: Generate plan prioritizing business requirements, using template styling as reference
        planner = WebsitePlanner()
        
        # Generate plan with template styling as reference (if available)
        plan_json = planner(description=business_description, template_styling=template_styling)
        # plan_json = planner.forward(description=state["description"])
        
        logger.info(f"Raw plan response length: {len(plan_json)} chars")
        logger.info(f"Raw plan preview: {plan_json[:200]}...")
        
        # Parse JSON with multiple fallback strategies
        plan = None
        parse_error = None
        
        # Strategy 1: Direct JSON parse
        try:
            plan = json.loads(plan_json)
            logger.info("✓ JSON parsed directly")
        except json.JSONDecodeError as e:
            parse_error = str(e)
            logger.warning(f"Direct JSON parse failed: {e}")
            
            # Strategy 2: Extract from markdown code blocks
            try:
                if "```json" in plan_json:
                    logger.info("Attempting to extract JSON from ```json block")
                    plan_json = plan_json.split("```json")[1].split("```")[0].strip()
                elif "```" in plan_json:
                    logger.info("Attempting to extract JSON from ``` block")
                    plan_json = plan_json.split("```")[1].split("```")[0].strip()
                
                plan = json.loads(plan_json)
                logger.info("✓ JSON extracted from code block")
            except (json.JSONDecodeError, IndexError) as e2:
                logger.warning(f"Code block extraction failed: {e2}")
                
                # Strategy 3: Find JSON object using regex
                json_match = re.search(r'\{[^{}]*"pages"[^{}]*\}|\{.*"pages".*\}', plan_json, re.DOTALL)
                if json_match:
                    logger.info("Attempting regex extraction of JSON")
                    try:
                        plan = json.loads(json_match.group(0))
                        logger.info("✓ JSON extracted using regex")
                    except json.JSONDecodeError as e3:
                        logger.error(f"Regex extraction failed: {e3}")
                
                # Strategy 4: Create a fallback plan
                if plan is None:
                    logger.warning("All JSON parsing strategies failed, using fallback plan")
                    plan = {
                        "pages": [
                            {"name": "home", "purpose": "Landing page", "sections": ["hero", "features", "cta"]},
                            {"name": "about", "purpose": "About page", "sections": ["story", "team"]},
                            {"name": "contact", "purpose": "Contact page", "sections": ["form", "info"]}
                        ],
                        "styling": {
                            "theme": "modern",
                            "primary_color": "#3B82F6",
                            "secondary_color": "#64748B",
                            "font_family": "sans-serif",
                            "design_style": "clean and professional"
                        },
                        "image_sections": ["hero", "features", "testimonials"],
                        "navigation": ["home", "about", "contact"]
                    }
        
        # Validate plan structure
        if not isinstance(plan, dict):
            raise ValueError("Plan must be a dictionary")
        
        if "pages" not in plan or not isinstance(plan["pages"], list):
            raise ValueError("Plan must contain 'pages' array")
        
        if len(plan["pages"]) == 0:
            raise ValueError("Plan must contain at least one page")
        
        logger.info(f"✓ Generated plan with {len(plan.get('pages', []))} pages")
        logger.info(f"Pages: {[p.get('name', 'unknown') for p in plan.get('pages', [])]}")
        
        # Update state with plan, template styling, and CSS theme
        return {
            **state,
            "plan": plan,
            "plan_json": json.dumps(plan),  # Store normalized JSON
            "template_styling": template_styling,  # Store extracted template styling
            "css_theme": css_theme,  # Store extracted CSS theme
            "current_step": "image_description",  
            "status": "in_progress",
            "progress": 25,
            "progress_message": f"✓ Planning complete: {len(plan.get('pages', []))} pages planned" + (", template styling applied" if template_styling else "")
        }
        
    except Exception as e:
        logger.error(f"Planning node error: {str(e)}")
        return {
            **state,
            "current_step": "failed",
            "status": "failed",
            "error": f"Planning failed: {str(e)}",
            "progress": 0,
            "progress_message": f"✗ Planning failed: {str(e)}"
        }


def extract_css_theme_from_template(template_html: str) -> Optional[str]:
    """
    Extract and normalize CSS from template HTML.
    Returns CSS string or None if no CSS found.
    """
    try:
        # Extract CSS from <style> tags
        style_pattern = r'<style[^>]*>(.*?)</style>'
        css_matches = re.findall(style_pattern, template_html, re.DOTALL | re.IGNORECASE)
        
        if css_matches:
            # Combine all CSS from style tags
            extracted_css = '\n\n'.join(css_matches).strip()
            
            # Basic normalization (remove comments, normalize whitespace)
            # Keep it simple - just clean up excessive whitespace
            normalized_css = re.sub(r'\n\s*\n\s*\n+', '\n\n', extracted_css)
            
            logger.info(f"Extracted {len(normalized_css)} chars of CSS from template")
            return normalized_css
        
        return None
    except Exception as e:
        logger.warning(f"Error extracting CSS from template: {str(e)}")
        return None


async def image_description_node(state: WorkflowState) -> WorkflowState:
    """
    Step 2a: Generate image descriptions for sections based on plan.
    Executing in parallel for speed.
    """
    logger.info("Starting image description node...")
    
    try:
        plan = state["plan"]
        # Only generate images for these 3 specific sections
        image_sections = ["hero", "features", "testimonials"]
        
        # Initialize generator
        generator = ImageDescriptionGenerator()
        
        # Generator wrapper for async execution
        def generate_description_safe(section, page_name):
            try:
                logger.info(f"Generating image description for {section} on {page_name}")
                plan_str = json.dumps(plan)
                description = generator(
                    plan=plan_str,
                    section_name=section,
                    page_name=page_name,
                    business_description=state["description"]
                )
                return (section, description)
            except Exception as e:
                return (section, e)

        # Prepare tasks
        tasks = []
        
        for section in image_sections:
            # Determine which page has this section
            page_name = "home"  # Default to home page
            for page in plan.get("pages", []):
                if section in page.get("sections", []):
                    page_name = page["name"]
                    break
            
            # Create async task for this section
            tasks.append(
                asyncio.to_thread(
                    generate_description_safe, 
                    section, 
                    page_name
                )
            )
            
        # Execute in parallel
        logger.info(f"Starting parallel generation of {len(tasks)} image descriptions...")
        results = await asyncio.gather(*tasks)
        
        # Process results
        image_descriptions = {}
        fallback_descriptions = {
            "hero": "Professional business hero banner with modern design, clean layout, and welcoming atmosphere",
            "features": "Clean feature section with minimalist icons and professional presentation",
            "testimonials": "Professional testimonial section with friendly atmosphere and trust-building design"
        }
        
        for section, result in results:
            if isinstance(result, Exception):
                logger.error(f"Error generating description for {section}: {str(result)}")
                # Use fallback
                fallback = fallback_descriptions.get(
                    section,
                    f"Professional {section} section with modern, clean design"
                )
                image_descriptions[section] = fallback
                logger.info(f"Using fallback description for {section}")
            else:
                image_descriptions[section] = result
                logger.info(f"✓ Generated description for {section}")
        
        logger.info(f"Generated {len(image_descriptions)} image descriptions")
        
        # Update state
        return {
            **state,
            "image_descriptions": image_descriptions,
            "current_step": "image_generation",
            "progress": 40,
            "progress_message": f"✓ Image descriptions ready for {len(image_descriptions)} sections"
        }
        
    except Exception as e:
        logger.error(f"Image description node error: {str(e)}")
        
        # For catastrophic errors, fail the workflow
        return {
            **state,
            "current_step": "failed",
            "status": "failed",
            "error": f"Image description generation failed: {str(e)}",
            "progress": 25,
            "progress_message": f"✗ Image description failed: {str(e)}"
        }



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
            "hero": "hero_1769255744.png",
            "features": "features_1769255742.png",
            "testimonials": "testimonials_1769255743.png"
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


def html_generation_node(state: WorkflowState) -> WorkflowState:
    """
    Step 3: Generate HTML/CSS for each page based on plan.
    """
    logger.info("Starting HTML generation node...")
    
    try:
        plan = state["plan"]
        image_urls = state["image_urls"]
        pages_output = {}
        
        # Initialize generator
        generator = MultiPageGenerator()
        
        # Format image URLs for DSPy
        image_urls_text = "\n".join([f"{section}: {url}" for section, url in image_urls.items()])
        
        # Extract all page names for navigation context
        all_pages = plan.get("pages", [])
        page_names = [page["name"] for page in all_pages]
        
        # CRITICAL FIX: Detect if this is a single-page or multi-page website
        is_single_page = len(all_pages) == 1
        
        logger.info(f"Website type: {'SINGLE-PAGE' if is_single_page else 'MULTI-PAGE'}")
        logger.info(f"Generating HTML for {len(all_pages)} pages: {page_names}")
        
        # Generate HTML for each page
        total_pages = len(all_pages)
        for idx, page in enumerate(all_pages):
            page_name = page["name"]
            logger.info(f"Generating HTML for page: {page_name} ({idx + 1}/{total_pages})")
            
            # CRITICAL FIX: Different navigation strategy for single-page vs multi-page
            if is_single_page:
                # For single-page websites, get section names from the page config
                sections = page.get("sections", [])
                navigation_info = {
                    "navigation_type": "single-page",
                    "navigation_method": "anchor-links",
                    "sections": sections,
                    "instruction": f"CRITICAL: This is a SINGLE-PAGE website. Create navigation using ANCHOR LINKS to sections on the SAME PAGE. Use href='#section-name' format (e.g., href='#hero', href='#features', href='#contact'). Do NOT create links to separate HTML files. Navigation should scroll to sections within this one page."
                }
                logger.info(f"Single-page mode: Creating anchor links for {len(sections)} sections")
            else:
                # For multi-page websites, create links to separate pages
                navigation_info = {
                    "navigation_type": "multi-page",
                    "navigation_method": "page-links",
                    "pages": page_names,
                    "instruction": f"This is a MULTI-PAGE website. Create navigation links to different pages using href='[page_name].html' format (e.g., href='home.html', href='about.html', href='contact.html')."
                }
                logger.info(f"Multi-page mode: Creating page links for {len(page_names)} pages")
            
            # Create enhanced plan with proper navigation info
            enhanced_plan = {
                **plan,
                "current_page": page_name,
                "all_pages": page_names,
                "is_single_page": is_single_page,
                "navigation": navigation_info
            }
            
            # Get template styling from state (if available)
            template_styling = state.get("template_styling")
            
            # Generate HTML with template styling as reference (if available)
            html = generator(
                plan=json.dumps(enhanced_plan),
                page_name=page_name,
                page_config=json.dumps(page),
                image_urls=image_urls_text,
                business_description=state["description"],
                template_styling=template_styling
            )
            
            # CRITICAL: Clean up markdown blocks and validate
            html = html.strip()
            
            # Remove markdown code blocks if present
            if html.startswith("```html"):
                logger.info(f"Removing ```html markdown wrapper from {page_name}")
                html = html[7:]  # Remove ```html
            elif html.startswith("```"):
                logger.info(f"Removing ``` markdown wrapper from {page_name}")
                html = html[3:]  # Remove ```
            
            if html.endswith("```"):
                logger.info(f"Removing trailing ``` from {page_name}")
                html = html[:-3]
            
            html = html.strip()
            
            # Validate HTML content
            if not html or len(html) < 100:
                logger.error(f"❌ Empty or too short HTML generated for {page_name} ({len(html)} chars)")
                raise ValueError(f"HTML generation failed for {page_name}: Response too short or empty")
            
            if not html.startswith("<!DOCTYPE") and not html.startswith("<html"):
                logger.error(f"❌ Invalid HTML structure for {page_name}. First 100 chars: {html[:100]}")
                raise ValueError(f"HTML generation failed for {page_name}: Invalid HTML structure")
            
            # Check for truncation warning
            if "</html>" not in html.lower():
                logger.warning(f"⚠ HTML for {page_name} might be truncated - missing closing </html> tag")
            
            # CRITICAL FIX: For single-page websites, add section IDs if missing
            if is_single_page:
                logger.info(f"Post-processing single-page HTML to ensure section IDs are present...")
                # This ensures sections have proper IDs for anchor navigation
                # We'll do basic validation here - the LLM should generate correct IDs
                sections = page.get("sections", [])
                missing_ids = []
                for section_name in sections:
                    if f'id="{section_name}"' not in html and f"id='{section_name}'" not in html:
                        missing_ids.append(section_name)
                
                if missing_ids:
                    logger.warning(f"⚠ Missing section IDs in HTML: {missing_ids}")
                    logger.warning("The LLM should have generated these IDs. Navigation might not work properly.")
            
            # Extract CSS from HTML
            css = ""
            if "<style>" in html and "</style>" in html:
                css = html.split("<style>")[1].split("</style>")[0].strip()
            
            pages_output[page_name] = {
                "html": html,
                "css": css
            }
            
            # Log success
            logger.info(f"✓ Generated HTML for {page_name} ({len(html)} chars)")
            
            # Update progress
            page_progress = 65 + int((idx + 1) / total_pages * 25)
            
        logger.info(f"Generated HTML for {len(pages_output)} pages")
        
        
        # Update state - don't mark as complete yet, we need to save files
        return {
            **state,
            "pages": pages_output,
            "current_step": "file_storage",
            "status": "in_progress",
            "progress": 90,
            "progress_message": f"✓ HTML generated for {len(pages_output)} pages, preparing to save files..."
        }
        
    except Exception as e:
        logger.error(f"HTML generation node error: {str(e)}")
        return {
            **state,
            "current_step": "failed",
            "status": "failed",
            "error": f"HTML generation failed: {str(e)}",
            "progress": 65,
            "progress_message": f"✗ HTML generation failed: {str(e)}"
        }


def html_validation_node(state: WorkflowState) -> WorkflowState:
    """
    Step 3.5: Validate and fix HTML for responsiveness.
    """
    logger.info("Starting HTML validation node...")
    
    try:
        pages = state["pages"]
        css_theme = state.get("css_theme", "")
        
        validated_pages = {}
        
        for page_name, page_content in pages.items():
            html = page_content["html"]
            
            try:
                # Validate and fix HTML
                fixed_html = validate_and_fix_html(html, css_theme)
                
                validated_pages[page_name] = {
                    "html": fixed_html,
                    "css": page_content.get("css", "")
                }
                
                logger.info(f"✓ Validated and fixed {page_name}")
                
            except Exception as fix_error:
                logger.warning(f"Could not validate {page_name}: {str(fix_error)}, using original")
                # Use original if fixing fails
                validated_pages[page_name] = page_content
        
        return {
            **state,
            "pages": validated_pages,
            "current_step": "file_storage",
            "progress": 95,
            "progress_message": f"✓ HTML validated - {len(validated_pages)} pages optimized for responsiveness"
        }
        
    except Exception as e:
        logger.error(f"HTML validation node error: {str(e)}")
        # Don't fail the workflow - continue with unvalidated HTML
        logger.warning("Continuing without validation")
        return {
            **state,
            "current_step": "file_storage",
            "progress": 95,
            "progress_message": "⚠ HTML validation skipped - using generated HTML as-is"
        }


def validate_and_fix_html(html: str, css_theme: str) -> str:
    """
    Validate HTML and fix common responsive issues.
    
    Fixes:
    - Adds .container wrappers where missing
    - Replaces custom grid classes with CSS theme grid classes
    - Ensures hamburger menu exists for mobile
    - Adds section-padding to sections
    """
    try:
        from bs4 import BeautifulSoup
        import re
        
    except ImportError:
        logger.warning("BeautifulSoup not available, skipping HTML validation")
        return html
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Fix 1: Ensure sections have proper structure
        main = soup.find('main')
        if main:
            sections = main.find_all('section')
            for section in sections:
                # Add section-padding class if not hero and doesn't have it
                classes = section.get('class', [])
                if isinstance(classes, str):
                    classes = classes.split()
                
                if 'hero' not in classes and 'section-padding' not in classes:
                    classes.append('section-padding')
                    section['class'] = classes
                
                # Ensure container div exists (skip hero sections)
                if 'hero' not in classes:
                    container = section.find('div', class_='container')
                    if not container:
                        # Wrap content in container
                        container_div = soup.new_tag('div')
                        container_div['class'] = 'container'
                        
                        # Move all children to container
                        children = list(section.children)
                        for child in children:
                            container_div.append(child.extract())
                        
                        section.append(container_div)
        
        # Fix 2: Replace custom grid/wrapper classes with CSS theme grid
        # Find elements with common custom class patterns
        custom_patterns = [
            r'.*-grid',
            r'.*-list',
            r'.*-wrapper',
            r'.*-container',
            r'.*-items'
        ]
        
        for pattern in custom_patterns:
            for elem in soup.find_all(class_=re.compile(pattern)):
                # Check if it's not already using grid classes
                elem_classes = elem.get('class', [])
                if isinstance(elem_classes, str):
                    elem_classes = elem_classes.split()
                
                if 'grid' not in elem_classes:
                    # Replace with proper grid classes
                    elem['class'] = ['grid', 'grid-cols-1', 'grid-cols-md-3', 'gap-lg']
        
        # Fix 3: Ensure hamburger menu exists
        navbar = soup.find(class_='navbar')
        if navbar:
            hamburger = soup.find(class_='hamburger-menu')
            if not hamburger:
                # Create hamburger menu button
                button = soup.new_tag('button')
                button['class'] = 'hamburger-menu'
                button['aria-label'] = 'Toggle menu'
                
                # Add three spans for hamburger icon
                for _ in range(3):
                    span = soup.new_tag('span')
                    button.append(span)
                
                # Insert after logo or at beginning of navbar
                logo = navbar.find(class_='logo')
                if logo:
                    logo.insert_after(button)
                else:
                    navbar.insert(0, button)
        
        # Fix 4: Ensure nav-menu class on navigation ul
        nav_ul = soup.find('nav').find('ul') if soup.find('nav') else None
        if nav_ul:
            ul_classes = nav_ul.get('class', [])
            if isinstance(ul_classes, str):
                ul_classes = ul_classes.split()
            if 'nav-menu' not in ul_classes:
                ul_classes.append('nav-menu')
                nav_ul['class'] = ul_classes
        
        return str(soup)
        
    except Exception as e:
        logger.error(f"Error during HTML validation: {str(e)}")
        # Return original HTML if validation fails
        return html



def file_storage_node(state: WorkflowState) -> WorkflowState:
    """
    Step 4: Save generated website files to structured folders.
    """
    logger.info("Starting file storage node...")
    
    try:
        pages = state["pages"]
        plan = state.get("plan")
        description = state.get("description")
        image_urls = state.get("image_urls")
        css_theme = state.get("css_theme")  # Get global CSS theme
        
        # Extract website name from description or plan
        website_name = None
        if plan and "name" in plan:
            website_name = plan["name"]
        elif description:
            # Use first few words of description as website name
            words = description.split()[:3]
            website_name = "_".join(words)
        
        # Initialize file manager
        file_manager = WebsiteFileManager()
        
        # Save complete website with global CSS theme
        logger.info(f"Saving website with {len(pages)} pages...")
        if css_theme:
            logger.info(f"Using global CSS theme ({len(css_theme)} chars)")
        result = file_manager.save_complete_website(
            pages=pages,
            plan=plan,
            description=description,
            website_name=website_name,
            image_urls=image_urls,
            css_theme=css_theme,  # Pass global CSS theme
            business_plan=state.get("business_plan")
        )
        
        folder_path = result['folder_path']
        saved_files = result['saved_files']
        
        logger.info(f"✓ Website saved to: {folder_path}")
        logger.info(f"✓ Saved {len(saved_files)} HTML files")
        
        # Update state with file information
        return {
            **state,
            "folder_path": folder_path,
            "saved_files": saved_files,
            "current_step": "complete",
            "status": "completed",
            "progress": 100,
            "progress_message": f"✓ Website generation complete: {len(saved_files)} pages saved to {os.path.basename(folder_path)}"
        }
        
    except Exception as e:
        logger.error(f"File storage node error: {str(e)}")
        # Even if file storage fails, we still have the HTML in memory
        # So we'll mark it as completed but with a warning
        return {
            **state,
            "current_step": "complete",
            "status": "completed",
            "progress": 100,
            "progress_message": f"✓ HTML generated but file storage failed: {str(e)}",
            "error": f"File storage warning: {str(e)}"
        }

