import { HiUser } from 'react-icons/hi2'
import ConnectlyLogo from './ConnectlyLogo'
import './Message.css'

export default function Message({ msg }) {
  const isUser = msg.role === 'user'

  function formatText(text) {
    return text
      .split('\n')
      .map((line, i) => {
        const parts = line.split(/(\*\*.*?\*\*)/)
        return (
          <span key={i}>
            {parts.map((p, j) =>
              p.startsWith('**') && p.endsWith('**')
                ? <strong key={j}>{p.slice(2, -2)}</strong>
                : p
            )}
            {i < text.split('\n').length - 1 && <br />}
          </span>
        )
      })
  }

  const bubble = (
    <div className={`bubble ${isUser ? 'bubble-user' : 'bubble-ai'} ${msg.isError ? 'bubble-error' : ''}`}>
      <div className="bubble-text">{formatText(msg.text)}</div>
      <div className="bubble-footer">
        <span className="bubble-time">{msg.time}</span>
        {msg.intent && !isUser && (
          <span className="intent-tag">{msg.intent}</span>
        )}
      </div>
    </div>
  )

  if (isUser) {
    return (
      <div className="message-row user">
        {bubble}
        <div className="msg-avatar user-avatar">
          <HiUser />
        </div>
      </div>
    )
  }

  return (
    <div className="message-row ai">
      <div className="msg-avatar ai-avatar">
        <ConnectlyLogo size={18} />
      </div>
      {bubble}
    </div>
  )
}
