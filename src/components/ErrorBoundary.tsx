'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
    children?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error("Uncaught error:", error, errorInfo);
    }

    public render() {
        if (this.state.hasError) {
            const errorString = this.state.error?.toString().toLowerCase() || "";
            const isChunkError = errorString.includes("loading chunk") ||
                errorString.includes("failed to load chunk") ||
                errorString.includes("missing") ||
                this.state.error?.name === 'ChunkLoadError';

            // Automatic Recovery Strategy
            if (isChunkError && typeof window !== 'undefined') {
                const lastReload = sessionStorage.getItem('chunk_error_reload');
                const now = Date.now();

                // If we haven't reloaded for this reason in the last 10 seconds, do it now
                if (!lastReload || (now - parseInt(lastReload) > 10000)) {
                    sessionStorage.setItem('chunk_error_reload', now.toString());
                    window.location.href = window.location.pathname + '?v=' + now;
                    return null; // Render nothing while reloading
                }
            }

            return (
                <div style={{ padding: '2rem', textAlign: 'center', color: '#ff4444' }}>
                    <h2 style={{ marginBottom: '1rem' }}>일시적인 오류가 발생했습니다.</h2>
                    <p style={{ marginBottom: '1rem', color: '#666' }}>
                        앱의 새로운 버전이 배포되었거나 네트워크 상태가 불안정할 수 있습니다.
                    </p>
                    <details style={{ whiteSpace: 'pre-wrap', marginTop: '1rem', fontSize: '0.8rem', opacity: 0.7, textAlign: 'left', background: '#f5f5f5', padding: '1rem', borderRadius: '4px' }}>
                        {this.state.error && this.state.error.toString()}
                    </details>
                    <button
                        onClick={() => {
                            // Force reload on manual click regardless of history
                            sessionStorage.setItem('chunk_error_reload', Date.now().toString());
                            window.location.href = window.location.pathname + '?v=' + Date.now();
                        }}
                        style={{
                            marginTop: '1.5rem',
                            padding: '0.8rem 1.5rem',
                            background: '#0EA5E9',
                            color: 'white',
                            border: 'none',
                            borderRadius: '999px',
                            cursor: 'pointer',
                            fontSize: '1rem',
                            fontWeight: 'bold',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                        }}
                    >
                        새로고침 (Retry) ↻
                    </button>
                    <button
                        onClick={() => this.setState({ hasError: false, error: null })}
                        style={{
                            display: 'block',
                            margin: '1rem auto',
                            background: 'none',
                            border: 'none',
                            textDecoration: 'underline',
                            color: '#666',
                            cursor: 'pointer'
                        }}
                    >
                        오류 닫기 (개발자용)
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
