export type MediaType = 'image' | 'video';

export type MediaItem = {
    type: MediaType;
    src: string;
    alt?: string;
    width?: number; // Optional for timeline, required for gallery usually
    height?: number;
};

export type TimelineItem = {
    id: string;
    date: string;
    time: string;
    title: string;
    description: string;
    tags?: string[];
    media?: MediaItem[];
    region?: string; // e.g. 'Waikiki', 'North Shore'
    location?: { lat: number; lng: number };
};

export type GalleryItem = {
    id: string;
    type: MediaType;
    src: string;
    alt: string;
    width: number;
    height: number;
};

// Real-like placeholder images from Unsplash Source
const IMAGES = {
    airport: 'https://images.unsplash.com/photo-1542296332-2e44a996aa0d?auto=format&fit=crop&w=400&q=80',
    waikiki: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=400&q=80',
    sunset: 'https://images.unsplash.com/photo-1616036740257-230eb19890ba?auto=format&fit=crop&w=400&q=80',
    palace: 'https://images.unsplash.com/photo-1596207106096-7e923e354784?auto=format&fit=crop&w=400&q=80',
    poke: 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=400&q=80',
    diamondHead: 'https://images.unsplash.com/photo-1621539209706-5b4369e57833?auto=format&fit=crop&w=400&q=80',
    turtle: 'https://images.unsplash.com/photo-1437622368342-7a3d73a34c8f?auto=format&fit=crop&w=400&q=80',
    drive: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=400&q=80',
    kualoa: 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=400&q=80',
    northShore: 'https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=400&q=80',
    pineapple: 'https://images.unsplash.com/photo-1589606663952-2b9ef5e6ba63?auto=format&fit=crop&w=400&q=80',
    shopping: 'https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=400&q=80',
};

// Helper to wrap image string as MediaItem
const img = (src: string): MediaItem => ({ type: 'image', src });

export const DUMMY_TIMELINE: TimelineItem[] = [
    // Day 1: 도착 & 와이키키
    {
        id: '1',
        date: 'Day 1',
        time: '14:00',
        title: 'Honolulu 공항 도착',
        description: '따뜻한 공기와 함께 하와이에 도착했다. 렌트카 픽업 완료!',
        tags: ['Airport', 'Start'],
        location: { lat: 21.3187, lng: -157.9225 }, // HNL Airport
        media: [img(IMAGES.airport)]
    },
    {
        id: '2',
        date: 'Day 1',
        time: '17:00',
        title: 'Waikiki 해변 체크인',
        description: '호텔 체크인 후 바로 해변으로. 석양이 너무 아름답다.',
        tags: ['Waikiki', 'Sunset'],
        location: { lat: 21.2762, lng: -157.8270 }, // Waikiki Beach
        media: [img(IMAGES.sunset), img(IMAGES.waikiki)]
    },

    // Day 2: 다운타운 & 맛집
    {
        id: '3',
        date: 'Day 2',
        time: '10:00',
        title: 'Iolani Palace 투어',
        description: '미국 유일의 궁전. 하와이 왕조의 역사를 듣다.',
        tags: ['History', 'Culture'],
        location: { lat: 21.3069, lng: -157.8583 }, // Iolani Palace
        media: [img(IMAGES.palace)]
    },
    {
        id: '4',
        date: 'Day 2',
        time: '13:00',
        title: '나만의 포케 맛집 찾기',
        description: '현지인들이 추천하는 로컬 포케집. 참치가 입에서 녹는다.',
        tags: ['Food', 'Poke'],
        location: { lat: 21.2969, lng: -157.8560 }, // Somewhere in Honolulu
        media: [img(IMAGES.poke)]
    },

    // Day 3: 다이아몬드 헤드
    {
        id: '5',
        date: 'Day 3',
        time: '06:00',
        title: 'Diamond Head 일출 하이킹',
        description: '새벽같이 일어나 정상에 올랐다. 와이키키 전경이 한눈에!',
        tags: ['Hiking', 'Sunrise'],
        location: { lat: 21.2620, lng: -157.8060 }, // Diamond Head
        media: [img(IMAGES.diamondHead)]
    },

    // Day 4: 하나우마 베이
    {
        id: '6',
        date: 'Day 4',
        time: '08:00',
        title: 'Hanauma Bay 스노클링',
        description: '물반 고기반. 거북이를 드디어 만났다!',
        tags: ['Snorkeling', 'Turtle'],
        location: { lat: 21.2690, lng: -157.6938 }, // Hanauma Bay
        media: [img(IMAGES.turtle)]
    },

    // Day 5: 동부 해안 드라이브
    {
        id: '7',
        date: 'Day 5',
        time: '11:00',
        title: '72번 국도 드라이브',
        description: '바다를 끼고 달리는 환상적인 코스. 마카푸우 포인트 전망대.',
        tags: ['Drive', 'Coast'],
        location: { lat: 21.3106, lng: -157.6493 }, // Makapuu Point
        media: [img(IMAGES.drive)]
    },

    // Day 6: 쿠알로아 랜치
    {
        id: '8',
        date: 'Day 6',
        time: '14:00',
        title: 'Kualoa Ranch',
        description: '쥬라기 공원 촬영지. ATV를 타고 정글 탐험.',
        tags: ['Activity', 'Movie'],
        location: { lat: 21.5207, lng: -157.8373 }, // Kualoa Ranch
        media: [img(IMAGES.kualoa)]
    },

    // Day 7: 노스 쇼어
    {
        id: '9',
        date: 'Day 7',
        time: '12:00',
        title: 'North Shore & 거북이',
        description: '라니아케아 비치에서 쉬고 있는 거북이 구경. 새우 트럭은 필수.',
        tags: ['North Shore', 'Food'],
        location: { lat: 21.6189, lng: -158.0853 }, // Laniakea Beach
        media: [img(IMAGES.northShore)]
    },

    // Day 8: 돌 플랜테이션
    {
        id: '10',
        date: 'Day 8',
        time: '15:00',
        title: 'Dole Plantation',
        description: '파인애플 아이스크림을 먹으러 왔다. 미로 찾기는 덤.',
        tags: ['Pineapple', 'Dessert'],
        location: { lat: 21.5250, lng: -158.0374 }, // Dole Plantation
        media: [img(IMAGES.pineapple)]
    },

    // Day 9: 쇼핑 & 휴식
    {
        id: '11',
        date: 'Day 9',
        time: '16:00',
        title: 'Ala Moana 쇼핑',
        description: '마지막 날은 쇼핑과 기념품 사기. 엄청난 규모의 쇼핑몰.',
        tags: ['Shopping', 'Mall'],
        location: { lat: 21.2913, lng: -157.8435 }, // Ala Moana Center
        media: [img(IMAGES.shopping)]
    },

    // Day 10: 귀국
    {
        id: '12',
        date: 'Day 10',
        time: '10:00',
        title: 'Adios, Hawaii',
        description: '아쉬움을 뒤로하고 공항으로. 다시 올게!',
        tags: ['Departure'],
        location: { lat: 21.3187, lng: -157.9225 }, // HNL Airport
    }
];

export const DUMMY_GALLERY: GalleryItem[] = [
    { id: '1', type: 'image', src: IMAGES.waikiki, alt: 'Waikiki Beach', width: 400, height: 300 },
    { id: '2', type: 'image', src: IMAGES.sunset, alt: 'Sunset', width: 300, height: 400 },
    { id: '3', type: 'image', src: IMAGES.kualoa, alt: 'Kualoa Mountains', width: 400, height: 400 },
    { id: '4', type: 'image', src: IMAGES.pineapple, alt: 'Pineapple', width: 300, height: 300 },
    { id: '5', type: 'image', src: IMAGES.diamondHead, alt: 'Diamond Head', width: 400, height: 500 },
    { id: '6', type: 'image', src: IMAGES.shopping, alt: 'Night Market', width: 400, height: 300 },
    { id: '7', type: 'image', src: IMAGES.turtle, alt: 'Turtle', width: 300, height: 400 },
    { id: '8', type: 'image', src: IMAGES.drive, alt: 'Palm Trees', width: 400, height: 300 },
];
