import express from 'express'
import cors from 'cors'
import rateLimit from 'express-rate-limit'
import Anthropic from '@anthropic-ai/sdk'
import Database from 'better-sqlite3'
import { randomUUID } from 'crypto'
import { mkdirSync } from 'fs'

const app = express()
const PORT = 3001
const MAX_TURNS = 10
const DB_PATH = process.env.DB_PATH || '/var/lib/florida-ai-chat/conversations.db'
const ADMIN_USER = process.env.ADMIN_USER || 'george'
const ADMIN_PASS = process.env.ADMIN_PASS || ''

// --- Database setup ---
mkdirSync('/var/lib/florida-ai-chat', { recursive: true })
const db = new Database(DB_PATH)
db.exec(`
  CREATE TABLE IF NOT EXISTS sessions (
    session_id  TEXT PRIMARY KEY,
    started_at  TEXT DEFAULT (datetime('now')),
    last_active TEXT DEFAULT (datetime('now')),
    visitor_ip  TEXT,
    turn_count  INTEGER DEFAULT 0
  );
  CREATE TABLE IF NOT EXISTS messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      TEXT NOT NULL,
    turn_number     INTEGER,
    user_message    TEXT,
    assistant_reply TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
  );
`)

const upsertSession = db.prepare(`
  INSERT INTO sessions (session_id, visitor_ip)
  VALUES (@session_id, @visitor_ip)
  ON CONFLICT(session_id) DO UPDATE SET
    last_active = datetime('now'),
    turn_count  = turn_count + 1
`)

const insertMessage = db.prepare(`
  INSERT INTO messages (session_id, turn_number, user_message, assistant_reply)
  VALUES (@session_id, @turn_number, @user_message, @assistant_reply)
`)

// --- Anthropic ---
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

// --- Middleware ---
app.use(cors({ origin: '*' }))
app.use(express.json({ limit: '16kb' }))

const limiter = rateLimit({
  windowMs: 60 * 60 * 1000,
  max: 30,
  message: { error: 'Too many messages — please try again in an hour.' },
  standardHeaders: true,
  legacyHeaders: false
})

// --- Simple basic auth middleware for admin ---
function requireAuth(req, res, next) {
  if (!ADMIN_PASS) return res.status(503).send('Admin not configured.')
  const auth = req.headers.authorization || ''
  const [scheme, encoded] = auth.split(' ')
  if (scheme !== 'Basic' || !encoded) return challenge(res)
  const [user, pass] = Buffer.from(encoded, 'base64').toString().split(':')
  if (user === ADMIN_USER && pass === ADMIN_PASS) return next()
  return challenge(res)
}
function challenge(res) {
  res.set('WWW-Authenticate', 'Basic realm="Florida AI Admin"')
  res.status(401).send('Unauthorised')
}

// --- Chat endpoint ---
app.post('/api/chat', limiter, async (req, res) => {
  try {
    const { messages, sessionId } = req.body
    const session_id = (typeof sessionId === 'string' && sessionId.length < 64)
      ? sessionId
      : randomUUID()
    const visitor_ip = req.headers['x-forwarded-for']?.split(',')[0].trim() || req.ip

    if (!Array.isArray(messages) || messages.length === 0) {
      return res.status(400).json({ error: 'Invalid messages format.' })
    }

    if (messages.length > MAX_TURNS * 2) {
      return res.status(200).json({
        reply: "We've covered a lot of ground! The best next step is to fill in the contact form below — we'll be in touch within 24 hours to continue the conversation properly."
      })
    }

    const sanitised = messages
      .filter(m => ['user', 'assistant'].includes(m.role) && typeof m.content === 'string')
      .map(m => ({ role: m.role, content: m.content.slice(0, 1000) }))
      .slice(-20)

    const response = await client.messages.create({
      model: 'claude-haiku-4-5',
      max_tokens: 300,
      system: SYSTEM_PROMPT,
      messages: sanitised
    })

    const reply = response.content[0]?.text ?? "Sorry, I didn't catch that — could you rephrase?"

    // Log to SQLite
    const userMessages = sanitised.filter(m => m.role === 'user')
    const turn_number = userMessages.length
    const user_message = userMessages.at(-1)?.content ?? ''

    upsertSession.run({ session_id, visitor_ip })
    insertMessage.run({ session_id, turn_number, user_message, assistant_reply: reply })

    res.json({ reply })

  } catch (err) {
    console.error('Chat error:', err.message)
    res.status(500).json({ error: 'Something went wrong. Please try the contact form instead.' })
  }
})

// --- Admin viewer ---
app.get('/admin', requireAuth, (_req, res) => {
  const sessions = db.prepare(`
    SELECT s.session_id, s.started_at, s.last_active, s.visitor_ip, s.turn_count,
           substr(m.user_message, 1, 80) AS first_message
    FROM sessions s
    LEFT JOIN messages m ON m.session_id = s.session_id AND m.turn_number = 1
    ORDER BY s.started_at DESC
    LIMIT 200
  `).all()

  const rows = sessions.map(s => `
    <tr onclick="location.href='/admin/session/${s.session_id}'" style="cursor:pointer">
      <td>${s.started_at}</td>
      <td>${s.visitor_ip || '—'}</td>
      <td>${s.turn_count}</td>
      <td>${escHtml(s.first_message || '—')}</td>
    </tr>`).join('')

  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Florida AI — Chat Transcripts</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 1000px; margin: 2rem auto; padding: 0 1rem; color: #1e293b; }
    h1 { font-size: 1.5rem; margin-bottom: 1.5rem; }
    table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
    th { text-align: left; padding: 0.6rem 0.75rem; background: #f1f5f9; border-bottom: 2px solid #e2e8f0; }
    td { padding: 0.6rem 0.75rem; border-bottom: 1px solid #e2e8f0; }
    tr:hover td { background: #f8fafc; }
  </style>
</head>
<body>
  <h1>Chat Transcripts (${sessions.length})</h1>
  <table>
    <thead><tr><th>Started</th><th>IP</th><th>Turns</th><th>First message</th></tr></thead>
    <tbody>${rows || '<tr><td colspan="4">No conversations yet.</td></tr>'}</tbody>
  </table>
</body>
</html>`)
})

app.get('/admin/session/:id', requireAuth, (req, res) => {
  const session = db.prepare('SELECT * FROM sessions WHERE session_id = ?').get(req.params.id)
  if (!session) return res.status(404).send('Session not found.')

  const msgs = db.prepare('SELECT * FROM messages WHERE session_id = ? ORDER BY turn_number').all(req.params.id)

  const bubbles = msgs.map(m => `
    <div class="turn">
      <div class="bubble user">${escHtml(m.user_message)}</div>
      <div class="bubble bot">${escHtml(m.assistant_reply)}</div>
      <div class="ts">${m.created_at}</div>
    </div>`).join('')

  res.send(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Transcript — ${session.session_id.slice(0,8)}</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 700px; margin: 2rem auto; padding: 0 1rem; color: #1e293b; }
    a { color: #0284c7; text-decoration: none; font-size: 0.85rem; }
    h1 { font-size: 1.3rem; margin: 1rem 0; }
    .meta { font-size: 0.8rem; color: #64748b; margin-bottom: 1.5rem; }
    .turn { margin-bottom: 1.25rem; }
    .bubble { padding: 0.65rem 0.9rem; border-radius: 12px; margin-bottom: 0.35rem; font-size: 0.9rem; line-height: 1.5; max-width: 85%; white-space: pre-wrap; }
    .user { background: #0ea5e9; color: white; border-bottom-right-radius: 4px; margin-left: auto; }
    .bot  { background: #f1f5f9; color: #1e293b; border-bottom-left-radius: 4px; }
    .ts   { font-size: 0.72rem; color: #94a3b8; text-align: right; }
  </style>
</head>
<body>
  <a href="/admin">← All conversations</a>
  <h1>Transcript</h1>
  <div class="meta">
    Session: ${session.session_id}<br>
    Started: ${session.started_at} &nbsp;|&nbsp; Last active: ${session.last_active}<br>
    IP: ${session.visitor_ip || '—'} &nbsp;|&nbsp; Turns: ${session.turn_count}
  </div>
  ${bubbles || '<p>No messages.</p>'}
</body>
</html>`)
})

function escHtml(str) {
  return String(str ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')
}

// --- Health ---
app.get('/api/health', (_req, res) => res.json({ ok: true }))

app.listen(PORT, '127.0.0.1', () => {
  console.log(`Florida AI chat API listening on 127.0.0.1:${PORT}`)
})
