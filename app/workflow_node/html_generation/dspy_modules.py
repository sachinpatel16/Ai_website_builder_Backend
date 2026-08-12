# Standard library imports
import re
import json
import logging

# Third-party imports
import dspy
from typing import Dict, Optional

from .signature import MultiPageSignature, WebsiteUpdateAnalyzerSignature, HTMLEditSignature
from app.config import update_llm


class MultiPageGenerator(dspy.Module):
    """Generate HTML/CSS for individual pages."""
    
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(MultiPageSignature)
    
    def forward(self, plan: str, page_name: str, page_config: str, image_urls: str, business_description: str, template_styling: Optional[Dict] = None):
        generation_rules = """You are an expert frontend developer specializing in creating professional, responsive websites.

GENERATION STRATEGY - PRIORITIZE BUSINESS REQUIREMENTS:

**PRIMARY FOCUS: Business-Driven Content**
YOUR TASK:
- Generate a complete, production-ready HTML page based on the website plan
- Follow the page configuration and include all specified sections
- Use the provided image URLs for appropriate sections (hero, features, testimonials)
- Create realistic, professional content aligned with the business description
- Serve business purposes and goals with appropriate content

**SECONDARY REFERENCE: Template Styling (if provided)**
- Apply template styling patterns for visual consistency:
  - Use template font families and typography scale
  - Apply template color scheme (adapt if business needs different tone)
  - Follow template CSS structure patterns (grid systems, spacing)
  - Use template design patterns (buttons, cards, sections)
- Maintain template's design language while serving business-specific purposes

TECHNICAL REQUIREMENTS:

1. HTML STRUCTURE:
   - Start with <!DOCTYPE html>
   - Include proper <head> with meta tags, title, viewport
   - Use semantic HTML5 (header, nav, main, section, footer)
   - Proper heading hierarchy (h1, h2, h3)
   - Accessible markup (alt text, ARIA labels where needed)

2. CSS STYLING:
   - Embed ALL CSS in <style> tag in <head>
   - Mobile-first responsive design
   - Use CSS Grid and Flexbox for layouts
   - Smooth transitions and hover effects
   - Professional color scheme matching plan
   - Typography hierarchy with web-safe fonts or Google Fonts
   - Proper spacing and white space

3. RESPONSIVE DESIGN:
   - Mobile: < 768px
   - Tablet: 768px - 1024px
   - Desktop: > 1024px
   - Use media queries for breakpoints
   - Responsive images and typography

4. IMAGE INTEGRATION:
   - Use provided image URLs as background images or <img> tags
   - Ensure images are responsive
   - Add overlays for text legibility if needed
   - Fallback colors if images fail to load

5. CONTENT GUIDELINES:
   - Generate realistic, professional content (not Lorem Ipsum)
   - Align all content with the business description
   - Include compelling CTAs (Call-to-Actions)
   - Professional tone and messaging

6. NO EXTERNAL DEPENDENCIES:
   - No JavaScript (unless absolutely necessary for navigation)
   - No external CSS frameworks
   - Self-contained, single HTML file
   - Can use Google Fonts via CDN

7. UNIVERSAL NAVIGATION LAYOUT OPTIONS (APPLIES TO ALL WEBSITES - BOTH 2D AND 3D):

   Check the plan's `navigation_layout` attribute (`top_nav` vs `left_sidebar_slider`) to select the page structure layout for ANY website:

   A) TOP NAVBAR (`top_nav`):
   <header>
       <div class="navbar container">
           <a href="home.html" class="logo">Brand</a>
           <button class="hamburger-menu" onclick="toggleMenu()" aria-label="Toggle menu">
               <span></span><span></span><span></span>
           </button>
           <nav>
               <ul class="nav-menu">
                   <li><a href="home.html" class="nav-link active">Home</a></li>
                   <li><a href="about.html" class="nav-link">About</a></li>
               </ul>
           </nav>
       </div>
   </header>

   B) LEFT SIDEBAR SLIDER NAVIGATION (`left_sidebar_slider`):
   Use for creative websites or when sidebar/slider navigation is specified.
   <button class="sidebar-toggle" onclick="toggleSidebar()" aria-label="Toggle sidebar">☰</button>
   <aside class="sidebar-nav" id="sidebarNav">
       <div class="sidebar-header">
           <a href="home.html" class="logo">Brand</a>
           <button class="close-sidebar" onclick="toggleSidebar()">&times;</button>
       </div>
       <nav class="sidebar-menu">
           <a href="home.html" class="nav-link active">Home</a>
           <a href="about.html" class="nav-link">About</a>
           <a href="services.html" class="nav-link">Services</a>
           <a href="contact.html" class="nav-link">Contact</a>
       </nav>
       <div class="sidebar-footer">
           <a href="#contact" class="btn btn-primary">Get Started</a>
       </div>
   </aside>
   <div class="main-content-sidebar">
       <!-- Main Page Sections Here -->
   </div>
   <script>
       function toggleSidebar() { document.getElementById('sidebarNav').classList.toggle('active'); }
   </script>

8. 3D WEBGL & THREE.JS ENGINE INTEGRATION (CRITICAL IF is_3d_website=true):
   - Include Three.js via CDN in `<head>`:
     `<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>`
   - Place a canvas directly inside body:
     `<canvas id="webgl-canvas" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; pointer-events: none;"></canvas>`
   - Add inline JavaScript before `</body>` to render an interactive 3D particle field / floating geometric canvas with mouse parallax & window resize handlers:
     ```html
     <script>
     (function() {
         const canvas = document.getElementById('webgl-canvas');
         if (!canvas || typeof THREE === 'undefined') return;
         const scene = new THREE.Scene();
         const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
         camera.position.z = 30;
         const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
         renderer.setSize(window.innerWidth, window.innerHeight);
         renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

         // 3D Particles
         const geometry = new THREE.BufferGeometry();
         const count = 800;
         const positions = new Float32Array(count * 3);
         for(let i = 0; i < count * 3; i++) {
             positions[i] = (Math.random() - 0.5) * 100;
         }
         geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
         const material = new THREE.PointsMaterial({ size: 0.8, color: 0x3B82F6, transparent: true, opacity: 0.8 });
         const particles = new THREE.Points(geometry, material);
         scene.add(particles);

         // Mouse move parallax
         let mouseX = 0, mouseY = 0;
         window.addEventListener('mousemove', (e) => {
             mouseX = (e.clientX - window.innerWidth / 2) * 0.01;
             mouseY = (e.clientY - window.innerHeight / 2) * 0.01;
         });

         // Render Loop
         function animate() {
             requestAnimationFrame(animate);
             particles.rotation.y += 0.002;
             particles.rotation.x += (mouseY - particles.rotation.x) * 0.05;
             particles.rotation.y += (mouseX - particles.rotation.y) * 0.05;
             renderer.render(scene, camera);
         }
         animate();

         // Resize Listener
         window.addEventListener('resize', () => {
             camera.aspect = window.innerWidth / window.innerHeight;
             camera.updateProjectionMatrix();
             renderer.setSize(window.innerWidth, window.innerHeight);
         });
     })();
     </script>
     ```

OUTPUT: Complete, valid HTML5 document with Jinja2 template variables ready for production deployment."""
        
        full_prompt = f"{generation_rules}\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📋 GENERATION INPUTS:\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nBUSINESS DESCRIPTION:\n{business_description}\n\nNow create an EXCEPTIONAL HTML page for this business!"
        
        # PRINT COMPLETE PROMPT TO TERMINAL
        print("\n" + "="*80)
        print(f"🎯 GENERATING HTML FOR PAGE: {page_name}")
        print("="*80)
        print("\n📋 INPUTS TO DSPY:")
        print("-"*80)
        print(f"\n1️⃣  PAGE NAME: {page_name}")
        print(f"\n2️⃣  PAGE CONFIG:\n{page_config[:500]}..." if len(page_config) > 500 else f"\n2️⃣  PAGE CONFIG:\n{page_config}")
        print(f"\n3️⃣  IMAGE URLS:\n{image_urls}")
        print(f"\n4️⃣  PLAN (first 500 chars):\n{plan[:500]}...")
        print(f"\n5️⃣  BUSINESS DESCRIPTION:\n{business_description[:300]}...")
        print("\n" + "-"*80)
        print("📝 FULL PROMPT STRUCTURE:")
        print("-"*80)
        # print(f"Length: {len(full_prompt)} characters")
        # print(f"Generation Rules: {len(generation_rules)} chars")
        print(f"Business Context: {len(business_description)} chars")
        print("\n💬 PROMPT PREVIEW (First 1000 chars):")
        print("-"*80)
        print(full_prompt[:1000] + "...")
        print("\n" + "="*80 + "\n")
        
        result = self.predict(
            plan=plan,
            page_name=page_name,
            page_config=page_config,
            image_urls=image_urls,
            business_description=full_prompt
        )
        return result.html.strip()

class HTMLEditor(dspy.Module):
    """Edit existing HTML/CSS content."""
    
    def __init__(self):
        super().__init__()
        # Use update_llm for HTML editing (4K tokens sufficient) - imported at top
        self.predict = dspy.Predict(HTMLEditSignature)
        self.predict.lm = update_llm
    
    def forward(self, html: str, css: str, edit_request: str):
        # Build a detailed prompt for the edit request
        full_prompt = (
            f"Apply the following edit to the HTML page:\n\n"
            f"EDIT REQUEST: {edit_request}\n\n"
            f"RULES:\n"
            f"- Return the COMPLETE updated HTML document.\n"
            f"- Only change what the edit request specifies.\n"
            f"- Preserve all navigation, classes, IDs, and unrelated content.\n"
            f"- Include any modified CSS inside <style> tags in <head>.\n"
        )

        result = self.predict(
            html_input=html,
            css_input=css,
            edit_request=full_prompt
        )
        return result.html_output


class WebsiteUpdater(dspy.Module):
    """Intelligently update website pages and global CSS based on natural language requests."""
    
    def __init__(self):
        super().__init__()
        # Use planning_llm for analysis (short task, 2K tokens) - imported at top
        self.analyzer = dspy.Predict(WebsiteUpdateAnalyzerSignature)
        self.analyzer.lm = update_llm
        
        # Use HTMLEditor for actual modifications (which now uses update_llm with 4K tokens)
        self.html_editor = HTMLEditor()
    
    def forward(self, pages: dict, global_css: str, edit_request: str):
        """
        Analyze edit request and apply updates intelligently.

        Args:
            pages: Dict of page_name -> {html: str, css: str}
            global_css: Current global CSS content
            edit_request: User's natural language edit instructions

        Returns:
            Dict with:
                - updated_pages: Dict of modified pages only
                - updated_global_css: Modified global CSS if changed
                - changes_summary: Description of what was changed
        """
        # json, logging imported at top of file
        logger = logging.getLogger(__name__)

        # Step 1: Analyze the edit request
        available_pages_list = list(pages.keys())
        available_pages_text = ", ".join(available_pages_list)

        logger.info(f"Analyzing edit request: {edit_request[:100]}...")
        logger.info(f"Available pages: {available_pages_text}")

        try:
            analysis_result = self.analyzer(
                edit_request=edit_request,
                available_pages=available_pages_text,
                current_global_css=global_css[:500] if global_css else ""  # Just a sample for context
            )

            # Parse analysis
            try:
                analysis = json.loads(analysis_result.analysis)
                logger.info(f"Analysis result: {analysis}")
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse analysis JSON: {e}, using fallback")
                # Fallback: try to determine from keywords
                edit_lower = edit_request.lower()

                # Check for global styling keywords
                global_keywords = ['color', 'font', 'theme', 'all pages', 'everywhere', 'global', 'button', 'spacing']
                is_global = any(keyword in edit_lower for keyword in global_keywords)

                # Check for page-specific keywords
                page_specific = any(page_name in edit_lower for page_name in available_pages_list)

                if is_global and not page_specific:
                    analysis = {
                        "update_type": "global_css",
                        "target_pages": [],
                        "requires_css_update": True,
                        "interpretation": "Applying global styling changes"
                    }
                elif page_specific and not is_global:
                    # Try to identify which pages
                    target_pages = [page for page in available_pages_list if page in edit_lower]
                    analysis = {
                        "update_type": "specific_pages",
                        "target_pages": target_pages if target_pages else [available_pages_list[0]],
                        "requires_css_update": False,
                        "interpretation": f"Updating content on specific pages: {', '.join(target_pages)}"
                    }
                else:
                    # Both or ambiguous
                    target_pages = [page for page in available_pages_list if page in edit_lower]
                    if not target_pages:
                        target_pages = [available_pages_list[0]]  # Default to first page
                    analysis = {
                        "update_type": "both",
                        "target_pages": target_pages,
                        "requires_css_update": True,
                        "interpretation": "Updating both styling and page content"
                    }
        except Exception as e:
            logger.error(f"Analysis failed: {e}, using fallback analysis")
            # Ultra-fallback: update first page only
            analysis = {
                "update_type": "specific_pages",
                "target_pages": [available_pages_list[0]] if available_pages_list else [],
                "requires_css_update": False,
                "interpretation": "Updating page content"
            }

        # Step 2: Apply updates based on analysis
        updated_pages = {}
        updated_global_css = None
        changes_made = []

        # Update global CSS if needed
        if analysis.get("requires_css_update") and global_css:
            logger.info("Updating global CSS...")
            try:
                # Create a minimal HTML wrapper for CSS editing
                css_wrapper_html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
    {global_css}
    </style>
</head>
<body>
    <p>CSS Template</p>
</body>
</html>"""

                # Use HTMLEditor to modify the CSS
                modified_html = self.html_editor(
                    html=css_wrapper_html,
                    css=global_css,
                    edit_request=f"Update the CSS styling based on this request: {edit_request}. Only modify the CSS, preserve the HTML structure."
                )

                # Extract the modified CSS from the result
                import re
                style_pattern = r'<style[^>]*>(.*?)</style>'
                css_matches = re.findall(style_pattern, modified_html, re.DOTALL | re.IGNORECASE)
                if css_matches:
                    updated_global_css = '\n\n'.join(css_matches).strip()
                    changes_made.append("Updated global CSS styling")
                    logger.info(f"✓ Global CSS updated ({len(updated_global_css)} chars)")
                else:
                    logger.warning("Could not extract CSS from modified HTML, keeping original")
                    updated_global_css = global_css
            except Exception as e:
                logger.error(f"Error updating global CSS: {e}")
                updated_global_css = global_css

        # Update specific pages if needed
        target_pages = analysis.get("target_pages", [])
        # Fallback: if analyzer returned no target pages (e.g. update_type='global_css'),
        # update ALL pages so we never silently return nothing.
        if not target_pages:
            target_pages = available_pages_list
            logger.info(f"No target pages from analysis, defaulting to all pages: {target_pages}")
        if target_pages:
            for page_name in target_pages:
                if page_name not in pages:
                    logger.warning(f"Page '{page_name}' not found in provided pages")
                    continue

                logger.info(f"Updating page: {page_name}...")
                try:
                    page_data = pages[page_name]
                    current_html = page_data.get('html', '')
                    current_css = page_data.get('css', global_css if global_css else '')

                    # Use HTMLEditor to modify the page
                    modified_html = self.html_editor(
                        html=current_html,
                        css=current_css,
                        edit_request=edit_request
                    )

                    # Extract CSS if any (re imported at top)
                    html_clean, extracted_css = self._extract_css(modified_html)

                    updated_pages[page_name] = {
                        'html': html_clean,
                        'css': extracted_css if extracted_css else current_css
                    }
                    changes_made.append(f"Updated {page_name} page")
                    logger.info(f"✓ Page '{page_name}' updated")
                except Exception as e:
                    logger.error(f"Error updating page '{page_name}': {e}")

        # Generate summary
        if not changes_made:
            changes_summary = "No changes were made. Please check your request."
        else:
            changes_summary = f"Successfully applied changes: {', '.join(changes_made)}"

        logger.info(f"Update complete: {changes_summary}")

        return {
            "updated_pages": updated_pages,
            "updated_global_css": updated_global_css,
            "changes_summary": changes_summary,
            "analysis": analysis
        }
    def _extract_css(self, html: str):
        """Helper method to extract CSS from HTML. (re imported at top)"""
        style_pattern = r'<style[^>]*>(.*?)</style>'
        css_matches = re.findall(style_pattern, html, re.DOTALL | re.IGNORECASE)
        extracted_css = '\n\n'.join(css_matches).strip()
        html_without_style = re.sub(style_pattern, '', html, flags=re.DOTALL | re.IGNORECASE)
        return html_without_style, extracted_css
