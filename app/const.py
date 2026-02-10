fallback_css = """
/* CSS Reset */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { font-size: 16px; scroll-behavior: smooth; }
    body {
      font-family: var(--font-main);
      line-height: 1.6;
      color: var(--text-color);
      background-color: var(--bg-color);
      overflow-x: hidden;
      width: 100%;
    }
    img { max-width: 100%; height: auto; display: block; }
    a { text-decoration: none; color: inherit; }
    ul, ol { list-style: none; }
    button { cursor: pointer; border: none; background: none; font-family: inherit; }

    /* CSS Variables */
    :root {
      --primary-color: #2563eb;
      --secondary-color: #7c3aed;
      --accent-color: #f59e0b;
      --text-color: #1a1a1a;
      --text-muted: #6b7280;
      --text-light: #ffffff;
      --bg-color: #ffffff;
      --bg-light: #f9fafb;
      --bg-dark: #1a1a1a;
      --bg-overlay: rgba(0, 0, 0, 0.5);
      --border-color: #e5e7eb;
      --font-main: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      --font-heading: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      --spacing-xs: 0.5rem;
      --spacing-sm: 1rem;
      --spacing-md: 1.5rem;
      --spacing-lg: 2rem;
      --spacing-xl: 3rem;
      --spacing-2xl: 4rem;
      --border-radius: 8px;
      --border-radius-md: 12px;
      --border-radius-lg: 16px;
      --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
      --shadow: 0 4px 6px rgba(0,0,0,0.1);
      --shadow-md: 0 6px 12px rgba(0,0,0,0.1);
      --shadow-lg: 0 10px 24px rgba(0,0,0,0.15);
      --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Base Typography */
    h1 {
      font-size: clamp(2rem, 5vw + 1rem, 4rem);
      font-weight: 700;
      line-height: 1.2;
      margin-bottom: var(--spacing-md);
      color: var(--text-color);
    }
    h2 {
      font-size: clamp(1.75rem, 4vw + 0.5rem, 3rem);
      font-weight: 700;
      line-height: 1.3;
      margin-bottom: var(--spacing-md);
      color: var(--text-color);
    }
    h3 {
      font-size: clamp(1.5rem, 3vw + 0.5rem, 2rem);
      font-weight: 600;
      line-height: 1.4;
      margin-bottom: var(--spacing-sm);
      color: var(--text-color);
    }
    p {
      font-size: clamp(1rem, 2vw, 1.125rem);
      line-height: 1.7;
      margin-bottom: var(--spacing-md);
      color: var(--text-color);
    }
    body { font-size: 16px; }

    /* Container & Layout */
    .container {
      width: 100%;
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 var(--spacing-md);
    }
    @media (min-width: 768px) {
      .container { padding: 0 var(--spacing-lg); }
    }
    @media (min-width: 1024px) {
      .container { padding: 0 var(--spacing-xl); }
    }

    /* Components */
    .btn, .btn-primary {
      display: inline-block;
      padding: 14px 32px;
      font-size: 1rem;
      font-weight: 600;
      text-align: center;
      border-radius: var(--border-radius);
      transition: var(--transition);
      cursor: pointer;
      border: none;
      background-color: var(--accent-color);
      color: var(--text-light);
    }
    .btn:hover, .btn-primary:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-lg);
    }
    .btn:active, .btn-primary:active {
      transform: translateY(0);
    }
    .btn-secondary {
      background-color: transparent;
      border: 2px solid var(--primary-color);
      color: var(--primary-color);
    }
    .btn-secondary:hover {
      background-color: var(--primary-color);
      color: var(--text-light);
    }

    .card {
      background: var(--bg-color);
      border-radius: var(--border-radius-md);
      padding: var(--spacing-lg);
      box-shadow: var(--shadow);
      transition: var(--transition);
      height: 100%;
      display: flex;
      flex-direction: column;
    }
    .card:hover {
      transform: translateY(-4px);
      box-shadow: var(--shadow-lg);
    }
    .card img {
      width: 100%;
      height: auto;
      border-radius: var(--border-radius);
      margin-bottom: var(--spacing-md);
      object-fit: cover;
    }

    .form-group {
      margin-bottom: var(--spacing-md);
    }
    label {
      display: block;
      margin-bottom: var(--spacing-xs);
      font-weight: 500;
      font-size: 0.875rem;
      color: var(--text-color);
    }
    input[type="text"],
    input[type="email"],
    input[type="tel"],
    textarea {
      width: 100%;
      padding: 12px 16px;
      font-size: 1rem;
      font-family: inherit;
      border: 1px solid var(--border-color);
      border-radius: var(--border-radius);
      background-color: var(--bg-color);
      color: var(--text-color);
      transition: var(--transition);
    }
    input:focus, textarea:focus {
      outline: none;
      border-color: var(--primary-color);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    textarea {
      min-height: 120px;
      resize: vertical;
      font-family: inherit;
    }

    /* Grid Layouts */
    .grid {
      display: grid;
      gap: var(--spacing-lg);
      width: 100%;
    }
    .grid-1 { grid-template-columns: 1fr; }
    .grid-2 { grid-template-columns: repeat(2, 1fr); }
    .grid-3 { grid-template-columns: repeat(3, 1fr); }
    @media (max-width: 767px) {
      .grid-2, .grid-3 { grid-template-columns: 1fr; }
    }
    @media (min-width: 768px) and (max-width: 1023px) {
      .grid-3 { grid-template-columns: repeat(2, 1fr); }
    }

    /* Section Spacing */
    section {
      padding: var(--spacing-2xl) 0;
      width: 100%;
    }
    @media (max-width: 767px) {
      section { padding: var(--spacing-xl) 0; }
    }

    /* Image Handling */
    img {
      max-width: 100%;
      height: auto;
      display: block;
      object-fit: cover;
    }
    .hero-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .card-image {
      width: 100%;
      aspect-ratio: 16 / 9;
      object-fit: cover;
      border-radius: var(--border-radius);
    }

    /* Navigation Styles */
    .header {
      position: sticky;
      top: 0;
      z-index: 1000;
      background: var(--bg-dark);
      padding: var(--spacing-md) var(--spacing-lg);
      box-shadow: var(--shadow);
    }
    .nav-container {
      display: flex;
      justify-content: space-between;
      align-items: center;
      max-width: 1200px;
      margin: 0 auto;
    }
    .logo {
      font-weight: 700;
      font-size: clamp(1.25rem, 2vw, 1.5rem);
      color: var(--text-light);
    }
    .nav-toggle {
      display: none;
    }
    .nav-toggle-label {
      display: none;
      flex-direction: column;
      justify-content: space-around;
      width: 30px;
      height: 30px;
      cursor: pointer;
      z-index: 1001;
    }
    .nav-toggle-label span {
      width: 100%;
      height: 3px;
      background: var(--text-light);
      border-radius: 2px;
      transition: var(--transition);
    }
    .nav {
      display: flex;
    }
    .nav-list {
      display: flex;
      gap: var(--spacing-lg);
      align-items: center;
    }
    .nav-list a {
      padding: var(--spacing-sm) var(--spacing-md);
      color: var(--text-light);
      transition: var(--transition);
      border-bottom: 2px solid transparent;
      font-weight: 500;
    }
    .nav-list a:hover {
      border-bottom-color: var(--accent-color);
      color: var(--accent-color);
    }
    @media (max-width: 767px) {
      .nav-toggle-label {
        display: flex;
      }
      .nav {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        width: 100%;
        background: var(--bg-dark);
        box-shadow: var(--shadow-lg);
        padding: var(--spacing-md) 0;
      }
      .nav-toggle:checked ~ .nav {
        display: block;
      }
      .nav-list {
        flex-direction: column;
        gap: 0;
        padding: 0;
      }
      .nav-list li {
        width: 100%;
      }
      .nav-list a {
        display: block;
        padding: var(--spacing-md);
        min-height: 44px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
      }
      .nav-toggle:checked ~ .nav-toggle-label span:nth-child(1) {
        transform: rotate(45deg) translate(8px, 8px);
      }
      .nav-toggle:checked ~ .nav-toggle-label span:nth-child(2) {
        opacity: 0;
      }
      .nav-toggle:checked ~ .nav-toggle-label span:nth-child(3) {
        transform: rotate(-45deg) translate(7px, -7px);
      }
    }

    /* Responsive Breakpoints */
    @media (max-width: 767px) { /* Mobile */ }
    @media (min-width: 768px) and (max-width: 1023px) { /* Tablet */ }
    @media (min-width: 1024px) { /* Desktop */ }

    /* Animations & Transitions */
    * { transition: var(--transition); }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }
    }

"""

fallback_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Gift Shop Landing Page</title>
  
<link rel="stylesheet" href="style.css">
    </head>
<body>
  <header class="header">
    <div class="nav-container">
      <div class="logo">Gift Shop</div>
      <input type="checkbox" id="nav-toggle" class="nav-toggle">
      <label for="nav-toggle" class="nav-toggle-label">
        <span></span>
        <span></span>
        <span></span>
      </label>
      <nav class="nav">
        <ul class="nav-list">
          <li><a href="#home">Home</a></li>
          <li><a href="#about">About</a></li>
          <li><a href="#features">Features</a></li>
          <li><a href="#services">Services</a></li>
          <li><a href="#contact">Contact</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main>
    <section id="hero" style="background-image: url('http://localhost:8000/uploads/hero_1766490617.png'); position: relative; min-height: 70vh;">
      <div class="container" style="position: relative; z-index: 2;">
        <h1>EDIT .....Discover Unique Gifts</h1>
        <p>Find the perfect gift for every occasion</p>
        <button class="btn-primary">Shop Now</button>
      </div>
      <div style="content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: var(--bg-overlay); z-index: 1;"></div>
    </section>

    <section id="about" class="container">
      <div class="grid grid-2">
        <div>
          <h2>About Us</h2>
          <p>We offer a wide range of unique and personalized gifts for all occasions. Our mission is to help you find the perfect gift that will be cherished forever.</p>
        </div>
        <div>
          <img src="http://localhost:8000/uploads/features_1766490618.png" alt="About Image">
        </div>
      </div>
    </section>

    <section id="features" class="container">
      <h2>Our Features</h2>
      <div class="grid grid-3">
        <div class="card">
          <img src="http://localhost:8000/uploads/features_1766490618.png" alt="Feature Image" class="card-image">
          <h3>Quality Products</h3>
          <p>Our products are made with the highest quality materials to ensure durability and satisfaction.</p>
        </div>
        <div class="card">
          <img src="http://localhost:8000/uploads/features_1766490618.png" alt="Feature Image" class="card-image">
          <h3>Custom Designs</h3>
          <p>Personalize your gifts with our wide range of custom design options.</p>
        </div>
        <div class="card">
          <img src="http://localhost:8000/uploads/features_1766490618.png" alt="Feature Image" class="card-image">
          <h3>Fast Shipping</h3>
          <p>We ensure fast and reliable shipping to get your gifts delivered on time.</p>
        </div>
      </div>
    </section>

    <section id="services" class="container" style="background-color: var(--bg-light);">
      <h2>Our Services</h2>
      <div class="grid grid-3">
        <div class="card">
          <img src="http://localhost:8000/uploads/features_1766490618.png" alt="Service Image" class="card-image">
          <h3>Gift Wrapping</h3>
          <p>Beautiful gift wrapping services to add a special touch to your gift.</p>
        </div>
        <div class="card">
          <img src="http://localhost:8000/uploads/features_1766490618.png" alt="Service Image" class="card-image">
          <h3>Personalized Messages</h3>
          <p>Add a personalized message to your gift to make it even more special.</p>
        </div>
        <div class="card">
          <img src="http://localhost:8000/uploads/features_1766490618.png" alt="Service Image" class="card-image">
          <h3>Gift Consultation</h3>
          <p>Need help choosing the perfect gift? Our experts are here to help.</p>
        </div>
      </div>
    </section>

    <section id="testimonials" class="container">
      <h2>Testimonials</h2>
      <div class="grid grid-3">
        <div class="card">
          <img src="http://localhost:8000/uploads/testimonials_1766490616.png" alt="Avatar Image" class="avatar">
          <p>"The best gift shop I've ever visited! Their selection is amazing."</p>
          <p><strong>John Doe</strong></p>
          <p>Customer</p>
        </div>
        <div class="card">
          <img src="http://localhost:8000/uploads/testimonials_1766490616.png" alt="Avatar Image" class="avatar">
          <p>"Fast shipping and excellent customer service. Highly recommend!"</p>
          <p><strong>Jane Smith</strong></p>
          <p>Customer</p>
        </div>
        <div class="card">
          <img src="http://localhost:8000/uploads/testimonials_1766490616.png" alt="Avatar Image" class="avatar">
          <p>"I love their personalized gifts. They're perfect for any occasion."</p>
          <p><strong>Emily Johnson</strong></p>
          <p>Customer</p>
        </div>
      </div>
    </section>

    <section id="faq" class="container">
      <h2>Frequently Asked Questions</h2>
      <div>
        <details>
          <summary>What is your return policy?</summary>
          <p>We offer a 30-day return policy for unused and unopened products.</p>
        </details>
        <details>
          <summary>Do you offer international shipping?</summary>
          <p>Yes, we ship to select countries. Please contact us for more details.</p>
        </details>
        <details>
          <summary>Can I customize my order?</summary>
          <p>Yes, we offer customization options for many of our products.</p>
        </details>
        <details>
          <summary>How do I track my order?</summary>
          <p>You can track your order using the tracking number provided in your confirmation email.</p>
        </details>
        <details>
          <summary>What payment methods do you accept?</summary>
          <p>We accept all major credit cards, PayPal, and Apple Pay.</p>
        </details>
      </div>
    </section>

    <section id="contact" class="container">
      <h2>Contact Us</h2>
      <div class="grid grid-2">
        <div>
          <div class="form-group">
            <label for="name">Name</label>
            <input type="text" id="name" name="name">
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" name="email">
          </div>
          <div class="form-group">
            <label for="message">Message</label>
            <textarea id="message" name="message"></textarea>
          </div>
          <button class="btn-primary" type="submit">Send Message</button>
        </div>
        <div>
          <h3>Our Location</h3>
          <p>123 Gift Shop Lane</p>
          <p>City, State, 12345</p>
          <p>Email: contact@giftshop.com</p>
          <p>Phone: (123) 456-7890</p>
        </div>
      </div>
    </section>
  </main>

  <footer class="footer" style="background-color: var(--bg-dark);">
    <div class="container grid grid-4">
      <div>
        <h3>About Gift Shop</h3>
        <p>Your one-stop shop for unique and personalized gifts

"""


edit_fallback_css = """
/* CSS Reset */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { font-size: 16px; scroll-behavior: smooth; }
    body {
      font-family: var(--font-main);
      line-height: 1.6;
      color: var(--text-color);
      background-color: var(--bg-color);
      overflow-x: hidden;
      width: 100%;
    }
    img { max-width: 100%; height: auto; display: block; }
    a { text-decoration: none; color: inherit; }
    ul, ol { list-style: none; }
    button { cursor: pointer; border: none; background: none; font-family: inherit; }

    /* CSS Variables */
    :root {
      --primary-color: #2563eb;
      --secondary-color: #7c3aed;
      --accent-color: #f59e0b;
      --text-color: #1a1a1a;
      --text-muted: #6b7280;
      --text-light: #ffffff;
      --bg-color: #ffffff;
      --bg-light: #f9fafb;
      --bg-dark: #1a1a1a;
      --bg-overlay: rgba(0, 0, 0, 0.5);
      --border-color: #e5e7eb;
      --font-main: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      --font-heading: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      --spacing-xs: 0.5rem;
      --spacing-sm: 1rem;
      --spacing-md: 1.5rem;
      --spacing-lg: 2rem;
      --spacing-xl: 3rem;
      --spacing-2xl: 4rem;
      --border-radius: 8px;
      --border-radius-md: 12px;
      --border-radius-lg: 16px;
      --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
      --shadow: 0 4px 6px rgba(0,0,0,0.1);
      --shadow-md: 0 6px 12px rgba(0,0,0,0.1);
      --shadow-lg: 0 10px 24px rgba(0,0,0,0.15);
      --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Base Typography */
    h1 {
      font-size: clamp(2rem, 5vw + 1rem, 4rem);
      font-weight: 700;
      line-height: 1.2;
      margin-bottom: var(--spacing-md);
      color: var(--text-color);
    }
    h2 {
      font-size: clamp(1.75rem, 4vw + 0.5rem, 3rem);
      font-weight: 700;
      line-height: 1.3;
      margin-bottom: var(--spacing-md);
      color: var(--text-color);
    }
    h3 {
      font-size: clamp(1.5rem, 3vw + 0.5rem, 2rem);
      font-weight: 600;
      line-height: 1.4;
      margin-bottom: var(--spacing-sm);
      color: var(--text-color);
    }
    p {
      font-size: clamp(1rem, 2vw, 1.125rem);
      line-height: 1.7;
      margin-bottom: var(--spacing-md);
      color: var(--text-color);
    }
    body { font-size: 16px; }

    /* Container & Layout */
    .container {
      width: 100%;
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 var(--spacing-md);
    }
    @media (min-width: 768px) {
      .container { padding: 0 var(--spacing-lg); }
    }
    @media (min-width: 1024px) {
      .container { padding: 0 var(--spacing-xl); }
    }

    /* Components */
    .btn, .btn-primary {
      display: inline-block;
      padding: 14px 32px;
      font-size: 1rem;
      font-weight: 600;
      text-align: center;
      border-radius: var(--border-radius);
      transition: var(--transition);
      cursor: pointer;
      border: none;
      background-color: var(--accent-color);
      color: var(--text-light);
    }
    .btn:hover, .btn-primary:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-lg);
    }
    .btn:active, .btn-primary:active {
      transform: translateY(0);
    }
    .btn-secondary {
      background-color: transparent;
      border: 2px solid var(--primary-color);
      color: var(--primary-color);
    }
    .btn-secondary:hover {
      background-color: var(--primary-color);
      color: var(--text-light);
    }

    .card {
      background: var(--bg-color);
      border-radius: var(--border-radius-md);
      padding: var(--spacing-lg);
      box-shadow: var(--shadow);
      transition: var(--transition);
      height: 100%;
      display: flex;
      flex-direction: column;
    }
    .card:hover {
      transform: translateY(-4px);
      box-shadow: var(--shadow-lg);
    }
    .card img {
      width: 100%;
      height: auto;
      border-radius: var(--border-radius);
      margin-bottom: var(--spacing-md);
      object-fit: cover;
    }

    .form-group {
      margin-bottom: var(--spacing-md);
    }
    label {
      display: block;
      margin-bottom: var(--spacing-xs);
      font-weight: 500;
      font-size: 0.875rem;
      color: var(--text-color);
    }
    input[type="text"],
    input[type="email"],
    input[type="tel"],
    textarea {
      width: 100%;
      padding: 12px 16px;
      font-size: 1rem;
      font-family: inherit;
      border: 1px solid var(--border-color);
      border-radius: var(--border-radius);
      background-color: var(--bg-color);
      color: var(--text-color);
      transition: var(--transition);
    }
    input:focus, textarea:focus {
      outline: none;
      border-color: var(--primary-color);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    }
    textarea {
      min-height: 120px;
      resize: vertical;
      font-family: inherit;
    }

    /* Grid Layouts */
    .grid {
      display: grid;
      gap: var(--spacing-lg);
      width: 100%;
    }
    .grid-1 { grid-template-columns: 1fr; }
    .grid-2 { grid-template-columns: repeat(2, 1fr); }
    .grid-3 { grid-template-columns: repeat(3, 1fr); }
    @media (max-width: 767px) {
      .grid-2, .grid-3 { grid-template-columns: 1fr; }
    }
    @media (min-width: 768px) and (max-width: 1023px) {
      .grid-3 { grid-template-columns: repeat(2, 1fr); }
    }

    /* Section Spacing */
    section {
      padding: var(--spacing-2xl) 0;
      width: 100%;
    }
    @media (max-width: 767px) {
      section { padding: var(--spacing-xl) 0; }
    }

    /* Image Handling */
    img {
      max-width: 100%;
      height: auto;
      display: block;
      object-fit: cover;
    }
    .hero-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .card-image {
      width: 100%;
      aspect-ratio: 16 / 9;
      object-fit: cover;
      border-radius: var(--border-radius);
    }

    /* Navigation Styles */
    .header {
      position: sticky;
      top: 0;
      z-index: 1000;
      background: var(--bg-dark);
      padding: var(--spacing-md) var(--spacing-lg);
      box-shadow: var(--shadow);
    }
    .nav-container {
      display: flex;
      justify-content: space-between;
      align-items: center;
      max-width: 1200px;
      margin: 0 auto;
    }
    .logo {
      font-weight: 700;
      font-size: clamp(1.25rem, 2vw, 1.5rem);
      color: var(--text-light);
    }
    .nav-toggle {
      display: none;
    }
    .nav-toggle-label {
      display: none;
      flex-direction: column;
      justify-content: space-around;
      width: 30px;
      height: 30px;
      cursor: pointer;
      z-index: 1001;
    }
    .nav-toggle-label span {
      width: 100%;
      height: 3px;
      background: var(--text-light);
      border-radius: 2px;
      transition: var(--transition);
    }
    .nav {
      display: flex;
    }
    .nav-list {
      display: flex;
      gap: var(--spacing-lg);
      align-items: center;
    }
    .nav-list a {
      padding: var(--spacing-sm) var(--spacing-md);
      color: var(--text-light);
      transition: var(--transition);
      border-bottom: 2px solid transparent;
      font-weight: 500;
    }
    .nav-list a:hover {
      border-bottom-color: var(--accent-color);
      color: var(--accent-color);
    }
    @media (max-width: 767px) {
      .nav-toggle-label {
        display: flex;
      }
      .nav {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        width: 100%;
        background: var(--bg-dark);
        box-shadow: var(--shadow-lg);
        padding: var(--spacing-md) 0;
      }
      .nav-toggle:checked ~ .nav {
        display: block;
      }
      .nav-list {
        flex-direction: column;
        gap: 0;
        padding: 0;
      }
      .nav-list li {
        width: 100%;
      }
      .nav-list a {
        display: block;
        padding: var(--spacing-md);
        min-height: 44px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
      }
      .nav-toggle:checked ~ .nav-toggle-label span:nth-child(1) {
        transform: rotate(45deg) translate(8px, 8px);
      }
      .nav-toggle:checked ~ .nav-toggle-label span:nth-child(2) {
        opacity: 0;
      }
      .nav-toggle:checked ~ .nav-toggle-label span:nth-child(3) {
        transform: rotate(-45deg) translate(7px, -7px);
      }
    }

    /* Responsive Breakpoints */
    @media (max-width: 767px) { /* Mobile */ }
    @media (min-width: 768px) and (max-width: 1023px) { /* Tablet */ }
    @media (min-width: 1024px) { /* Desktop */ }

    /* Animations & Transitions */
    * { transition: var(--transition); }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
      }
    }

"""

edit_fallback_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>edit Gift Shop  Landing Page</title>
  
<link rel="stylesheet" href="style.css">
    </head>
<body>
  <header class="header">
    <div class="nav-container">
      <div class="logo">Gift Shop</div>
      <input type="checkbox" id="nav-toggle" class="nav-toggle">
      <label for="nav-toggle" class="nav-toggle-label">
        <span></span>
        <span></span>
        <span></span>
      </label>
      <nav class="nav">
        <ul class="nav-list">
          <li><a href="#home">Home</a></li>
          <li><a href="#about">About</a></li>
          <li><a href="#features">Features</a></li>
          <li><a href="#services">Services</a></li>
          <li><a href="#contact">Contact</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main>
    <section id="hero" style="background-image: url('http://localhost:8000/uploads/hero_1766490617.png'); position: relative; min-height: 70vh;">
      <div class="container" style="position: relative; z-index: 2;">
        <h1>Discover Unique Gifts</h1>
        <p>Find the perfect gift for every occasion</p>
        <button class="btn-primary">Shop Now</button>
      </div>
      <div style="content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: var(--bg-overlay); z-index: 1;"></div>
    </section>

    <section id="about" class="container">
      <div class="grid grid-2">
        <div>
          <h2>About Us</h2>
          <p>We offer a wide range of unique and personalized gifts for all occasions. Our mission is to help you find the perfect gift that will be cherished forever.</p>
        </div>
        <div>
          <img src="http://localhost:8000/uploads/features_1766490618.png" alt="About Image">
        </div>
      </div>
    </section>

    <section id="features" class="container">
      <h2>Our Features</h2>
      <div class="grid grid-3">
        <div class="card">
          <img src="http://localhost:8000/uploads/features_1766490618.png" alt="Feature Image" class="card-image">
          <h3>Quality Products</h3>
          <p>Our products are made with the highest quality materials to ensure durability and satisfaction.</p>
        </div>
        <div class="card">
          <img src="http://localhost:8000/uploads/features_1766490618.png" alt="Feature Image" class="card-image">
          <h3>Custom Designs</h3>
          <p>Personalize your gifts with our wide range of custom design options.</p>
        </div>
        <div class="card">
          <img src="http://localhost:8000/uploads/features_1766490618.png" alt="Feature Image" class="card-image">
          <h3>Fast Shipping</h3>
          <p>We ensure fast and reliable shipping to get your gifts delivered on time.</p>
        </div>
      </div>
    </section>

    <section id="services" class="container" style="background-color: var(--bg-light);">
      <h2>Our Services</h2>
      <div class="grid grid-3">
        <div class="card">
          <img src="http://localhost:8000/uploads/features_1766490618.png" alt="Service Image" class="card-image">
          <h3>Gift Wrapping</h3>
          <p>Beautiful gift wrapping services to add a special touch to your gift.</p>
        </div>
        <div class="card">
          <img src="http://localhost:8000/uploads/features_1766490618.png" alt="Service Image" class="card-image">
          <h3>Personalized Messages</h3>
          <p>Add a personalized message to your gift to make it even more special.</p>
        </div>
        <div class="card">
          <img src="http://localhost:8000/uploads/features_1766490618.png" alt="Service Image" class="card-image">
          <h3>Gift Consultation</h3>
          <p>Need help choosing the perfect gift? Our experts are here to help.</p>
        </div>
      </div>
    </section>

    <section id="testimonials" class="container">
      <h2>Testimonials</h2>
      <div class="grid grid-3">
        <div class="card">
          <img src="http://localhost:8000/uploads/testimonials_1766490616.png" alt="Avatar Image" class="avatar">
          <p>"The best gift shop I've ever visited! Their selection is amazing."</p>
          <p><strong>John Doe</strong></p>
          <p>Customer</p>
        </div>
        <div class="card">
          <img src="http://localhost:8000/uploads/testimonials_1766490616.png" alt="Avatar Image" class="avatar">
          <p>"Fast shipping and excellent customer service. Highly recommend!"</p>
          <p><strong>Jane Smith</strong></p>
          <p>Customer</p>
        </div>
        <div class="card">
          <img src="http://localhost:8000/uploads/testimonials_1766490616.png" alt="Avatar Image" class="avatar">
          <p>"I love their personalized gifts. They're perfect for any occasion."</p>
          <p><strong>Emily Johnson</strong></p>
          <p>Customer</p>
        </div>
      </div>
    </section>

    <section id="faq" class="container">
      <h2>Frequently Asked Questions</h2>
      <div>
        <details>
          <summary>What is your return policy?</summary>
          <p>We offer a 30-day return policy for unused and unopened products.</p>
        </details>
        <details>
          <summary>Do you offer international shipping?</summary>
          <p>Yes, we ship to select countries. Please contact us for more details.</p>
        </details>
        <details>
          <summary>Can I customize my order?</summary>
          <p>Yes, we offer customization options for many of our products.</p>
        </details>
        <details>
          <summary>How do I track my order?</summary>
          <p>You can track your order using the tracking number provided in your confirmation email.</p>
        </details>
        <details>
          <summary>What payment methods do you accept?</summary>
          <p>We accept all major credit cards, PayPal, and Apple Pay.</p>
        </details>
      </div>
    </section>

    <section id="contact" class="container">
      <h2>Contact Us</h2>
      <div class="grid grid-2">
        <div>
          <div class="form-group">
            <label for="name">Name</label>
            <input type="text" id="name" name="name">
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" name="email">
          </div>
          <div class="form-group">
            <label for="message">Message</label>
            <textarea id="message" name="message"></textarea>
          </div>
          <button class="btn-primary" type="submit">Send Message</button>
        </div>
        <div>
          <h3>Our Location</h3>
          <p>123 Gift Shop Lane</p>
          <p>City, State, 12345</p>
          <p>Email: contact@giftshop.com</p>
          <p>Phone: (123) 456-7890</p>
        </div>
      </div>
    </section>
  </main>

  <footer class="footer" style="background-color: var(--bg-dark);">
    <div class="container grid grid-4">
      <div>
        <h3>About Gift Shop</h3>
        <p>Your one-stop shop for unique and personalized gifts

"""