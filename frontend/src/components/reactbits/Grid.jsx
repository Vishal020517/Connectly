import { useEffect, useRef } from 'react'
import './Grid.css'

export default function Grid({ color = '#ffffff', opacity = 0.1 }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    let animationId

    // Set canvas size
    const setCanvasSize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }
    setCanvasSize()

    let mouseX = window.innerWidth / 2
    let mouseY = window.innerHeight / 2
    let targetMouseX = mouseX
    let targetMouseY = mouseY

    const handleMouseMove = (e) => {
      targetMouseX = e.clientX
      targetMouseY = e.clientY
    }

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('resize', setCanvasSize)

    const gridSize = 50
    let time = 0

    const animate = () => {
      time += 0.005

      // Smooth mouse following
      mouseX += (targetMouseX - mouseX) * 0.1
      mouseY += (targetMouseY - mouseY) * 0.1

      // Clear canvas
      ctx.fillStyle = 'rgba(0, 0, 0, 0.1)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      ctx.strokeStyle = color
      ctx.globalAlpha = opacity

      // Draw animated grid
      const startCol = Math.floor(mouseX / gridSize) - 3
      const endCol = Math.ceil((mouseX + canvas.width) / gridSize) + 3
      const startRow = Math.floor(mouseY / gridSize) - 3
      const endRow = Math.ceil((mouseY + canvas.height) / gridSize) + 3

      // Vertical lines
      for (let col = startCol; col < endCol; col++) {
        const x = col * gridSize
        const distance = Math.abs(x - mouseX)
        const distanceFactor = Math.max(0, 1 - distance / 400)

        ctx.lineWidth = 0.5 + distanceFactor * 0.7
        ctx.globalAlpha = opacity + distanceFactor * 0.18

        ctx.beginPath()
        ctx.moveTo(x, startRow * gridSize)
        ctx.lineTo(x, endRow * gridSize)
        ctx.stroke()
      }

      // Horizontal lines
      for (let row = startRow; row < endRow; row++) {
        const y = row * gridSize
        const distance = Math.abs(y - mouseY)
        const distanceFactor = Math.max(0, 1 - distance / 400)

        ctx.lineWidth = 0.5 + distanceFactor * 0.7
        ctx.globalAlpha = opacity + distanceFactor * 0.18

        ctx.beginPath()
        ctx.moveTo(startCol * gridSize, y)
        ctx.lineTo(endCol * gridSize, y)
        ctx.stroke()
      }

      // Draw interactive nodes
      ctx.globalAlpha = 0.6
      for (let col = startCol; col < endCol; col++) {
        for (let row = startRow; row < endRow; row++) {
          const x = col * gridSize
          const y = row * gridSize
          const distance = Math.hypot(x - mouseX, y - mouseY)
          const distanceFactor = Math.max(0, 1 - distance / 300)

          if (distanceFactor > 0) {
            const radius = 2 + distanceFactor * 6
            ctx.fillStyle = color
            ctx.globalAlpha = opacity * 0.5 + distanceFactor * 0.5
            ctx.beginPath()
            ctx.arc(x, y, radius, 0, Math.PI * 2)
            ctx.fill()
          }
        }
      }

      ctx.globalAlpha = 1
      animationId = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      cancelAnimationFrame(animationId)
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('resize', setCanvasSize)
    }
  }, [color, opacity])

  return <canvas ref={canvasRef} className="grid-canvas" />
}
