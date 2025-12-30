'use client';

import React, { useEffect, useCallback, useState, useRef } from 'react';
import { MediaItem } from '@/data/dummy';

interface LightboxProps {
    isOpen: boolean;
    media: MediaItem[];
    initialIndex?: number;
    title?: string;
    date?: string;
    onClose: () => void;
}

export default function Lightbox({ isOpen, media, initialIndex = 0, title, date, onClose }: LightboxProps) {
    const [currentIndex, setCurrentIndex] = useState(initialIndex);
    const [progress, setProgress] = useState(0);
    const [isPaused, setIsPaused] = useState(false);
    const [isMuted, setIsMuted] = useState(true); // Start muted for autoplay policy

    // Refs
    const videoRef = useRef<HTMLVideoElement>(null);
    const progressInterval = useRef<NodeJS.Timeout | null>(null);
    const STORY_DURATION = 5000; // 5 seconds for images
    const PROGRESS_UPDATE_MS = 50;

    // Reset state when opening or changing index externally
    useEffect(() => {
        if (isOpen) {
            setCurrentIndex(initialIndex);
            setProgress(0);
            setIsPaused(false);
        }
    }, [isOpen, initialIndex]);

    // Handle navigation
    const goNext = useCallback(() => {
        if (currentIndex < media.length - 1) {
            setCurrentIndex(prev => prev + 1);
            setProgress(0);
        } else {
            onClose(); // Close if at end
        }
    }, [currentIndex, media.length, onClose]);

    const goPrev = useCallback(() => {
        if (currentIndex > 0) {
            setCurrentIndex(prev => prev - 1);
            setProgress(0);
        }
    }, [currentIndex]);

    // Auto-advance logic
    useEffect(() => {
        if (!isOpen || isPaused) return;

        const currentItem = media[currentIndex];

        // Clear existing interval
        if (progressInterval.current) clearInterval(progressInterval.current);

        if (currentItem?.type === 'video') {
            // For video, progress is handled by timeUpdate event
            if (videoRef.current) {
                videoRef.current.play().catch(() => {
                    // Autoplay failed (likely due to unmuted), try muted
                    if (!isMuted) setIsMuted(true);
                });
            }
        } else {
            // For images, use timer
            const step = 100 / (STORY_DURATION / PROGRESS_UPDATE_MS);

            progressInterval.current = setInterval(() => {
                setProgress(prev => {
                    if (prev >= 100) {
                        clearInterval(progressInterval.current!);
                        goNext();
                        return 0; // Reset for logic, though component might unmount/update
                    }
                    return prev + step;
                });
            }, PROGRESS_UPDATE_MS);
        }

        return () => {
            if (progressInterval.current) clearInterval(progressInterval.current);
        };
    }, [currentIndex, isOpen, isPaused, goNext, media, isMuted]);

    // Video specific handlers
    const handleVideoTimeUpdate = () => {
        if (videoRef.current && !isPaused) {
            const { currentTime, duration } = videoRef.current;
            if (duration > 0) {
                setProgress((currentTime / duration) * 100);
            }
        }
    };

    const handleVideoEnded = () => {
        goNext();
    };

    // Keyboard navigation
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (!isOpen) return;
            if (e.key === 'Escape') onClose();
            if (e.key === 'ArrowRight') goNext();
            if (e.key === 'ArrowLeft') goPrev();
            if (e.key === ' ') {
                setIsPaused(p => !p);
                if (videoRef.current) {
                    if (videoRef.current.paused) videoRef.current.play();
                    else videoRef.current.pause();
                }
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, goNext, goPrev, onClose]);

    if (!isOpen || !media || media.length === 0) return null;

    const currentItem = media[currentIndex];

    // Touch handlers
    const handleTouchStart = () => setIsPaused(true);
    const handleTouchEnd = () => setIsPaused(false);

    // Tap navigation regions
    const handleTap = (e: React.MouseEvent) => {
        const width = e.currentTarget.clientWidth;
        const clickX = e.nativeEvent.offsetX;

        if (clickX < width * 0.3) { // Left 30%
            goPrev();
        } else { // Right 70%
            goNext();
        }
    };

    return (
        <div className="story-overlay">
            <div
                className="story-container"
                onMouseDown={handleTouchStart}
                onMouseUp={handleTouchEnd}
                onTouchStart={handleTouchStart}
                onTouchEnd={handleTouchEnd}
            >
                {/* Progress Bars */}
                <div className="progress-container">
                    {media.map((_, idx) => (
                        <div key={idx} className="progress-bar-bg">
                            <div
                                className="progress-bar-fill"
                                style={{
                                    width: idx === currentIndex ? `${progress}%` :
                                        idx < currentIndex ? '100%' : '0%'
                                }}
                            />
                        </div>
                    ))}
                </div>

                {/* Header Info */}
                <div className="story-header">
                    <div className="story-info">
                        <span className="story-date">{date}</span>
                        <h3 className="story-title">{title}</h3>
                    </div>
                    <div className="story-controls">
                        {currentItem.type === 'video' && (
                            <button
                                className="mute-btn"
                                onClick={(e) => { e.stopPropagation(); setIsMuted(!isMuted); }}
                            >
                                {isMuted ? '🔇' : '🔊'}
                            </button>
                        )}
                        <button className="close-btn" onClick={onClose}>&times;</button>
                    </div>
                </div>

                {/* Navigation Layer (Invisible) */}
                <div className="nav-layer" onClick={handleTap} />

                {/* Media Content */}
                <div className="media-content">
                    {currentItem.type === 'video' ? (
                        <video
                            ref={videoRef}
                            src={currentItem.src}
                            className="story-media"
                            playsInline
                            muted={isMuted}
                            onTimeUpdate={handleVideoTimeUpdate}
                            onEnded={handleVideoEnded}
                        // autoPlay is handled by useEffect
                        />
                    ) : (
                        <img
                            src={currentItem.src}
                            alt={currentItem.alt || `Story ${currentIndex + 1}`}
                            className="story-media"
                        />
                    )}
                </div>
            </div>

            <style jsx>{`
                .story-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: #1a1a1a;
                    z-index: 2000;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }

                .story-container {
                    position: relative;
                    width: 100%;
                    height: 100%;
                    max-width: 500px; /* Mobile story width */
                    background: black;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                }
                
                @media (min-width: 501px) {
                     .story-container {
                        height: 90vh;
                        border-radius: 16px;
                     }
                }

                .progress-container {
                    position: absolute;
                    top: 10px;
                    left: 0;
                    width: 100%;
                    padding: 0 10px;
                    display: flex;
                    gap: 4px;
                    z-index: 2020;
                }

                .progress-bar-bg {
                    flex: 1;
                    height: 3px;
                    background: rgba(255, 255, 255, 0.3);
                    border-radius: 2px;
                    overflow: hidden;
                }

                .progress-bar-fill {
                    height: 100%;
                    background: white;
                    transition: width 0.1s linear;
                }

                .story-header {
                    position: absolute;
                    top: 24px;
                    left: 0;
                    width: 100%;
                    padding: 0 16px;
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    z-index: 2020;
                    color: white;
                    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
                }

                .story-info {
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                }

                .story-date {
                    font-size: 0.8rem;
                    opacity: 0.8;
                }

                .story-title {
                    font-size: 1rem;
                    font-weight: 600;
                    margin: 0;
                }

                .story-controls {
                    display: flex;
                    gap: 16px;
                    align-items: center;
                }

                .mute-btn, .close-btn {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 1.5rem;
                    cursor: pointer;
                    padding: 4px;
                    line-height: 1;
                    opacity: 0.8;
                }
                
                .mute-btn:hover, .close-btn:hover {
                    opacity: 1;
                }

                .nav-layer {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 2010;
                    cursor: pointer;
                }

                .media-content {
                    width: 100%;
                    height: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: black;
                }

                .story-media {
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                }
            `}</style>
        </div>
    );
}
