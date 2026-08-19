import type { Metadata, Viewport } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import './globals.css'

const geistSans = Geist({
  subsets: ['latin'],
  variable: '--font-geist-sans',
  display: 'swap',
})

const geistMono = Geist_Mono({
  subsets: ['latin'],
  variable: '--font-geist-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Free Games Today — Epic Games Store',
  description:
    'A clean daily tracker for the games you can claim for free right now on the Epic Games Store. Updated every day.',
  keywords: [
    'epic games',
    'free games',
    'free game today',
    'epic games store',
    'giveaway',
  ],
  openGraph: {
    title: 'Free Games Today — Epic Games Store',
    description:
      'The games you can claim for free right now on the Epic Games Store.',
    type: 'website',
  },
}

export const viewport: Viewport = {
  themeColor: '#fbfbfa',
  width: 'device-width',
  initialScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} bg-background`}
    >
      <body className="font-sans">{children}</body>
    </html>
  )
}
