import { useRef, useState, useEffect } from 'react';

interface UseIntersectionObserverOptions extends IntersectionObserverInit {
    triggerOnce?: boolean;
}

export function useIntersectionObserver(options?: UseIntersectionObserverOptions) {
    // NUCLEAR FIX: Always return visible to ensure content renders.
    // We are bypassing the IntersectionObserver entirely to rule it out as the cause of invisibility.
    const elementRef = useRef<HTMLDivElement>(null);
    const [isVisible, setIsVisible] = useState(true);

    useEffect(() => {
        setIsVisible(true);
    }, []);

    return { elementRef, isVisible };
}
