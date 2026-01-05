
import os
import glob
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

IMAGE_DIR = '/Users/yunhyeok/honolulu/public/images/real'

def get_exif_data(image):
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
                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value
    return exif_data

def get_lat_lon(exif_data):
    gps_info = exif_data.get("GPSInfo")
    if not gps_info:
        return None, None

    def convert_to_degrees(value):
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)

    try:
        lat = convert_to_degrees(gps_info['GPSLatitude'])
        lat_ref = gps_info['GPSLatitudeRef']
        if lat_ref != "N": lat = -lat

        lon = convert_to_degrees(gps_info['GPSLongitude'])
        lon_ref = gps_info['GPSLongitudeRef']
        if lon_ref != "E": lon = -lon
        
        return lat, lon
    except Exception as e:
        return None, None

def main():
    files = glob.glob(os.path.join(IMAGE_DIR, '*'))
    count = 0
    gps_count = 0
    
    print("Checking for GPS data in images...")
    
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg')):
            try:
                img = Image.open(f)
                exif = get_exif_data(img)
                lat, lon = get_lat_lon(exif)
                if lat and lon:
                    # print(f"{os.path.basename(f)}: {lat}, {lon}")
                    gps_count += 1
                count += 1
            except Exception:
                pass
    
    print(f"Total Images Checked: {count}")
    print(f"Images with GPS Data: {gps_count}")

if __name__ == "__main__":
    main()
