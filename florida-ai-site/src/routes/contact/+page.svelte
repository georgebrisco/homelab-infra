<script>
  import { fadeIn } from '$lib/actions/fadeIn.js';

  let formData = {
    name: '',
    email: '',
    company: '',
    message: ''
  };

  let submitted = $state(false);
  let isSubmitting = $state(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    isSubmitting = true;
    
    // Simulate form submission
    setTimeout(() => {
      submitted = true;
      isSubmitting = false;
      // Reset form after 3 seconds
      setTimeout(() => {
        submitted = false;
        formData = { name: '', email: '', company: '', message: '' };
      }, 3000);
    }, 1000);
  };
</script>

<section class="section">
  <div class="container">
    <div class="contact-grid">
      <div class="contact-form-section fade-in" use:fadeIn>
        <h1>Get in Touch</h1>
        <p class="text-muted">Have questions? Our team is ready to help you transform your business.</p>

        {#if submitted}
          <div class="success-message">
            <div class="success-icon">✓</div>
            <h3>Thank You!</h3>
            <p>We've received your message and will get back to you soon.</p>
          </div>
        {:else}
          <form on:submit={handleSubmit} class="contact-form">
            <div class="form-group">
              <label for="name">Your Name</label>
              <input
                type="text"
                id="name"
                placeholder="John Smith"
                bind:value={formData.name}
                required
              />
            </div>

            <div class="form-group">
              <label for="email">Email Address</label>
              <input
                type="email"
                id="email"
                placeholder="john@company.com"
                bind:value={formData.email}
                required
              />
            </div>

            <div class="form-group">
              <label for="company">Company Name</label>
              <input
                type="text"
                id="company"
                placeholder="Your Company"
                bind:value={formData.company}
                required
              />
            </div>

            <div class="form-group">
              <label for="message">Message</label>
              <textarea
                id="message"
                placeholder="Tell us about your project and challenges..."
                rows="6"
                bind:value={formData.message}
                required
              ></textarea>
            </div>

            <button
              type="submit"
              class="btn btn-cta"
              disabled={isSubmitting}
              style="width: 100%;"
            >
              {isSubmitting ? 'Sending...' : 'Send Message'}
            </button>
          </form>
        {/if}
      </div>

      <div class="contact-info-section fade-in" use:fadeIn>
        <h2>Contact Information</h2>

        <div class="contact-info-item">
          <div class="contact-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 1118 0z"></path>
              <circle cx="12" cy="10" r="3"></circle>
            </svg>
          </div>
          <div>
            <h4>Location</h4>
            <p>Miami, Florida, USA</p>
          </div>
        </div>

        <div class="contact-info-item">
          <div class="contact-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.79 19.79 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"></path>
            </svg>
          </div>
          <div>
            <h4>Phone</h4>
            <p>(305) 555-0100</p>
          </div>
        </div>

        <div class="contact-info-item">
          <div class="contact-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="2" y="4" width="20" height="16" rx="2"></rect>
              <path d="M22 6l-10 8L2 6"></path>
            </svg>
          </div>
          <div>
            <h4>Email</h4>
            <p>hello@floridaai.com</p>
          </div>
        </div>

        <div class="contact-info-item">
          <div class="contact-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="1"></circle>
              <path d="M12 1v6m0 6v6M4.22 4.22l4.24 4.24m6.08 0l4.24-4.24M1 12h6m6 0h6M4.22 19.78l4.24-4.24m6.08 0l4.24 4.24"></path>
            </svg>
          </div>
          <div>
            <h4>Hours</h4>
            <p>Monday - Friday: 9am - 6pm EST</p>
          </div>
        </div>

        <div class="social-links">
          <a href="#" class="social-link" title="Twitter">f</a>
          <a href="#" class="social-link" title="LinkedIn">in</a>
          <a href="#" class="social-link" title="GitHub">gh</a>
        </div>
      </div>
    </div>
  </div>
</section>

<style>
  .contact-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-3xl);
    align-items: start;
  }

  .contact-form-section h1 {
    font-size: var(--font-size-4xl);
    margin-bottom: var(--spacing-lg);
    background: linear-gradient(135deg, var(--accent) 0%, var(--cta) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .contact-form {
    margin-top: var(--spacing-2xl);
  }

  .form-group {
    margin-bottom: var(--spacing-lg);
    display: flex;
    flex-direction: column;
  }

  .form-group label {
    font-weight: 600;
    margin-bottom: var(--spacing-sm);
    color: var(--neutral-700);
  }

  .form-group input,
  .form-group textarea {
    padding: var(--spacing-md);
    border: 1px solid var(--neutral-300);
    border-radius: var(--radius-lg);
    font-size: var(--font-size-base);
    font-family: var(--font-family-base);
    transition: all var(--transition-base);
  }

  .form-group input:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1);
  }

  .form-group textarea {
    resize: none;
  }

  .success-message {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
    border: 2px solid var(--success);
    border-radius: var(--radius-xl);
    padding: var(--spacing-2xl);
    text-align: center;
    margin-top: var(--spacing-2xl);
  }

  .success-icon {
    width: 64px;
    height: 64px;
    background: var(--success);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: var(--font-size-3xl);
    font-weight: 700;
    margin: 0 auto var(--spacing-lg);
  }

  .success-message h3 {
    color: var(--success);
    margin-bottom: var(--spacing-md);
  }

  .success-message p {
    color: var(--neutral-600);
    margin: 0;
  }

  .contact-info-section h2 {
    margin-bottom: var(--spacing-2xl);
  }

  .contact-info-item {
    display: flex;
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-2xl);
  }

  .contact-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--cta) 100%);
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    flex-shrink: 0;
  }

  .contact-icon svg {
    width: 24px;
    height: 24px;
  }

  .contact-info-item h4 {
    margin-bottom: var(--spacing-sm);
  }

  .contact-info-item p {
    color: var(--neutral-600);
    margin: 0;
  }

  .social-links {
    display: flex;
    gap: var(--spacing-md);
    margin-top: var(--spacing-2xl);
  }

  .social-link {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, var(--accent) 0%, var(--cta) 100%);
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 700;
    transition: all var(--transition-base);
  }

  .social-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
  }

  @media (max-width: 768px) {
    .contact-grid {
      grid-template-columns: 1fr;
    }

    .contact-form-section h1 {
      font-size: var(--font-size-3xl);
    }
  }
</style>
