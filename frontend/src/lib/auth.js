const USERS_KEY = 'whispernet_users'
const SESSION_KEY = 'whispernet_session'

async function hashPassword(password) {
  const data = new TextEncoder().encode(password)
  const hash = await crypto.subtle.digest('SHA-256', data)
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')
}

function getUsers() {
  try {
    return JSON.parse(localStorage.getItem(USERS_KEY) || '[]')
  } catch {
    return []
  }
}

function saveUsers(users) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users))
}

export function getSession() {
  try {
    const raw = localStorage.getItem(SESSION_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function setSession(session) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session))
}

export function logout() {
  localStorage.removeItem(SESSION_KEY)
}

export async function signup({ userId, password, role, name }) {
  const id = userId.trim().toLowerCase()
  if (!id || id.length < 3) return { error: 'User ID must be at least 3 characters' }
  if (!/^[a-z0-9_]+$/.test(id)) return { error: 'Use only letters, numbers, and underscores' }
  if (!password || password.length < 6) return { error: 'Password must be at least 6 characters' }

  const users = getUsers()
  if (users.some(u => u.userId === id)) {
    return { error: 'This user ID is already taken. Try signing in instead.' }
  }

  const passwordHash = await hashPassword(password)
  users.push({
    userId: id,
    passwordHash,
    role,
    name: name?.trim() || id,
    createdAt: Date.now(),
  })
  saveUsers(users)

  const session = { userId: id, role, name: name?.trim() || id }
  setSession(session)
  return { session }
}

export async function login({ userId, password }) {
  const id = userId.trim().toLowerCase()
  if (!id || !password) return { error: 'Please enter your user ID and password' }

  const users = getUsers()
  const user = users.find(u => u.userId === id)
  if (!user) {
    return { error: 'No account found. Create a new account to get started.' }
  }

  const passwordHash = await hashPassword(password)
  if (user.passwordHash !== passwordHash) {
    return { error: 'Incorrect password. Please try again.' }
  }

  const session = { userId: user.userId, role: user.role, name: user.name }
  setSession(session)
  return { session }
}
