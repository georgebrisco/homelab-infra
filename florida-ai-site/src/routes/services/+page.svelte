<script>
  import { fadeIn } from '$lib/actions/fadeIn.js';

  let expandedService = $state(null);
</script>

<section class="section">
  <div class="container">
    <div class="text-center mb-2xl">
      <h1 class="fade-in">Our Services</h1>
      <p class="fade-in text-muted">Comprehensive AI solutions tailored to your business needs</p>
    </div>

    <div class="grid grid-3">
      <div class="service-card fade-in" use:fadeIn onclick={() => expandedService = expandedService === 0 ? null : 0} role="button" tabindex="0">
        <div class="service-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 6V2m0 20v-4m10-4h-4m-12 0H2m17-7l2.828-2.828M4.172 4.172L7 7m10 10l2.828 2.828M4.172 19.828L7 17"></path>
            <circle cx="12" cy="12" r="3"></circle>
          </svg>
        </div>
        <h3>Process Automation</h3>
        <p>Eliminate manual tasks and streamline workflows with intelligent automation.</p>
        {#if expandedService === 0}
          <div class="service-details">
            <ul>
              <li>RPA implementation</li>
              <li>Workflow optimization</li>
              <li>Data entry automation</li>
              <li>Document processing</li>
            </ul>
          </div>
        {/if}
      </div>

      <div class="service-card fade-in" use:fadeIn onclick={() => expandedService = expandedService === 1 ? null : 1} role="button" tabindex="0">
        <div class="service-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"></path>
            <circle cx="9" cy="10" r="1"></circle>
            <circle cx="12" cy="10" r="1"></circle>
            <circle cx="15" cy="10" r="1"></circle>
          </svg>
        </div>
        <h3>AI Chatbots</h3>
        <p>Intelligent conversational AI to enhance customer support and engagement.</p>
        {#if expandedService === 1}
          <div class="service-details">
            <ul>
              <li>Customer service chatbots</li>
              <li>Lead qualification</li>
              <li>24/7 availability</li>
              <li>Multi-language support</li>
            </ul>
          </div>
        {/if}
      </div>

      <div class="service-card fade-in" use:fadeIn onclick={() => expandedService = expandedService === 2 ? null : 2} role="button" tabindex="0">
        <div class="service-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 3h18v18H3z"></path>
            <path d="M3 9h18M9 9v12M15 9v12"></path>
          </svg>
        </div>
        <h3>Data Analytics</h3>
        <p>Transform raw data into actionable insights for better business decisions.</p>
        {#if expandedService === 2}
          <div class="service-details">
            <ul>
              <li>Predictive analytics</li>
              <li>Custom dashboards</li>
              <li>Data visualization</li>
              <li>Business intelligence</li>
            </ul>
          </div>
        {/if}
      </div>

      <div class="service-card fade-in" use:fadeIn onclick={() => expandedService = expandedService === 3 ? null : 3} role="button" tabindex="0">
        <div class="service-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 00-3-3.87"></path>
            <path d="M16 3.13a4 4 0 010 7.75"></path>
          </svg>
        </div>
        <h3>Predictive Lead Scoring</h3>
        <p>Identify and prioritize high-value leads using advanced machine learning.</p>
        {#if expandedService === 3}
          <div class="service-details">
            <ul>
              <li>Lead scoring models</li>
              <li>Sales pipeline optimization</li>
              <li>Conversion prediction</li>
              <li>Customer lifetime value</li>
            </ul>
          </div>
        {/if}
      </div>

      <div class="service-card fade-in" use:fadeIn onclick={() => expandedService = expandedService === 4 ? null : 4} role="button" tabindex="0">
        <div class="service-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 9v3m0 3v3m0-12a9 9 0 110 18 9 9 0 010-18z"></path>
          </svg>
        </div>
        <h3>Computer Vision</h3>
        <p>Leverage image recognition and analysis for quality control and insights.</p>
        {#if expandedService === 4}
          <div class="service-details">
            <ul>
              <li>Image recognition</li>
              <li>Quality inspection</li>
              <li>Object detection</li>
              <li>Video analysis</li>
            </ul>
          </div>
        {/if}
      </div>

      <div class="service-card fade-in" use:fadeIn onclick={() => expandedService = expandedService === 5 ? null : 5} role="button" tabindex="0">
        <div class="service-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
        </div>
        <h3>Custom AI Development</h3>
        <p>Build proprietary AI models specifically designed for your unique challenges.</p>
        {#if expandedService === 5}
          <div class="service-details">
            <ul>
              <li>Model development</li>
              <li>Training & optimization</li>
              <li>Integration & deployment</li>
              <li>Ongoing maintenance</li>
            </ul>
          </div>
        {/if}
      </div>
    </div>
  </div>
</section>

<section class="section section-dark">
  <div class="container">
    <div class="text-center mb-2xl">
      <h2 class="fade-in">Why Choose Florida AI?</h2>
      <p class="fade-in text-muted">What sets us apart</p>
    </div>

    <div class="grid grid-2">
      <div class="benefit-item fade-in" use:fadeIn>
        <div class="benefit-check">✓</div>
        <div>
          <h3>Local Expertise</h3>
          <p>We understand Florida's unique business landscape and challenges.</p>
        </div>
      </div>

      <div class="benefit-item fade-in" use:fadeIn>
        <div class="benefit-check">✓</div>
        <div>
          <h3>Proven Track Record</h3>
          <p>Over 120 successful implementations with measurable ROI.</p>
        </div>
      </div>

      <div class="benefit-item fade-in" use:fadeIn>
        <div class="benefit-check">✓</div>
        <div>
          <h3>Dedicated Support</h3>
          <p>Your success is our mission. We provide ongoing support and optimization.</p>
        </div>
      </div>

      <div class="benefit-item fade-in" use:fadeIn>
        <div class="benefit-check">✓</div>
        <div>
          <h3>Transparent Pricing</h3>
          <p>No hidden fees. You know exactly what you're paying for.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<style>
  .service-card {
    background: white;
    border-radius: var(--radius-xl);
    padding: var(--spacing-xl);
    box-shadow: var(--shadow-md);
    transition: all var(--transition-slow);
    border: 1px solid var(--neutral-100);
    cursor: pointer;
    position: relative;
  }

  .service-card:hover {
    box-shadow: var(--shadow-xl);
    transform: translateY(-4px);
  }

  .service-icon {
    width: 56px;
    height: 56px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--cta) 100%);
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    margin-bottom: var(--spacing-md);
  }

  .service-icon svg {
    width: 28px;
    height: 28px;
  }

  .service-card h3 {
    margin-bottom: var(--spacing-md);
  }

  .service-card p {
    color: var(--neutral-600);
    margin: 0;
  }

  .service-details {
    margin-top: var(--spacing-lg);
    padding-top: var(--spacing-lg);
    border-top: 1px solid var(--neutral-200);
    animation: slideInDown 0.3s ease-out;
  }

  .service-details ul {
    list-style: none;
    margin: 0;
  }

  .service-details li {
    padding: var(--spacing-sm) 0;
    color: var(--neutral-600);
    padding-left: var(--spacing-lg);
    position: relative;
  }

  .service-details li:before {
    content: '→';
    position: absolute;
    left: 0;
    color: var(--accent);
    font-weight: 600;
  }

  @keyframes slideInDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .benefit-item {
    display: flex;
    gap: var(--spacing-lg);
    align-items: flex-start;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
  }

  .benefit-check {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--cta) 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    flex-shrink: 0;
    font-size: var(--font-size-lg);
  }

  .benefit-item h3 {
    color: var(--accent-light);
    margin-bottom: var(--spacing-sm);
  }

  .benefit-item p {
    color: rgba(255, 255, 255, 0.7);
    margin: 0;
  }

  @media (max-width: 768px) {
    .service-card {
      padding: var(--spacing-lg);
    }
  }
</style>
