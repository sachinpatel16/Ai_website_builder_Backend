"""
LangGraph workflow state definition for website generation.
"""
from typing import TypedDict, Dict, List, Optional, Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class WorkflowState(TypedDict):
    """State schema for the website generation workflow."""
    
    # User input
    description: str
    template: Optional[str]  # Original template HTML for styling reference
    
    business_description: Optional[str]
    
    # Step 0: Business information gathering
    ready: bool  # Whether enough business information has been gathered
    business_plan: Optional[str]  # Initial business understanding/summary before detailed planning
    clarification_questions: Optional[List[str]]  # Questions to ask user if information is insufficient
    
    # Step 1: Planning output
    plan: Optional[Dict]  # Website structure plan
    plan_json: Optional[str]  # Raw JSON string from LLM
    template_styling: Optional[Dict]  # Extracted styling patterns (fonts, colors, CSS structure)
    css_theme: Optional[str]  # Global CSS theme extracted/derived from template
    
    # Step 2: Image generation
    image_descriptions: Optional[Dict]  # Section name -> image description
    image_urls: Optional[Dict]  # Section name -> image URL
    
    # Step 3: Multi-page HTML generation
    pages: Optional[Dict]  # Page name -> {html: str, css: str}
    
    # Step 4: File storage
    folder_path: Optional[str]  # Path to saved website folder
    saved_files: Optional[Dict]  # Page name -> file path
    
    # Workflow state tracking
    current_step: str  # "planning", "image_description", "image_generation", "html_generation", "file_storage", "complete"
    status: str  # "in_progress", "completed", "failed"
    error: Optional[str]  # Error message if failed
    
    # Progress tracking for streaming
    progress: int  # 0-100
    progress_message: str  # Human-readable progress message
    
    # Messages for LangChain compatibility (optional)
    messages: Annotated[List[BaseMessage], add_messages]


class PlanStructure(TypedDict):
    """Structure of the website plan."""
    pages: List[Dict[str, any]]  # List of page configurations
    styling: Dict[str, str]  # Styling strategy (colors, fonts, theme)
    image_sections: List[str]  # Sections requiring images (hero, features, testimonials)
    navigation: List[str]  # Navigation structure
