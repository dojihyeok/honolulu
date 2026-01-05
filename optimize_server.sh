
set -e

# 1. Install FFmpeg and ImageMagick if needed
if ! command -v ffmpeg &> /dev/null; then
    echo "Installing FFmpeg..."
    apt-get update && apt-get install -y ffmpeg
fi

if ! command -v mogrify &> /dev/null; then
    echo "Installing ImageMagick..."
    apt-get update && apt-get install -y imagemagick
fi

cd /root/honolulu/public/images/real

echo "--- Optimizing Images (Max 1920px, 80% quality) ---"
# Use mogrify for in-place batch processing. 
# Only process huge files (larger than 500kb) to save time/quality on already small ones? 
# Or just enforcing max dimension is safer.
find . -iname "*.jpg" -o -iname "*.png" -o -iname "*.jpeg" | xargs -P 4 -I {} mogrify -resize "1920x1920>" -quality 80 {}

echo "--- Optimizing Videos (720p, CRF 28) ---"
# We need to process via temp file then overwrite
find . -name "*.mp4" | while read file; do
    # Check if already optimized (skip if filename contains _opt, specific logic needed? 
    # Or just check file size/bitrate? simpler to just re-encode safely to tmp)
    
    echo "Processing $file..."
    ffmpeg -y -i "$file" -vf "scale='min(1280,iw)':-2" -vcodec libx264 -crf 28 -preset fast -acodec aac -b:a 128k "${file}.tmp.mp4" < /dev/null
    
    if [ -f "${file}.tmp.mp4" ]; then
        mv "${file}.tmp.mp4" "$file"
        echo "Done: $file"
    else
        echo "Failed to convert $file"
    fi
done

echo "--- Optimization Complete ---"
