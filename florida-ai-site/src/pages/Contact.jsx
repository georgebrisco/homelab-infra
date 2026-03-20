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
        <h1>Let us Talk</h1>
        <p style={{ fontSize: '1.125rem' }}>
          Ready to explore AI for your business? We would love to help.
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
              />
              <label className='form-label'>Phone (optional)</label>
            </div>

            <div className='form-group'>
              <input
                type='text'
                name='business'
                className='form-input'
                placeholder=' '
                value={formData.business}
                onChange={handleChange}
              />
              <label className='form-label'>Business Name (optional)</label>
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
              <label className='form-label'>Tell us about your needs</label>
            </div>

            <button 
              type='submit' 
              className={isSubmitting ? 'form-submit loading' : 'form-submit'}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Sending...' : 'Send Message'}
            </button>
          </form>

          <div className='contact-info'>
            <div className='info-card'>
              <div className='info-icon'>Email Icon</div>
              <h3>Email</h3>
              <p>hello@floridaai.com</p>
            </div>

            <div className='info-card'>
              <div className='info-icon'>Phone Icon</div>
              <h3>Phone</h3>
              <p>(305) 555-0123</p>
            </div>

            <div className='info-card'>
              <div className='info-icon'>Location Icon</div>
              <h3>Location</h3>
              <p>Serving all of Florida</p>
            </div>

            <div className='info-card'>
              <div className='info-icon'>Time Icon</div>
              <h3>Response Time</h3>
              <p>24 hours or less</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
