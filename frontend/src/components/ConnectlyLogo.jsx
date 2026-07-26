import './ConnectlyLogo.css'

const DOTS = 10
const CX = 50
const CY = 50
const RING_R = 28
const DOT_R = 14

function dotPositions() {
  return Array.from({ length: DOTS }, (_, i) => {
    const angle = (i / DOTS) * Math.PI * 2 - Math.PI / 2
    return {
      x: CX + RING_R * Math.cos(angle),
      y: CY + RING_R * Math.sin(angle),
    }
  })
}

export default function ConnectlyLogo({ size = 36, animated = false, className = '' }) {
  const dots = dotPositions()

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      className={`connectly-logo ${animated ? 'connectly-logo--animated' : ''} ${className}`}
      aria-hidden="true"
    >
      <g className="connectly-logo-ring">
        {dots.map((d, i) => (
          <circle
            key={i}
            className="connectly-logo-dot"
            cx={d.x}
            cy={d.y}
            r={DOT_R}
            style={{ '--i': i }}
          />
        ))}
      </g>
    </svg>
  )
}

export function ConnectlyWordmark({ className = '' }) {
  return (
    <span className={`connectly-wordmark ${className}`}>CONNECTLY</span>
  )
}
