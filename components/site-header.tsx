export function SiteHeader({ count }: { count: number }) {
  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })

  return (
    <header className="flex flex-col gap-6 border-b pb-10">
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs uppercase tracking-widest text-muted">
          Epic Games Store
        </span>
        <time className="font-mono text-xs text-muted">{today}</time>
      </div>

      <div className="flex flex-col gap-4">
        <h1 className="text-balance text-4xl font-semibold tracking-tight sm:text-5xl">
          Free games, today.
        </h1>
        <p className="max-w-xl text-pretty leading-relaxed text-muted">
          {count > 0
            ? `${count} game${count === 1 ? '' : 's'} you can claim for free right now. New titles arrive weekly, and our bot also pings Discord the moment they drop.`
            : 'No free games are live right now. Check back soon — new titles drop every week and we ping Discord the moment they do.'}
        </p>
      </div>
    </header>
  )
}
