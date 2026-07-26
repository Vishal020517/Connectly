import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { HiChatBubbleLeftRight, HiXMark } from 'react-icons/hi2'
import { getProfiles, getJobs } from '../api/chat'
import ConnectlyLogo, { ConnectlyWordmark } from './ConnectlyLogo'
import './Sidebar.css'

export default function Sidebar({
  role, userId, userName,
  chatSessions, activeSession,
  onSelectSession, onNewChat, onDeleteChat,
  onSelectProfile, onSelectJob,
  onLogout, refreshTrigger,
}) {
  const [profiles, setProfiles] = useState([])
  const [jobs, setJobs]         = useState([])
  const [tab, setTab]           = useState('chats')
  const [hoveredChat, setHoveredChat] = useState(null)

  useEffect(() => {
    if (!userId) return
    if (role === 'candidate') {
      getProfiles(userId).then(setProfiles).catch(() => {})
    } else {
      getJobs(userId).then(setJobs).catch(() => {})
    }
  }, [userId, role, refreshTrigger])

  const initials = (userName || userId).slice(0, 2).toUpperCase()

  return (
    <aside className="sidebar glass-panel">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <ConnectlyLogo size={22} />
          <ConnectlyWordmark className="sidebar-wordmark" />
        </div>

        <div className="sidebar-user-card glass">
          <div className={`user-avatar ${role}`}>{initials}</div>
          <div className="user-info">
            <span className="user-name">{userName || userId}</span>
            <span className="user-role">
              {role === 'candidate' ? 'Candidate' : 'Recruiter'}
            </span>
          </div>
        </div>
      </div>

      <div className="sidebar-tabs glass">
        <button
          className={`stab ${tab === 'chats' ? 'active' : ''}`}
          onClick={() => setTab('chats')}
        >
          Chats
        </button>
        <button
          className={`stab ${tab === 'items' ? 'active' : ''}`}
          onClick={() => setTab('items')}
        >
          {role === 'candidate' ? 'Profiles' : 'Jobs'}
        </button>
      </div>

      <motion.button
        className="new-chat-btn glass"
        onClick={onNewChat}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <span className="new-chat-icon">+</span>
        New Chat
      </motion.button>

      <div className="sidebar-content">
        {tab === 'chats' && (
          <div className="chat-list">
            <p className="sidebar-section-label">Recent Chats</p>
            {chatSessions.length === 0 && (
              <p className="empty-hint">No chats yet. Start one above.</p>
            )}
            {chatSessions.map((s, i) => (
              <motion.div
                key={s.id}
                className={`chat-item ${s.id === activeSession ? 'active' : ''}`}
                onClick={() => onSelectSession(s.id)}
                onMouseEnter={() => setHoveredChat(s.id)}
                onMouseLeave={() => setHoveredChat(null)}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.03 }}
              >
                <span className="chat-icon"><HiChatBubbleLeftRight /></span>
                <div className="chat-meta">
                  <span className="chat-title">{s.title}</span>
                  <span className="chat-time">{s.time}</span>
                </div>
                <AnimatePresence>
                  {(hoveredChat === s.id || s.id === activeSession) && (
                    <motion.button
                      className="chat-delete-btn"
                      onClick={e => onDeleteChat(s.id, e)}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      title="Delete chat"
                      aria-label="Delete chat"
                    >
                      <HiXMark />
                    </motion.button>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </div>
        )}

        {tab === 'items' && role === 'candidate' && (
          <div className="items-list">
            <p className="sidebar-section-label">Your Profiles</p>
            {profiles.length === 0 && <p className="empty-hint">No profiles yet. Start chatting to create one.</p>}
            {profiles.map((p, i) => (
              <motion.div
                key={p.profile_id}
                className="item-card glass"
                onClick={() => onSelectProfile?.(p)}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                whileHover={{ x: 2 }}
              >
                <div className="item-header">
                  <span className="item-short-id">#{p.short_id}</span>
                  <span className={`item-badge ${p.completeness === 100 ? 'complete' : 'partial'}`}>
                    {p.completeness}%
                  </span>
                </div>
                <div className="item-title">{p.role_hint || p.skills?.slice(0, 2).join(', ') || 'Profile'}</div>
                <div className="item-meta">{p.work_type} · {p.experience} yrs</div>
              </motion.div>
            ))}
          </div>
        )}

        {tab === 'items' && role === 'recruiter' && (
          <div className="items-list">
            <p className="sidebar-section-label">Your Jobs</p>
            {jobs.length === 0 && <p className="empty-hint">No jobs posted yet. Start chatting to post one.</p>}
            {jobs.map((j, i) => (
              <motion.div
                key={j.job_id}
                className="item-card glass"
                onClick={() => onSelectJob?.(j)}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                whileHover={{ x: 2 }}
              >
                <div className="item-header">
                  <span className="item-short-id">#{j.short_id}</span>
                </div>
                <div className="item-title">{j.role}</div>
                <div className="item-meta">{j.company} · {j.location}</div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        <button className="logout-btn glass" onClick={onLogout}>
          Sign Out
        </button>
      </div>
    </aside>
  )
}
