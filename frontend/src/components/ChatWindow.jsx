import { useState, useRef, useEffect } from 'react'
import { HiUserCircle, HiBuildingOffice2, HiArrowUp } from 'react-icons/hi2'
import { sendCandidateMessage, sendRecruiterMessage } from '../api/chat'
import { getSessionMessages, saveSessionMessages } from '../lib/chatStorage'
import Message from './Message'
import TypingIndicator from './TypingIndicator'
import './ChatWindow.css'

function welcomeMessage(role) {
  return {
    id: 'welcome',
    role: 'ai',
    text: role === 'candidate'
      ? `Hi! I'm your AI career assistant.\nTell me about yourself and I'll build your profile, find matching jobs, and more.`
      : `Hi! I'm your AI recruiting assistant.\nDescribe a role to post a job, search for candidates, and manage your listings.`,
    time: now(),
  }
}

export default function ChatWindow({ role, userId, userName, sessionId, onMessageSent, injectMessage }) {
  const [messages, setMessages]     = useState([])
  const [input, setInput]           = useState('')
  const [loading, setLoading]       = useState(false)
  const [profileId, setProfileId]   = useState(null)
  const [jobId, setJobId]           = useState(null)
  const [quickPicks, setQuickPicks] = useState([])
  const [hydrated, setHydrated]     = useState(false)
  const bottomRef = useRef(null)
  const inputRef  = useRef(null)

  // Load persisted messages for this chat session
  useEffect(() => {
    setHydrated(false)
    const stored = getSessionMessages(userId, sessionId)
    if (stored.messages?.length) {
      setMessages(stored.messages)
      setProfileId(stored.profileId)
      setJobId(stored.jobId)
    } else {
      setMessages([welcomeMessage(role)])
      setProfileId(null)
      setJobId(null)
    }
    setQuickPicks([])
    setInput('')
    setHydrated(true)
  }, [sessionId, userId, role])

  // Persist messages + meta whenever they change
  useEffect(() => {
    if (!hydrated || !userId || !sessionId) return
    saveSessionMessages(userId, sessionId, { messages, profileId, jobId })
  }, [messages, profileId, jobId, userId, sessionId, hydrated])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading, quickPicks])

  const lastInjectKey = useRef(null)
  useEffect(() => {
    if (!hydrated || !injectMessage || injectMessage.key === lastInjectKey.current) return
    lastInjectKey.current = injectMessage.key
    if (injectMessage.profileId) setProfileId(injectMessage.profileId)
    if (injectMessage.jobId) setJobId(injectMessage.jobId)
    send(injectMessage.message, {
      profileId: injectMessage.profileId,
      jobId: injectMessage.jobId,
    })
  }, [injectMessage, hydrated])

  async function send(text, overrides = {}) {
    if (!text.trim() || loading) return
    const userMsg = { id: Date.now(), role: 'user', text: text.trim(), time: now() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setQuickPicks([])
    setLoading(true)

    try {
      let data
      const activeProfileId = overrides.profileId ?? profileId
      const activeJobId     = overrides.jobId ?? jobId

      if (role === 'candidate') {
        data = await sendCandidateMessage({
          user_id: userId,
          message: text.trim(),
          session_id: sessionId,
          profile_id: activeProfileId,
        })
        if (data.profile_id) setProfileId(data.profile_id)
        if (data.available_profiles?.length) {
          setQuickPicks(data.available_profiles.map(p => ({
            label: `#${p.profile_id?.slice(0, 8)} — ${(p.skills || []).slice(0, 2).join(', ')}`,
            value: p.profile_id,
          })))
        }
      } else {
        data = await sendRecruiterMessage({
          user_id: userId,
          message: text.trim(),
          session_id: sessionId,
          job_id: activeJobId,
        })
        if (data.job_id) setJobId(data.job_id)
        if (data.available_jobs?.length) {
          setQuickPicks(data.available_jobs.map(j => ({
            label: `#${j.job_id?.slice(0, 8)} — ${j.role} @ ${j.company}`,
            value: j.job_id,
          })))
        }
      }

      const aiMsg = { id: Date.now() + 1, role: 'ai', text: data.reply, time: now(), intent: data.intent }
      setMessages(prev => [...prev, aiMsg])
      onMessageSent?.(text.trim())
    } catch (err) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'ai',
        text: `⚠️ ${err.message}`,
        time: now(),
        isError: true,
      }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(input) }
  }

  return (
    <div className="chat-window">
      <div className="chat-header glass">
        <div className="chat-header-left">
          <div className="chat-avatar">
            {role === 'candidate' ? <HiUserCircle /> : <HiBuildingOffice2 />}
          </div>
          <div>
            <div className="chat-header-title">
              {role === 'candidate' ? 'Candidate Assistant' : 'Recruiter Assistant'}
            </div>
            <div className="chat-header-sub">
              {profileId && <span className="active-id">Profile: #{profileId.slice(0, 8)}</span>}
              {jobId && <span className="active-id">Job: #{jobId.slice(0, 8)}</span>}
              {!profileId && !jobId && (
                <span className="online-dot-wrap">
                  <span className="online-dot" />AI Online
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="chat-header-right">
          <span className="session-badge">@{userId}</span>
        </div>
      </div>

      <div className="messages-area">
        <div className="messages-inner">
          {messages.map(m => <Message key={m.id} msg={m} />)}
          {loading && <TypingIndicator />}

          {!loading && quickPicks.length > 0 && (
            <div className="quickpick-row">
              <span className="quickpick-hint">Select one:</span>
              {quickPicks.map((p, i) => (
                <button key={i} className="quickpick-chip glass" onClick={() => send(p.value)}>
                  {p.label}
                </button>
              ))}
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      <div className="input-area">
        <div className="input-inner">
          <textarea
            ref={inputRef}
            className="chat-input"
            placeholder={role === 'candidate'
              ? 'Tell me your skills, ask for jobs, view profiles…'
              : 'Post a job, search candidates, manage listings…'}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            rows={1}
            disabled={loading}
          />
          <button
            className={`send-btn ${loading ? 'loading' : ''}`}
            onClick={() => send(input)}
            disabled={loading || !input.trim()}
            aria-label="Send"
          >
            {loading ? <span className="send-spinner" /> : <HiArrowUp />}
          </button>
        </div>
      </div>
    </div>
  )
}

function now() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
