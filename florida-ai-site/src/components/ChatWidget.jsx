import { useState, useRef, useEffect, useMemo } from 'react'

const INITIAL_MESSAGE = {
  role: 'assistant',
  content: "Hi! I'm here to help you figure out if AI could make a real difference for your business. What kind of work do you do?"
}

function generateSessionId() {
  return crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2) + Date.now().toString(36)
}

export default function ChatWidget() {
  const sessionId = useMemo(() => generateSessionId(), [])
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([INITIAL_MESSAGE])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    if (open) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
      inputRef.current?.focus()
    }
  }, [open, messages])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || loading) return

    const userMsg = { role: 'user', content: text }
    const updated = [...messages, userMsg]
    setMessages(updated)
    setInput('')
    setLoading(true)
    setError(null)

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: updated, sessionId })
      })
      const data = await res.json()
      if (data.error) throw new Error(data.error)
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try the contact form.')
    } finally {
      setLoading(false)
    }
  }

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <>
      {/* Floating button */}
      <button
        className="chat-widget-toggle"
        onClick={() => setOpen(o => !o)}
        aria-label={open ? 'Close chat' : 'Chat with us'}
      >
        {open ? (
          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
        )}
        {!open && <span className="chat-widget-label">Ask us anything</span>}
      </button>

      {/* Chat window */}
      {open && (
        <div className="chat-widget-window">
          <div className="chat-widget-header">
            <div className="chat-widget-avatar">AI</div>
            <div>
              <div className="chat-widget-name">Florida AI Assistant</div>
              <div className="chat-widget-status">
                <span className="chat-widget-dot" />
                Online now
              </div>
            </div>
          </div>

          <div className="chat-widget-messages">
            {messages.map((m, i) => (
              <div key={i} className={`chat-bubble ${m.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-assistant'}`}>
                {m.content}
              </div>
            ))}
            {loading && (
              <div className="chat-bubble chat-bubble-assistant chat-bubble-typing">
                <span /><span /><span />
              </div>
            )}
            {error && (
              <div className="chat-bubble chat-bubble-assistant chat-bubble-error">{error}</div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="chat-widget-input-row">
            <textarea
              ref={inputRef}
              className="chat-widget-input"
              placeholder="Type a message..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              rows={1}
              disabled={loading}
            />
            <button
              className="chat-widget-send"
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              aria-label="Send"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </div>
        </div>
      )}
    </>
  )
}
