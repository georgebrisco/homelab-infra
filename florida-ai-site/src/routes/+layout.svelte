<script>
  import '../app.css';
  import { onMount } from 'svelte';

  let mobileMenuOpen = $state(false);
  let scrolled = $state(false);
  let { children } = $props();

  onMount(() => {
    const handleScroll = () => {
      scrolled = window.scrollY > 50;
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  });

  const toggleMobileMenu = () => {
    mobileMenuOpen = !mobileMenuOpen;
  };

  const closeMobileMenu = () => {
    mobileMenuOpen = false;
  };
</script>

<header class="navbar" class:scrolled>
  <nav class="nav-container">
    <div class="nav-brand">
      <a href="/" class="logo">
        <div class="logo-icon">AI</div>
        <span>Florida AI</span>
      </a>
    </div>

    <div class="nav-menu" class:open={mobileMenuOpen}>
      <a href="/" class="nav-link" onclick={closeMobileMenu}>Home</a>
      <a href="/about" class="nav-link" onclick={closeMobileMenu}>About</a>
      <a href="/services" class="nav-link" onclick={closeMobileMenu}>Services</a>
      <a href="/contact" class="nav-link nav-link-cta" onclick={closeMobileMenu}>Contact</a>
    </div>

    <button class="mobile-toggle" onclick={toggleMobileMenu} aria-label="Toggle menu">
      <span></span>
      <span></span>
      <span></span>
    </button>
  </nav>
</header>

<main>
  {@render children()}
</main>

<footer class="footer">
  <div class="container">
    <div class="footer-content">
      <div class="footer-section">
        <h3>Florida AI</h3>
        <p>Empowering Florida's small businesses with intelligent AI solutions.</p>
      </div>
      <div class="footer-section">
        <h4>Links</h4>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/about">About</a></li>
          <li><a href="/services">Services</a></li>
          <li><a href="/contact">Contact</a></li>
        </ul>
      </div>
      <div class="footer-section">
        <h4>Connect</h4>
        <ul>
          <li><a href="#">Twitter</a></li>
          <li><a href="#">LinkedIn</a></li>
          <li><a href="#">GitHub</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; 2024 Florida AI. All rights reserved.</p>
    </div>
  </div>
</footer>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
  }

  .navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;
    background: transparent;
    transition: all var(--transition-slow);
    backdrop-filter: none;
  }

  .navbar.scrolled {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    box-shadow: var(--shadow-md);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  }

  .nav-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--spacing-md) var(--spacing-lg);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .nav-brand {
    flex-shrink: 0;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    color: var(--primary);
    font-weight: 700;
    font-size: var(--font-size-lg);
    transition: color var(--transition-base);
  }

  .logo-icon {
    width: 32px;
    height: 32px;
    border-radius: var(--radius-lg);
    background: linear-gradient(135deg, var(--accent) 0%, var(--cta) 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: var(--font-size-sm);
  }

  .navbar.scrolled .logo {
    color: var(--primary);
  }

  .logo:hover {
    color: var(--accent);
  }

  .nav-menu {
    display: flex;
    gap: var(--spacing-xl);
    align-items: center;
  }

  .nav-link {
    color: var(--primary);
    font-weight: 500;
    font-size: var(--font-size-sm);
    transition: color var(--transition-base);
    position: relative;
  }

  .navbar.scrolled .nav-link {
    color: var(--primary);
  }

  .nav-link:hover {
    color: var(--accent);
  }

  .nav-link-cta {
    padding: var(--spacing-sm) var(--spacing-lg);
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%);
    color: white;
    border-radius: var(--radius-lg);
    font-weight: 600;
  }

  .nav-link-cta:hover {
    color: white;
  }

  .mobile-toggle {
    display: none;
    flex-direction: column;
    gap: 6px;
    background: none;
    border: none;
    cursor: pointer;
    padding: var(--spacing-sm);
  }

  .mobile-toggle span {
    width: 24px;
    height: 2px;
    background: var(--primary);
    border-radius: var(--radius-full);
    transition: all var(--transition-base);
  }

  .mobile-toggle.open span:nth-child(1) {
    transform: rotate(45deg) translateY(10px);
  }

  .mobile-toggle.open span:nth-child(2) {
    opacity: 0;
  }

  .mobile-toggle.open span:nth-child(3) {
    transform: rotate(-45deg) translateY(-10px);
  }

  main {
    padding-top: 80px;
  }

  .footer {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
    color: white;
    padding: var(--spacing-4xl) 0 var(--spacing-2xl);
    margin-top: var(--spacing-4xl);
  }

  .footer-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-2xl);
    margin-bottom: var(--spacing-2xl);
  }

  .footer-section h3,
  .footer-section h4 {
    margin-bottom: var(--spacing-md);
    color: var(--accent-light);
  }

  .footer-section p {
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 0;
  }

  .footer-section ul {
    list-style: none;
  }

  .footer-section li {
    margin-bottom: var(--spacing-sm);
  }

  .footer-section a {
    color: rgba(255, 255, 255, 0.7);
    transition: color var(--transition-base);
  }

  .footer-section a:hover {
    color: var(--accent-light);
  }

  .footer-bottom {
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: var(--spacing-lg);
    text-align: center;
    color: rgba(255, 255, 255, 0.6);
    font-size: var(--font-size-sm);
  }

  @media (max-width: 768px) {
    main {
      padding-top: 70px;
    }

    .mobile-toggle {
      display: flex;
    }

    .nav-menu {
      position: absolute;
      top: 70px;
      left: 0;
      right: 0;
      background: white;
      flex-direction: column;
      gap: 0;
      max-height: 0;
      overflow: hidden;
      transition: max-height var(--transition-slow);
      box-shadow: var(--shadow-md);
    }

    .nav-menu.open {
      max-height: 500px;
    }

    .nav-link {
      display: block;
      padding: var(--spacing-lg);
      border-bottom: 1px solid var(--neutral-100);
      color: var(--primary);
    }

    .nav-link-cta {
      margin: var(--spacing-md);
    }
  }
</style>
