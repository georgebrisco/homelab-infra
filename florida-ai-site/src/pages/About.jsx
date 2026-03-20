import FadeIn from '../components/FadeIn'

export default function About() {
  return (
    <div>
      <section className="about-hero">
        <h1>About Florida AI</h1>
        <p style={{ fontSize: '1.25rem', maxWidth: '600px' }}>
          We make AI simple and practical for small businesses
        </p>
      </section>

      <section className="mission">
        <div className="section-inner">
          <div className="mission-content">
            <h2 className="section-title">Our Mission</h2>
            <p>
              We believe every small business in Florida deserves access to AI tools and expertise, regardless of budget or technical background. We're on a mission to cut through the hype, demystify AI, and help you implement real solutions that drive results. No jargon. No overselling. Just practical advice and solid implementation.
            </p>
          </div>
        </div>
      </section>

      <section className="values">
        <div className="section-inner">
          <h2 className="section-title">Our Values</h2>
          <div className="values-grid">
            <FadeIn delay={0} className="value-card">
              <div className="value-icon">✓</div>
              <h3>Practical Results</h3>
              <p>
                We focus on real business outcomes. If it doesn't save you time or money, we don't recommend it.
              </p>
            </FadeIn>

            <FadeIn delay={100} className="value-card">
              <div className="value-icon">💬</div>
              <h3>Plain English</h3>
              <p>
                No tech jargon. We explain everything in simple terms so you understand exactly what you're getting.
              </p>
            </FadeIn>

            <FadeIn delay={200} className="value-card">
              <div className="value-icon">🤝</div>
              <h3>Long-term Partnership</h3>
              <p>
                We stick around. Ongoing support means you're never left alone figuring things out.
              </p>
            </FadeIn>
          </div>
        </div>
      </section>

      <section className="timeline">
        <h2 className="section-title" style={{ textAlign: 'left', marginBottom: '3rem' }}>
          Our Journey
        </h2>
        
        <div className="timeline-item">
          <div className="timeline-content">
            <h3>2024 - The Beginning</h3>
            <p>
              Founded Florida AI with a vision to make artificial intelligence accessible to small businesses across Florida.
            </p>
          </div>
        </div>

        <div className="timeline-item">
          <div className="timeline-content">
            <h3>Early 2025 - First Clients</h3>
            <p>
              Launched our AI Audit service and helped our first customers save time and boost productivity with tailored AI solutions.
            </p>
          </div>
        </div>

        <div className="timeline-item">
          <div className="timeline-content">
            <h3>Spring 2026 - Growing Strong</h3>
            <p>
              Expanded our team and services. Now helping dozens of small businesses across Florida harness the power of AI.
            </p>
          </div>
        </div>

        <div className="timeline-item">
          <div className="timeline-content">
            <h3>Future - Scaling Up</h3>
            <p>
              Building partnerships with other Florida businesses to make AI implementation even more accessible.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
