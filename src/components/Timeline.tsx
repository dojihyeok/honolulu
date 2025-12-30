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
// ---------------------------------------------------------------------------
// VideoItem Component: Handles safe video playback & mute state
// ---------------------------------------------------------------------------
interface VideoItemProps {
    src: string;
    isActive: boolean;  // Is this specific slide currently active/centered?
}

const VideoItem = ({ src, isActive }: VideoItemProps) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const { elementRef, isVisible } = useIntersectionObserver({ threshold: 0.5, triggerOnce: false });
    const [isMuted, setIsMuted] = useState(true); // Default to muted for autoplay support

    // Effect to safely handle play/pause based on visibility and active state
    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        // Play if:
        // 1. The video element is visible in viewport (>50%)
        // 2. It is the active slide in the carousel
        if (isVisible && isActive) {
            // video.muted = isMuted; // React prop handles this, but explicit sync can be safer
            const playPromise = video.play();
            if (playPromise !== undefined) {
                playPromise.catch(() => {
                    // Autoplay prevented (usually shouldn't happen if muted)
                });
            }
        } else {
            video.pause();
            if (!isMuted) setIsMuted(true); // Reset to muted if it was playing sound
        }

        // Cleanup function to ensure pause on unmount
        return () => {
            video.pause();
        };
    }, [isVisible, isActive]);

    const toggleMute = (e: React.MouseEvent) => {
        e.stopPropagation(); // Prevent carousel navigation
        setIsMuted(!isMuted);
    };

    return (
        <div
            ref={elementRef}
            className="video-thumbnail"
            style={{
                cursor: 'pointer',
                background: '#000',
                position: 'relative'
            }}
        >
            <video
                ref={videoRef}
                playsInline
                // @ts-ignore
                x5-playsinline="true"
                loop
                muted={isMuted}
                preload="metadata" // Load metadata immediately for fast start
                style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'contain',
                    display: 'block'
                }}
            >
                <source src={src.replace('.mp4', '_mobile.mp4')} media="(max-width: 768px)" type="video/mp4" />
                <source src={src} type="video/mp4" />
            </video>

            {/* Volume Toggle Button */}
            <button
                onClick={toggleMute}
                className="volume-btn"
                aria-label={isMuted ? "Unmute" : "Mute"}
            >
                {isMuted ? (
                    // Muted Icon
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                        <path d="M13.5 4.06c0-1.336-1.616-2.005-2.56-1.06l-4.5 4.5H4.508c-1.141 0-2.318.664-2.66 1.905A9.76 9.76 0 001.5 12c0 .898.121 1.768.35 2.595.341 1.24 1.518 1.905 2.659 1.905h1.93l4.5 4.5c.945.945 2.561.276 2.561-1.06V4.06zM18.529 3.029a.75.75 0 011.06 0A13.98 13.98 0 0124 12c0 3.691-1.42 7.056-3.712 9.734a.75.75 0 01-1.096-.98A12.48 12.48 0 0022.5 12c0-3.297-1.27-6.304-3.321-8.697a.75.75 0 01-1.096-.98z" />
                        <path d="M8.25 19.5v-15L4.5 9h-2v6h2l3.75 4.5z" />
                        <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 8.25L21 12m0 0l-3.75 3.75M21 12H9" opacity="0.5" />
                        <line x1="1" y1="1" x2="23" y2="23" stroke="currentColor" strokeWidth="2" />
                    </svg>
                ) : (
                    // Unmuted Icon (Speaker Wave)
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                        <path d="M13.5 4.06c0-1.336-1.616-2.005-2.56-1.06l-4.5 4.5H4.508c-1.141 0-2.318.664-2.66 1.905A9.76 9.76 0 001.5 12c0 .898.121 1.768.35 2.595.341 1.24 1.518 1.905 2.659 1.905h1.93l4.5 4.5c.945.945 2.561.276 2.561-1.06V4.06zM17.78 9.22a.75.75 0 10-1.06 1.06L18.44 12l-1.72 1.72a.75.75 0 101.06 1.06l1.72-1.72 1.72 1.72a.75.75 0 101.06-1.06L20.56 12l1.72-1.72a.75.75 0 10-1.06-1.06l-1.72 1.72-1.72-1.72z" />
                    </svg>
                )}
            </button>
            <style jsx>{`
                .volume-btn {
                    position: absolute;
                    bottom: 15px;
                    right: 15px;
                    background: rgba(0, 0, 0, 0.6);
                    border: none;
                    border-radius: 50%;
                    width: 36px;
                    height: 36px;
                    padding: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    color: white;
                    z-index: 10;
                    transition: transform 0.2s, background 0.2s;
                    backdrop-filter: blur(4px);
                }
                .volume-btn:active {
                    transform: scale(0.95);
                    background: rgba(0, 0, 0, 0.8);
                }
                .volume-btn svg {
                    width: 100%;
                    height: 100%;
                }
            `}</style>
        </div>
    );
};

// ---------------------------------------------------------------------------
// TimelineItemView Component
// ---------------------------------------------------------------------------
const TimelineItemView = ({ item }: { item: TimelineItem }) => {
    // TRIGGER ONCE: TRUE -> Keeps the component mounted after first load
    // This prevents "Layout Thrashing" and scroll stutter on mobile
    const { elementRef, isVisible } = useIntersectionObserver({ triggerOnce: true, threshold: 0.1 });
    const [scrollIndex, setScrollIndex] = useState(0);
    const scrollContainerRef = useRef<HTMLDivElement>(null);
    const scrollTimeout = useRef<NodeJS.Timeout | null>(null);

    // Infinite Loop: Clone last item to start AND first item to end for bidirectional loop
    const itemCount = item.media?.length || 0;
    const isInfinite = itemCount > 1;

    // [Clone Last, ...Real Items, Clone First]
    const displayMedia = isInfinite
        ? [item.media![itemCount - 1], ...(item.media || []), item.media![0]]
        : (item.media || []);

    // Initial Scroll Position (Start at Index 1, which is the first REAL item)
    useEffect(() => {
        if (isInfinite && isVisible && scrollContainerRef.current) {
            const { clientWidth } = scrollContainerRef.current;
            // Immediate jump to show the first real item (Index 1) instead of the clone (Index 0)
            scrollContainerRef.current.scrollTo({ left: clientWidth, behavior: 'auto' });
        }
    }, [isVisible, isInfinite]);

    const handleScroll = () => {
        if (scrollContainerRef.current) {
            const { scrollLeft, clientWidth } = scrollContainerRef.current;
            if (clientWidth === 0) return;

            const index = Math.round(scrollLeft / clientWidth);

            // Normalize index for dots (Virtual Index 1..N -> Real Index 0..N-1)
            // If Index 0 (Clone Last) -> Real Index N-1
            // If Index N+1 (Clone First) -> Real Index 0
            let realIndex = index - 1;
            if (realIndex < 0) realIndex = itemCount - 1;
            if (realIndex >= itemCount) realIndex = 0;

            setScrollIndex(realIndex);

            // Infinite Loop Reset Logic
            if (isInfinite) {
                if (scrollTimeout.current) clearTimeout(scrollTimeout.current);

                // Use simple timeout to debounce the reset check till after scroll settles
                scrollTimeout.current = setTimeout(() => {
                    if (!scrollContainerRef.current) return;

                    // Re-measure in case of resize
                    const currentScroll = scrollContainerRef.current.scrollLeft;
                    const currentWidth = scrollContainerRef.current.clientWidth;
                    const currentIndex = Math.round(currentScroll / currentWidth);

                    // Case A: Scrolled to Index 0 (Clone of Last) -> Jump to Real Last (Index N)
                    if (currentIndex === 0) {
                        scrollContainerRef.current.scrollTo({
                            left: itemCount * currentWidth,
                            behavior: 'auto' // Instant jump
                        });
                    }
                    // Case B: Scrolled to Index N+1 (Clone of First) -> Jump to Real First (Index 1)
                    else if (currentIndex === itemCount + 1) {
                        scrollContainerRef.current.scrollTo({
                            left: currentWidth,
                            behavior: 'auto' // Instant jump
                        });
                    }
                }, 500); // Wait for scroll animation to finish
            }
        }
    };

    const scrollPrev = () => {
        if (scrollContainerRef.current) {
            const { clientWidth } = scrollContainerRef.current;
            // Just scroll left. If we hit Index 0 (Clone), handleScroll will reset us to Index N.
            scrollContainerRef.current.scrollBy({ left: -clientWidth, behavior: 'smooth' });
        }
    };

    const scrollNext = () => {
        if (scrollContainerRef.current) {
            const { clientWidth } = scrollContainerRef.current;
            // Just scroll right. If we hit Index N+1 (Clone), handleScroll will reset us to Index 1.
            scrollContainerRef.current.scrollBy({ left: clientWidth, behavior: 'smooth' });
        }
    };

    return (
        <div
            ref={elementRef}
            className="timeline-item-view"
            style={{
                marginBottom: '4rem',
                position: 'relative',
                minHeight: '200px',
                containIntrinsicSize: '500px'
            }}
        >
            {/* Content Card - Always rendered and visible */}
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

                {/* Enhanced Image/Video Layout - Always rendered once parent is visible */}
                {displayMedia.length > 0 && (
                    <div className="carousel-container" style={{ position: 'relative' }}>
                        <div className="image-grid" ref={scrollContainerRef} onScroll={handleScroll}>
                            {displayMedia.map((mediaItem, idx) => {
                                // Calculate which "Real Index" (0..N-1) this item represents
                                let itemRealIndex = idx;
                                if (isInfinite) {
                                    if (idx === 0) itemRealIndex = itemCount - 1; // Clone of Last
                                    else if (idx === itemCount + 1) itemRealIndex = 0; // Clone of First
                                    else itemRealIndex = idx - 1; // Real items shifted by 1
                                }

                                return (
                                    <div
                                        key={idx}
                                        className="image-wrapper"
                                    >
                                        {mediaItem.type === 'video' ? (
                                            <VideoItem
                                                src={mediaItem.src}
                                                // Active if current scroll state matches this item's real content
                                                isActive={scrollIndex === itemRealIndex}
                                            />
                                        ) : (
                                            <Image
                                                src={mediaItem.src}
                                                alt={mediaItem.alt || `Trip photo ${idx + 1}`}
                                                fill
                                                sizes="(max-width: 768px) 100vw, 800px"
                                                style={{ objectFit: 'cover' }}
                                                priority={idx === 0} // Prioritize first image
                                            />
                                        )}
                                    </div>
                                );
                            })}
                        </div>

                        {/* Navigation Arrows */}
                        {itemCount > 1 && (
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
                        {itemCount > 1 && (
                            <div className="mobile-dots">
                                {item.media?.map((_, idx) => (
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
                    -webkit-overflow-scrolling: touch; /* Smooth scrolling for iOS */
                    
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
        </div >
    );
};

export default function Timeline({ items }: TimelineProps) {
    return (
        <div className="timeline-container">
            <h2 style={{ textAlign: 'center', marginBottom: '2rem', fontSize: '2rem', color: 'var(--secondary)', wordBreak: 'keep-all' }}>
                Travel Episodes
            </h2>

            <div style={{ position: 'relative', border: '1px solid transparent' }}>
                {items.length === 0 && (
                    <div style={{ padding: '2rem', textAlign: 'center', fontSize: '1.5rem', color: 'red' }}>
                        데이터가 없습니다 (0 items)
                    </div>
                )}
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
