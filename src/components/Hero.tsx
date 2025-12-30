'use client';

import React from 'react';
// Hero & Header
export default function Hero() {
    // Background Image Slideshow
    const [currentBgIndex, setCurrentBgIndex] = React.useState(0);
    const bgImages = [
        'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1920&q=80', // Waikiki Beach (Day)
        'https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=1920&q=80', // Turtles/Ocean
        'https://images.unsplash.com/photo-1444491741275-3747c53c99b4?auto=format&fit=crop&w=1920&q=80'  // Palm Trees Sunset (Reliable)
    ];

    React.useEffect(() => {
        const interval = setInterval(() => {
            setCurrentBgIndex((prev) => (prev + 1) % bgImages.length);
        }, 7000); // Change every 7 seconds
        return () => clearInterval(interval);
    }, [bgImages.length]);

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
            backgroundColor: '#0EA5E9', // Fallback Blue (Ocean)
            marginBottom: '2rem',
            borderRadius: '0 0 var(--radius) var(--radius)',
            boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
            overflow: 'hidden'
        }}>
            {/* Background Slideshow Layers */}
            {bgImages.map((img, index) => (
                <div key={img} style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    backgroundImage: `linear-gradient(rgba(0,0,0,0.25), rgba(0,0,0,0.25)), url(${img})`,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                    opacity: currentBgIndex === index ? 1 : 0,
                    transition: 'opacity 1.5s ease-in-out',
                    zIndex: 0
                }} />
            ))}

            <h1 style={{
                fontSize: '4.5rem', /* Increased from 3.5rem */
                marginBottom: '1.5rem',
                textShadow: '0 4px 20px rgba(0,0,0,0.8)',
                lineHeight: 1.1,
                color: '#FFFFFF',
                zIndex: 1
            }}>
                도헌이 가족의<br />
                <span style={{ color: '#FFB74D', textShadow: '0 4px 20px rgba(0,0,0,0.8)' }}>하와이 대모험! 🌴</span>
            </h1>
            <p style={{
                fontSize: '1.5rem', /* Increased from 1.25rem */
                maxWidth: '700px',
                textShadow: '0 2px 10px rgba(0,0,0,0.9)',
                fontWeight: 600,
                color: '#F0F9FF',
                zIndex: 1,
                lineHeight: 1.6
            }}>
                엄마 아빠 결혼 10주년과 도헌이 생일 파티를 위한 우리 가족 여행기.<br />
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
