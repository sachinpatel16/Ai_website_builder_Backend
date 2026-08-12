"""
File storage node for website generation workflow.
Saves generated website files to structured folders.
"""
import logging
import os
from typing import Dict

from app.workflow_state import WorkflowState
from app.file_manager import WebsiteFileManager

# Configure logging
logger = logging.getLogger(__name__)


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
            css_theme=css_theme  # Pass global CSS theme
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
