import os
import subprocess
import glob

# Directory containing videos
VIDEO_DIR = "public/images/real"

def optimize_video_for_mobile(file_path):
    if file_path.endswith("_mobile.mp4"):
        return

    base_name = os.path.splitext(file_path)[0]
    mobile_output = f"{base_name}_mobile.mp4"

    if os.path.exists(mobile_output):
        print(f"⏭️  Skipping (Mobile version exists): {mobile_output}")
        return

    print(f"📱 Processing Mobile Video: {file_path} -> {mobile_output}")

    # FFmpeg command for Mobile Optimization
    # - scale=-2:540 : Resize height to 540p, keep aspect ratio (divisible by 2)
    # - crf 32 : Lower quality for mobile (smaller size)
    # - preset fast : Faster encoding
    # - movflags +faststart : Web optimization
    command = [
        "ffmpeg", "-y",
        "-i", file_path,
        "-vf", "scale=-2:540",
        "-c:v", "libx264",
        "-crf", "32",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "96k", # Lower audio bitrate
        "-movflags", "+faststart",
        mobile_output
    ]

    try:
        subprocess.run(command, check=True)
        print(f"✅ Generated: {mobile_output}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to process {file_path}: {e}")

if __name__ == "__main__":
    # Remove hidden MacOS files first if any
    os.system("find . -name '._*' -delete")
    
    video_files = glob.glob(os.path.join(VIDEO_DIR, "*.mp4"))
    video_files.sort()

    print(f"Found {len(video_files)} videos. Starting mobile optimization...")
    
    for video in video_files:
        optimize_video_for_mobile(video)
    
    print("\n🎉 Mobile optimization complete!")
