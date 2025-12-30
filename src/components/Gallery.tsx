'use client';

import React, { useState } from 'react';
import { GalleryItem, MediaItem } from '@/data/dummy';
import Lightbox from '@/components/Lightbox';

import { useIntersectionObserver } from '@/hooks/useIntersectionObserver';

interface GalleryProps {
    items: GalleryItem[];
}

const GalleryItemView = ({ item, onClick }: { item: GalleryItem; onClick: (item: GalleryItem) => void }) => {
    const { elementRef, isVisible } = useIntersectionObserver();

    return (
        <div
            ref={elementRef}
            className={isVisible ? 'fade-in-up' : ''}
            onClick={() => onClick(item)}
            style={{
                position: 'relative',
                borderRadius: 'var(--radius)',
                overflow: 'hidden',
                aspectRatio: `${item.width} / ${item.height}`,
                background: 'var(--muted)',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)',
                cursor: 'pointer',
                transition: 'transform 0.2s',
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
        >
            {item.type === 'video' ? (
                <div style={{ width: '100%', height: '100%', position: 'relative', background: 'black' }}>
                    <video
                        src={item.src}
                        muted
                        playsInline
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                    <div className="play-icon">▶</div>
                </div>
            ) : (
                <img
                    src={item.src}
                    alt={item.alt}
                    style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                />
            )}

            <style jsx>{`
                .play-icon {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    color: white;
                    font-size: 2rem;
                    background: rgba(0,0,0,0.5);
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
            `}</style>
        </div>
    );
};

export default function Gallery({ items }: GalleryProps) {
    const [lightboxOpen, setLightboxOpen] = useState(false);
    const [initialIndex, setInitialIndex] = useState(0);

    const handleItemClick = (index: number) => {
        setInitialIndex(index);
        setLightboxOpen(true);
    };

    // Prepare media items for lightbox (mapping GalleryItem to MediaItem structure if needed, but Lightbox accepts MediaItem)
    // GalleryItem closely matches MediaItem but let's be explicit if needed.
    // Actually GalleryItem has type, src, alt, which matches Lightbox expectations mostly.
    // However, Lightbox expects MediaItem[], GalleryItem has width/height which are extra but fine.
    // We just need to ensure 'type' is present.
    const allMedia: MediaItem[] = items;

    return (
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '4rem 1rem' }}>
            <h2 className="section-title">
                Memories
            </h2>
            <p className="section-subtitle">
                카메라에 담긴 잊지 못할 순간들
            </p>

            <div className="masonry-grid">
                {items.map((item, index) => (
                    <div className="masonry-item" key={item.id} style={{ marginBottom: '1rem' }}>
                        <GalleryItemView item={item} onClick={() => handleItemClick(index)} />
                    </div>
                ))}
            </div>

            <Lightbox
                isOpen={lightboxOpen}
                media={allMedia}
                initialIndex={initialIndex}
                onClose={() => setLightboxOpen(false)}
            />

            <style jsx>{`
                .section-title {
                    text-align: center;
                    margin-bottom: 1rem;
                    font-size: 2.5rem;
                    color: var(--secondary);
                }
                .section-subtitle {
                    text-align: center;
                    margin-bottom: 3rem;
                    color: var(--muted-foreground);
                }

                .masonry-grid {
                    column-count: 2;
                    column-gap: 1rem;
                }

                .masonry-item {
                    break-inside: avoid;
                    margin-bottom: 1rem;
                }

                @media (min-width: 640px) {
                    .masonry-grid {
                        column-count: 3;
                    }
                }

                @media (min-width: 1024px) {
                    .masonry-grid {
                        column-count: 4;
                    }
                }
            `}</style>
        </div>
    );
}
