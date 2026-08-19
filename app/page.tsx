import { getFreeGames, type FreeGame } from '@/lib/epic'
import { SiteHeader } from '@/components/site-header'
import { GameCard } from '@/components/game-card'

// Rebuild the page at most once per day.
export const revalidate = 86400

export default async function HomePage() {
  let games: FreeGame[] = []
  let failed = false

  try {
    games = await getFreeGames()
  } catch {
    failed = true
  }

  return (
    <main className="mx-auto flex min-h-dvh w-full max-w-5xl flex-col px-5 py-12 sm:px-8 sm:py-16">
      <SiteHeader count={games.length} />

      <section className="flex-1 py-10">
        {failed ? (
          <div className="rounded-[var(--radius)] border bg-surface p-8 text-center">
            <p className="font-medium">Couldn&apos;t reach the Epic Games Store.</p>
            <p className="mt-1 text-sm text-muted">
              Please try again in a little while.
            </p>
          </div>
        ) : games.length === 0 ? (
          <div className="rounded-[var(--radius)] border border-dashed bg-surface p-12 text-center">
            <p className="font-medium">Nothing free at the moment.</p>
            <p className="mt-1 text-sm text-muted">
              The next giveaway is usually just a few days away.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {games.map((game) => (
              <GameCard key={game.id} game={game} />
            ))}
          </div>
        )}
      </section>

      <footer className="mt-auto flex flex-col gap-1 border-t pt-8 text-sm text-muted">
        <p>
          Data from the public Epic Games Store promotions API. Not affiliated
          with Epic Games.
        </p>
        <p className="font-mono text-xs">
          Updated daily via GitHub Actions · Discord alerts included
        </p>
      </footer>
    </main>
  )
}
