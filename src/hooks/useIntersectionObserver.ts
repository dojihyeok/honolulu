import { useRef, useState, useEffect } from 'react';

interface UseIntersectionObserverOptions extends IntersectionObserverInit {
    triggerOnce?: boolean;
}

export function useIntersectionObserver(options?: UseIntersectionObserverOptions) {
    const elementRef = useRef<HTMLDivElement>(null);
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const element = elementRef.current;
        if (!element) return;

        // Fallback for browsers without IntersectionObserver support
        if (!window.IntersectionObserver) {
            setIsVisible(true);
            return;
        }

        const observer = new IntersectionObserver(([entry]) => {
            // Trigger deeply before element enters viewport (1200px buffer)
            if (entry.isIntersecting) {
                setIsVisible(true);
                if (options?.triggerOnce) {
                    observer.unobserve(element);
                }
            } else if (!options?.triggerOnce) {
                // Only hide if we explicitly want to toggle visibility (e.g. video playback auto-pause)
                setIsVisible(false);
            }
        }, {
            threshold: 0, // Trigger as soon as 1 pixel is within the margin
            rootMargin: options?.rootMargin || '600px 0px', // Moderate pre-loading buffer (approx 1 screen height)
            ...options
        });

        observer.observe(element);

        return () => {
            if (element) observer.unobserve(element);
        };
    }, [options?.triggerOnce, options?.threshold, options?.rootMargin]);

    return { elementRef, isVisible };
}
