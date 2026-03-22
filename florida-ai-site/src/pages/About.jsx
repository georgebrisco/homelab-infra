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


    </div>
  )
}
