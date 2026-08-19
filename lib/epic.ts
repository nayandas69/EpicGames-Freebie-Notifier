export type FreeGame = {
  id: string
  title: string
  description: string
  url: string
  image: string
  originalPrice: string
  endTimestamp: number | null
}

const EPIC_GAMES_API =
  'https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US&allowCountries=US'
const EPIC_STORE_BASE = 'https://store.epicgames.com/en-US/p/'

const PREFERRED_IMAGE_TYPES = [
  'OfferImageWide',
  'DieselStoreFrontWide',
  'featuredMedia',
  'Thumbnail',
]

// Minimal shapes for the parts of the Epic API response we read.
type KeyImage = { type?: string; url?: string }
type Mapping = { pageSlug?: string }
type PromoOffer = { endDate?: string }
type PromoGroup = { promotionalOffers?: PromoOffer[] }

type EpicElement = {
  id?: string
  title?: string
  description?: string
  productSlug?: string
  urlSlug?: string
  keyImages?: KeyImage[]
  catalogNs?: { mappings?: Mapping[] }
  offerMappings?: Mapping[]
  price?: {
    totalPrice?: {
      discountPrice?: number
      originalPrice?: number
      fmtPrice?: { originalPrice?: string }
    }
  }
  promotions?: {
    promotionalOffers?: PromoGroup[]
    upcomingPromotionalOffers?: PromoGroup[]
  }
}

function resolveSlug(game: EpicElement): string | null {
  if (game.productSlug) return game.productSlug
  const nsSlug = game.catalogNs?.mappings?.[0]?.pageSlug
  if (nsSlug) return nsSlug
  const offerSlug = game.offerMappings?.[0]?.pageSlug
  if (offerSlug) return offerSlug
  if (game.urlSlug) return game.urlSlug
  return game.id ?? null
}

function resolveImage(game: EpicElement): string {
  const images = game.keyImages ?? []
  for (const wanted of PREFERRED_IMAGE_TYPES) {
    const match = images.find((img) => img.type === wanted && img.url)
    if (match?.url) return match.url
  }
  return images[0]?.url ?? ''
}

function resolveOriginalPrice(game: EpicElement): string {
  const price = game.price?.totalPrice
  if (!price) return 'Free'
  const original = price.originalPrice ?? 0
  const discount = price.discountPrice ?? 0
  if (original && original > discount) {
    return `$${(original / 100).toFixed(2)}`
  }
  const fmt = price.fmtPrice?.originalPrice
  if (fmt && fmt !== '0') return fmt
  return 'Free'
}

function resolveEndTimestamp(game: EpicElement): number | null {
  const promotions = game.promotions
  if (!promotions) return null
  const groups =
    promotions.promotionalOffers ?? promotions.upcomingPromotionalOffers ?? []
  const endDate = groups[0]?.promotionalOffers?.[0]?.endDate
  if (!endDate) return null
  const parsed = Date.parse(endDate)
  return Number.isNaN(parsed) ? null : Math.floor(parsed / 1000)
}

function isCurrentlyFree(game: EpicElement): boolean {
  const discount = game.price?.totalPrice?.discountPrice
  if (discount !== 0) return false
  const active = game.promotions?.promotionalOffers ?? []
  return active.length > 0
}

export async function getFreeGames(): Promise<FreeGame[]> {
  const response = await fetch(EPIC_GAMES_API, {
    headers: { 'User-Agent': 'EpicGames-Freebie-Notifier/2.0' },
    // Revalidate the Epic catalog once per day.
    next: { revalidate: 86400 },
  })

  if (!response.ok) {
    throw new Error(`Epic API request failed: ${response.status}`)
  }

  const json = await response.json()
  const elements: EpicElement[] =
    json?.data?.Catalog?.searchStore?.elements ?? []

  const games: FreeGame[] = []
  for (const element of elements) {
    if (!isCurrentlyFree(element)) continue
    const title = element.title ?? ''
    if (!title || title.toLowerCase().includes('mystery')) continue

    const slug = resolveSlug(element)
    if (!slug) continue

    games.push({
      id: element.id ?? slug,
      title,
      description: (element.description ?? '').trim(),
      url: `${EPIC_STORE_BASE}${slug}`,
      image: resolveImage(element),
      originalPrice: resolveOriginalPrice(element),
      endTimestamp: resolveEndTimestamp(element),
    })
  }

  return games
}
