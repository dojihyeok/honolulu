'use client';

import { useEffect } from 'react';

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        // Check for chunk load error
        const errorString = error.toString().toLowerCase();
        const isChunkError = errorString.includes('loading chunk') ||
            errorString.includes('failed to load chunk') ||
            errorString.includes('missing') ||
            error.name === 'ChunkLoadError';

        if (isChunkError && typeof window !== 'undefined') {
            const lastReload = sessionStorage.getItem('chunk_error_reload');
            const now = Date.now();
            if (!lastReload || (now - parseInt(lastReload) > 10000)) {
                sessionStorage.setItem('chunk_error_reload', now.toString());
                window.location.reload();
            }
        }
    }, [error]);

    return (
        <html>
            <body>
                <div style={{ padding: '2rem', textAlign: 'center', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontFamily: 'system-ui, sans-serif' }}>
                    <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: '#ff4444' }}>치명적인 오류가 발생했습니다.</h2>
                    <p style={{ marginBottom: '1.5rem', color: '#666' }}>
                        앱을 불러오는 데 실패했습니다.<br />
                        새로고침을 시도합니다.
                    </p>
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
                            cursor: 'pointer'
                        }}
                    >
                        새로고침 (Retry)
                    </button>
                    <pre style={{ marginTop: '2rem', fontSize: '0.7rem', color: '#999' }}>{error.message}</pre>
                </div>
            </body>
        </html>
    );
}
