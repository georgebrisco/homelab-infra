<script>
  import { fadeIn } from '$lib/actions/fadeIn.js';
</script>

<section class="section">
  <div class="container">
    <div class="about-header fade-in" use:fadeIn>
      <h1>About Florida AI</h1>
      <p class="lead">We're on a mission to democratize AI for Florida's small businesses.</p>
    </div>

    <div class="about-grid">
      <div class="about-content fade-in" use:fadeIn>
        <h2>Our Story</h2>
        <p>Florida AI was founded with a simple belief: artificial intelligence shouldn't be exclusive to large enterprises. Small businesses deserve access to the same powerful AI tools that drive innovation and growth at Fortune 500 companies.</p>
        <p>Our team of AI experts and business consultants combines deep technical knowledge with real-world experience helping Florida's diverse small business community thrive in an increasingly digital world.</p>
      </div>

      <div class="about-image fade-in" use:fadeIn>
        <div class="image-placeholder">
          <div class="placeholder-icon">
            <svg viewBox="0 0 100 100" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="50" cy="50" r="40"></circle>
              <path d="M30 40c0-5.523 4.477-10 10-10h20c5.523 0 10 4.477 10 10"></path>
              <circle cx="40" cy="35" r="3"></circle>
              <circle cx="60" cy="35" r="3"></circle>
              <path d="M45 60c5 3 10 3 10 0"></path>
            </svg>
          </div>
          Team Photo Area
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section-dark">
  <div class="container">
    <div class="text-center mb-2xl">
      <h2 class="fade-in">Our Values</h2>
      <p class="fade-in text-muted">What drives us every day</p>
    </div>

    <div class="grid grid-3">
      <div class="value-card fade-in" use:fadeIn>
        <div class="value-icon">AI</div>
        <h3>Innovation First</h3>
        <p>We stay at the cutting edge of AI technology to deliver the best solutions for our clients.</p>
      </div>

      <div class="value-card fade-in" use:fadeIn>
        <div class="value-icon">✓</div>
        <h3>Customer Success</h3>
        <p>Your success is our success. We're committed to delivering measurable results and long-term partnerships.</p>
      </div>

      <div class="value-card fade-in" use:fadeIn>
        <div class="value-icon">◆</div>
        <h3>Transparency</h3>
        <p>We believe in clear communication, honest pricing, and transparent partnerships from day one.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="text-center mb-2xl">
      <h2 class="fade-in">Company Timeline</h2>
      <p class="fade-in text-muted">Our journey so far</p>
    </div>

    <div class="timeline-vertical">
      <div class="timeline-event fade-in" use:fadeIn>
        <div class="event-dot"></div>
        <div class="event-content">
          <h3>2022</h3>
          <p>Florida AI founded with a vision to democratize AI access for small businesses</p>
        </div>
      </div>

      <div class="timeline-event fade-in" use:fadeIn>
        <div class="event-dot"></div>
        <div class="event-content">
          <h3>2023</h3>
          <p>Completed first 50 AI implementations across Florida's diverse industries</p>
        </div>
      </div>

      <div class="timeline-event fade-in" use:fadeIn>
        <div class="event-dot"></div>
        <div class="event-content">
          <h3>2024</h3>
          <p>Expanded to 150+ happy clients with 98% satisfaction rate</p>
        </div>
      </div>

      <div class="timeline-event fade-in" use:fadeIn>
        <div class="event-dot"></div>
        <div class="event-content">
          <h3>2025</h3>
          <p>Launching enterprise solutions and strategic partnerships across the region</p>
        </div>
      </div>
    </div>
  </div>
</section>

<style>
  .about-header {
    text-align: center;
    margin-bottom: var(--spacing-4xl);
  }

  .about-header h1 {
    font-size: var(--font-size-5xl);
    margin-bottom: var(--spacing-lg);
    background: linear-gradient(135deg, var(--accent) 0%, var(--cta) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .lead {
    font-size: var(--font-size-xl);
    color: var(--neutral-600);
    max-width: 600px;
    margin: 0 auto;
  }

  .about-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-3xl);
    align-items: center;
    margin-bottom: var(--spacing-4xl);
  }

  .about-content h2 {
    margin-bottom: var(--spacing-lg);
  }

  .about-content p {
    font-size: var(--font-size-lg);
    line-height: 1.8;
    color: var(--neutral-600);
    margin-bottom: var(--spacing-lg);
  }

  .image-placeholder {
    width: 100%;
    aspect-ratio: 1;
    background: linear-gradient(135deg, var(--neutral-100) 0%, var(--neutral-200) 100%);
    border-radius: var(--radius-2xl);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 2px dashed var(--neutral-300);
    color: var(--neutral-500);
  }

  .placeholder-icon {
    width: 80px;
    height: 80px;
    color: var(--neutral-400);
    margin-bottom: var(--spacing-md);
  }

  .value-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xl);
    text-align: center;
    color: white;
    backdrop-filter: blur(10px);
  }

  .value-icon {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--cta) 100%);
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: var(--font-size-2xl);
    margin: 0 auto var(--spacing-lg);
  }

  .value-card h3 {
    color: var(--accent-light);
    margin-bottom: var(--spacing-md);
  }

  .value-card p {
    color: rgba(255, 255, 255, 0.7);
    margin: 0;
  }

  .timeline-vertical {
    position: relative;
    padding: var(--spacing-lg) 0;
  }

  .timeline-vertical:before {
    content: '';
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(to bottom, var(--accent), var(--cta));
  }

  .timeline-event {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    gap: var(--spacing-2xl);
    align-items: center;
    margin-bottom: var(--spacing-3xl);
  }

  .timeline-event:nth-child(even) {
    direction: rtl;
  }

  .event-dot {
    width: 16px;
    height: 16px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--cta) 100%);
    border-radius: 50%;
    box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
  }

  .event-content {
    direction: ltr;
  }

  .event-content h3 {
    color: var(--accent);
    margin-bottom: var(--spacing-sm);
  }

  .event-content p {
    color: var(--neutral-600);
    margin: 0;
  }

  @media (max-width: 768px) {
    .about-grid {
      grid-template-columns: 1fr;
    }

    .timeline-vertical:before {
      left: 8px;
    }

    .timeline-event {
      grid-template-columns: auto 1fr;
      direction: ltr;
    }

    .timeline-event:nth-child(even) {
      direction: ltr;
    }

    .event-dot {
      margin-top: 6px;
    }
  }
</style>
