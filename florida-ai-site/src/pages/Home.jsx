import { useState } from 'react'
import { Link } from 'react-router-dom'
import FadeIn from '../components/FadeIn'

const painPoints = [
  {
    icon: '💻',
    title: 'Tried ChatGPT but don\'t know how to use it',
    summary: 'You\'ve heard about AI but have no idea how to apply it to your business workflow.',
    story: 'ChatGPT gets all the headlines, but it\'s just one tool in a crowded landscape. There\'s Claude for deep analysis and writing, Midjourney for visual content, Copilot for Office automation, Jasper for marketing copy, and dozens more — each designed for different tasks. The problem isn\'t that you tried AI and it didn\'t work. The problem is you tried one tool and expected it to do everything. Our consultants assess your actual workflow, identify where AI fits naturally, and match you with the right tools for each job. Most clients are surprised to find that the best solution isn\'t the one they\'ve heard of.'
  },
  {
    icon: '🔒',
    title: 'Worried about sending confidential data',
    summary: 'Concerned about data security and where your sensitive information ends up when using AI tools.',
    story: 'Your instinct is right — many free AI tools use your data to train their models, and anything you type could resurface elsewhere. But that doesn\'t mean AI is off-limits for your business. Enterprise-grade tools offer strict data privacy agreements where nothing you share is stored or used for training. For highly sensitive work, there are models that run entirely on your own hardware, never touching the internet. And for everything in between, there are simple policies your team can follow to get the benefits of AI without the risk. We help you draw those lines clearly and set up the right tools for your comfort level.'
  },
  {
    icon: '⏰',
    title: 'Staff spend hours on emails and repetitive tasks',
    summary: 'Your team is drowning in routine work that could be automated, leaving no time for what matters.',
    story: 'That two-hour daily email grind, the weekly reports nobody reads but everyone has to write, the copy-paste data entry between systems — it all adds up. AI can draft email responses in your team\'s voice, sort and prioritize inboxes automatically, generate reports from raw data in seconds, and handle routine customer queries around the clock. We don\'t just install tools and walk away. We sit with your team, identify the three or four biggest time sinks, and automate them one by one. Most businesses get 2+ hours back per person per day within the first month.'
  },
  {
    icon: '💰',
    title: 'Can\'t afford a tech team but falling behind',
    summary: 'You need technical expertise but don\'t have the budget for a full IT department.',
    story: 'Here\'s the truth: you don\'t need a $200,000 developer or a dedicated IT department to use AI effectively. Most of the wins for small businesses come from tools that cost $20–50 per month, configured properly and integrated into your existing workflow. The gap isn\'t money — it\'s knowing which tools to use and how to set them up. That\'s exactly what we do. We bring enterprise-level AI capability to small businesses at a fraction of the cost, train your existing team to use it confidently, and stay on call when questions come up. Big-company results, small-business budget.'
  },
  {
    icon: '🏃',
    title: 'My competitors are already using AI',
    summary: 'You can see other businesses pulling ahead with automation and smarter workflows, and you\'re not sure how to catch up.',
    story: 'They might be using AI, but most of them are doing it badly — paying for tools they barely use, feeding it poor prompts, or applying it to the wrong problems. The businesses actually winning with AI aren\'t the ones who adopted first. They\'re the ones who adopted strategically. A well-implemented AI workflow in the right part of your business will outperform a competitor who slapped a chatbot on their website and called it innovation. We help you skip the trial-and-error phase entirely and go straight to the implementations that deliver measurable ROI.'
  },
  {
    icon: '🔧',
    title: 'Too many AI tools, no idea which ones to pick',
    summary: 'Every week there\'s a new app or platform promising to transform your business. You just want someone to tell you what actually works.',
    story: 'There are over 10,000 AI tools on the market right now, and a new one launches practically every day. Most are hype. Some are genuinely useful but only for specific tasks. A handful are transformative for small businesses — but finding them on your own means weeks of research, free trials, and frustration. We\'ve tested hundreds of tools across dozens of industries and know which ones actually deliver. Instead of wading through the noise, you get a curated shortlist of 3–5 tools tailored to your business, set up and ready to use. No more analysis paralysis.'
  }
]

function PainCard({ point, delay }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <FadeIn delay={delay} className={`pain-card ${expanded ? 'expanded' : ''}`}>
      <div className="pain-card-header" onClick={() => setExpanded(!expanded)}>
        <div className="pain-icon">{point.icon}</div>
        <h3>{point.title}</h3>
        <p>{point.summary}</p>
        <div className="pain-card-toggle">{expanded ? 'Read less ↑' : 'Learn more ↓'}</div>
      </div>
      {expanded && (
        <div className="pain-card-story">
          <p>{point.story}</p>
          <Link to="/contact" className="pain-card-cta">Let's talk about this →</Link>
        </div>
      )}
    </FadeIn>
  )
}

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
            {painPoints.map((point, i) => (
              <PainCard key={i} point={point} delay={i * 100} />
            ))}
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
              <div className="pricing-price">$750 <span>one-time</span></div>
              <div className="pricing-description">
                Complete setup of AI tools, implementation, and 30 days of training and support.
              </div>
              <button className="btn btn-primary">Get Started</button>
            </FadeIn>

            <FadeIn delay={200} className="pricing-card">
              <h3 className="pricing-title">AI Powerhouse</h3>
              <div className="pricing-price">$2,200 <span>one-time</span></div>
              <div className="pricing-description">
                Full custom AI implementation with advanced automation and comprehensive training.
              </div>
              <button className="btn btn-secondary">Schedule Call</button>
            </FadeIn>
          </div>
          <div className="pricing-note">
            All packages include ongoing support at $200/month (optional)
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
