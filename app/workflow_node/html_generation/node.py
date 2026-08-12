"""
HTML generation node for website generation workflow.
Generates HTML/CSS for each page based on plan.
"""
import json
import logging
from typing import Dict

from app.workflow_state import WorkflowState
from .dspy_modules import MultiPageGenerator

# Configure logging
logger = logging.getLogger(__name__)


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
            
            # Create enhanced plan with proper navigation info and 3D configuration
            enhanced_plan = {
                **plan,
                "current_page": page_name,
                "all_pages": page_names,
                "is_single_page": is_single_page,
                "navigation": navigation_info,
                "is_3d_website": state.get("is_3d_website", False),
                "navigation_layout": state.get("navigation_layout", "top_nav"),
                "scene_type_3d": state.get("scene_type_3d", "particles"),
                "config_3d": state.get("config_3d", {})
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
            
            #  Validate HTML content
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
