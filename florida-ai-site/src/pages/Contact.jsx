import { useState } from 'react'

export default function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    business: '',
    message: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)

    setTimeout(() => {
      setIsSubmitting(false)
      setShowSuccess(true)
      setFormData({
        name: '',
        email: '',
        phone: '',
        business: '',
        message: ''
      })

      setTimeout(() => {
        setShowSuccess(false)
      }, 5000)
    }, 1000)
  }

  return (
    <div>
      <section className='contact-hero'>
        <h1>Let's talk</h1>
        <p style={{ fontSize: '1.125rem' }}>
          No pressure, no jargon — just a friendly conversation about what AI could do for your business.
        </p>
      </section>

      <section className='contact-container'>
        <div className={showSuccess ? 'success-message show' : 'success-message'}>
          <strong>Thank you!</strong> We have received your message and will be in touch within 24 hours.
        </div>

        <div className='contact-content'>
          <form className='contact-form' onSubmit={handleSubmit}>
            <div className='form-group'>
              <input
                type='text'
                name='name'
                className='form-input'
                placeholder=' '
                value={formData.name}
                onChange={handleChange}
                required
              />
              <label className='form-label'>Your Name</label>
            </div>

            <div className='form-group'>
              <input
                type='email'
                name='email'
                className='form-input'
                placeholder=' '
                value={formData.email}
                onChange={handleChange}
                required
              />
              <label className='form-label'>Email Address</label>
            </div>

            <div className='form-group'>
              <input
                type='tel'
                name='phone'
                className='form-input'
                placeholder=' '
                value={formData.phone}
                onChange={handleChange}
                required
              />
              <label className='form-label'>Phone Number</label>
            </div>

            <div className='form-group'>
              <input
                type='text'
                name='business'
                className='form-input'
                placeholder=' '
                value={formData.business}
                onChange={handleChange}
                required
              />
              <label className='form-label'>Business Name</label>
            </div>

            <div className='form-group'>
              <textarea
                name='message'
                className='form-textarea'
                placeholder=' '
                value={formData.message}
                onChange={handleChange}
                required
              ></textarea>
              <label className='form-label'>What's on your mind? Tell us a bit about your business and what you're hoping AI might help with.</label>
            </div>

            <button
              type='submit'
              className={isSubmitting ? 'form-submit loading' : 'form-submit'}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Sending...' : 'Start the conversation →'}
            </button>
          </form>

          <div className='contact-info'>
            <div className='info-card'>
              <div className='info-icon'>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="32" height="32">
                  <rect width="20" height="16" x="2" y="4" rx="2"/>
                  <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
                </svg>
              </div>
              <h3>Email</h3>
              <p>hello@floridaai.com</p>
            </div>

            <div className='info-card'>
              <div className='info-icon'>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="32" height="32">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 13.5a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.6 2.69h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.91 10a16 16 0 0 0 6 6l.92-.92a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 21.5 17z"/>
                </svg>
              </div>
              <h3>Phone</h3>
              <p>(305) 555-0123</p>
            </div>

            <div className='info-card'>
              <div className='info-icon'>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="32" height="32">
                  <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
                  <circle cx="12" cy="10" r="3"/>
                </svg>
              </div>
              <h3>Location</h3>
              <p>Serving all of Florida</p>
            </div>

            <div className='info-card'>
              <div className='info-icon'>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="32" height="32">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
              <h3>Response Time</h3>
              <p>24 hours or less</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
