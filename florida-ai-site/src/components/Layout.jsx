import { useState, useEffect } from "react"
import { Link, useLocation } from "react-router-dom"

export default function Layout({ children }) {
  const [isScrolled, setIsScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10)
    }

    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  useEffect(() => {
    setMobileMenuOpen(false)
  }, [location])

  return (
    <div className="layout">
      <nav className={isScrolled ? "navbar scrolled" : "navbar"}>
        <div className="nav-container">
          <Link to="/" className="logo">
            <div className="logo-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="url(#logoGrad)" strokeWidth="2"/>
                <path d="M8 12h8M12 8v8" stroke="url(#logoGrad)" strokeWidth="2" strokeLinecap="round"/>
                <defs>
                  <linearGradient id="logoGrad" x1="0" y1="0" x2="24" y2="24">
                    <stop offset="0%" stopColor="#06b6d4"/>
                    <stop offset="100%" stopColor="#f97316"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <span className="logo-text">Florida AI</span>
          </Link>

          <button 
            className="hamburger"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            <span></span>
            <span></span>
            <span></span>
          </button>

          <ul className={mobileMenuOpen ? "nav-links active" : "nav-links"}>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/about">About</Link></li>
            <li><Link to="/services">Services</Link></li>
            <li className="nav-cta">
              <Link to="/contact">Contact</Link>
            </li>
          </ul>
        </div>
      </nav>

      <main className="main-content">
        {children}
      </main>

      <footer className="footer">
        <div className="footer-content">
          <div className="footer-column">
            <h4>Florida AI</h4>
            <p>Practical AI solutions for small businesses in Florida.</p>
          </div>
          <div className="footer-column">
            <h4>Quick Links</h4>
            <ul>
              <li><Link to="/">Home</Link></li>
              <li><Link to="/about">About</Link></li>
              <li><Link to="/services">Services</Link></li>
            </ul>
          </div>
          <div className="footer-column">
            <h4>Get Started</h4>
            <ul>
              <li><Link to="/contact">Book Free Audit</Link></li>
              <li><Link to="/contact">Schedule a Call</Link></li>
              <li><Link to="/services">View Services</Link></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2026 Florida AI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
