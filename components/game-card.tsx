import Image from 'next/image'
import type { FreeGame } from '@/lib/epic'
import { Countdown } from './countdown'

function formatUntil(timestamp: number | null): string {
  if (!timestamp) return 'Limited time'
  return new Date(timestamp * 1000).toLocaleDateString('en-US', {
    day: 'numeric',
    month: 'long',
  })
}

export function GameCard({ game }: { game: FreeGame }) {
  return (
    <article className="group flex flex-col overflow-hidden rounded-[var(--radius)] border bg-surface transition-shadow hover:shadow-[0_8px_30px_rgba(0,0,0,0.06)]">
      <div className="relative aspect-[16/9] w-full overflow-hidden bg-border">
        {game.image ? (
          <Image
            src={game.image || '/placeholder.svg'}
            alt={`Cover art for ${game.title}`}
            fill
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
            className="object-cover transition-transform duration-500 group-hover:scale-[1.03]"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-sm text-muted">
            No image
          </div>
        )}
        <span className="absolute left-3 top-3 rounded-full bg-accent px-2.5 py-1 text-xs font-semibold text-accent-foreground">
          Free
        </span>
      </div>

      <div className="flex flex-1 flex-col gap-4 p-5">
        <div className="flex flex-col gap-1">
          <h2 className="text-pretty text-lg font-semibold leading-snug">
            {game.title}
          </h2>
          <p className="flex items-center gap-2 text-sm text-muted">
            {game.originalPrice !== 'Free' && (
              <span className="line-through">{game.originalPrice}</span>
            )}
            <span className="font-medium text-foreground">$0.00</span>
          </p>
        </div>

        <div className="mt-auto flex flex-col gap-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted">
              Until {formatUntil(game.endTimestamp)}
            </span>
            {game.endTimestamp && (
              <Countdown endTimestamp={game.endTimestamp} />
            )}
          </div>

          <a
            href={game.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center rounded-lg bg-foreground px-4 py-2.5 text-sm font-semibold text-background transition-opacity hover:opacity-90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          >
            Claim on Epic Games
          </a>
        </div>
      </div>
    </article>
  )
}
