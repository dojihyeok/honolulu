import Hero from '@/components/Hero';
import TravelJournal from '@/components/TravelJournal';
import ErrorBoundary from '@/components/ErrorBoundary';

export const dynamic = 'force-dynamic';

export default function Home() {
  return (
    <main style={{ minHeight: '100vh', background: 'var(--background)' }}>
      <Hero />
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
