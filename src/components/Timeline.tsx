'use client';

import React, { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import { TimelineItem, MediaItem } from '@/data/dummy';
import { useIntersectionObserver } from '@/hooks/useIntersectionObserver';

interface TimelineProps {
    items: TimelineItem[];
}

// ---------------------------------------------------------------------------
// VideoItem Component: Handles safe video playback & mute state
// ---------------------------------------------------------------------------
interface VideoItemProps {
    src: string;
    isActive: boolean;  // Is this specific slide currently active/centered?
    isVisible: boolean; // Is the parent card currently visible in viewport?
    isMuted: boolean;
    onToggleMute: () => void;
}

const VideoItem = ({ src, isActive, isVisible, isMuted, onToggleMute }: VideoItemProps) => {
    const videoRef = useRef<HTMLVideoElement>(null);

    // Effect to safely handle play/pause based on props
    // This avoids the "play() failed because the user didn't interact" error spam locally
    // And prevents the "ref callback" crash on rapid state updates
    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        // If card is visible and this slide is active, try to play
        if (isVisible && isActive) {
            // Mute state must be set before play for autoplay policies
            video.muted = isMuted;

            const playPromise = video.play();
            if (playPromise !== undefined) {
                playPromise.catch((error) => {
                    // Autoplay was prevented or suppressed.
                    // This is expected in many browsers if not muted.
                    // console.warn("Autoplay prevent:", error);
                });
            }
        } else {
            // Otherwise pause to save resources
            video.pause();
        }
    }, [isVisible, isActive, isMuted]);

    // Also sync muted property directly
    useEffect(() => {
        if (videoRef.current) {
            videoRef.current.muted = isMuted;
        }
    }, [isMuted]);

    return (
        <div
            className="video-thumbnail"
            onClick={(e) => {
                e.stopPropagation();
                onToggleMute();
            }}
            style={{ cursor: 'pointer' }}
        >
            <video
                ref={videoRef}
                src={src}
                playsInline
                loop
                muted={isMuted} // React prop for initial render
                preload="metadata"
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            />
            <div className="mute-indicator">
                {isMuted ? '🔇' : '🔊'}
            </div>
        </div>
    );
};

// ---------------------------------------------------------------------------
// TimelineItemView Component
// ---------------------------------------------------------------------------
const TimelineItemView = ({ item }: { item: TimelineItem }) => {
    const { elementRef, isVisible } = useIntersectionObserver({ triggerOnce: false });
    const [scrollIndex, setScrollIndex] = useState(0);
    // Key: index, Value: isMuted boolean (default true if undefined)
    const [mutedStates, setMutedStates] = useState<Record<number, boolean>>({});

    const scrollContainerRef = useRef<HTMLDivElement>(null);

    const handleScroll = () => {
        if (scrollContainerRef.current) {
            const { scrollLeft, clientWidth } = scrollContainerRef.current;
            const index = Math.round(scrollLeft / clientWidth);
            setScrollIndex(index);
        }
    };

    const scrollPrev = () => {
        if (scrollContainerRef.current) {
            const { scrollLeft, clientWidth, scrollWidth } = scrollContainerRef.current;
            if (scrollLeft <= 10) { // At start, loop to end
                scrollContainerRef.current.scrollTo({ left: scrollWidth, behavior: 'smooth' });
            } else {
                scrollContainerRef.current.scrollBy({ left: -clientWidth, behavior: 'smooth' });
            }
        }
    };

    const scrollNext = () => {
        if (scrollContainerRef.current) {
            const { scrollLeft, clientWidth, scrollWidth } = scrollContainerRef.current;
            // Tolerance to detect end
            if (scrollLeft + clientWidth >= scrollWidth - 10) { // At end, loop to start
                scrollContainerRef.current.scrollTo({ left: 0, behavior: 'smooth' });
            } else {
                scrollContainerRef.current.scrollBy({ left: clientWidth, behavior: 'smooth' });
            }
        }
    };

    const toggleMute = (idx: number) => {
        setMutedStates(prev => {
            const currentMuted = prev[idx] ?? true; // Default to muted
            return {
                ...prev,
                [idx]: !currentMuted
            };
        });
    };

    return (
        <div
            ref={elementRef}
            className={isVisible ? 'fade-in-up' : ''}
            style={{ marginBottom: '4rem', position: 'relative' }}
        >
            {/* Content Card */}
            <div className="timeline-card">
                <div className="timeline-header">
                    <span className="timeline-date">
                        {item.date} • {item.time}
                    </span>
                    {item.region && (
                        <span className="region-badge">
                            📍 {item.region}
                        </span>
                    )}
                </div>

                <div className="timeline-title-row">
                    <h3 className="timeline-title">{item.title}</h3>
                </div>

                <p className="timeline-desc">
                    {item.description}
                </p>

                {/* Enhanced Image/Video Layout - Lazy Loaded */}
                {isVisible && item.media && item.media.length > 0 && (
                    <div className="carousel-container" style={{ position: 'relative' }}>
                        <div className="image-grid" ref={scrollContainerRef} onScroll={handleScroll}>
                            {item.media.map((mediaItem, idx) => (
                                <div
                                    key={idx}
                                    className="image-wrapper"
                                >
                                    {mediaItem.type === 'video' ? (
                                        <VideoItem
                                            src={mediaItem.src}
                                            isActive={idx === scrollIndex}
                                            isVisible={isVisible}
                                            isMuted={mutedStates[idx] ?? true}
                                            onToggleMute={() => toggleMute(idx)}
                                        />
                                    ) : (
                                        <Image
                                            src={mediaItem.src}
                                            alt={mediaItem.alt || `Trip photo ${idx + 1}`}
                                            fill
                                            sizes="(max-width: 768px) 100vw, 800px"
                                            quality={50}
                                            style={{ objectFit: 'cover' }}
                                        />
                                    )}
                                </div>
                            ))}
                        </div>

                        {/* Navigation Arrows */}
                        {item.media.length > 1 && (
                            <>
                                <button
                                    className="nav-btn prev visible"
                                    onClick={(e) => { e.stopPropagation(); scrollPrev(); }}
                                    aria-label="Previous photo"
                                >
                                    &#10094;
                                </button>
                                <button
                                    className="nav-btn next visible"
                                    onClick={(e) => { e.stopPropagation(); scrollNext(); }}
                                    aria-label="Next photo"
                                >
                                    &#10095;
                                </button>
                            </>
                        )}

                        {/* Mobile Pagination Dots */}
                        {item.media.length > 1 && (
                            <div className="mobile-dots">
                                {item.media.map((_, idx) => (
                                    <div
                                        key={idx}
                                        className={`dot ${idx === scrollIndex ? 'active' : ''}`}
                                    />
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>

            <style jsx>{`
                .timeline-card {
                    background: var(--card);
                    border-radius: var(--radius);
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                    border: 1px solid var(--border);
                    overflow: hidden;
                }

                .timeline-header {
                    padding: 1.5rem 1.5rem 0.5rem 1.5rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    flex-wrap: wrap;
                    gap: 0.5rem;
                }

                .timeline-date {
                    font-size: 1.1rem; /* Increased from 0.875rem */
                    font-weight: 600;
                    color: var(--primary);
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }

                .region-badge {
                    font-size: 1rem;
                    font-weight: 700;
                    color: #fff;
                    background: #F59E0B; /* More vivid amber/orange */
                    padding: 0.4rem 1rem;
                    border-radius: 999px;
                    border: none;
                    box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
                    display: inline-flex;
                    align-items: center;
                    gap: 0.3rem;
                }

                .timeline-title-row {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    padding-right: 1.5rem;
                }

                .timeline-title {
                    padding: 0 1.5rem; /* Remove right padding handled by row */
                    padding-right: 0.5rem;
                    font-size: 2rem; /* Increased from 1.5rem */
                    margin-bottom: 0.75rem;
                    flex: 1;
                    line-height: 1.3;
                }

                .timeline-desc {
                    padding: 0 1.5rem 1rem 1.5rem;
                    color: var(--muted-foreground);
                    font-size: 1.15rem; 
                    line-height: 1.6;
                    margin-bottom: 0;
                    word-break: keep-all; /* Prevent awkward word breaks */
                    overflow-wrap: break-word;
                }

                /* Universal Image Carousel Styles */
                .image-grid {
                    display: flex;
                    flex-wrap: nowrap;
                    overflow-x: auto;
                    scroll-snap-type: x mandatory;
                    gap: 0;
                    width: 100%;
                    border-radius: 4px;
                    
                    /* Hide scrollbar */
                    -ms-overflow-style: none;
                    scrollbar-width: none;
                }
                .image-grid::-webkit-scrollbar { display: none; }

                .image-wrapper {
                    position: relative;
                    height: 500px; /* Default Desktop Height */
                    min-width: 100%;
                    flex: 0 0 100%;
                    cursor: pointer;
                    overflow: hidden;
                    scroll-snap-align: center;
                }

                .image-wrapper img {
                    width: 100%;
                    height: 100%;
                    object-fit: cover; /* Instagram-like crop */
                    transition: transform 0.3s ease;
                }

                .video-thumbnail {
                    width: 100%;
                    height: 100%;
                    position: relative;
                    background: black;
                }
                
                .mute-indicator {
                    position: absolute;
                    bottom: 10px;
                    right: 10px;
                    background: rgba(0,0,0,0.6);
                    color: white;
                    border-radius: 50%;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 0.9rem;
                    pointer-events: none;
                }
                
                /* Navigation Buttons */
                .nav-btn {
                    position: absolute;
                    top: 50%;
                    transform: translateY(-50%);
                    background: rgba(255, 255, 255, 0.8);
                    border: none;
                    border-radius: 50%;
                    width: 30px;
                    height: 30px;
                    font-size: 1.2rem;
                    color: #333;
                    cursor: pointer;
                    z-index: 15;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    opacity: 0; 
                    transition: opacity 0.2s, background 0.2s;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }
                
                .carousel-container:hover .nav-btn.visible {
                    opacity: 1;
                }

                .nav-btn:hover {
                    background: white;
                }

                .prev { left: 10px; }
                .next { right: 10px; }

                .mobile-dots {
                    display: flex;
                    position: absolute;
                    bottom: 15px;
                    left: 50%;
                    transform: translateX(-50%);
                    gap: 6px;
                    z-index: 20;
                    pointer-events: none;
                }
                
                .dot {
                    width: 6px;
                    height: 6px;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.4);
                    transition: all 0.2s;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.3);
                }
                
                .dot.active {
                    background: white;
                    transform: scale(1.2);
                    box-shadow: 0 1px 3px rgba(0,0,0,0.5);
                }

                @media (max-width: 768px) {
                    .image-wrapper {
                        height: 400px;
                    }
                    .timeline-card {
                        border-radius: 0; 
                        box-shadow: none;
                        border-left: none;
                        border-right: none;
                    }
                    .timeline-title {
                        font-size: 1.75rem;
                         word-break: keep-all;
                    }
                }
            `}</style>
        </div>
    );
};

export default function Timeline({ items }: TimelineProps) {
    return (
        <div className="timeline-container">
            <h2 style={{ textAlign: 'center', marginBottom: '2rem', fontSize: '2rem', color: 'var(--secondary)', wordBreak: 'keep-all' }}>
                Travel Schedule
            </h2>

            <div style={{ position: 'relative' }}>
                {items.map((item) => (
                    <TimelineItemView
                        key={item.id}
                        item={item}
                    />
                ))}
            </div>

            <style jsx>{`
                .timeline-container {
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 4rem 1.5rem;
                }
                @media (max-width: 768px) {
                    .timeline-container {
                        padding: 2rem 0.5rem; /* Reduce padding significantly on mobile */
                    }
                }
            `}</style>
        </div>
    );
}
