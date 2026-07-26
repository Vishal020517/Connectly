import { useState } from 'react'
import {
  HiUserCircle,
  HiBuildingOffice2,
  HiChatBubbleLeftRight,
  HiLockClosed,
  HiUserPlus,
} from 'react-icons/hi2'
import ConnectlyLogo, { ConnectlyWordmark } from '../components/ConnectlyLogo'
import LightRays from '../components/reactbits/LightRays'
import { login, signup } from '../lib/auth'
import './Auth.css'

const FEATURES = [
  { icon: HiUserCircle, text: 'Candidates build profiles & find jobs' },
  { icon: HiBuildingOffice2, text: 'Recruiters post roles & hire talent' },
  { icon: HiChatBubbleLeftRight, text: 'Everything through one AI chat' },
]

export default function Auth({ onAuth }) {
  const [mode, setMode]         = useState('login')
  const [role, setRole]         = useState('candidate')
  const [userId, setUserId]     = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm]   = useState('')
  const [name, setName]         = useState('')
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (mode === 'signup') {
        if (password !== confirm) {
          setError('Passwords do not match')
          return
        }
        const result = await signup({ userId, password, role, name })
        if (result.error) { setError(result.error); return }
        onAuth(result.session)
      } else {
        const result = await login({ userId, password })
        if (result.error) { setError(result.error); return }
        onAuth(result.session)
      }
    } finally {
      setLoading(false)
    }
  }

  function switchMode(next) {
    setMode(next)
    setError('')
    setPassword('')
    setConfirm('')
  }

  return (
    <div className="auth-page">
      <LightRays
        raysOrigin="top-center"
        raysColor="#ffffff"
        raysSpeed={1.5}
        lightSpread={0.8}
        rayLength={1.2}
        followMouse={true}
        mouseInfluence={0.08}
        noiseAmount={0.08}
        distortion={0.04}
        className="auth-light-rays"
      />
      <div className="auth-shell">
        {/* Left panel */}
        <aside className="auth-left glass">
          <div className="auth-logo-row">
            <ConnectlyLogo size={40} animated />
            <ConnectlyWordmark />
          </div>

          <h1 className="auth-headline">Connect talent with opportunity.</h1>
          <p className="auth-desc">
            AI-powered hiring for candidates and recruiters — profiles, jobs, and matches in one chat.
          </p>

          <ul className="auth-features">
            {FEATURES.map(({ icon: Icon, text }) => (
              <li key={text}>
                <span className="auth-feature-icon"><Icon /></span>
                <span>{text}</span>
              </li>
            ))}
          </ul>
        </aside>

        {/* Right panel */}
        <div className="auth-right">
          <div className="auth-card glass">
            <div className="auth-card-header">
              <div className="auth-card-icon">
                {mode === 'login' ? <HiLockClosed /> : <HiUserPlus />}
              </div>
              <div>
                <h2 className="auth-card-title">
                  {mode === 'login' ? 'Welcome back' : 'Create your account'}
                </h2>
                <p className="auth-card-sub">
                  {mode === 'login'
                    ? 'Sign in to continue to your workspace'
                    : 'Join as a candidate or recruiter'}
                </p>
              </div>
            </div>

            <div className="auth-tabs glass">
              <button
                type="button"
                className={`auth-tab ${mode === 'login' ? 'active' : ''}`}
                onClick={() => switchMode('login')}
              >
                Sign In
              </button>
              <button
                type="button"
                className={`auth-tab ${mode === 'signup' ? 'active' : ''}`}
                onClick={() => switchMode('signup')}
              >
                Create Account
              </button>
              <div
                className="auth-tab-indicator"
                style={{ left: mode === 'login' ? '4px' : 'calc(50% + 2px)' }}
              />
            </div>

            <form key={mode} className="auth-form" onSubmit={handleSubmit}>
              {mode === 'signup' && (
                <>
                  <div className="field">
                    <label>I am a</label>
                    <div className="auth-role-toggle">
                      <button
                        type="button"
                        className={`role-pill glass ${role === 'candidate' ? 'active' : ''}`}
                        onClick={() => setRole('candidate')}
                      >
                        <HiUserCircle className="role-icon" />
                        Candidate
                      </button>
                      <button
                        type="button"
                        className={`role-pill glass ${role === 'recruiter' ? 'active' : ''}`}
                        onClick={() => setRole('recruiter')}
                      >
                        <HiBuildingOffice2 className="role-icon" />
                        Recruiter
                      </button>
                    </div>
                  </div>

                  <div className="field">
                    <label htmlFor="name">Full Name</label>
                    <input
                      id="name"
                      className="glass-input"
                      type="text"
                      placeholder="Your name"
                      value={name}
                      onChange={e => { setName(e.target.value); setError('') }}
                      autoComplete="name"
                    />
                  </div>
                </>
              )}

              <div className="field">
                <label htmlFor="uid">User ID</label>
                <input
                  id="uid"
                  className="glass-input"
                  type="text"
                  placeholder="e.g. vishal_dev"
                  value={userId}
                  onChange={e => { setUserId(e.target.value); setError('') }}
                  autoComplete="username"
                  spellCheck={false}
                  required
                />
              </div>

              <div className="field">
                <label htmlFor="pass">Password</label>
                <div className="pass-wrap">
                  <input
                    id="pass"
                    className="glass-input"
                    type={showPass ? 'text' : 'password'}
                    placeholder={mode === 'signup' ? 'Min. 6 characters' : 'Your password'}
                    value={password}
                    onChange={e => { setPassword(e.target.value); setError('') }}
                    autoComplete={mode === 'signup' ? 'new-password' : 'current-password'}
                    required
                  />
                  <button
                    type="button"
                    className="pass-toggle"
                    onClick={() => setShowPass(v => !v)}
                    aria-label="Toggle password visibility"
                  >
                    {showPass ? 'Hide' : 'Show'}
                  </button>
                </div>
              </div>

              {mode === 'signup' && (
                <div className="field">
                  <label htmlFor="confirm">Confirm Password</label>
                  <input
                    id="confirm"
                    className="glass-input"
                    type={showPass ? 'text' : 'password'}
                    placeholder="Re-enter password"
                    value={confirm}
                    onChange={e => { setConfirm(e.target.value); setError('') }}
                    autoComplete="new-password"
                    required
                  />
                </div>
              )}

              {error && <div className="auth-error glass">{error}</div>}

              <button type="submit" className="auth-submit" disabled={loading}>
                {loading ? (
                  <span className="auth-spinner" />
                ) : mode === 'login' ? (
                  'Sign In'
                ) : (
                  'Create Account'
                )}
              </button>
            </form>

            <p className="auth-switch">
              {mode === 'login' ? (
                <>
                  New here?{' '}
                  <button type="button" onClick={() => switchMode('signup')}>
                    Create an account
                  </button>
                </>
              ) : (
                <>
                  Already signed up?{' '}
                  <button type="button" onClick={() => switchMode('login')}>
                    Sign in
                  </button>
                </>
              )}
            </p>
          </div>

          <div className="auth-mobile-brand">
            <ConnectlyLogo size={28} />
            <ConnectlyWordmark />
          </div>
        </div>
      </div>
    </div>
  )
}
