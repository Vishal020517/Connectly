import { useState, useCallback, useEffect } from 'react'
import Auth       from './pages/Auth'
import Sidebar    from './components/Sidebar'
import ChatWindow from './components/ChatWindow'
import { getSession, logout } from './lib/auth'
import {
  loadChatData,
  saveSessions,
  deleteSession,
  createDefaultSession,
} from './lib/chatStorage'
import './App.css'

function initChats(userId) {
  const data = loadChatData(userId)
  if (data.sessions.length > 0) {
    return {
      sessions: data.sessions,
      active: data.activeSessionId || data.sessions[0].id,
    }
  }
  const { id, session } = createDefaultSession()
  saveSessions(userId, [session], id)
  return { sessions: [session], active: id }
}

export default function App() {
  const [session, setSession]               = useState(null)
  const [chatSessions, setChatSessions]     = useState([])
  const [activeSession, setActiveSession]   = useState(null)
  const [sidebarRefresh, setSidebarRefresh] = useState(0)
  const [injectMessage, setInjectMessage]   = useState(null)
  const [authChecked, setAuthChecked]       = useState(false)

  useEffect(() => {
    const saved = getSession()
    if (saved) {
      setSession(saved)
      const { sessions, active } = initChats(saved.userId)
      setChatSessions(sessions)
      setActiveSession(active)
    }
    setAuthChecked(true)
  }, [])

  function handleAuth(authSession) {
    setSession(authSession)
    const { sessions, active } = initChats(authSession.userId)
    setChatSessions(sessions)
    setActiveSession(active)
  }

  function handleLogout() {
    logout()
    setSession(null)
    setChatSessions([])
    setActiveSession(null)
    setInjectMessage(null)
  }

  function handleNewChat() {
    const { id, session: s } = createDefaultSession()
    setChatSessions(prev => {
      const next = [s, ...prev]
      saveSessions(session.userId, next, id)
      return next
    })
    setActiveSession(id)
  }

  function handleSelectSession(id) {
    setActiveSession(id)
    saveSessions(session.userId, chatSessions, id)
  }

  function handleDeleteChat(sessionId, e) {
    e.stopPropagation()
    if (!session) return

    const msg = chatSessions.length === 1
      ? 'Delete this chat? A new empty chat will be started.'
      : 'Delete this chat? This cannot be undone.'
    if (!window.confirm(msg)) return

    const { sessions, activeSessionId } = deleteSession(session.userId, sessionId)

    if (sessions.length === 0) {
      const { id, session: s } = createDefaultSession()
      const next = [s]
      saveSessions(session.userId, next, id)
      setChatSessions(next)
      setActiveSession(id)
    } else {
      setChatSessions(sessions)
      setActiveSession(activeSessionId)
    }
  }

  const handleMessageSent = useCallback((text) => {
    if (!session) return
    setChatSessions(prev => {
      const updated = prev.map(s =>
        s.id === activeSession && s.title === 'New Chat'
          ? { ...s, title: text.slice(0, 36) + (text.length > 36 ? '…' : '') }
          : s
      )
      saveSessions(session.userId, updated, activeSession)
      return updated
    })
    setSidebarRefresh(n => n + 1)
  }, [activeSession, session])

  function handleSelectProfile(profile) {
    setInjectMessage({
      key: Date.now(),
      sessionId: activeSession,
      message: `View my profile ${profile.profile_id}`,
      profileId: profile.profile_id,
    })
  }

  function handleSelectJob(job) {
    setInjectMessage({
      key: Date.now(),
      sessionId: activeSession,
      message: `Show details for job ${job.job_id}`,
      jobId: job.job_id,
    })
  }

  if (!authChecked) return null
  if (!session) return <Auth onAuth={handleAuth} />

  return (
    <div className="app-layout">
      <Sidebar
        role={session.role}
        userId={session.userId}
        userName={session.name}
        chatSessions={chatSessions}
        activeSession={activeSession}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        onSelectProfile={handleSelectProfile}
        onSelectJob={handleSelectJob}
        onLogout={handleLogout}
        refreshTrigger={sidebarRefresh}
      />
      <main className="app-main">
        {activeSession && (
          <ChatWindow
            key={activeSession}
            role={session.role}
            userId={session.userId}
            userName={session.name}
            sessionId={activeSession}
            onMessageSent={handleMessageSent}
            injectMessage={injectMessage?.sessionId === activeSession ? injectMessage : null}
          />
        )}
      </main>
    </div>
  )
}
