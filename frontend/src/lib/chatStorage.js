const PREFIX = 'whispernet_chats_'

function key(userId) {
  return `${PREFIX}${userId}`
}

function emptyData() {
  return { sessions: [], messages: {}, meta: {}, activeSessionId: null }
}

export function loadChatData(userId) {
  try {
    const raw = localStorage.getItem(key(userId))
    if (!raw) return emptyData()
    const data = JSON.parse(raw)
    return {
      sessions: data.sessions || [],
      messages: data.messages || {},
      meta: data.meta || {},
      activeSessionId: data.activeSessionId || null,
    }
  } catch {
    return emptyData()
  }
}

export function saveChatData(userId, data) {
  localStorage.setItem(key(userId), JSON.stringify(data))
}

export function getSessionMessages(userId, sessionId) {
  const data = loadChatData(userId)
  return {
    messages: data.messages[sessionId] || null,
    profileId: data.meta[sessionId]?.profileId || null,
    jobId: data.meta[sessionId]?.jobId || null,
  }
}

export function saveSessionMessages(userId, sessionId, { messages, profileId, jobId }) {
  const data = loadChatData(userId)
  data.messages[sessionId] = messages
  data.meta[sessionId] = { profileId: profileId || null, jobId: jobId || null }
  saveChatData(userId, data)
}

export function saveSessions(userId, sessions, activeSessionId) {
  const data = loadChatData(userId)
  data.sessions = sessions
  data.activeSessionId = activeSessionId
  saveChatData(userId, data)
}

export function deleteSession(userId, sessionId) {
  const data = loadChatData(userId)
  data.sessions = data.sessions.filter(s => s.id !== sessionId)
  delete data.messages[sessionId]
  delete data.meta[sessionId]

  if (data.activeSessionId === sessionId) {
    data.activeSessionId = data.sessions[0]?.id || null
  }

  saveChatData(userId, data)
  return {
    sessions: data.sessions,
    activeSessionId: data.activeSessionId,
  }
}

export function createDefaultSession() {
  const id = `${Date.now()}`
  return {
    id,
    session: { id, title: 'New Chat', time: _time() },
  }
}

function _time() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
