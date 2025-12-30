const fs = require('fs');
const path = require('path');
const exifr = require('exifr');

const IMAGES_DIR = path.join(process.cwd(), 'public/images/real');
const OUTPUT_FILE = path.join(process.cwd(), 'src/data/real.ts');

// Configuration
const CLUSTER_TIME_THRESHOLD = 60 * 60 * 1000; // 1 Hour (in ms)
const BURST_TIME_THRESHOLD = 2 * 1000; // 2 Seconds (in ms) - for burst shots

// Location Definitions (Approximate Bounding Boxes or Points)
// Simple radius check: ~0.02 degrees is roughly 2km
const LOCATIONS = [
    { name: '와이키키 해변', lat: 21.276, lng: -157.826 },
    { name: '호놀룰루 공항', lat: 21.318, lng: -157.923 },
    { name: '거북이 해변 (North Shore)', lat: 21.618, lng: -158.085 },
    { name: '쿠알로아 랜치', lat: 21.520, lng: -157.837 },
    { name: '다이아몬드 헤드', lat: 21.262, lng: -157.803 },
    { name: '하나우마 베이', lat: 21.269, lng: -157.694 },
    { name: '펄 하버', lat: 21.365, lng: -157.950 },
    { name: '돌 플랜테이션', lat: 21.523, lng: -158.037 },
    { name: '알라모아나 쇼핑센터', lat: 21.291, lng: -157.843 },
    { name: '탄탈루스 전망대', lat: 21.315, lng: -157.815 }
];

// Specific files to be forced into the Incheon Airport episode
const INCHEON_FILES = [
    '20251219_193047.jpg',
    '20251219_193050.jpg',
    '20251219_193104.jpg',
    '20251219_193106.jpg',
    '20251220_030729.jpg',
    '20251220_030737.jpg',
    '20251220_030743.jpg'
];

// Merged Episodes Configuration
const MERGED_EPISODES = [
    {
        title: '메리어트 리조트 도착 후 주변 탐방',
        files: [
            '20251219_120358.jpg', '20251219_120404.mp4', '20251219_124532.mp4',
            '20251219_124547.jpg', '20251219_124550.jpg', '20251219_124555.jpg',
            '20251219_134711.jpg', '20251219_134718.jpg', '20251219_134719.jpg',
            '20251219_134722.jpg'
        ]
    },
    {
        title: '와이키키 해변 오전 물놀이 시작~',
        files: [
            '20251220_102553.jpg', '20251220_102600.mp4', '20251220_102614.mp4',
            '20251220_121052.mp4', '20251220_121129.mp4', '20251220_121200.jpg',
            '20251220_121204.mp4', '20251220_121247.mp4', '20251220_121301.mp4',
            '20251220_121322.jpg', '20251220_121323.jpg', '20251220_121324.jpg',
            '20251220_121327.jpg', '20251220_121332.mp4', '20251220_121348.mp4',
            '20251220_121409.mp4', '20251220_121415.jpg'
        ]
    },
    {
        title: '와이키키 마켓 투어 & 야간 산책',
        description: '인터네셔널 마켓 플레이스에서 만난 워미스 버섯',
        files: [
            '20251220_171346.mp4', '20251220_172014.jpg', '20251220_172021.jpg',
            '20251220_172024.mp4', '20251220_172038.jpg', '20251220_172039.jpg',
            '20251220_172041.jpg', '20251220_172156.mp4', '20251220_172738.jpg',
            '20251220_172740.mp4',
            '20251220_183809.jpg', '20251220_183811.jpg', '20251220_183813.jpg',
            '20251220_183820.jpg', '20251220_183822.jpg', '20251220_183839.jpg',
            '20251220_185008.jpg', '20251220_185011.jpg'
        ]
    },
    {
        title: '온종일 폴리네시안 문화 센터에서 원주민 문화 체험',
        description: '하루 종일 알차게 즐긴 폴리네시안 문화 체험!',
        files: [
            // 11:42 AM Episode
            '20251222_114204.jpg', '20251222_114207.jpg', '20251222_114211.jpg',
            '20251222_120942.mp4', '20251222_121004.jpg', '20251222_121006.jpg',
            '20251222_123555.mp4', '20251222_123616.jpg', '20251222_123620.jpg',
            '20251222_123808.jpg', '20251222_123810.mp4', '20251222_123821.mp4',
            '20251222_124605.mp4', '20251222_124745.mp4', '1766772414226.jpg',
            '20251222_124934.mp4', '20251222_125424.mp4', '1766772414124.jpg',
            '1766772414043.jpg', '20251222_131246.jpg', '20251222_131257.mp4',
            '20251222_131454.jpg', '20251222_131525.jpg', '20251222_131702.jpg',
            '20251222_131704.jpg', '20251222_131707.jpg', '20251222_131709.jpg',
            '20251222_131746.mp4', '20251222_131759.jpg', '20251222_131802.jpg',
            '20251222_131853.jpg', '20251222_132156.jpg', '20251222_132352.mp4',
            '1766772413858.jpg', '20251222_132433.jpg', '1766772413760.jpg',
            '1766772413543.jpg', '1766772413643.jpg', '1766772413456.jpg',
            '1766772413361.jpg', '1766772413214.jpg', '20251222_135416.jpg',
            '20251222_135419.jpg', '20251222_135422.jpg',
            // 02:54 PM Episode
            '1766772413121.jpg', '1766772413031.jpg', '1766772412931.jpg',
            '1766772412804.jpg', '20251222_150041.jpg', '20251222_150050.jpg',
            '20251222_150122.jpg', '20251222_150123.jpg', '20251222_150143.jpg',
            '20251222_150144.jpg', '20251222_150146.jpg', '20251222_150148.jpg',
            '20251222_150553.mp4', '20251222_150614.mp4', '20251222_150641.mp4',
            '20251222_150711.mp4', '1766772412677.jpg', '20251222_152833.jpg',
            '20251222_152844.jpg', '20251222_155207.jpg',
            // Files seen in the tail end of 02:54 PM episode but potentially part of it or next?
            // The story_15 ended at 181242.jpg in previous view? No.
            // Let's re-read the specific block.
            // Story 15 (02:54 PM) media ends at line 2333 with 20251222_181242.jpg
            // The view I just did showed:
            // 20251222_155209.jpg ... 20251222_162648.mp4 ... 20251222_171303.jpg ... 20251222_181242.jpg
            // I need to include ALL of these.
            '20251222_155209.jpg', '20251222_155211.jpg', '20251222_155230.jpg',
            '20251222_155231.jpg', '20251222_162449.mp4', '20251222_162509.mp4',
            '20251222_162529.mp4', '20251222_162628.mp4', '20251222_162648.mp4',
            '20251222_171258.jpg', '20251222_171301.jpg', '20251222_171303.jpg',
            '20251222_171331.mp4', '20251222_172228.mp4', '20251222_181242.jpg'
        ]
    },
    {
        title: '폴리네시안 문화 센터 공연으로 마무리, 도헌 추장과 함께',
        files: [
            // 07:17 PM
            '20251222_191739.mp4', '20251222_192245.jpg', '20251222_192246.jpg',
            '20251222_192247.jpg', '20251222_192249.jpg', '20251222_192251.jpg',
            '20251222_192252.jpg', '20251222_192256.jpg', '20251222_192815.jpg',
            '20251222_192832.jpg', '20251222_192853.jpg',
            // 08:50 PM
            '20251222_205000.jpg', '20251222_205003.jpg', '1766647170333.jpg',
            '1766647170242.jpg',
            // 11:04 PM (Merged)
            '1766647170142.jpg', '1766647170043.jpg'
        ]
    }
];

const STORY_OVERRIDES = {
    '20251219_101100.jpg': {
        title: '호놀룰루 공항 도착!',
        description: '호텔 가는 버스에서 비소식 ㅠ.ㅠ'
    },
    '20251219_192302.jpg': {
        title: '비오는 첫날',
        description: '날씨 요정이 오려나??'
    },
    '20251220_140454.jpg': {
        title: '반짝 반짝 하와이',
        description: '와이키키 해변 주변 탐방! 🌴'
    },
    '20251221_120020.jpg': {
        title: "다이아몬드 헤드 투어 & Betty's 버거",
        description: "다이아몬드 헤드 정상에 도착한 뿌듯함과 성취감을 느꼈다."
    },

    '20251222_093328.jpg': {
        title: '아사이볼로 시작하는 모닝 식사'
    },
    '1766647170142.jpg': {
        title: '알로힐라니 리조트 모닝 수영으로 시작하는 하루'
    },
    '20251223_165439.jpg': {
        title: '와이키키 노을 산책'
    },
    '1766647168362.jpg': {
        title: '와이키키 맛집 투어'
    },

    '20251224_135836.mp4': {
        title: '래니카이 비치에서 스노쿨링'
    },
    '20251224_112205.jpg': {
        description: '렌탈 하기위한 현지인'
    },
    '20251224_170628.jpg': {
        title: 'The Pig and The Lady에서 저녁 식사 후 드라이브'
    },
    '1766772933529.jpg': {
        title: '힐튼 하와이안 빌리지에서 수영 & Activity'
    },
    '20251225_163201.jpg': {
        title: '탄날루스 전망대에서 추억 만들기'
    },
    '1766772932167.jpg': {
        title: '두번째 위기~ 호텔키가 사라졌다.'
    },
    '20251226_125714.jpg': {
        title: "Shark's Cove & North Shore Market 투어"
    },
    '20251225_114842.jpg': {
        title: 'GOOFY Cafe & Dine 에서 즐기는 아점'
    },
    '20251226_185819.jpg': {
        title: '우리 도헌이 9번째 생일 파티 모래는 푱푱하다 푱푱한~'
    }
};

const IGNORED_FILES = [
    '1766647168803.jpg', // 2025. 12. 23. 03:34 PM Story
    '20251223_190230.jpg',
    '1766647168460.jpg',
    '20251223_190228.jpg',
    '1766772933640.jpg', // 2025. 12. 24. 09:26 PM Story
    '20251225_090743.jpg',  // 2025. 12. 25. 09:07 AM Story
    'Screenshot_20251225_170406_Maps.jpg',
    '20251226_164936.jpg',
    'Screenshot_20251224_110458_ChatGPT.jpg',
    '20251221_210057.mp4',
    '20251221_210132.mp4'
];

function getLocationName(lat, lng) {
    if (!lat || !lng) return null;
    for (const loc of LOCATIONS) {
        // Simple Euclidean distance heuristic check (rough)
        const dLat = Math.abs(lat - loc.lat);
        const dLng = Math.abs(lng - loc.lng);
        // Approx 2-3km radius
        if (dLat < 0.03 && dLng < 0.03) {
            return loc.name;
        }
    }
    return null;
}

function getTimeOfDay(date) {
    const hour = date.getHours();
    if (hour >= 5 && hour < 9) return '이른 아침';
    if (hour >= 9 && hour < 12) return '오전';
    if (hour >= 12 && hour < 14) return '점심 시간';
    if (hour >= 14 && hour < 17) return '오후';
    if (hour >= 17 && hour < 19) return '해질 무렵';
    if (hour >= 19 && hour < 22) return '저녁';
    return '늦은 밤';
}

// Diary Templates
// Diary Templates
const DIARY_TEMPLATES = {
    '호놀룰루 공항': {
        default: [
            "비행기가 엄청 컸다! 두근두근 하와이로 출발!",
            "공항에 사람들이 정말 많았다. 얼른 바다 보러 가고 싶다!",
            "드디어 하와이에 도착했다. 밖이 진짜 따뜻하다."
        ]
    },
    '와이키키 해변': {
        '이른 아침': ["아침 일찍 바다에 나왔다. 물이 반짝반짝 빛나서 참 예뻤다."],
        '점심 시간': ["햇살이 쨍쨍해서 바다 색깔이 더 예뻐 보였다.", "사람들이 바다에서 즐겁게 놀고 있었다. 나도 신났다!"],
        '해질 무렵': ["시원한 바람이 불어서 기분이 좋았다."],
        default: ["바다 색깔이 에메랄드 색이었다."]
    },
    '거북이 해변 (North Shore)': {
        default: [
            "바다가 정말 맑았다. 거북이가 살기 좋은 곳 같았다.",
            "파도가 조금 셌지만 보는 건 재미있었다.",
            "거북이를 혹시 볼 수 있을까? 두근두근했다."
        ]
    },
    '쿠알로아 랜치': {
        default: [
            "초록색 산이 엄청 컸다. 공룡이 나올 것 같았다!",
            "바람이 시원하게 불었다. 풍경이 정말 멋졌다."
        ]
    },
    '다이아몬드 헤드': {
        default: [
            "높은 곳에서 바다를 보니 가슴이 뻥 뚫리는 것 같았다.",
            "바람이 엄청 많이 불어서 모자가 날아갈 뻔 했다."
        ]
    },
    '하나우마 베이': {
        default: [
            "물이 정말 맑아서 물고기가 다 보일 것 같았다!",
            "산호초가 많이 보였다. 바닷속 세상은 침 신기하다."
        ]
    },
    '음식': {
        '점심 시간': ["배가 고팠는데 맛있는 걸 먹어서 기분이 좋아졌다.", "시원한 음료수를 마시니까 더위가 싹 날아갔다."],
        '저녁': ["저녁을 먹고 나니 잠이 솔솔 왔다.", "오늘 하루도 정말 알차게 보냈다."]
    },
    common: [
        "오늘 하루는 정말 잊지 못할 것 같다. 😊",
        "엄마 아빠랑 함께라서 더 좋았다. ❤️",
        "다리가 조금 아팠지만 꾹 참았다. 난 씩씩하니까! 💪",
        "사진을 많이 찍었다. 나중에 보면 또 생각나겠지? 📸",
        "하와이는 정말 천국 같은 곳이다. 🌈"
    ]
};

function getRandomTemplate(category, subCategory = 'default') {
    const templates = DIARY_TEMPLATES[category]?.[subCategory] || DIARY_TEMPLATES[category]?.['default'] || [];
    if (templates.length === 0) return null;
    return templates[Math.floor(Math.random() * templates.length)];
}

function generateDescription(timeOfDay, locationName, mediaCount) {
    let sentences = [];

    // 1. Context specific sentence
    if (locationName) {
        const sentence = getRandomTemplate(locationName, timeOfDay);
        if (sentence) sentences.push(sentence);
        else sentences.push(`${locationName}에 왔다. 정말 멋진 곳이었다.`);
    } else {
        // Time based fallback
        if (timeOfDay === '점심 시간' || timeOfDay === '저녁') {
            const foodSentence = getRandomTemplate('음식', timeOfDay);
            if (foodSentence) sentences.push(foodSentence);
        } else {
            sentences.push(`하와이에서의 ${timeOfDay}. 날씨가 참 좋았다.`);
        }
    }

    // 2. Common emotion sentence (Randomly add)
    if (Math.random() > 0.3) {
        const commonSentence = getRandomTemplate('common');
        if (commonSentence) sentences.push(commonSentence);
    }

    return sentences.join(' ');
}

function generateTitle(timeOfDay, locationName, mediaCount) {
    const context = locationName ? `${locationName}에서의` : `하와이에서의`;

    // Variety based on time
    if (timeOfDay === '이른 아침') return `${context} 상쾌한 아침 시작! ☀️`;
    if (timeOfDay === '해질 무렵') return `${context} 아름다운 석양 🌅`;
    if (timeOfDay === '점심 시간') return `${context} 맛있는 점심과 휴식 🍱`;
    if (timeOfDay === '늦은 밤') return `${context} 하루를 마무리하며 🌙`;

    // Default
    if (locationName === '인천국제공항') return "출발 전 라운지 탐방 후 비행기 출발";
    if (locationName) return `${locationName} 탐방! 🌴`;
    return `${timeOfDay}의 여유로운 순간들 ✨`;
}

async function generateTimeline() {
    console.log('📸 미디어 정보를 분석하여 여행기를 생성합니다... (스마트 그룹핑 적용)');

    if (!fs.existsSync(IMAGES_DIR)) {
        console.error(`❌ 이미지 폴더가 없습니다: ${IMAGES_DIR}`);
        return;
    }

    // Support Images and Videos
    const files = fs.readdirSync(IMAGES_DIR).filter(file => /\.(jpg|jpeg|png|heic|mp4|mov)$/i.test(file));

    if (files.length === 0) {
        console.log('⚠️  public/images/real 폴더에 미디어 파일이 없습니다.');
        return;
    }

    console.log(`🔍 총 ${files.length}개의 미디어 파일을 발견했습니다. 메타데이터 추출 및 그룹핑 중...`);

    const rawItems = [];

    // 1. Extract Metadata for ALL files
    for (const [index, file] of files.entries()) {
        if (IGNORED_FILES.includes(file)) continue;

        const filePath = path.join(IMAGES_DIR, file);
        const relativePath = `/images/real/${file}`;
        const isVideo = /\.(mp4|mov)$/i.test(file);

        try {
            let metadata = null;
            let dateObj = fs.statSync(filePath).birthtime; // Default to file creation time

            // EXIF extraction
            if (!isVideo) {
                try {
                    metadata = await exifr.parse(filePath, {
                        tiff: true,
                        exif: true,
                        gps: true // Force GPS extraction
                    });
                    if (metadata?.DateTimeOriginal) dateObj = metadata.DateTimeOriginal;
                } catch (e) {
                    // Ignore EXIF errors
                }
            } else {
                // Try to get date from filename if possible (e.g., 20251219_101100)
                const match = file.match(/^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})/);
                if (match) {
                    dateObj = new Date(match[1], match[2] - 1, match[3], match[4], match[5], match[6]);
                }
            }

            // Ensure valid date
            if (isNaN(dateObj.getTime())) {
                dateObj = fs.statSync(filePath).birthtime;
            }

            rawItems.push({
                file,
                src: relativePath,
                date: dateObj,
                metadata,
                isVideo,
                width: metadata?.ExifImageWidth || 800,
                height: metadata?.ExifImageHeight || 600
            });

        } catch (error) {
            console.error(`❌ 오류 발생 (${file}):`, error.message);
        }
    }

    // 2. Sort by Date
    rawItems.sort((a, b) => a.date - b.date);

    // 3. Cluster Items

    // Helper to extract items by filename list
    const usedFiles = new Set();
    const clusters = [];

    // A. Process Incheon Files (Strict)
    const incheonItems = [];
    for (const item of rawItems) {
        if (INCHEON_FILES.includes(item.file)) {
            incheonItems.push(item);
            usedFiles.add(item.file);
        }
    }

    if (incheonItems.length > 0) {
        incheonItems.sort((a, b) => a.date - b.date);
        clusters.push({
            startTime: incheonItems[0].date,
            endTime: incheonItems[incheonItems.length - 1].date,
            items: incheonItems,
            locations: [{ lat: 37.447, lng: 126.448 }],
            overrideLocationName: '인천국제공항'
        });
        console.log(`✈️  인천공항 에피소드 생성 (파일 ${incheonItems.length}개 통합)`);
    }

    // B. Process Merged Episodes
    for (const mergeConfig of MERGED_EPISODES) {
        const mergedItems = [];
        for (const item of rawItems) {
            if (mergeConfig.files.includes(item.file)) {
                mergedItems.push(item);
                usedFiles.add(item.file);
            }
        }

        if (mergedItems.length > 0) {
            mergedItems.sort((a, b) => a.date - b.date);
            clusters.push({
                startTime: mergedItems[0].date,
                endTime: mergedItems[mergedItems.length - 1].date,
                items: mergedItems,
                locations: mergedItems.map(i => ({ lat: i.metadata?.latitude, lng: i.metadata?.longitude })).filter(l => l.lat),
                customTitle: mergeConfig.title,
                customDescription: mergeConfig.description
            });
            console.log(`🔗 에피소드 통합: ${mergeConfig.title} (${mergedItems.length}개)`);
        }
    }

    // C. Process Remaining Items (Standard Clustering)
    const otherItems = rawItems.filter(item => !usedFiles.has(item.file));
    let currentCluster = null;

    for (const item of otherItems) {

        // Start a new cluster if none exists
        if (!currentCluster) {
            currentCluster = {
                startTime: item.date,
                endTime: item.date,
                items: [item],
                locations: []
            };
            if (item.metadata?.latitude) currentCluster.locations.push({ lat: item.metadata.latitude, lng: item.metadata.longitude });
            continue;
        }

        const timeDiff = item.date - currentCluster.endTime;

        // Check conditions to start a new cluster
        // If > 1 hour gap, break cluster
        if (timeDiff > CLUSTER_TIME_THRESHOLD) {
            clusters.push(currentCluster);
            currentCluster = {
                startTime: item.date,
                endTime: item.date,
                items: [item],
                locations: []
            };
            if (item.metadata?.latitude) currentCluster.locations.push({ lat: item.metadata.latitude, lng: item.metadata.longitude });
        } else {
            // Add to current cluster
            currentCluster.items.push(item);
            currentCluster.endTime = item.date; // Extend cluster time
            if (item.metadata?.latitude) currentCluster.locations.push({ lat: item.metadata.latitude, lng: item.metadata.longitude });
        }
    }
    // Push the last cluster
    if (currentCluster) clusters.push(currentCluster);

    // 4. Sort Clusters (Keep Incheon First, Sort Rest by Time)
    const incheonCluster = clusters.find(c => c.overrideLocationName === '인천국제공항');
    const variableClusters = clusters.filter(c => c.overrideLocationName !== '인천국제공항');

    variableClusters.sort((a, b) => a.startTime - b.startTime);

    clusters.length = 0; // Clear
    if (incheonCluster) clusters.push(incheonCluster);
    clusters.push(...variableClusters);

    // 5. Generate Timeline Items from Clusters


    // 4. Generate Timeline Items from Clusters
    const timelineItems = [];
    const galleryItems = []; // Still strictly flat for gallery view? Or maybe we can't change gallery structure too much.
    // Actually, let's keep gallery items flat but generated cleanly.

    let globalIdIndex = 1;

    for (const cluster of clusters) {
        const firstItem = cluster.items[0];
        const dateObj = firstItem.date;

        // Date Formatting
        const dateStr = dateObj.toLocaleDateString('ko-KR', { year: 'numeric', month: '2-digit', day: '2-digit' });
        const timeStr = dateObj.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

        // Determine main location for this cluster (average or first valid)
        let clusterLocation = null;
        let locationName = null;

        if (cluster.overrideLocationName) {
            locationName = cluster.overrideLocationName;
            clusterLocation = cluster.locations[0];
        } else {
            // Find first valid location or average? Use first valid for simplicity
            const validLoc = cluster.locations.find(l => l.lat && l.lng);
            if (validLoc) {
                clusterLocation = validLoc;
                locationName = getLocationName(validLoc.lat, validLoc.lng);
            }
        }

        // (Removed old special logic for Date override as we use INCHEON_FILES now)

        // (Special date logic removed to strict follow whitelist)

        const timeOfDay = getTimeOfDay(dateObj);
        let title = generateTitle(timeOfDay, locationName, cluster.items.length);
        let description = generateDescription(timeOfDay, locationName, cluster.items.length);

        // Apply Custom Title from Merged Cluster
        if (cluster.customTitle) {
            title = cluster.customTitle;
        }
        if (cluster.customDescription) {
            description = cluster.customDescription;
        }

        // Check for overrides (Files still take precedence if matched, or maybe overrides apply on top of merged?)
        // Let's say item overrides check first. But usually merged title is what we want.
        // Actually the loop below applies per-item override. If a merged cluster has a file with override, it might overwrite the merged title.
        // Let's allow that flexibility.

        // Check for overrides
        for (const item of cluster.items) {
            if (STORY_OVERRIDES[item.file]) {
                if (STORY_OVERRIDES[item.file].title) title = STORY_OVERRIDES[item.file].title;
                if (STORY_OVERRIDES[item.file].description) description = STORY_OVERRIDES[item.file].description;
                break; // Apply first match
            }
        }

        // Process media items (Handle Deduplication/Burst)
        // We will just include all non-duplicate-looking images for now, but maybe limit distinct display in the UI? 
        // For 'media' array, let's just push all of them. The UI handles horizontal scroll.
        const mediaList = cluster.items.map(it => ({
            type: it.isVideo ? 'video' : 'image',
            src: it.src,
            width: it.width,
            height: it.height
        }));



        // Add to timelines
        timelineItems.push({
            id: `story_${globalIdIndex}`,
            date: dateStr,
            time: timeStr,
            title: title,
            description: description,
            tags: ['Trip', timeOfDay, locationName || 'Hawaii'].filter(Boolean),
            media: mediaList,
            location: clusterLocation || undefined,
            region: locationName || undefined // New field for badge
        });

        // Add to gallery (Flattened)
        for (const item of cluster.items) {
            galleryItems.push({
                id: `g_${globalIdIndex}_${item.file}`,
                type: item.isVideo ? 'video' : 'image',
                src: item.src,
                alt: title,
                width: item.width,
                height: item.height,
            });
        }

        globalIdIndex++;
    }

    // Write File
    const fileContent = `
import { TimelineItem, GalleryItem, MediaItem } from './dummy';

export const REAL_TIMELINE: TimelineItem[] = ${JSON.stringify(timelineItems, null, 4)};

export const REAL_GALLERY: GalleryItem[] = ${JSON.stringify(galleryItems, null, 4)};
    `.trim();

    fs.writeFileSync(OUTPUT_FILE, fileContent);
    console.log(`✅ 스마트 여행기 생성 완료!`);
    console.log(`📊 생성된 스토리: ${timelineItems.length}개 (원본 파일: ${rawItems.length}개)`);
    console.log(`📂 저장된 파일: ${OUTPUT_FILE}`);
}

generateTimeline();
