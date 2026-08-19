'use client'

import { useEffect, useState } from 'react'

function formatRemaining(endMs: number, nowMs: number): string {
  const diff = Math.max(0, endMs - nowMs)
  const totalMinutes = Math.floor(diff / 60000)
  const days = Math.floor(totalMinutes / (60 * 24))
  const hours = Math.floor((totalMinutes % (60 * 24)) / 60)
  const minutes = totalMinutes % 60

  if (diff === 0) return 'Ended'
  if (days > 0) return `${days}d ${hours}h left`
  if (hours > 0) return `${hours}h ${minutes}m left`
  return `${minutes}m left`
}

export function Countdown({ endTimestamp }: { endTimestamp: number }) {
  const endMs = endTimestamp * 1000
  const [label, setLabel] = useState(() => formatRemaining(endMs, Date.now()))

  useEffect(() => {
    const tick = () => setLabel(formatRemaining(endMs, Date.now()))
    tick()
    const interval = setInterval(tick, 60000)
    return () => clearInterval(interval)
  }, [endMs])

  const ended = label === 'Ended'

  return (
    <span
      className={`inline-flex items-center gap-1.5 text-sm font-medium ${
        ended ? 'text-muted' : 'text-foreground'
      }`}
    >
      <span
        aria-hidden
        className={`h-1.5 w-1.5 rounded-full ${
          ended ? 'bg-muted' : 'bg-accent'
        }`}
      />
      {label}
    </span>
  )
}
