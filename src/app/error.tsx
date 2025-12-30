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

        // Check for chunk load error
        const errorString = error.toString().toLowerCase();
        const isChunkError = errorString.includes('loading chunk') ||
            errorString.includes('failed to load chunk') ||
            errorString.includes('missing') ||
            error.name === 'ChunkLoadError';

        if (isChunkError && typeof window !== 'undefined') {
            const lastReload = sessionStorage.getItem('chunk_error_reload');
            const now = Date.now();

            // Auto-reload if not reloaded recently (10s)
            if (!lastReload || (now - parseInt(lastReload) > 10000)) {
                sessionStorage.setItem('chunk_error_reload', now.toString());
                window.location.reload();
            }
        }
    }, [error]);

    return (
        <div style={{ padding: '2rem', textAlign: 'center', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: '#ff4444' }}>일시적인 오류가 발생했습니다.</h2>
            <p style={{ marginBottom: '1.5rem', color: '#666', lineHeight: 1.6 }}>
                앱이 업데이트되었거나 연결이 불안정합니다.<br />
                새로고침을 눌러주세요.
            </p>
            <pre style={{
                color: '#888',
                whiteSpace: 'pre-wrap',
                margin: '1rem 0',
                fontSize: '0.8rem',
                background: '#f1f1f1',
                padding: '1rem',
                borderRadius: '8px',
                maxWidth: '90%'
            }}>
                {error.message}
            </pre>
            <button
                onClick={() => {
                    sessionStorage.setItem('chunk_error_reload', Date.now().toString());
                    window.location.reload();
                }}
                style={{
                    padding: '0.8rem 1.5rem',
                    background: '#0EA5E9',
                    color: 'white',
                    border: 'none',
                    borderRadius: '999px',
                    fontSize: '1rem',
                    fontWeight: 'bold',
                    boxShadow: '0 4px 12px rgba(14, 165, 233, 0.4)',
                    cursor: 'pointer'
                }}
            >
                새로고침 (Retry) ↻
            </button>
        </div>
    );
}
