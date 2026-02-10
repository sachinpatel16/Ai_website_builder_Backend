# API Documentation

**Version:** 1.0.0  
**Base URL:** `http://localhost:8000` (configurable via `BASE_URL` environment variable)

---

## Overview

This API provides a multi-stage process for generating AI-powered landing pages:
1. **Stage 1:** Generate image prompts for different sections
2. **Stage 2:** Generate images using DALL-E 3
3. **Stage 3:** Generate complete HTML landing page
4. **Stage 4:** Edit existing HTML/CSS content

---

## Endpoints

### 1. Root Endpoint

**URL:** `GET /`

**Description:** Returns basic API information and version.

**Request Body:** None

**Response:**
```json
{
  "message": "AI Landing Page Generator API",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK` - Success

---

### 2. Generate Prompts (Stage 1)

**URL:** `POST /api/generate-prompts`

**Description:** Generates AI image prompts for hero, features, and testimonials sections based on the provided business/product description. This is the first stage of the landing page generation process.

**Request Body:**
```json
{
  "description": "string (minimum 10 characters)"
}
```

**Example Request:**
```json
{
  "description": "A modern SaaS platform for project management with team collaboration features, real-time updates, and advanced analytics"
}
```

**Response:**
```json
{
  "prompts": {
    "hero": "string - Generated prompt for hero section background image",
    "features": "string - Generated prompt for features section background image",
    "testimonials": "string - Generated prompt for testimonials section background image"
  }
}
```

**Example Response:**
```json
{
  "prompts": {
    "hero": "Modern workspace with team collaboration, sleek design, professional atmosphere, wide aspect ratio, eye-catching, suitable for large header area with text overlay space",
    "features": "Clean, minimal dashboard interface showing project management tools, clean UI, productivity focus, supports multiple feature cards, subtle and professional",
    "testimonials": "Trustworthy, professional atmosphere, subtle patterns or gradients, warm and inviting background suitable for testimonials section"
  }
}
```

**Status Codes:**
- `200 OK` - Prompts generated successfully
- `400 Bad Request` - Description is missing or less than 10 characters
- `500 Internal Server Error` - Server error or OpenAI API error

**Error Response:**
```json
{
  "detail": "Description must be at least 10 characters long"
}
```

---

### 3. Generate Images (Stage 2)

**URL:** `POST /api/generate-images`

**Description:** Generates images using DALL-E 3 API for each provided prompt. Images are generated in parallel for better performance. Hero images are generated at 1792x1024 resolution, while features and testimonials images are generated at 1024x1024. This is the second stage of the landing page generation process.

**Request Body:**
```json
{
  "prompts": {
    "hero": "string - Prompt for hero section image",
    "features": "string - Prompt for features section image",
    "testimonials": "string - Prompt for testimonials section image"
  }
}
```

**Example Request:**
```json
{
  "prompts": {
    "hero": "Modern workspace with team collaboration, sleek design, professional atmosphere, wide aspect ratio, eye-catching, suitable for large header area with text overlay space",
    "features": "Clean, minimal dashboard interface showing project management tools, clean UI, productivity focus, supports multiple feature cards, subtle and professional",
    "testimonials": "Trustworthy, professional atmosphere, subtle patterns or gradients, warm and inviting background suitable for testimonials section"
  }
}
```

**Response:**
```json
{
  "images": {
    "hero": "string - Local URL of generated hero image (e.g., /uploads/hero_1234567890.png)",
    "features": "string - Local URL of generated features image (e.g., /uploads/features_1234567890.png)",
    "testimonials": "string - Local URL of generated testimonials image (e.g., /uploads/testimonials_1234567890.png)"
  }
}
```

**Example Response:**
```json
{
  "images": {
    "hero": "/uploads/hero_1728123456.png",
    "features": "/uploads/features_1728123457.png",
    "testimonials": "/uploads/testimonials_1728123458.png"
  }
}
```

**Status Codes:**
- `200 OK` - Images generated successfully
- `400 Bad Request` - Prompts are missing or required sections (hero, features, testimonials) are not provided
- `500 Internal Server Error` - Server error or DALL-E API error

**Error Response:**
```json
{
  "detail": "Missing prompt for hero section"
}
```

---

### 4. Generate HTML (Stage 3)

**URL:** `POST /api/generate-html`

**Description:** Generates a complete, responsive HTML landing page using OpenAI GPT-4o. The HTML includes a link tag to an external CSS file, and the CSS is extracted from style tags. The generated HTML incorporates the provided images into hero, features, and testimonials sections. If a template is provided, it modifies the template according to the description; otherwise, it generates HTML from scratch. This is the third stage of the landing page generation process.

**Request Body:**
```json
{
  "description": "string (minimum 10 characters) - Original landing page description",
  "images": {
    "hero": "string - URL of hero image",
    "features": "string - URL of features image",
    "testimonials": "string - URL of testimonials image"
  },
  "template": "string (optional) - Existing HTML template to modify"
}
```

**Example Request:**
```json
{
  "description": "A modern SaaS platform for project management with team collaboration features, real-time updates, and advanced analytics",
  "images": {
    "hero": "/uploads/hero_1728123456.png",
    "features": "/uploads/features_1728123457.png",
    "testimonials": "/uploads/testimonials_1728123458.png"
  },
  "template": null
}
```

**Example Request with Template:**
```json
{
  "description": "A modern SaaS platform for project management with team collaboration features",
  "images": {
    "hero": "/uploads/hero_1728123456.png",
    "features": "/uploads/features_1728123457.png",
    "testimonials": "/uploads/testimonials_1728123458.png"
  },
  "template": "<!DOCTYPE html><html><head><title>Template</title></head><body>...</body></html>"
}
```

**Response:**
```json
{
  "html": "string - Complete HTML code with external CSS link tag",
  "css": "string - Extracted CSS content"
}
```

**Example Response:**
```json
{
  "html": "<!DOCTYPE html><html><head><title>Landing Page</title><link rel=\"stylesheet\" href=\"style.css\"></head><body>...</body></html>",
  "css": "body { margin: 0; padding: 0; font-family: Arial, sans-serif; } ..."
}
```

**Status Codes:**
- `200 OK` - HTML generated successfully
- `400 Bad Request` - Description is missing/too short or images are missing/required sections not provided
- `500 Internal Server Error` - Server error or OpenAI API error

**Error Response:**
```json
{
  "detail": "Description must be at least 10 characters long"
}
```

---

### 5. Edit HTML (Stage 4)

**URL:** `POST /api/edit-html`

**Description:** Edits existing HTML/CSS content based on user's edit request. The AI modifies the provided HTML and CSS while preserving structure, functionality, and responsive design. CSS is extracted from HTML style tags if not provided separately. The response includes HTML with external CSS link tag and extracted CSS content.

**Request Body:**
```json
{
  "html": "string - Existing HTML content",
  "css": "string - Existing CSS content (optional, will be extracted from HTML if not provided)",
  "edit_request": "string (minimum 5 characters) - Description of desired changes"
}
```

**Example Request:**
```json
{
  "html": "<!DOCTYPE html><html><head><title>Landing Page</title><link rel=\"stylesheet\" href=\"style.css\"></head><body><h1>Welcome</h1></body></html>",
  "css": "body { margin: 0; padding: 0; } h1 { color: blue; }",
  "edit_request": "Change the heading color to red and add a blue background to the body"
}
```

**Response:**
```json
{
  "html": "string - Modified HTML code with external CSS link tag",
  "css": "string - Modified CSS content"
}
```

**Example Response:**
```json
{
  "html": "<!DOCTYPE html><html><head><title>Landing Page</title><link rel=\"stylesheet\" href=\"style.css\"></head><body><h1>Welcome</h1></body></html>",
  "css": "body { margin: 0; padding: 0; background-color: blue; } h1 { color: red; }"
}
```

**Status Codes:**
- `200 OK` - HTML edited successfully
- `400 Bad Request` - HTML content is missing or edit request is too short (less than 5 characters)
- `500 Internal Server Error` - Server error or OpenAI API error

**Error Response:**
```json
{
  "detail": "HTML content is required"
}
```

---

## Complete Workflow Example

### Step 1: Generate Prompts
```bash
curl -X POST "http://localhost:8000/api/generate-prompts" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "A modern SaaS platform for project management with team collaboration features"
  }'
```

### Step 2: Generate Images
```bash
curl -X POST "http://localhost:8000/api/generate-images" \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": {
      "hero": "Modern workspace with team collaboration, sleek design, professional atmosphere",
      "features": "Dashboard interface showing project management tools, clean UI, productivity focus",
      "testimonials": "Trustworthy, professional atmosphere, subtle patterns or gradients, warm and inviting"
    }
  }'
```

### Step 3: Generate HTML
```bash
curl -X POST "http://localhost:8000/api/generate-html" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "A modern SaaS platform for project management with team collaboration features",
    "images": {
      "hero": "/uploads/hero_1728123456.png",
      "features": "/uploads/features_1728123457.png",
      "testimonials": "/uploads/testimonials_1728123458.png"
    }
  }'
```

### Step 4: Edit HTML (Optional)
```bash
curl -X POST "http://localhost:8000/api/edit-html" \
  -H "Content-Type: application/json" \
  -d '{
    "html": "<!DOCTYPE html>...",
    "css": "body { margin: 0; }",
    "edit_request": "Change the background color to dark blue and make text white"
  }'
```

---

## Error Handling

All endpoints return standard HTTP status codes. Error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

### Common Error Scenarios

1. **400 Bad Request**
   - Missing required fields
   - Invalid input format
   - Description too short (< 10 characters)
   - Edit request too short (< 5 characters)
   - Missing required sections in prompts/images

2. **500 Internal Server Error**
   - OpenAI API errors
   - DALL-E API errors
   - Internal server errors

---

## Environment Variables

The API requires the following environment variables to be configured:

- `OPENAI_API_KEY` - OpenAI API key (required for prompt generation and HTML generation)
- `BASE_URL` - Base URL for the API (default: `http://localhost:8000`, used for converting relative image paths to full URLs)

---

## Notes

- All endpoints use JSON for request and response bodies
- The API uses async/await for better performance
- Image generation (Stage 2) runs in parallel for all three sections
- HTML generation (Stage 3) automatically extracts CSS from style tags and replaces them with external link tags
- Image URLs are served via the `/uploads` static file endpoint
- All endpoints support CORS (configured to accept requests from any origin)
- Hero images are generated at 1792x1024 resolution
- Features and testimonials images are generated at 1024x1024 resolution

