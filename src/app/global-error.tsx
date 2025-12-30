'use client';

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    return (
        <html>
            <body>
                <div style={{ padding: '2rem', textAlign: 'center' }}>
                    <h2>Global Error</h2>
                    <pre style={{ color: 'red', margin: '1rem 0' }}>{error.message}</pre>
                    <button onClick={() => reset()}>Try again</button>
                </div>
            </body>
        </html>
    );
}
