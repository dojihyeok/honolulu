
import os
import glob
import re
import json
import math
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# Configuration
IMAGE_DIR = '/Users/yunhyeok/honolulu/public/images/real'
TARGET_FILE = '/Users/yunhyeok/honolulu/src/data/real.ts'

# Reference POIs extracted from the file itself (approximate based on inspection)
# Format: Name, Lat, Lng
POIS = [
    ("인천국제공항 제1여객터미널", 37.447, 126.448),
    ("Daniel K. Inouye Int'l Airport", 21.3296, -157.9166),
    ("Waikiki Beach Marriott Resort", 21.2740, -157.8222),
    ("Waikiki Beach (Kalakaua Ave)", 21.2762, -157.8228),
    ("Waikiki Beach Center", 21.2764, -157.8235),
    ("International Market Place", 21.2778, -157.8269),
    ("Duke Paoa Kahanamoku Statue", 21.2758, -157.8242),
    ("Ala Moana Center", 21.2910, -157.8435),
    ("Kualoa Ranch", 21.5212, -157.8373),
    ("Pearl Harbor National Memorial", 21.3650, -157.9360),
    ("Hanauma Bay", 21.2690, -157.6938),
    ("Diamond Head State Monument", 21.2640, -157.8036),
    ("North Shore (Haleiwa)", 21.5925, -158.1030),
    ("Dole Plantation", 21.5262, -158.0378),
    ("Polynesian Cultural Center", 21.6394, -157.9270),
    ("Marukame Udon Waikiki", 21.2797, -157.8265),
    ("Hyatt Regency Waikiki", 21.2761, -157.8245),
    ("Royal Hawaiian Center", 21.2783, -157.8291),
    ("Sheraton Waikiki", 21.2782, -157.8300),
    ("Hilton Hawaiian Village", 21.2846, -157.8374),
    ("Honolulu Zoo", 21.2713, -157.8213),
    ("Waikiki Aquarium", 21.2662, -157.8220),
    ("Magic Island", 21.2882, -157.8471),
    ("Iolani Palace", 21.3069, -157.8587),
    ("Kamehameha Statue", 21.3051, -157.8581),
    ("Salt at Our Kaka'ako", 21.2982, -157.8617),
    ("Leonard's Bakery", 21.2849, -157.8133),
    ("Rainbow Drive-In", 21.2842, -157.8118),
    ("Giovanni's Shrimp Truck", 21.5794, -157.9734),
    ("Matsumoto Shave Ice", 21.5911, -158.1028),
    ("Waimea Valley", 21.6373, -158.0583),
    ("Sunset Beach", 21.6666, -158.0519),
    ("Banzai Pipeline", 21.6640, -158.0530),
    ("Shark's Cove", 21.6508, -158.0620),
    ("Laniakea Beach (Turtle Beach)", 21.6186, -158.0854),
    ("Byodo-In Temple", 21.4312, -157.8327),
    ("Kailua Beach Park", 21.3970, -157.7247),
    ("Lanikai Beach", 21.3934, -157.7144),
    ("Makapuu Point Lighthouse Trail", 21.3090, -157.6503),
    ("Halona Blowhole Outlet", 21.2764, -157.6775)
]

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_nearest_poi(lat, lon):
    min_dist = float('inf')
    nearest_name = None
    
    for name, poi_lat, poi_lon in POIS:
        dist = haversine_distance(lat, lon, poi_lat, poi_lon)
        if dist < min_dist:
            min_dist = dist
            nearest_name = name
            
    # If distance is too far (e.g. > 2km), maybe don't assign? 
    # For now, let's look for fairly close matches (within 1km)
    if min_dist < 1.0: 
        return nearest_name
    elif min_dist < 5.0 and "공항" in nearest_name: # Airport can be large
        return nearest_name
    return None

def get_exif_gps(image):
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                return gps_data
    return None

def get_lat_lon(gps_info):
    if not gps_info: return None, None
    def convert(value):
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    try:
        lat = convert(gps_info['GPSLatitude'])
        if gps_info['GPSLatitudeRef'] != "N": lat = -lat
        lon = convert(gps_info['GPSLongitude'])
        if gps_info['GPSLongitudeRef'] != "E": lon = -lon
        return lat, lon
    except:
        return None, None

def main():
    if not os.path.exists(TARGET_FILE):
        print("Target file not found")
        return

    # Pre-calculate mapping: Filename -> Region
    file_region_map = {}
    
    files = glob.glob(os.path.join(IMAGE_DIR, '*'))
    print(f"Scanning {len(files)} files for GPS data...")
    
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg')):
            try:
                img = Image.open(f)
                gps = get_exif_gps(img)
                lat, lon = get_lat_lon(gps)
                if lat and lon:
                    poi = get_nearest_poi(lat, lon)
                    if poi:
                        filename = os.path.basename(f)
                        file_region_map[filename] = poi
                        # print(f"Mapped {filename} -> {poi}")
            except Exception:
                pass

    print(f"Found {len(file_region_map)} matches.")

    # Read and update TARGET_FILE
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    src_pattern = re.compile(r'"src":\s*"/images/real/([^"]+)"')
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        match = src_pattern.search(line)
        if match:
            filename = match.group(1)
            if filename in file_region_map:
                region = file_region_map[filename]
                
                # Check directly subsequent lines for "region" to avoid duplication if running multiple times
                # If "region" exists in next few lines (before closing }), we skip adding or replace?
                # For simplicity, we assume we just check if "region" is already there. 
                # Ideally, we should detect if it's there and UPDATE it.
                # But my previous simple injection script just APPENDED. 
                # Let's peek ahead.
                
                has_region = False
                j = 1
                while i + j < len(lines):
                    next_line = lines[i+j]
                    if '}' in next_line:
                        break
                    if '"region":' in next_line:
                        has_region = True
                        break
                    j += 1
                
                indent = line[:line.find('"src"')]
                
                if not has_region:
                   new_lines.append(f'{indent}"region": "{region}",\n')

    with open(TARGET_FILE, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
    print("Updated real.ts with inferred regions.")

if __name__ == "__main__":
    main()
