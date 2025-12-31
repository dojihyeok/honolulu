'use client';

import React from 'react';
import Timeline from '@/components/Timeline';
import { REAL_TIMELINE } from '@/data/real';
// Map removed as per user request

export default function TravelJournal() {
  return (
    <div className="journal-container relative">
      {/* Timeline Section */}
      <div className="timeline-section">
        <Timeline
          items={REAL_TIMELINE}
        />
      </div>

      <style jsx>{`
        .journal-container {
            max-width: 800px; /* Centered single column */
            margin: 0 auto;
            position: relative;
        }

        /* Timeline Area */
        .timeline-section {
            width: 100%;
            background: var(--background);
            z-index: 10;
        }
      `}</style>
    </div>
  );
}
