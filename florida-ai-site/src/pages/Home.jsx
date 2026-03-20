import { Link } from 'react-router-dom'
import FadeIn from '../components/FadeIn'

export default function Home() {
  return (
    <div>
      <section className="hero">
        <div className="hero-content">
          <h1>
            Stop worrying about AI. Start <span className="gradient-text">using</span> it.
          </h1>
          <p className="hero-subtitle">
            Cut through the noise and confusion. We help small businesses in Florida implement practical AI solutions that actually save time and money.
          </p>
          <div className="hero-cta">
            <button className="btn btn-primary">Book a Free AI Audit</button>
            <Link to="/services" className="btn btn-secondary">See Our Services</Link>
          </div>
        </div>
      </section>

      <section className="pain-points">
        <div className="section-inner">
          <h2 className="section-title">Sound familiar?</h2>
          <div className="pain-grid">
            <FadeIn delay={0} className="pain-card">
              <div className="pain-icon">💻</div>
              <h3>Tried ChatGPT but don't know how to use it</h3>
              <p>You've heard about AI but have no idea how to apply it to your business workflow.</p>
            </FadeIn>

            <FadeIn delay={100} className="pain-card">
              <div className="pain-icon">🔒</div>
              <h3>Worried about sending confidential data</h3>
              <p>Concerned about data security and where your sensitive information ends up when using AI tools.</p>
            </FadeIn>

            <FadeIn delay={200} className="pain-card">
              <div className="pain-icon">⏰</div>
              <h3>Staff spend hours on emails and repetitive tasks</h3>
              <p>Your team is drowning in routine work that could be automated, leaving no time for what matters.</p>
            </FadeIn>

            <FadeIn delay={300} className="pain-card">
              <div className="pain-icon">💰</div>
              <h3>Can't afford a tech team but falling behind</h3>
              <p>You need technical expertise but don't have the budget for a full IT department.</p>
            </FadeIn>
          </div>
        </div>
      </section>

      <section className="how-it-works">
        <div className="section-inner">
          <h2 className="section-title">How It Works</h2>
          <div className="steps-container">
            <FadeIn delay={0} className="step">
              <div className="step-number">1</div>
              <h3>Free AI Audit</h3>
              <p>We analyze your business and identify quick wins where AI can help you save time and money.</p>
            </FadeIn>

            <FadeIn delay={100} className="step">
              <div className="step-number">2</div>
              <h3>Setup & Training</h3>
              <p>We implement tailored AI solutions and train your team to use them confidently.</p>
            </FadeIn>

            <FadeIn delay={200} className="step">
              <div className="step-number">3</div>
              <h3>Ongoing Support</h3>
              <p>Monthly check-ins to ensure everything is working and optimize your AI usage.</p>
            </FadeIn>
          </div>
        </div>
      </section>

      <section className="pricing">
        <div className="section-inner">
          <h2 className="section-title">Simple, Transparent Pricing</h2>
          <div className="pricing-grid">
            <FadeIn delay={0} className="pricing-card">
              <h3 className="pricing-title">AI Kickstart</h3>
              <div className="pricing-price">Free</div>
              <div className="pricing-description">
                Free AI audit to identify opportunities in your business.
              </div>
              <button className="btn btn-secondary">Schedule Audit</button>
            </FadeIn>

            <FadeIn delay={100} className="pricing-card featured">
              <h3 className="pricing-title">AI Ready</h3>
              <div className="pricing-price">50 <span>one-time</span></div>
              <div className="pricing-description">
                Complete setup of AI tools, implementation, and 30 days of training and support.
              </div>
              <button className="btn btn-primary">Get Started</button>
            </FadeIn>

            <FadeIn delay={200} className="pricing-card">
              <h3 className="pricing-title">AI Powerhouse</h3>
              <div className="pricing-price">,200 <span>one-time</span></div>
              <div className="pricing-description">
                Full custom AI implementation with advanced automation and comprehensive training.
              </div>
              <button className="btn btn-secondary">Schedule Call</button>
            </FadeIn>
          </div>
          <div className="pricing-note">
            All packages include ongoing support at 00/month (optional)
          </div>
        </div>
      </section>

      <section className="stats">
        <div className="section-inner">
          <div className="stats-grid">
            <FadeIn delay={0} className="stat">
              <div className="stat-number">2hrs</div>
              <div className="stat-label">Saved per day on average</div>
            </FadeIn>

            <FadeIn delay={100} className="stat">
              <div className="stat-number">45min</div>
              <div className="stat-label">Duration of your free audit</div>
            </FadeIn>

            <FadeIn delay={200} className="stat">
              <div className="stat-number">100%</div>
              <div className="stat-label">Plain English, no jargon</div>
            </FadeIn>
          </div>
        </div>
      </section>

      <section className="cta-section">
        <div className="section-inner">
          <h2>Ready to see what AI can do for you?</h2>
          <button className="btn btn-primary">Book Your Free AI Audit Today</button>
        </div>
      </section>
    </div>
  )
}
