import { useState } from 'react'
import FadeIn from '../components/FadeIn'

export default function Services() {
  const [expandedService, setExpandedService] = useState(null)

  const services = [
    {
      id: 'audit',
      title: 'AI Strategy Audit',
      icon: '🔍',
      description: 'We analyze your business processes and identify where AI can save you time and money.',
      details: 'Includes a 45-minute consultation, process analysis, and a custom report with specific recommendations.'
    },
    {
      id: 'setup',
      title: 'Custom AI Setup',
      icon: '⚙️',
      description: 'We implement and configure AI tools tailored to your specific business needs.',
      details: 'Integration with your existing systems, data security setup, and initial testing to ensure everything works perfectly.'
    },
    {
      id: 'training',
      title: 'Team Training',
      icon: '👥',
      description: 'Your team learns how to use AI tools effectively and confidently in their daily work.',
      details: 'Hands-on training sessions, documentation, and ongoing support to ensure adoption.'
    },
    {
      id: 'automation',
      title: 'Document Automation',
      icon: '📄',
      description: 'Automate repetitive document tasks like emails, reports, and customer communications.',
      details: 'Custom workflows that save hours per week and reduce errors.'
    },
    {
      id: 'customer',
      title: 'Customer Service AI',
      icon: '💬',
      description: 'Deploy AI chatbots and support systems to handle customer inquiries 24/7.',
      details: 'Improves response times, increases customer satisfaction, and frees up your team.'
    },
    {
      id: 'support',
      title: 'Ongoing Support',
      icon: '🛠️',
      description: 'Monthly check-ins and optimization to keep your AI systems running smoothly.',
      details: '00/month includes updates, troubleshooting, and recommendations for improvements.'
    }
  ]

  const toggleService = (id) => {
    setExpandedService(expandedService === id ? null : id)
  }

  return (
    <div>
      <section className="services-hero">
        <h1>Our Services</h1>
        <p style={{ fontSize: '1.125rem', maxWidth: '500px' }}>
          Complete AI solutions designed for small businesses
        </p>
      </section>

      <section className="services-grid">
        <div className="section-inner">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem' }}>
            {services.map((service, index) => (
              <FadeIn key={service.id} delay={index * 100}>
                <div 
                  className={expandedService === service.id ? 'service-card expanded' : 'service-card'}
                  onClick={() => toggleService(service.id)}
                >
                  <div className="service-icon">{service.icon}</div>
                  <h3>{service.title}</h3>
                  <p className="service-description">{service.description}</p>
                  <div className="service-details">{service.details}</div>
                </div>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
