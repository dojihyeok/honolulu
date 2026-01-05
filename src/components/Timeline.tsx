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
    const [isMuted, setIsMuted] = useState(true);

    // 1. Smart Preload Observer (Loads when close but not too aggressively)
    const { elementRef: preloadRef, isVisible: isClose } = useIntersectionObserver({
        threshold: 0,
        rootMargin: '800px 0px 800px 0px' // Reduced from 1200px to focus bandwidth on nearer content
    });

    // 2. Playback Observer (Plays when 40% visible)
    const { elementRef: playbackRef, isVisible: isPlayingVisible } = useIntersectionObserver({
        threshold: 0.4, // Playing starts earlier
        triggerOnce: false,
        rootMargin: '0px'
    });

    // Merge refs to attach both observers to the same element
    const setRefs = (node: HTMLDivElement | null) => {
        // Fix: useIntersectionObserver returns a RefObject, not a callback ref.
        // We must assign to .current, NOT call it as a function.
        if (playbackRef && 'current' in playbackRef) {
            // @ts-ignore
            playbackRef.current = node;
        }
        if (preloadRef && 'current' in preloadRef) {
            // @ts-ignore
            preloadRef.current = node;
        }
    };

    // Effect to safely handle play/pause based on visibility and active state
    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        if (isPlayingVisible && isActive) {
            const playPromise = video.play();
            if (playPromise !== undefined) {
                playPromise.catch(() => { });
            }
        } else {
            video.pause();
            if (!isMuted) setIsMuted(true);
        }

        return () => {
            video.pause();
        };
    }, [isPlayingVisible, isActive]);

    const toggleMute = (e: React.MouseEvent) => {
        e.stopPropagation(); // Prevent carousel navigation
        setIsMuted(!isMuted);
    };

    return (
        <div
            ref={setRefs}
            className="video-thumbnail"
            style={{
                cursor: 'pointer',
                background: '#000',
                position: 'relative',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
            }}
        >
            <video
                ref={videoRef}
                playsInline
                // @ts-ignore
                x5-playsinline="true"
                loop
                muted={isMuted}
                // Smart Preload: 'auto' when close, 'metadata' otherwise (or 'none' to save more data)
                preload={isClose ? "auto" : "metadata"}
                poster={src.replace('.mp4', '_poster.jpg')} // Instant start visual
                style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover', // Changed to cover to ensure immersive 3:4 experience
                    objectPosition: 'center', // Ensure centered content
                    display: 'block'
                }}
            >
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
    const { elementRef, isVisible } = useIntersectionObserver({
        triggerOnce: true,
        threshold: 0,
        rootMargin: '2000px 0px 2000px 0px' // Load images very early (2000px range) as they are lightweight
    });
    const [scrollIndex, setScrollIndex] = useState(0);
    const scrollContainerRef = useRef<HTMLDivElement>(null);
    const scrollTimeout = useRef<NodeJS.Timeout | null>(null);
    const [imageFits, setImageFits] = useState<Record<number, "cover" | "contain">>(
        {}
    );

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
            const { clientWidth, scrollLeft } = scrollContainerRef.current;
            const target = Math.max(scrollLeft - clientWidth, 0);
            scrollContainerRef.current.scrollTo({ left: target, behavior: 'auto' });
        }
    };

    const scrollNext = () => {
        if (scrollContainerRef.current) {
            const { clientWidth, scrollLeft, scrollWidth } = scrollContainerRef.current;
            const maxScroll = scrollWidth - clientWidth;
            const target = Math.min(scrollLeft + clientWidth, maxScroll);
            scrollContainerRef.current.scrollTo({ left: target, behavior: 'auto' });
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
            <div className="timeline-card" style={{
                background: 'var(--card)',
                borderRadius: 'var(--radius)',
                overflow: 'hidden',
                border: '1px solid var(--border)',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)'
            }}>
                <div className="timeline-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1.5rem 1.5rem 0.5rem 1.5rem' }}>
                    <span className="timeline-date">
                        {(item.media && item.media[scrollIndex] ? (item.media[scrollIndex].date || item.date) : item.date)} • {(item.media && item.media[scrollIndex] ? (item.media[scrollIndex].time || item.time) : item.time)}
                    </span>
                    {(item.media && item.media[scrollIndex] && item.media[scrollIndex].region ? item.media[scrollIndex].region : item.region) && (
                        <span className="region-badge">
                            📍 {(item.media && item.media[scrollIndex] && item.media[scrollIndex].region ? item.media[scrollIndex].region : item.region)}
                        </span>
                    )}
                </div>

                <div className="timeline-title-row">
                    <h3 className="timeline-title">{item.title}</h3>
                </div>

                <p className="timeline-desc">
                    {item.description}
                </p>

                {/* Enhanced Image/Video Layout - Always render to prevent Layout Shift. Next.js Image handles lazy loading. */}
                {displayMedia.length > 0 && (
                    <div className="carousel-container" style={{ position: 'relative' }}>
                        <div className="image-grid" ref={scrollContainerRef} onScroll={handleScroll} style={{
                            display: 'flex',
                            flexWrap: 'nowrap',
                            overflowX: 'auto',
                            scrollSnapType: 'x mandatory',
                            gap: '0',
                            width: '100%',
                            borderRadius: '4px',
                            scrollbarWidth: 'none',
                        }}>
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
                                        className="image-wrapper image-wrapper-mobile-v14"
                                        style={{
                                            position: 'relative',
                                            // height is handled by CSS (500px desktop, 3:4 aspect ratio mobile)
                                            width: '100%',
                                            overflow: 'hidden',
                                            flex: '0 0 100%',
                                            background: 'black'
                                        }}
                                    >
                                        {mediaItem.type === 'video' ? (
                                            <VideoItem
                                                src={mediaItem.src}
                                                // Active if current scroll state matches this item's real content
                                                isActive={scrollIndex === itemRealIndex}
                                            />
                                        ) : (
                                            (() => {
                                                const hasMetadata = mediaItem.width && mediaItem.height;
                                                const isWideMeta = hasMetadata ? (mediaItem.width! > mediaItem.height!) : false;

                                                // If metadata exists, use it. Otherwise fall back to state (or 'contain' initially).
                                                const currentFit = hasMetadata
                                                    ? (isWideMeta ? 'cover' : 'contain')
                                                    : (imageFits[idx] || 'contain');

                                                return (
                                                    <Image
                                                        src={mediaItem.src}
                                                        alt={mediaItem.alt || `Trip photo ${idx + 1}`}
                                                        fill
                                                        quality={75}
                                                        sizes="100vw"
                                                        unoptimized // Serve original file directly (faster if files are small)
                                                        style={{
                                                            objectFit: currentFit,
                                                            transition: 'object-fit 0.3s, transform 0.3s',
                                                            // Apply specific transform to VERTICAL (contain) images
                                                            // scale(1.4): Uniform 1.4x scaling, translateY(-8%): Top crop
                                                            transform: currentFit === 'contain' ? 'scale(1.4) translateY(-8%)' : 'none',
                                                            objectPosition: 'center',
                                                            opacity: 1 // Ensure visible
                                                        }}
                                                        priority={idx === (isInfinite ? 1 : 0)}
                                                        onLoad={(e) => {
                                                            const img = e.target as HTMLImageElement;
                                                            // Only update state if we didn't have metadata, to avoid re-renders
                                                            if (!hasMetadata) {
                                                                const isWide = img.naturalWidth > img.naturalHeight;
                                                                setImageFits(prev => ({ ...prev, [idx]: isWide ? 'cover' : 'contain' }));
                                                            }
                                                        }}
                                                    />
                                                );
                                            })()
                                        )}
                                    </div>
                                );
                            })}
                        </div>

                        {/* Navigation Arrows - Force visibility and styling inline */}
                        {itemCount > 1 && (
                            <>
                                <button
                                    onClick={(e) => { e.stopPropagation(); scrollPrev(); }}
                                    aria-label="Previous photo"
                                    className="nav-btn prev"
                                    style={{
                                        position: 'absolute',
                                        left: '10px',
                                        top: '50%',
                                        transform: 'translateY(-50%)',
                                        zIndex: 15,
                                        opacity: 1, // Always visible
                                        border: 'none',
                                        background: 'rgba(255, 255, 255, 0.8)',
                                        borderRadius: '50%',
                                        width: '30px',
                                        height: '30px',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        color: '#333',
                                        fontSize: '1.2rem'
                                    }}
                                >
                                    &#10094;
                                </button>
                                <button
                                    onClick={(e) => { e.stopPropagation(); scrollNext(); }}
                                    aria-label="Next photo"
                                    className="nav-btn next"
                                    style={{
                                        position: 'absolute',
                                        right: '10px',
                                        top: '50%',
                                        transform: 'translateY(-50%)',
                                        zIndex: 15,
                                        opacity: 1, // Always visible
                                        border: 'none',
                                        background: 'rgba(255, 255, 255, 0.8)',
                                        borderRadius: '50%',
                                        width: '30px',
                                        height: '30px',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        color: '#333',
                                        fontSize: '1.2rem'
                                    }}
                                >
                                    &#10095;
                                </button>
                            </>
                        )}

                        {/* Gradient Overlay for visibility */}
                        <div style={{
                            position: 'absolute',
                            bottom: 0,
                            left: 0,
                            width: '100%',
                            height: '80px',
                            background: 'linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 100%)',
                            zIndex: 40,
                            pointerEvents: 'none'
                        }} />

                        {/* Mobile Pagination Dots - Inline Styles */}
                        {itemCount > 1 && (
                            <div style={{
                                display: 'flex',
                                position: 'absolute',
                                bottom: '16px',
                                left: '50%',
                                transform: 'translateX(-50%)',
                                gap: '10px',
                                zIndex: 100,
                                pointerEvents: 'none',
                                background: 'transparent',
                                padding: '0',
                                borderRadius: '0',
                                backdropFilter: 'none',
                                width: 'fit-content' // Ensure it doesn't collapse
                            }}>
                                {item.media?.map((_, idx) => (
                                    <div
                                        key={idx}
                                        style={{
                                            width: '8px',
                                            height: '8px',
                                            borderRadius: '50%',
                                            background: idx === scrollIndex ? '#fff' : 'rgba(255, 255, 255, 0.4)',
                                            border: idx === scrollIndex ? 'none' : '1px solid rgba(255, 255, 255, 0.1)',
                                            transform: idx === scrollIndex ? 'scale(1.2)' : 'scale(1)',
                                            boxShadow: idx === scrollIndex ? '0 0 6px rgba(0,0,0,0.5)' : 'none',
                                            transition: 'all 0.2s',
                                            display: 'block' // Force block
                                        }}
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
                    /* height: 500px;  Removed fixed height in favor of aspect ratio */
                    aspect-ratio: 16 / 9; /* Default to 16/9 for desktop too for consistency unless overridden */
                    width: 100%;
                    min-width: 100%;
                    flex: 0 0 100%;
                    cursor: pointer;
                    overflow: hidden;
                    scroll-snap-align: center;
                    background-color: transparent; /* Transparent as requested */
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
                    overflow: hidden; /* Ensure no spillover */
                }
                .video-thumbnail video {
                    width: 100%;
                    height: 100%;
                    object-fit: cover; /* Maintain cover for immersive feel */
                    position: absolute;
                    top: 0;
                    left: 0;
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
                
                .carousel-container:hover .nav-btn {
                    opacity: 1;
                }

                .nav-btn:hover {
                    background: white;
                }

                .prev { left: 10px; }
                .next { right: 10px; }

                .gradient-overlay {
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    width: 100%;
                    height: 50px; /* Reduced from 60px */
                    background: linear-gradient(to top, rgba(0,0,0,0.4) 0%, transparent 100%);
                    z-index: 40;
                    pointer-events: none;
                }

                .mobile-dots {
                    display: flex;
                    position: absolute;
                    bottom: 12px; /* Move closer to bottom edge */
                    left: 50%;
                    transform: translateX(-50%);
                    gap: 8px;
                    z-index: 100; /* Max Z-index */
                    pointer-events: none;
                    background: transparent; /* Transparent background */
                    padding: 0; /* Remove padding */
                    border-radius: 0;
                    backdrop-filter: none; /* Remove blur */
                }
                
                .dot {
                    width: 8px; 
                    height: 8px;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.4); 
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    transition: all 0.2s;
                }
                
                .dot.active {
                    background: #fff;
                    transform: scale(1.2);
                    box-shadow: 0 0 6px rgba(0,0,0,0.5);
                    border: none;
                }

                @media (max-width: 768px) {
                    .timeline-container {
                        padding: 0 !important; /* Full bleed, no padding */
                        width: 100vw;
                        max-width: 100vw;
                        overflow-x: hidden; /* Prevent horizontal scroll */
                    }
                    /* Add padding back to title since container lost it */
                    .timeline-container :global(h2) {
                        padding: 2rem 1rem 1rem 1rem;
                        font-size: 1.5rem !important; /* Slightly smaller for mobile */
                    }
                    /* Mobile Specific Overrides - High Specificity */
                    div.image-wrapper.image-wrapper-mobile-v14 {
                        width: 100vw !important;
                        max-width: 100vw !important;
                        flex: 0 0 100vw !important;
                        
                        aspect-ratio: 16 / 10.5 !important; /* Increase width relative to height (wider than 16/11) */
                        height: auto !important;
                        min-height: auto !important;
                        
                        background-color: transparent !important;
                        overflow: hidden;
                        position: relative;
                        margin: 0 !important;
                        padding: 0 !important;
                    }
                    .image-wrapper img, .image-wrapper-mobile-v14 img {
                        /* object-fit handled inline via JS */
                        position: absolute !important;
                        top: 0;
                        left: 0;
                        width: 100% !important;
                        height: 100% !important;
                    }
                    /* Ensure video also covers the 3:4 area */
                    /* Target video thumbnail specifically */
                     div.image-wrapper.image-wrapper-mobile-v14 :global(.video-thumbnail) {
                        position: absolute !important;
                        top: 0;
                        left: 0;
                        width: 100% !important;
                        height: 100% !important;
                        z-index: 1;
                    }
                    div.image-wrapper.image-wrapper-mobile-v14 :global(video) {
                         object-fit: cover !important;
                         width: 100% !important;
                         height: 100% !important;
                         position: absolute !important;
                         top: 0;
                         left: 0;
                    }

                    .timeline-card {
                        border-radius: 0; 
                        box-shadow: none;
                        border: none; /* completely remove border for clean look */
                        margin-bottom: 2rem; /* Add space between episodes */
                    }
                    .timeline-title {
                        font-size: 1.5rem;
                        word-break: keep-all;
                        padding: 0 1rem;
                        margin-bottom: 0.5rem;
                    }
                    .timeline-header {
                        padding: 1rem 1rem 0.5rem 1rem; /* tighter padding */
                    }
                    .timeline-desc {
                        display: none;
                    }
                }
            `}</style>
        </div >
    );
};

export default function Timeline({ items }: TimelineProps) {
    return (
        <div className="timeline-container" style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>
            <h2 className="section-title" style={{ textAlign: 'center', marginBottom: '2rem', fontSize: '2rem', color: 'var(--secondary)', wordBreak: 'keep-all' }}>
                Travel Episodes
            </h2>

            <div style={{ position: 'relative', border: '1px solid transparent' }}>
                <style dangerouslySetInnerHTML={{
                    __html: `
                    .gradient-overlay {
                        position: absolute;
                        bottom: 0;
                        left: 0;
                        width: 100%;
                        height: 80px;
                        background: linear-gradient(to top, rgba(0,0,0,0.6) 0%, transparent 100%);
                        z-index: 40;
                        pointer-events: none;
                        display: block !important;
                        content: '';
                    }
                    .mobile-dots {
                        display: flex !important;
                        position: absolute;
                        bottom: 12px;
                        left: 50%;
                        transform: translateX(-50%);
                        gap: 10px;
                        z-index: 100;
                        pointer-events: none;
                        background: transparent;
                        padding: 0;
                        border-radius: 0;
                        backdrop-filter: none;
                        opacity: 1 !important;
                        visibility: visible !important;
                        height: auto !important;
                    }
                    .dot {
                        width: 8px !important;
                        height: 8px !important;
                        border-radius: 50% !important;
                        background: rgba(255, 255, 255, 0.4);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        transition: all 0.2s;
                        display: block !important;
                    }
                    .dot.active {
                        background: #fff !important;
                        transform: scale(1.2);
                        box-shadow: 0 0 6px rgba(0,0,0,0.5);
                        border: none;
                    }
                `}} />
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
                    padding: 4rem 1.5rem; /* Default Desktop Padding */
                }
                @media (max-width: 768px) {
                    .timeline-container {
                        padding: 2rem 0 !important; /* Full width on mobile */
                    }
                    /* Add padding back to title since container lost it */
                    .timeline-container :global(h2) {
                        padding: 0 1rem;
                    }
                }
            `}</style>
        </div>
    );
}
