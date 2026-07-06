import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Blog Cloner - WordPress Importer',
  description: 'Import blog posts from any website to WordPress',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
