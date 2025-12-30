'use client';

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { TimelineItem } from '@/data/dummy';
import L from 'leaflet';

// Fix Leaflet's default icon path issues in React
// @ts-expect-error: Leaflet's default icon path issue
delete L.Icon.Default.prototype._getIconUrl;

const DefaultIcon = L.icon({
    iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface TravelMapProps {
    items: TimelineItem[];
    selectedId?: string;
}

// Component to handle map center changes
function ChangeView({ center }: { center: [number, number] }) {
    const map = useMap();
    useEffect(() => {
        map.flyTo(center, 13);
    }, [center, map]);
    return null;
}

export default function TravelMap({ items, selectedId }: TravelMapProps) {
    // Default center (Honolulu)
    const defaultCenter: [number, number] = [21.3069, -157.8583];

    // Find selected item location or keep default
    const selectedItem = items.find(item => item.id === selectedId);
    const center = selectedItem?.location
        ? [selectedItem.location.lat, selectedItem.location.lng] as [number, number]
        : defaultCenter;

    return (
        <div style={{ width: '100%', height: '100%', borderRadius: 'var(--radius)', overflow: 'hidden' }}>
            <MapContainer
                center={defaultCenter}
                zoom={11}
                style={{ height: '100%', width: '100%' }}
                scrollWheelZoom={false}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />

                {items.map((item) => (
                    item.location && (
                        <Marker
                            key={item.id}
                            position={[item.location.lat, item.location.lng]}
                        >
                            <Popup>
                                <strong>{item.title}</strong><br />
                                {item.date} {item.time}
                            </Popup>
                        </Marker>
                    )
                ))}

                <ChangeView center={center} />
            </MapContainer>
        </div>
    );
}
