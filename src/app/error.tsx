'use client';

import { useEffect } from 'react';

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        console.error(error);
    }, [error]);

    return (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
            <h2>Something went wrong!</h2>
            <pre style={{ color: 'red', whiteSpace: 'pre-wrap', margin: '1rem 0' }}>
                {error.message}
            </pre>
            <button
                onClick={() => reset()}
                style={{
                    padding: '0.5rem 1rem',
                    background: 'var(--primary)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px'
                }}
            >
                Try again
            </button>
        </div>
    );
}
