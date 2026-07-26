import ConnectlyLogo from './ConnectlyLogo'
import './TypingIndicator.css'

export default function TypingIndicator() {
  return (
    <div className="typing-row">
      <div className="msg-avatar ai-avatar">
        <ConnectlyLogo size={18} />
      </div>
      <div className="typing-bubble bubble-ai">
        <span className="dot" style={{ animationDelay: '0ms' }} />
        <span className="dot" style={{ animationDelay: '160ms' }} />
        <span className="dot" style={{ animationDelay: '320ms' }} />
      </div>
    </div>
  )
}
