import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Hawaii Travel Album',
  description: 'A visual journal of our trip to Honolulu.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <head>
        <link rel="stylesheet" href="https://hangeul.pstatic.net/hangeul_static/css/maru-buri.css" />
      </head>
      <body>
        {children}
        <div style={{
          position: 'fixed',
          bottom: '10px',
          right: '10px',
          background: 'transparent',
          color: 'rgba(0,0,0,0.5)',
          padding: '4px 8px',
          borderRadius: '4px',
          fontSize: '10px',
          zIndex: 9999,
          pointerEvents: 'none',
          fontFamily: 'monospace'
        }}>
          v0.23
        </div>
      </body>
    </html>
  )
}
