<script>
  import { onMount } from 'svelte';
  import { fadeIn } from '$lib/actions/fadeIn.js';

  let stats = $state({
    clients: 0,
    projects: 0,
    satisfaction: 0
  });

  onMount(() => {
    const delay = setTimeout(() => {
      stats.clients = 50;
      stats.projects = 120;
      stats.satisfaction = 98;
    }, 500);

    return () => clearTimeout(delay);
  });
</script>

<!-- HERO SECTION -->
<section class="hero">
  <div class="hero-background"></div>
  <div class="hero-blob hero-blob-1"></div>
  <div class="hero-blob hero-blob-2"></div>

  <div class="hero-content">
    <h1 class="hero-title">Transform Your Business with AI</h1>
    <p class="hero-subtitle">Custom AI solutions designed for Florida's small businesses. Automate workflows, enhance customer experience, and drive growth.</p>
    <div class="hero-buttons">
      <button class="btn btn-cta">Get Started Today</button>
      <button class="btn btn-secondary">Learn More</button>
    </div>
  </div>
</section>

<!-- PAIN POINTS SECTION -->
<section class="section">
  <div class="container">
    <div class="text-center mb-2xl">
      <h2 class="fade-in">We Solve Real Problems</h2>
      <p class="fade-in text-muted">Challenges small businesses face with manual processes</p>
    </div>

    <div class="grid grid-3">
      <div class="card card-glass fade-in" use:fadeIn>
        <div class="icon-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="1"></circle>
            <path d="M12 9v3m0 3v3m-9-3h3m3-3v3"></path>
            <path d="M3 12a9 9 0 1118 0 9 9 0 01-18 0z"></path>
          </svg>
        </div>
        <h3>Manual Workflows Drain Time</h3>
        <p class="text-muted">Repetitive tasks waste hours every day that could be spent on growing your business.</p>
      </div>

      <div class="card card-glass fade-in" use:fadeIn>
        <div class="icon-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 9v2m0 4v2m0-12h.01M15 9h.01m-6 0h.01M9 15h.01m3 0h.01"></path>
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"></path>
          </svg>
        </div>
        <h3>Security & Data Concerns</h3>
        <p class="text-muted">Protecting customer data and maintaining compliance becomes increasingly complex.</p>
      </div>

      <div class="card card-glass fade-in" use:fadeIn>
        <div class="icon-box">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M13 10V3L4 14h7v7l9-11h-7z"></path>
          </svg>
        </div>
        <h3>Missing Revenue Opportunities</h3>
        <p class="text-muted">Lack of insight into customer behavior means lost opportunities for growth.</p>
      </div>
    </div>
  </div>
</section>

<!-- HOW IT WORKS SECTION -->
<section class="section section-dark">
  <div class="container">
    <div class="text-center mb-2xl">
      <h2 class="fade-in">How It Works</h2>
      <p class="fade-in text-muted">A simple, proven process</p>
    </div>

    <div class="timeline">
      <div class="timeline-item fade-in" use:fadeIn>
        <div class="timeline-number">1</div>
        <h3>Discovery & Analysis</h3>
        <p>We understand your business challenges, goals, and current systems.</p>
      </div>

      <div class="timeline-item fade-in" use:fadeIn>
        <div class="timeline-number">2</div>
        <h3>Custom Solution Design</h3>
        <p>Our AI experts design a tailored solution that fits your workflow.</p>
      </div>

      <div class="timeline-item fade-in" use:fadeIn>
        <div class="timeline-number">3</div>
        <h3>Implementation</h3>
        <p>We deploy and integrate the solution with your existing systems.</p>
      </div>

      <div class="timeline-item fade-in" use:fadeIn>
        <div class="timeline-number">4</div>
        <h3>Training & Support</h3>
        <p>Your team is trained and we provide ongoing support and optimization.</p>
      </div>
    </div>
  </div>
</section>

<!-- PRICING SECTION -->
<section class="section">
  <div class="container">
    <div class="text-center mb-2xl">
      <h2 class="fade-in">Simple, Transparent Pricing</h2>
      <p class="fade-in text-muted">Choose the plan that fits your business</p>
    </div>

    <div class="grid grid-3">
      <div class="card-accent-border fade-in" use:fadeIn>
        <div class="card" style="border: none; background: white;">
          <h3>Starter</h3>
          <div class="price">$999<span>/month</span></div>
          <p class="text-muted">Perfect for small teams just getting started.</p>
          <ul class="feature-list">
            <li>1 AI workflow automation</li>
            <li>Basic support</li>
            <li>Up to 1,000 tasks/month</li>
            <li>Email support</li>
          </ul>
          <button class="btn btn-secondary" style="width: 100%;">Get Started</button>
        </div>
      </div>

      <div class="card-accent-border fade-in featured" use:fadeIn>
        <div class="featured-badge">Most Popular</div>
        <div class="card" style="border: none; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: white;">
          <h3 style="color: white;">Professional</h3>
          <div class="price" style="color: var(--accent-light);">$2,999<span>/month</span></div>
          <p style="color: rgba(255, 255, 255, 0.7);">Best for growing businesses.</p>
          <ul class="feature-list" style="color: rgba(255, 255, 255, 0.8);">
            <li>5 AI workflow automations</li>
            <li>Priority support</li>
            <li>Up to 10,000 tasks/month</li>
            <li>Phone & email support</li>
          </ul>
          <button class="btn btn-cta" style="width: 100%;">Get Started</button>
        </div>
      </div>

      <div class="card-accent-border fade-in" use:fadeIn>
        <div class="card" style="border: none; background: white;">
          <h3>Enterprise</h3>
          <div class="price">Custom</div>
          <p class="text-muted">For enterprises needing custom solutions.</p>
          <ul class="feature-list">
            <li>Unlimited AI workflows</li>
            <li>Dedicated support</li>
            <li>Unlimited tasks</li>
            <li>Custom integrations</li>
          </ul>
          <button class="btn btn-primary" style="width: 100%;">Contact Sales</button>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- TRUST SECTION -->
<section class="section section-dark">
  <div class="container">
    <div class="text-center mb-2xl">
      <h2 class="fade-in">Trusted by Businesses Across Florida</h2>
    </div>

    <div class="grid grid-3">
      <div class="stat-card fade-in" use:fadeIn>
        <div class="stat-number">{stats.clients}+</div>
        <div class="stat-label">Happy Clients</div>
      </div>
      <div class="stat-card fade-in" use:fadeIn>
        <div class="stat-number">{stats.projects}+</div>
        <div class="stat-label">Projects Completed</div>
      </div>
      <div class="stat-card fade-in" use:fadeIn>
        <div class="stat-number">{stats.satisfaction}%</div>
        <div class="stat-label">Satisfaction Rate</div>
      </div>
    </div>
  </div>
</section>

<!-- FINAL CTA SECTION -->
<section class="section section-accent">
  <div class="container">
    <div class="cta-content fade-in" use:fadeIn>
      <h2>Ready to Transform Your Business?</h2>
      <p>Get in touch with our AI experts today and discover how we can help you automate, streamline, and grow.</p>
      <button class="btn btn-secondary">Schedule a Free Consultation</button>
    </div>
  </div>
</section>

<style>
  .hero {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    padding: var(--spacing-3xl) 0;
  }

  .hero-background {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      135deg,
      rgba(15, 23, 42, 0.9) 0%,
      rgba(30, 41, 59, 0.8) 25%,
      rgba(8, 145, 178, 0.3) 50%,
      rgba(15, 23, 42, 0.8) 75%,
      rgba(249, 115, 22, 0.1) 100%
    );
    background-size: 400% 400%;
    animation: gradientMesh 15s ease infinite;
    z-index: 0;
  }

  .hero-blob {
    position: absolute;
    border-radius: 50%;
    mix-blend-mode: screen;
    filter: blur(40px);
  }

  .hero-blob-1 {
    width: 300px;
    height: 300px;
    background: rgba(6, 182, 212, 0.2);
    top: -50px;
    left: -50px;
    animation: float 8s ease-in-out infinite;
  }

  .hero-blob-2 {
    width: 250px;
    height: 250px;
    background: rgba(249, 115, 22, 0.15);
    bottom: -30px;
    right: -30px;
    animation: floatAlt 10s ease-in-out infinite;
  }

  .hero-content {
    position: relative;
    z-index: 2;
    text-align: center;
    color: white;
    animation: fadeInUp 1s ease-out 0.2s backwards;
  }

  .hero-title {
    font-size: var(--font-size-5xl);
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: var(--spacing-lg);
    background: linear-gradient(135deg, white 0%, var(--accent-light) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .hero-subtitle {
    font-size: var(--font-size-xl);
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: var(--spacing-2xl);
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
  }

  .hero-buttons {
    display: flex;
    gap: var(--spacing-md);
    justify-content: center;
    flex-wrap: wrap;
    animation: fadeInUp 1s ease-out 0.4s backwards;
  }

  .icon-box {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--cta) 100%);
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    margin-bottom: var(--spacing-md);
  }

  .icon-box svg {
    width: 24px;
    height: 24px;
  }

  .timeline {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-2xl);
    position: relative;
  }

  .timeline-item {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xl);
    position: relative;
    z-index: 2;
  }

  .timeline-item h3 {
    color: var(--accent-light);
    margin-bottom: var(--spacing-md);
  }

  .timeline-item p {
    color: rgba(255, 255, 255, 0.7);
    margin: 0;
  }

  .timeline-number {
    position: absolute;
    top: -20px;
    left: var(--spacing-lg);
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--cta) 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: var(--font-size-lg);
    color: white;
  }

  .price {
    font-size: var(--font-size-4xl);
    font-weight: 800;
    margin: var(--spacing-lg) 0;
  }

  .price span {
    font-size: var(--font-size-base);
    font-weight: 400;
    color: var(--neutral-600);
  }

  .feature-list {
    list-style: none;
    margin: var(--spacing-xl) 0;
  }

  .feature-list li {
    padding: var(--spacing-sm) 0;
    color: var(--neutral-600);
    display: flex;
    align-items: center;
  }

  .feature-list li:before {
    content: '✓';
    margin-right: var(--spacing-md);
    color: var(--accent);
    font-weight: 700;
  }

  .featured {
    transform: scale(1.05);
  }

  .featured-badge {
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(135deg, var(--accent) 0%, var(--cta) 100%);
    color: white;
    padding: var(--spacing-sm) var(--spacing-lg);
    border-radius: var(--radius-full);
    font-size: var(--font-size-sm);
    font-weight: 600;
    z-index: 10;
  }

  .stat-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-xl);
    padding: var(--spacing-2xl);
    text-align: center;
    backdrop-filter: blur(10px);
  }

  .stat-number {
    font-size: var(--font-size-5xl);
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent-light) 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: var(--spacing-md);
  }

  .stat-label {
    color: rgba(255, 255, 255, 0.7);
    font-weight: 600;
  }

  .cta-content {
    text-align: center;
    color: white;
    max-width: 600px;
    margin: 0 auto;
  }

  .cta-content h2 {
    margin-bottom: var(--spacing-lg);
    color: white;
  }

  .cta-content p {
    font-size: var(--font-size-lg);
    margin-bottom: var(--spacing-2xl);
    color: rgba(255, 255, 255, 0.9);
  }

  @media (max-width: 768px) {
    .hero-title {
      font-size: var(--font-size-4xl);
    }

    .hero-subtitle {
      font-size: var(--font-size-base);
    }

    .timeline {
      grid-template-columns: 1fr;
    }

    .featured {
      transform: scale(1);
    }

    .hero-buttons {
      flex-direction: column;
    }

    .hero-buttons button {
      width: 100%;
    }
  }
</style>
