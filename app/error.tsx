'use client'

export default function Error({
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {

  return (
    <main className="flex min-h-dvh items-center justify-center bg-background px-5 py-12 text-foreground sm:px-8">
      <section className="w-full max-w-xl text-center">
        <p className="font-mono text-sm font-medium uppercase tracking-[0.2em] text-muted-foreground">
          Epic Games Freebie Notifier
        </p>
        <div className="mt-8 border-y border-dashed py-10 sm:py-14">
          <p className="font-mono text-7xl font-semibold tracking-[-0.08em] text-destructive sm:text-8xl">
            500
          </p>
          <h1 className="mt-5 text-balance text-2xl font-semibold tracking-tight sm:text-3xl">
            The giveaway feed hit a snag.
          </h1>
          <p className="mx-auto mt-3 max-w-md text-pretty leading-6 text-muted-foreground">
            Something went wrong while loading this page. Try again, or head back to the latest free games.
          </p>
        </div>
        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <button
            type="button"
            onClick={() => reset()}
            className="inline-flex min-h-11 items-center justify-center rounded-lg bg-primary px-5 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-85 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
          >
            Try again
          </button>
          <a
            href="/"
            className="inline-flex min-h-11 items-center justify-center rounded-lg border border-border px-5 text-sm font-medium text-foreground transition-colors hover:bg-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
          >
            Back to free games
          </a>
        </div>
      </section>
    </main>
  )
}
