'use client';

import React from 'react';
import Image from 'next/image';

interface HeroProps {
    heroImages: string[];
}

// Hero & Header
export default function Hero({ heroImages = [] }: HeroProps) {
    // Background Image Slideshow
    const [currentBgIndex, setCurrentBgIndex] = React.useState(0);

    React.useEffect(() => {
        if (heroImages.length === 0) return;

        const interval = setInterval(() => {
            setCurrentBgIndex((prev) => (prev + 1) % heroImages.length);
        }, 7000); // Change every 7 seconds
        return () => clearInterval(interval);
    }, [heroImages]);

    return (
        <div style={{
            height: '60vh',
            minHeight: '400px',
            position: 'relative',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            textAlign: 'center',
            color: 'var(--primary-foreground)',
            padding: '2rem',
            marginBottom: '2rem',
            borderRadius: '0 0 var(--radius) var(--radius)',
            boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
            overflow: 'hidden',
            backgroundColor: '#0EA5E9', // Fallback
        }}>
            {/* Background Slideshow Layers with Next.js Image */}
            {heroImages.map((img, index) => (
                <div key={img} style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    opacity: currentBgIndex === index ? 1 : 0,
                    transition: 'opacity 1.5s ease-in-out',
                    zIndex: 0
                }}>
                    <Image
                        src={img}
                        alt={`Hero Background ${index + 1}`}
                        fill
                        priority={index === 0} // Prioritize the first image for LCP
                        sizes="100vw"
                        style={{
                            objectFit: 'cover',
                            objectPosition: 'center',
                        }}
                    />
                    {/* Overlay for readability */}
                    <div style={{
                        position: 'absolute',
                        inset: 0,
                        background: 'linear-gradient(rgba(0,0,0,0.25), rgba(0,0,0,0.25))',
                        zIndex: 1
                    }} />
                </div>
            ))}

            <h1 style={{
                fontSize: 'clamp(2.0rem, 6vw, 3.8rem)',
                marginBottom: '1.2rem',
                textShadow: '0 4px 20px rgba(0,0,0,0.8)',
                lineHeight: 1.1,
                color: '#FFFFFF',
                zIndex: 1
            }}>
                도헌이 가족의<br />
                <span style={{ color: '#FFB74D', textShadow: '0 4px 20px rgba(0,0,0,0.8)' }}>하와이 대모험! 🌴</span>
            </h1>
            <p style={{
                fontSize: 'clamp(1.1rem, 4vw, 1.5rem)',
                maxWidth: '700px',
                textShadow: '0 2px 10px rgba(0,0,0,0.9)',
                fontWeight: 600,
                color: '#F0F9FF',
                zIndex: 1,
                lineHeight: 1.6,
                letterSpacing: '-0.025em',
                wordBreak: 'keep-all',
                wordWrap: 'break-word',
                padding: '0 1rem' /* Add side padding for safety */
            }}>
                결혼 10주년 & 도헌이 생일 파티 여행기<br />
                진짜 멋진 물고기랑 어마어마한 파도를 봤다. 😎 🌊
            </p>
            <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', zIndex: 1 }}>
                <a href="#journal" style={{
                    background: '#0EA5E9', /* Ocean Blue */
                    color: '#FFFFFF',
                    fontSize: '1.25rem', /* Increased size */
                    padding: '1rem 2.5rem', /* Larger button */
                    borderRadius: '999px',
                    fontWeight: 700, /* Bolder text */
                    transition: 'transform 0.2s',
                    boxShadow: '0 4px 15px rgba(14, 165, 233, 0.5), 0 2px 4px rgba(0,0,0,0.1)', /* Stronger shadow */
                    textShadow: '0 1px 2px rgba(0,0,0,0.1)', /* Subtle text shadow for contrast */
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                }}
                    onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                    onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                >
                    여행 구경하기 👇
                </a>
            </div>
        </div>
    );
}
