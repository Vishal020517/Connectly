const BASE = ''  // proxied by vite to http://localhost:8000

export async function sendCandidateMessage({ user_id, message, session_id, profile_id }) {
  const res = await fetch(`${BASE}/candidate/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id, message, session_id, profile_id }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Server error')
  }
  return res.json()
}

export async function sendRecruiterMessage({ user_id, message, session_id, job_id }) {
  const res = await fetch(`${BASE}/recruiter/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id, message, session_id, job_id }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Server error')
  }
  return res.json()
}

export async function getProfiles(user_id) {
  const res = await fetch(`${BASE}/sidebar/profiles/${user_id}`)
  if (!res.ok) return []
  return res.json()
}

export async function getJobs(user_id) {
  const res = await fetch(`${BASE}/sidebar/jobs/${user_id}`)
  if (!res.ok) return []
  return res.json()
}
