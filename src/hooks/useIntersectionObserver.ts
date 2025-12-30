import { useEffect, useRef, useState } from 'react';

interface UseIntersectionObserverOptions extends IntersectionObserverInit {
    triggerOnce?: boolean;
}

export function useIntersectionObserver(options?: UseIntersectionObserverOptions) {
    const elementRef = useRef<HTMLDivElement>(null);
    const [isVisible, setIsVisible] = useState(false);
    const triggerOnce = options?.triggerOnce ?? true; // Default to true

    // Use a ref to keep track of options to avoid re-running effect if options object identity changes but content is same
    // However, simplest fix for the current usage (no args) is to ensure we don't depend on a new object every time.
    // We will assume options are stable or don't change often. 
    // If 'options' is undefined, we use a local constant or just let implicit undefined work if we handle it.
    // Actually, deep comparison or JSON.stringify is safer for small options objects.

    useEffect(() => {
        const element = elementRef.current;
        if (!element) return;

        // If explicitly strictly required to support dynamic options, we should use a ref or deep compare.
        // For now, let's assume standard usage.

        const observer = new IntersectionObserver(([entry]) => {
            if (triggerOnce) {
                if (entry.isIntersecting) {
                    setIsVisible(true);
                    // Only trigger once
                    observer.unobserve(element);
                }
            } else {
                setIsVisible(entry.isIntersecting);
            }
        }, {
            threshold: 0.1,
            rootMargin: '50px',
            ...options
        });

        observer.observe(element);

        return () => {
            if (element) {
                observer.unobserve(element);
            }
            observer.disconnect();
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [JSON.stringify(options), triggerOnce]);

    return { elementRef, isVisible };
}
