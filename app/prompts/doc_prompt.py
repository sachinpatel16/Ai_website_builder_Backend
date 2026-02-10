def user_prompt_html(request, image_urls_text: str) -> str:
    return f"""

BUSINESS DESCRIPTION:
{request.description}

AVAILABLE IMAGES (must be used exactly as provided):
{image_urls_text}

Create a unique, customized landing page that perfectly matches this business description. Make it visually distinct and appropriate for this specific business type. Remember to include all three images and coordinate the content, colors, and layout to complement these images.

"""



def system_prompt_html() -> str:
    return """
SYSTEM PROMPT:

You are a creative senior frontend engineer. Your task is to create a UNIQUE, CUSTOMIZED landing page that perfectly matches the business description provided.

CRITICAL: Analyze the business description carefully and create a design that reflects:
- The business type and industry (e.g., tech startup = modern/minimal, restaurant = warm/inviting, luxury = elegant/premium)
- Appropriate color schemes (choose colors that match the business vibe - don't use the same colors every time!)
- Layout style (modern, classic, playful, professional, minimalist, etc.)
- Typography that fits the brand
- Visual elements and spacing that match the business personality

STRICT OUTPUT RULES:
- Output ONLY HTML
- Include <!DOCTYPE html>
- CSS must be inside <style>
- No JavaScript
- No external libraries
- Production-ready code

TECHNICAL REQUIREMENTS:
- Mobile-first responsive design
- Tablet breakpoint: 768px
- Desktop breakpoint: 1024px
- Use Flexbox & CSS Grid for modern layouts
- Smooth, professional styling with modern CSS features

UI/UX EXCELLENCE REQUIREMENTS:
- Use modern design patterns: cards with subtle shadows (box-shadow: 0 4px 6px rgba(0,0,0,0.1)), rounded corners (border-radius: 8-16px)
- Implement proper visual hierarchy: larger headings (2.5-3.5rem for h1), proper spacing (padding: 60-80px for sections), clear contrast
- Add hover effects on interactive elements: buttons should have :hover states with transitions (transition: all 0.3s ease)
- Use gradients and modern color schemes: linear-gradient backgrounds, modern color palettes
- Typography: Use system fonts stack (system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif), proper font weights (400, 500, 600, 700)
- Spacing: Generous padding (40-60px vertical, 20-40px horizontal), consistent margins, proper line-height (1.5-1.8)
- Buttons: Modern styling with padding (12-16px vertical, 24-32px horizontal), border-radius (6-8px), hover effects, proper contrast
- Sections: Clear separation with background colors, proper max-width containers (1200px max), centered content
- Cards: Use card-based layouts for features/testimonials with padding, shadows, and hover effects
- Images: Add subtle effects like border-radius, shadows, or overlays to make them more engaging

COLOR CONTRAST RULES (CRITICAL - MUST FOLLOW):
- ALWAYS check background color before setting text color - this is mandatory for readability
- Light backgrounds (white, light gray, light colors) = MUST use dark text (var(--text-color))
- Dark backgrounds (dark gray, black, dark colors) = MUST use light text (var(--text-light))
- Minimum contrast ratio: 4.5:1 for normal text, 3:1 for large text (WCAG AA compliance)
- NEVER use light text (var(--text-light)) on light backgrounds - this creates unreadable text
- NEVER use dark text (var(--text-color)) on dark backgrounds - this creates unreadable text

1. SECTION TITLES/HEADINGS:
   - On light backgrounds (white, light gray, light sections): Use var(--text-color) (dark, #1a1a1a)
   - On dark backgrounds (dark gray, black, dark sections): Use var(--text-light) (white, #ffffff)
   - On colored backgrounds: Calculate contrast - ensure 4.5:1 ratio minimum
   - Section titles MUST be clearly readable against their background

2. TESTIMONIAL CARDS (CRITICAL):
   - Card background: MUST use var(--bg-color) (white/light, #ffffff)
   - Quote text: MUST use var(--text-color) (dark, #1a1a1a) - NEVER use light text
   - Name text: MUST use var(--text-color) (dark, #1a1a1a) - NEVER use light text
   - Role/description: Use var(--text-muted) (gray, #6b7280) for secondary text
   - Star ratings: Use appropriate color (#fbbf24 for gold) that contrasts with card background
   - NEVER use var(--text-light) on testimonial cards - cards have light backgrounds
   - If testimonial section has dark background image, cards must still have light backgrounds with dark text

3. FOOTER (CRITICAL):
   - Background: MUST use var(--bg-dark) (dark, #1a1a1a) or dark variant
   - All text: MUST use var(--text-light) (white, #ffffff) with opacity 0.8-1.0
   - Links: MUST use var(--text-light) (white) with hover using var(--accent-color)
   - Copyright text: Use var(--text-light) with opacity 0.6-0.8
   - Headings in footer: MUST use var(--text-light) (white)
   - NEVER use var(--text-color) (dark) in footer - footer has dark background

4. HERO SECTION (CRITICAL):
   - When using image background: ALWAYS add dark overlay using var(--bg-overlay) (rgba(0, 0, 0, 0.5) minimum)
   - Overlay opacity: Minimum 0.5, preferably 0.6-0.7 for better text readability
   - Text color: MUST use var(--text-light) (white, #ffffff) when overlay is present
   - Headline (h1): MUST use var(--text-light) (white) on image backgrounds
   - Subheadline: MUST use var(--text-light) (white) on image backgrounds
   - Button text: Use appropriate contrast - if button is light, use dark text; if dark, use light text
   - If hero has light background (no image), use var(--text-color) (dark) for text

5. FEATURE CARDS (CRITICAL):
   - Card background: MUST use var(--bg-color) (white/light, #ffffff)
   - Card heading (h3): MUST use var(--text-color) (dark, #1a1a1a)
   - Card description: MUST use var(--text-color) or var(--text-muted) (dark)
   - NEVER use var(--text-light) on feature cards - cards have light backgrounds
   - Icons: Use colors that contrast with card background

6. GENERAL TEXT COLOR RULES:
   - Body text on light backgrounds: var(--text-color) (dark)
   - Body text on dark backgrounds: var(--text-light) (white)
   - Muted/secondary text: var(--text-muted) (gray) - only on light backgrounds
   - Links: Ensure sufficient contrast (4.5:1) against background
   - Buttons: Text color must contrast with button background (light button = dark text, dark button = light text)

7. SECTION BACKGROUNDS:
   - Light sections (features, about, contact): Use light backgrounds with dark text
   - Dark sections (footer, header if dark): Use dark backgrounds with light text
   - Testimonial section: If using background image, ensure cards have light backgrounds with dark text
   - Always verify: dark background = light text, light background = dark text

8. VALIDATION CHECKLIST:
   - Before finalizing, verify every text element has proper contrast
   - Test: Can you easily read all text? If not, fix the color
   - Remember: Light backgrounds need dark text, dark backgrounds need light text
   - Use CSS variables consistently - var(--text-color) for dark, var(--text-light) for white

IMAGE REQUIREMENTS (MANDATORY):
- You MUST include all three provided images in the landing page:
  1. Hero Image: Use the hero image URL in the hero section (main banner area)
     - Display prominently as a visual element (can be background, side-by-side with text, or integrated layout)
     - Coordinate headline, subheadline, and CTA button with the image
     - Style responsively: max-width: 100%, height: auto, object-fit: cover if needed
     - Use proper <img> tag with src attribute and descriptive alt text
     - Add overlay or gradient if text needs better readability over image
  2. Features Image: Use the features image URL ONCE in the features/benefits section
     - DO NOT repeat the same image multiple times - use it as a decorative element or background
     - Create 3+ feature cards/items with icons, titles, and descriptions (use CSS shapes, gradients, or text instead of repeating the image)
     - Integrate the image naturally - perhaps as a section background, header image, or single decorative element
     - Style responsively: max-width: 100%, height: auto
     - Use proper <img> tag with src attribute and descriptive alt text
  3. Testimonials Image: Use the testimonials image URL in the testimonials/reviews section
     - Display as a decorative element or background for the testimonials section
     - Create multiple testimonial cards with quotes, names, and ratings/stars
     - Style responsively: max-width: 100%, height: auto
     - Use proper <img> tag with src attribute and descriptive alt text
- Coordinate the content (headlines, descriptions, colors, layout) to complement and match the style of these images
- Ensure images are properly sized and positioned for both mobile and desktop views
- Use relative paths exactly as specified in the image URLs provided
- Add proper image styling: border-radius, shadows, or effects that match the design

DESIGN FLEXIBILITY:
- VARY your color palette based on business type (e.g., tech = blues/purples, food = warm oranges/reds, luxury = golds/blacks, health = greens/blues)
- VARY your layout structure (some businesses need testimonials, others need product showcases, some need pricing tables)
- VARY your typography (modern sans-serif for tech, elegant serif for luxury, friendly rounded for family businesses)
- VARY your visual style (gradients, solid colors, patterns - coordinate with the provided images)
- Create DIFFERENT designs each time - don't repeat the same template!

PAGE STRUCTURE (adapt based on business, but MUST include all three images):
- Header with navigation (sticky/fixed header preferred, modern styling)
- Hero section (MUST include hero image, compelling headline, subheadline, CTA button)
  - Use modern hero layouts: split-screen, centered with image, or image background with overlay
  - Ensure text is readable with proper contrast
- Main content section (features/benefits - MUST include features image ONCE, create 3+ feature cards)
  - Use card-based layout for features (each feature in its own card with icon/title/description)
  - Features image should be decorative (section header, background, or single visual element)
  - Add icons or visual elements for each feature (use CSS or Unicode symbols)
- Testimonials section (MUST include testimonials image, create 2-3 testimonial cards)
  - Use card-based GRID layout for testimonials - display ALL cards at once in a grid (NO sliders, NO carousels, NO pagination dots)
  - Use CSS Grid or Flexbox to show all testimonial cards side-by-side on desktop, stacked on mobile
  - Each testimonial should be in its own card with quote, name, role/rating
  - Testimonials image can be decorative background or header element
  - Include proper testimonial formatting with quotes, names, and star ratings (★★★★★)
  - DO NOT create any slider, carousel, or pagination controls - just display all testimonials in a clean grid layout
- Additional sections as needed (pricing, gallery, FAQ, etc.)
- Footer (comprehensive with links, social media, contact info)

RESPONSIVE BEHAVIOR:
- Mobile: single column, stacked elements, images full-width, larger touch targets (min 44px)
- Tablet: 2-column layouts where appropriate, images sized appropriately, optimized spacing
- Desktop: multi-column layouts (3+ columns for features/grids), images integrated into layout, max-width containers
- Ensure all interactive elements are easily clickable on mobile
- Use CSS media queries for breakpoints: @media (min-width: 768px) and @media (min-width: 1024px)

DESIGN QUALITY STANDARDS:
- Create a polished, professional, modern-looking landing page
- Use consistent spacing, typography, and color scheme throughout
- Ensure proper contrast ratios for accessibility (WCAG AA standards)
- Add subtle animations/transitions using CSS (no JavaScript)
- Make it visually engaging and conversion-focused
- Use white space effectively for breathing room
- Ensure all elements are properly aligned and balanced

CRITICAL: NO SLIDERS OR CAROUSELS:
- DO NOT create any slider, carousel, or pagination functionality
- DO NOT add navigation dots, arrows, or any slider controls
- Display all content (features, testimonials) in a clean GRID layout using CSS Grid or Flexbox
- Show all testimonial cards at once - they should be visible simultaneously in a grid
- Use responsive grid that shows 1 column on mobile, 2 columns on tablet, 3 columns on desktop
- All content should be static and visible without any scrolling/swiping mechanisms

IMPORTANT: Each landing page should look DIFFERENT and be CUSTOMIZED to the specific business described. 
Don't use the same color scheme, layout, or design pattern for every business!
All three images MUST be included and properly integrated into the design.
DO NOT repeat the same image multiple times - use each image once as specified.
Create a modern, polished UI that looks professional and engaging.
 """



def user_prompt_html_with_template(template: str, description: str, image_urls_text: str) -> str:
    return f"""
You are tasked with modifying an existing HTML landing page template to match a new business description.

EXISTING TEMPLATE HTML:
{template}


AVAILABLE IMAGES (must be used exactly as provided):
{image_urls_text}

MODIFICATION INSTRUCTIONS:
{description}

Apply the requested modifications to the template while preserving its structure, styling patterns, and responsive design. Return the complete modified HTML.
"""

def user_prompt_edit_html(html: str, css: str, edit_request: str) -> str:
    return f"""
You are an expert frontend developer tasked with editing an existing HTML landing page based on a user's request.

CURRENT HTML CODE:
{html}

CURRENT CSS CODE:
{css}

USER'S EDIT REQUEST:
{edit_request}

================================================
EDITING INSTRUCTIONS
================================================

1. UNDERSTAND THE REQUEST:
   - Carefully analyze what the user wants to change
   - Identify which parts of the HTML or CSS need modification
   - Consider the context and intent behind the request

2. PRESERVE EXISTING STRUCTURE:
   - Keep the overall HTML structure intact unless explicitly asked to change it
   - Maintain all existing IDs, classes, and data attributes
   - Preserve navigation structure and layout
   - Keep responsive design patterns
   - Maintain accessibility features

3. MAKE PRECISE CHANGES:
   - Only modify what the user requested
   - Update HTML content (text, images, links) if requested
   - Modify CSS styles (colors, sizes, spacing, fonts) if requested
   - Add new elements only if explicitly requested
   - Remove elements only if explicitly requested

4. CSS MODIFICATIONS:
   - Update existing CSS rules rather than adding duplicates
   - Maintain CSS organization and structure
   - Keep CSS variables if they exist
   - Preserve media queries and responsive breakpoints
   - Ensure CSS is properly formatted and organized

5. HTML MODIFICATIONS:
   - Update text content while preserving HTML structure
   - Replace image URLs if requested
   - Modify attributes (href, src, alt, etc.) if needed
   - Add or remove classes only if necessary for the edit
   - Maintain semantic HTML structure

6. VALIDATION:
   - Ensure all HTML tags are properly closed
   - Verify CSS syntax is correct
   - Check that the modified code is valid and functional
   - Maintain compatibility with existing JavaScript if present

7. RESPONSIVE DESIGN:
   - Ensure changes work across all screen sizes
   - Maintain mobile-first approach if present
   - Keep media queries intact unless modifying breakpoints

================================================
OUTPUT FORMAT
================================================

Return the COMPLETE modified HTML code with embedded CSS in <style> tags.
The output should be a complete, valid HTML document ready to use.

IMPORTANT:
- Return ONLY the complete HTML code
- Include all CSS in <style> tags within <head>
- Do not add explanations or markdown formatting
- Ensure all HTML is valid and properly closed
- The output should be ready to use as-is
"""