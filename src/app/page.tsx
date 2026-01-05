import Hero from '@/components/Hero';
import TravelJournal from '@/components/TravelJournal';
import ErrorBoundary from '@/components/ErrorBoundary';
import { REAL_TIMELINE } from '@/data/real';

export const dynamic = 'force-dynamic';

export default function Home() {
  // Server-Side: Pick 5 random images for the Hero
  const allImages = REAL_TIMELINE.flatMap(item => item.media || [])
    .filter(m => m.type === 'image')
    .map(m => m.src);

  // Shuffle safely on server
  const shuffled = [...allImages].sort(() => Math.random() - 0.5);
  const heroImages = shuffled.slice(0, 5);

  return (
    <main style={{ minHeight: '100vh', background: 'var(--background)' }}>
      <Hero heroImages={heroImages} />
      <div id="journal">
        {/* Timeline + Map Integration */}
        <ErrorBoundary>
          <TravelJournal />
        </ErrorBoundary>
      </div>


      <footer style={{
        textAlign: 'center',
        padding: '2rem',
        background: 'var(--foreground)',
        color: 'var(--background)'
      }}>
        <p style={{ opacity: 0.8, fontSize: '0.9rem' }}>
          &copy; {new Date().getFullYear()} 도헌이의 하와이 여행기. (불펌 금지! 🚫)
        </p>
      </footer>
    </main>
  )
}
