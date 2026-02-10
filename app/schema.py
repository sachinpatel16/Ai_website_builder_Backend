from pydantic import BaseModel
from typing import Dict, Optional


class GeneratePromptsRequest(BaseModel):
    description: str

class PromptsResponse(BaseModel):
    prompts: Dict[str, str]

class GenerateImagesRequest(BaseModel):
    prompts: Optional[Dict[str, str]] = None

class ImagesResponse(BaseModel):
    images: Dict[str, str]

class GenerateHTMLRequest(BaseModel):
    description: str
    images: Dict[str, str]
    template: Optional[str] = None

class HTMLResponse(BaseModel):
    html: str
    css: str

class EditHTMLRequest(BaseModel):
    html: str
    css: str
    edit_request: str

class EditHTMLResponse(BaseModel):
    html: str
    css: str


class GenerateWebsiteRequest(BaseModel):
    description: str
    template: Optional[str] = None  # Single-page HTML template for styling reference
    thread_id: Optional[str] = None  # For conversation continuity across multiple requests
    messages: Optional[list] = None  # Previous conversation messages

class WebsitePlanResponse(BaseModel):
    plan: Dict
    status: str
    progress: int
    progress_message: str

class WebsiteGenerationResponse(BaseModel):
    pages: Dict[str, Dict[str, str]]
    image_urls: Dict[str, str]
    plan: Dict
    status: str
    progress: int
    progress_message: str


class UpdateWebsiteRequest(BaseModel):
    pages: Dict[str, Dict[str, str]]
    global_css: Optional[str] = None
    edit_request: str
    folder_path: Optional[str] = None

class UpdateWebsiteResponse(BaseModel):
    updated_pages: Dict[str, Dict[str, str]]
    updated_global_css: Optional[str] = None
    changes_summary: str
    folder_path: Optional[str] = None