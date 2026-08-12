import dspy  # type: ignore


class MultiPageSignature(dspy.Signature):
    """Generate HTML/CSS for a specific page based on the plan."""
    plan: str = dspy.InputField(
        desc="Complete website plan JSON containing all pages and navigation structure"
    )
    page_name: str = dspy.InputField(
        desc="Name of the page to generate"
    )
    page_config: str = dspy.InputField(
        desc="Specific page configuration from plan"
    )
    image_urls: str = dspy.InputField(
        desc="Available image URLs formatted as: section_name: url"
    )
    business_description: str = dspy.InputField(
        desc="Original business description for content generation"
    )
    html: str = dspy.OutputField(
        desc="""Complete responsive HTML page with embedded CSS.
        
        ⚠️ TOKEN LIMIT - CRITICAL REQUIREMENT:
        - TOTAL OUTPUT MUST BE UNDER 8000 TOKENS (approximately 5000-6000 words)
        - Keep ALL content SHORT and CONCISE
        - NO verbose descriptions or lengthy paragraphs
        - Maximum 2-3 sentences per section text
        - Maximum 3-4 items in any list/grid
        - Minimize CSS - use only essential styles, no redundant rules
        
        CONTENT LENGTH LIMITS (STRICT):
        - Hero section: 1 heading (6-10 words) + 1 description (15-25 words) + 1 CTA button
        - Features: Max 3 features, each with title (3-5 words) + text (15-20 words max)
        - Testimonials: Max 2-3 items, each quote under 20 words
        - About/Other sections: 2-3 sentences maximum (30-50 words total)
        - Footer: Minimal - just essential links and copyright
        
        REQUIREMENTS:
        - Include <!DOCTYPE html>
        - Fully responsive design (mobile-first)
        - Use provided image URLs for appropriate sections
        - Generate realistic, professional content aligned with business description
        - Include all sections specified in page_config
        - Modern, clean design matching the styling strategy
        - Proper semantic HTML5
        - Embedded CSS in <style> tag
        - No external dependencies or JavaScript
        - Production-ready code
        
        CRITICAL - NAVIGATION LINKS:
        ⚠️ IMPORTANT: You MUST create a navigation menu with proper page links.
        
        1. Extract the page list from the 'plan' JSON (look for "pages" array or "navigation" array)
        2. For EACH page in the navigation, create a link with the pattern: href="[page_name].html"
        3. NEVER use href="#" - this is incorrect and breaks navigation
        4. The current page should have an "active" class or style
        
        CORRECT Navigation Examples:
        ✅ <a href="home.html">Home</a>
        ✅ <a href="about.html">About</a>
        ✅ <a href="products.html">Products</a>
        ✅ <a href="services.html">Services</a>
        ✅ <a href="contact.html">Contact</a>
        ✅ <a href="home.html" class="active">Home</a>  (if current page is home)
        
        INCORRECT Navigation Examples (DO NOT USE):
        ❌ <a href="#">Home</a>
        ❌ <a href="#">About</a>
        ❌ <a href="/">Contact</a>
        ❌ <a>Home</a>
        
        ⚠️ CRITICAL - COMPLETE HEADER STRUCTURE:
        
        Generate a complete header with proper structure. DO NOT create incomplete or broken headers.
        
        **REQUIRED HEADER HTML:**
        
        <header>
            <div class="navbar container">
                <!-- Logo on the left -->
                <a href="home.html" class="logo">Website Name</a>
                
                <!-- Navigation on the right -->
                <nav>
                    <ul class="nav-menu">
                        <li><a href="home.html" class="nav-link active">Home</a></li>
                        <li><a href="about.html" class="nav-link">About</a></li>
                        <li><a href="services.html" class="nav-link">Services</a></li>
                        <li><a href="contact.html" class="nav-link">Contact</a></li>
                    </ul>
                </nav>
            </div>
        </header>
        
        **REQUIRED HEADER CSS:**
        
        header {
            background: #fff;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 5%;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            color: #333;
            text-decoration: none;
        }
        
        .nav-menu {
            display: flex;
            gap: 2rem;
            list-style: none;
            margin: 0;
            padding: 0;
        }
        
        .nav-link {
            text-decoration: none;
            color: #333;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-link:hover,
        .nav-link.active {
            color: #007bff;
        }
        
        **CRITICAL RULES:**
        1. ALWAYS wrap navbar in a container div for proper layout
        2. Logo MUST be on the left
        3. Navigation MUST be on the right
        4. Use flexbox with space-between for alignment
        5. Include sticky positioning for header
        6. Every page link follows href="[page_name].html"
        
        Remember: Every page link MUST follow the pattern href="[page_name].html"
        
        ⚠️ CRITICAL - MOBILE MENU FUNCTIONALITY:
        
        For the hamburger menu button to work, you MUST include:
        
        **1. HAMBURGER BUTTON (in header):**
        <button class="hamburger-menu" onclick="toggleMenu()" aria-label="Toggle menu">
            <span></span>
            <span></span>
            <span></span>
        </button>
        
        **2. MOBILE RESPONSIVE CSS (in <style> tag):**
        .hamburger-menu {
            display: none;
            flex-direction: column;
            gap: 4px;
            background: none;
            border: none;
            cursor: pointer;
            padding: 8px;
        }
        
        .hamburger-menu span {
            width: 25px;
            height: 3px;
            background: #333;
            transition: 0.3s;
        }
        
        @media (max-width: 768px) {
            .hamburger-menu {
                display: flex;
            }
            
            .nav-menu {
                position: fixed;
                left: -100%;
                top: 70px;
                flex-direction: column;
                background: #fff;
                width: 100%;
                text-align: center;
                transition: left 0.3s ease;
                box-shadow: 0 10px 27px rgba(0,0,0,0.1);
                padding: 2rem 0;
                z-index: 999;
            }
            
            .nav-menu.active {
                left: 0;
            }
            
            .nav-menu li {
                padding: 1rem 0;
            }
        }
        
        **3. JAVASCRIPT (before closing </body> tag):**
        <script>
        function toggleMenu() {
            const navMenu = document.querySelector('.nav-menu');
            if (navMenu) {
                navMenu.classList.toggle('active');
            }
        }
        
        // Close menu when clicking a link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                const navMenu = document.querySelector('.nav-menu');
                if (navMenu) {
                    navMenu.classList.remove('active');
                }
            });
        });
        </script>
        
        **YOU MUST INCLUDE ALL THREE:** hamburger button, CSS media queries, and JavaScript function.
        Without these, the mobile menu will not work!
        

        
        ⚠️ CRITICAL - CSS THEME CLASS USAGE:
        
        A global CSS theme has been pre-generated for this website.
        YOU MUST USE THE CSS THEME CLASSES. DO NOT CREATE CUSTOM CLASSES.
        
        Available CSS Theme Classes:
        
        LAYOUT: .container, .grid .grid-cols-1 .grid-cols-md-3, .flex .justify-between .items-center, .section-padding
        COMPONENTS: .navbar, .nav-menu, .nav-link, .hero, .hero-content, .btn .btn-primary, .card .product-card .testimonial-card
        SPACING: .p-lg .py-md .px-sm, .mt-lg .mb-md, .gap-lg
        TEXT: .text-center, .text-primary, .font-bold
        
        REQUIRED STRUCTURE FOR EVERY SECTION:
        
        <section class="section-padding">
            <div class="container">
                <h2 class="section-title">Title</h2>
                <div class="grid grid-cols-1 grid-cols-md-3 gap-lg">
                    <div class="card">Content</div>
                </div>
            </div>
        </section>
        
        NAVIGATION MUST INCLUDE (for mobile):
        
        <div class="navbar container">
            <a href="home.html" class="logo">Brand</a>
            <button class="hamburger-menu" aria-label="Toggle menu">
                <span></span><span></span><span></span>
            </button>
            <nav>
                <ul class="nav-menu">
                    <li><a href="home.html" class="nav-link active">Home</a></li>
                </ul>
            </nav>
        </div>
        
        DO NOT create custom classes like: .product-grid, .feature-list, .category-wrapper
        ALWAYS use: .grid .grid-cols-1 .grid-cols-md-3 .gap-lg with .card
        """
    )

class WebsiteUpdateAnalyzerSignature(dspy.Signature):
    """Analyze edit request and determine what needs to be updated."""
    edit_request: str = dspy.InputField(
        desc="User's natural language edit request (e.g., 'change colors to blue', 'update hero text on home page')"
    )
    available_pages: str = dspy.InputField(
        desc="List of available page names in the website"
    )
    current_global_css: str = dspy.InputField(
        desc="Current global CSS content (optional, can be empty)"
    )
    analysis: str = dspy.OutputField(
        desc="""JSON-formatted analysis of what needs to be updated:
        {
            "update_type": "global_css" | "specific_pages" | "both",
            "target_pages": ["home", "about"] or [],
            "requires_css_update": true/false,
            "interpretation": "Brief explanation of what will be changed"
        }
        
        Examples:
        - "Change all colors to blue" → {"update_type": "global_css", "target_pages": [], "requires_css_update": true}
        - "Update hero text on home page" → {"update_type": "specific_pages", "target_pages": ["home"], "requires_css_update": false}
        - "Make buttons larger and update about page content" -> {"update_type": "both", "target_pages": ["about"], "requires_css_update": true}
        """
    )

class HTMLEditSignature(dspy.Signature):
    """Edit an existing HTML page based on a natural language edit request."""
    html_input: str = dspy.InputField(
        desc="Current HTML content of the page to be edited"
    )
    css_input: str = dspy.InputField(
        desc="Current CSS content associated with the page (can be empty)"
    )
    edit_request: str = dspy.InputField(
        desc="Natural language description of the changes to make to the HTML/CSS"
    )
    html_output: str = dspy.OutputField(
        desc="""Complete, updated HTML document after applying the requested changes.

        REQUIREMENTS:
        - Return the full HTML document (not just the changed parts)
        - Maintain the original structure and all existing content not affected by the edit
        - Apply ONLY the changes described in edit_request
        - Preserve all navigation links, classes, and IDs
        - Keep all responsive design and CSS intact
        - Return valid HTML5 with proper DOCTYPE
        - Include any updated or new CSS inside <style> tags in <head>
        """
    )


# class HTMLEditSignature(dspy.Signature):
#     """Edit existing HTML/CSS based on user request."""
#     html_input: str = dspy.InputField(
#         desc="Current HTML content"
#     )
#     css_input: str = dspy.InputField(
#         desc="Current CSS content"
#     )
#     edit_request: str = dspy.InputField(
#         desc="User's edit instructions"
#     )
#     html_output: str = dspy.OutputField(
#         desc="Modified HTML with embedded CSS"
#     )