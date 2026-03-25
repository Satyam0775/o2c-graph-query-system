import { useState, useRef, useEffect } from 'react'
import { runQuery } from '../services/api'

const SUGGESTED_QUERIES = [
  'Which customers have the most sales orders?',
  'Show billing documents that are cancelled',
  'Find sales orders with delivery block',
  'Which products appear in the most orders?',
  'Show recent payments and their amounts',
  'List journal entries linked to billing document 90504274',
  'What is the total revenue by customer?',
  'Find incomplete sales orders',
]

function TypingDots() {
  return (
    <span style={{ display: 'inline-flex', gap: 3 }}>
      {[0, 1, 2].map(i => (
        <span key={i} style={{
          width: 6,
          height: 6,
          borderRadius: '50%',
          background: '#94A3B8',
          animation: 'bounce 1.2s infinite',
          animationDelay: `${i * 0.2}s`,
        }} />
      ))}
    </span>
  )
}

export default function ChatPanel({ onQueryResult }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      text: 'Hi! I can help you analyze the Order to Cash process.',
    }
  ])

  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (question) => {
    if (!question.trim() || loading) return

    const q = question.trim()
    setInput('')
    setLoading(true)

    const userMsg = {
      id: Date.now(),
      role: 'user',
      text: q,
    }

    const loadingId = Date.now() + 1

    setMessages(prev => [
      ...prev,
      userMsg,
      { id: loadingId, role: 'assistant', loading: true }
    ])

    try {
      // 🔥 FINAL FIX
      const data = await runQuery(q)

      setMessages(prev =>
        prev.map(m =>
          m.id === loadingId
            ? {
                id: loadingId,
                role: 'assistant',
                text: data.answer,
                sql: data.sql,
                results: data.results,
                rowCount: data.row_count,
              }
            : m
        )
      )

      if (onQueryResult) onQueryResult(data)

    } catch (err) {
      const errMsg =
        err.response?.data?.detail ||
        err.message ||
        'Request failed'

      setMessages(prev =>
        prev.map(m =>
          m.id === loadingId
            ? {
                id: loadingId,
                role: 'assistant',
                text: `Error: ${errMsg}`,
                isError: true,
              }
            : m
        )
      )
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      sendMessage(input)
    }
  }

  return (
    <div style={{
      width: '100%',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      background: '#fff'
    }}>

      {/* Messages */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: 12
      }}>
        {messages.map(msg => (
          <div key={msg.id} style={{
            textAlign: msg.role === 'user' ? 'right' : 'left',
            marginBottom: 10
          }}>
            <div style={{
              display: 'inline-block',
              padding: '8px 12px',
              borderRadius: 10,
              background: msg.role === 'user' ? '#0F172A' : '#F1F5F9',
              color: msg.role === 'user' ? '#fff' : '#000'
            }}>
              {msg.loading ? <TypingDots /> : msg.text}
            </div>

            {/* SQL */}
            {msg.sql && (
              <pre style={{
                marginTop: 6,
                fontSize: 10,
                background: '#000',
                color: '#0f0',
                padding: 6,
                borderRadius: 6
              }}>
                {msg.sql}
              </pre>
            )}

            {/* Results */}
            {msg.results?.length > 0 && (
              <pre style={{
                marginTop: 6,
                fontSize: 10,
                background: '#f9fafb',
                padding: 6,
                borderRadius: 6
              }}>
                {JSON.stringify(msg.results.slice(0, 5), null, 2)}
              </pre>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {!loading && messages.length === 1 && (
        <div style={{ padding: 10 }}>
          {SUGGESTED_QUERIES.map((q, i) => (
            <button key={i}
              style={{
                margin: 4,
                padding: '6px 10px',
                fontSize: 12,
                borderRadius: 20,
                border: '1px solid #ccc',
                cursor: 'pointer'
              }}
              onClick={() => sendMessage(q)}
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div style={{
        padding: 10,
        borderTop: '1px solid #eee',
        display: 'flex',
        gap: 8
      }}>
        <input
          ref={inputRef}
          style={{
            flex: 1,
            padding: 8,
            borderRadius: 6,
            border: '1px solid #ccc'
          }}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask something..."
          disabled={loading}
        />

        <button
          onClick={() => sendMessage(input)}
          disabled={!input.trim() || loading}
          style={{
            padding: '8px 12px',
            background: '#0F172A',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            cursor: 'pointer'
          }}
        >
          {loading ? '...' : 'Send'}
        </button>
      </div>

    </div>
  )
}