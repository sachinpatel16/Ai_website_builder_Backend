"""
File manager for website template storage.
Handles creation of website folders and file storage in webtemplates directory.
"""
import os
import re
import json
import logging
from datetime import datetime
from typing import Dict, Tuple, List
from pathlib import Path

logger = logging.getLogger(__name__)


class WebsiteFileManager:
    """Manages website file storage in structured folders."""
    
    def __init__(self, base_templates_dir: str = None):
        """
        Initialize the file manager.
        
        Args:
            base_templates_dir: Base directory for storing website templates.
                              Defaults to Backend/webtemplates
        """
        if base_templates_dir is None:
            # Get the Backend directory
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            base_templates_dir = os.path.join(backend_dir, "webtemplates")
        
        self.base_dir = base_templates_dir
        os.makedirs(self.base_dir, exist_ok=True)
        logger.info(f"WebsiteFileManager initialized with base directory: {self.base_dir}")
    
    def create_website_folder(self, website_name: str = None) -> str:
        """
        Create a unique folder for a website.
        
        Args:
            website_name: Optional name for the website. If not provided, 
                         generates a timestamp-based name.
        
        Returns:
            Absolute path to the created website folder.
        """
        if website_name is None:
            # Generate timestamp-based folder name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            website_name = f"website_{timestamp}"
        else:
            # Sanitize website name (remove special characters)
            website_name = re.sub(r'[^\w\s-]', '', website_name)
            website_name = re.sub(r'[\s]+', '_', website_name)
            
            # Add timestamp to ensure uniqueness
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            website_name = f"{website_name}_{timestamp}"
        
        website_folder = os.path.join(self.base_dir, website_name)
        os.makedirs(website_folder, exist_ok=True)
        
        logger.info(f"Created website folder: {website_folder}")
        return website_folder
    
    def extract_css_from_html(self, html: str) -> Tuple[str, str]:
        """
        Extract CSS from HTML <style> tags and create separate CSS file.
        
        Args:
            html: HTML content containing <style> tags
        
        Returns:
            Tuple of (html_without_style_tags, extracted_css)
        """
        # Pattern to match <style> tags with optional attributes
        style_pattern = r'<style[^>]*>(.*?)</style>'
        
        # Extract all CSS content from style tags
        css_matches = re.findall(style_pattern, html, re.DOTALL | re.IGNORECASE)
        extracted_css = '\n\n'.join(css_matches).strip()
        
        # Remove all style tags from HTML
        html_without_style = re.sub(style_pattern, '', html, flags=re.DOTALL | re.IGNORECASE)
        
        return html_without_style, extracted_css
    
    def add_css_link_to_html(self, html: str, css_filename: str = "style.css") -> str:
        """
        Add CSS link tag to HTML if not present.
        
        Args:
            html: HTML content
            css_filename: Name of the CSS file to link
        
        Returns:
            HTML with CSS link tag added
        """
        link_tag = f'<link rel="stylesheet" href="{css_filename}">'
        
        # Check if link tag already exists
        if css_filename in html:
            return html
        
        # Try to insert before </head>
        if '</head>' in html.lower():
            html = re.sub(
                r'(</head>)',
                f'    {link_tag}\n    \\1',
                html,
                flags=re.IGNORECASE,
                count=1
            )
        # Fallback: insert at beginning of <body>
        elif '<body' in html.lower():
            html = re.sub(
                r'(<body[^>]*>)',
                f'\\1\n    {link_tag}',
                html,
                flags=re.IGNORECASE,
                count=1
            )
        else:
            # Last fallback: prepend to HTML
            html = f'{link_tag}\n{html}'
        
        return html
    
    def save_website_files(
        self,
        pages: Dict[str, Dict[str, str]],
        website_folder: str,
        create_global_css: bool = True,
        global_css_theme: str = None
    ) -> Dict[str, str]:
        """
        Save all website pages and CSS files to the website folder.
        
        Args:
            pages: Dictionary mapping page_name -> {html: str, css: str}
            website_folder: Path to the website folder
            create_global_css: If True, creates a single global style.css file.
                             If False, creates separate CSS files for each page.
            global_css_theme: Optional pre-generated CSS theme for the entire website.
                            If provided, this will be used instead of extracting CSS from pages.
        
        Returns:
            Dictionary mapping page_name -> saved_file_path
        """
        saved_files = {}
        all_css_content = []
        
        # Use global CSS theme if provided, otherwise collect from pages
        if create_global_css:
            if global_css_theme:
                # Use the provided global CSS theme
                logger.info("Using pre-generated global CSS theme")
                global_css = global_css_theme
            else:
                # Fallback: collect CSS from individual pages
                logger.info("No global CSS theme provided, extracting from pages")
                for page_name, page_content in pages.items():
                    # Get CSS from the page_content
                    css = page_content.get('css', '')
                    html = page_content.get('html', '')
                    
                    # Extract additional CSS from HTML if present
                    html_clean, extracted_css = self.extract_css_from_html(html)
                    
                    # Combine CSS
                    combined_css = css
                    if extracted_css:
                        combined_css = f"{css}\n\n{extracted_css}" if css else extracted_css
                    
                    if combined_css:
                        all_css_content.append(f"/* CSS for {page_name} page */\n{combined_css}")
                
                global_css = '\n\n'.join(all_css_content)
            
            # Save global CSS file
            if global_css:
                css_path = os.path.join(website_folder, "style.css")
                with open(css_path, 'w', encoding='utf-8') as f:
                    f.write(global_css)
                logger.info(f"Saved global CSS file: {css_path} ({len(global_css)} chars)")
        
        # Second pass: save HTML files
        for page_name, page_content in pages.items():
            html = page_content.get('html', '')
            css = page_content.get('css', '')
            
            # Clean HTML and extract CSS
            html_clean, extracted_css = self.extract_css_from_html(html)
            
            # Add CSS link to HTML
            if create_global_css:
                html_final = self.add_css_link_to_html(html_clean, "style.css")
            else:
                # Create separate CSS file for this page
                page_css = f"{css}\n\n{extracted_css}" if css else extracted_css
                if page_css:
                    css_filename = f"{page_name}.css"
                    css_path = os.path.join(website_folder, css_filename)
                    with open(css_path, 'w', encoding='utf-8') as f:
                        f.write(page_css)
                    logger.info(f"Saved CSS file: {css_path}")
                    html_final = self.add_css_link_to_html(html_clean, css_filename)
                else:
                    html_final = html_clean
            
            # Save HTML file
            html_filename = f"{page_name}.html"
            html_path = os.path.join(website_folder, html_filename)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_final)
            
            saved_files[page_name] = html_path
            logger.info(f"Saved HTML file: {html_path}")
        
        return saved_files
    
    def fix_internal_links(self, website_folder: str, pages: List[str]):
        """
        Fix internal page links in all HTML files to ensure proper navigation.
        Updates links like <a href="about.html"> to work correctly.
        
        Args:
            website_folder: Path to the website folder
            pages: List of page names (without .html extension)
        """
        for page_name in pages:
            html_path = os.path.join(website_folder, f"{page_name}.html")
            
            if not os.path.exists(html_path):
                logger.warning(f"HTML file not found for link fixing: {html_path}")
                continue
            
            # Read HTML content
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Fix links to other pages
            # Pattern: href="page_name" or href="page_name.html" or href="#"
            for target_page in pages:
                # Replace href="page_name" with href="page_name.html"
                html_content = re.sub(
                    rf'href=["\']({target_page})(["\'])',
                    rf'href="\1.html\2',
                    html_content,
                    flags=re.IGNORECASE
                )
            
            # Write updated HTML back
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Fixed internal links in: {html_path}")
    
    def create_index_html(self, website_folder: str, home_page: str = "home"):
        """
        Create an index.html file that redirects to the home page.
        
        Args:
            website_folder: Path to the website folder
            home_page: Name of the home page (without .html extension)
        """
        index_path = os.path.join(website_folder, "index.html")
        redirect_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="0; url={home_page}.html">
    <title>Redirecting...</title>
</head>
<body>
    <p>If you are not redirected automatically, <a href="{home_page}.html">click here</a>.</p>
</body>
</html>
"""
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(redirect_html)
        
        logger.info(f"Created index.html redirect file: {index_path}")
    
    def save_metadata(self, website_folder: str, metadata: Dict):
        """
        Save website metadata (plan, description, etc.) to a JSON file.
        
        Args:
            website_folder: Path to the website folder
            metadata: Dictionary containing website metadata
        """
        metadata_path = os.path.join(website_folder, "metadata.json")
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved metadata file: {metadata_path}")
    
    def save_complete_website(
        self,
        pages: Dict[str, Dict[str, str]],
        plan: Dict = None,
        description: str = None,
        website_name: str = None,
        image_urls: Dict[str, str] = None,
        css_theme: str = None,
        business_plan: str = None
    ) -> Dict[str, any]:
        """
        Complete workflow to save a website with all files and proper structure.
        
        Args:
            pages: Dictionary mapping page_name -> {html: str, css: str}
            plan: Website plan dictionary
            description: Business/website description
            website_name: Optional custom name for the website
            image_urls: Dictionary of image URLs used in the website
            css_theme: Optional pre-generated global CSS theme
        
        Returns:
            Dictionary containing:
                - folder_path: Path to the website folder
                - saved_files: Dictionary of saved file paths
                - metadata_path: Path to metadata file
        """
        # Create website folder
        website_folder = self.create_website_folder(website_name)
        
        # Save all pages and CSS (using global CSS theme if provided)
        saved_files = self.save_website_files(
            pages, 
            website_folder, 
            create_global_css=True,
            global_css_theme=css_theme
        )
        
        # Fix internal links
        page_names = list(pages.keys())
        self.fix_internal_links(website_folder, page_names)
        
        # Create index.html redirect (assumes 'home' is the main page, fallback to first page)
        home_page = 'home' if 'home' in pages else page_names[0]
        self.create_index_html(website_folder, home_page)
        
        # Save metadata
        metadata = {
            'created_at': datetime.now().isoformat(),
            'description': description,
            'plan': plan,
            'business_plan': business_plan,
            'pages': page_names,
            'image_urls': image_urls or {},
            'has_global_css_theme': bool(css_theme)
        }
        self.save_metadata(website_folder, metadata)
        
        logger.info(f"✓ Website saved successfully to: {website_folder}")
        
        return {
            'folder_path': website_folder,
            'saved_files': saved_files,
            'metadata_path': os.path.join(website_folder, "metadata.json"),
            'pages': page_names
        }
