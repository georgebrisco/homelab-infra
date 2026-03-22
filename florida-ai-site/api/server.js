import express from 'express'
import cors from 'cors'
import rateLimit from 'express-rate-limit'
import Anthropic from '@anthropic-ai/sdk'

const app = express()
const PORT = 3001
const MAX_TURNS = 10

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY })

const SYSTEM_PROMPT = `You are a friendly, helpful assistant for Florida AI — a consultancy that helps small businesses in Florida get practical value from AI tools. You're warm, conversational, and avoid jargon.

Our services:
- AI Strategy Audit: A 1-hour consultation plus a custom written report identifying where AI can save the business time and money. This is most people's starting point.
- Custom AI Setup: We implement and configure AI tools tailored to the business — integrated with existing systems.
- Team Training: Hands-on sessions so staff actually use the tools confidently day-to-day.
- Document Automation: Automating repetitive tasks like emails, reports, and client communications.
- Customer Service AI: AI chatbots and support systems handling customer queries 24/7.
- Ongoing Support: Monthly check-ins and optimisation to keep everything running smoothly.

Your job is to:
1. Help visitors understand which service might fit their situation by asking friendly questions about their business.
2. Answer questions about our services honestly.
3. When someone is ready or curious, encourage them to fill in the contact form on this page — we respond within 24 hours.

Keep responses concise — 2-4 sentences. Don't pretend to know specific pricing (tell them to get in touch for a quote). Don't go off-topic into general AI advice. If someone asks something outside Florida AI's services, gently steer back.

At turn 8 or beyond, naturally suggest they drop their details in the contact form so we can have a proper conversation.`

app.use(cors({ origin: '*' }))
app.use(express.json({ limit: '16kb' }))

// Rate limit: 30 requests per IP per hour
const limiter = rateLimit({
  windowMs: 60 * 60 * 1000,
  max: 30,
  message: { error: 'Too many messages — please try again in an hour.' },
  standardHeaders: true,
  legacyHeaders: false
})

app.post('/api/chat', limiter, async (req, res) => {
  try {
    const { messages } = req.body

    if (!Array.isArray(messages) || messages.length === 0) {
      return res.status(400).json({ error: 'Invalid messages format.' })
    }

    // Enforce max turns
    if (messages.length > MAX_TURNS * 2) {
      return res.status(200).json({
        reply: "We've covered a lot of ground! The best next step is to fill in the contact form below — we'll be in touch within 24 hours to continue the conversation properly."
      })
    }

    // Sanitise: only allow user/assistant roles, string content, reasonable length
    const sanitised = messages
      .filter(m => ['user', 'assistant'].includes(m.role) && typeof m.content === 'string')
      .map(m => ({ role: m.role, content: m.content.slice(0, 1000) }))
      .slice(-20) // keep last 20 messages max

    const response = await client.messages.create({
      model: 'claude-haiku-4-5',
      max_tokens: 300,
      system: SYSTEM_PROMPT,
      messages: sanitised
    })

    const reply = response.content[0]?.text ?? "Sorry, I didn't catch that — could you rephrase?"
    res.json({ reply })

  } catch (err) {
    console.error('Chat error:', err.message)
    res.status(500).json({ error: 'Something went wrong. Please try the contact form instead.' })
  }
})

app.get('/api/health', (_req, res) => res.json({ ok: true }))

app.listen(PORT, '127.0.0.1', () => {
  console.log(`Florida AI chat API listening on 127.0.0.1:${PORT}`)
})
