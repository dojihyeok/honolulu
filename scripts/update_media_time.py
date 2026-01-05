import re
import os

# Source file path
FILE_PATH = '/Users/yunhyeok/honolulu/src/data/real.ts'

def format_12hr_time(time_str):
    # HHMMSS -> HH:MM AM/PM
    hour = int(time_str[:2])
    minute = time_str[2:4]
    
    period = "AM"
    if hour >= 12:
        period = "PM"
    
    if hour > 12:
        hour -= 12
    elif hour == 0:
        hour = 12
        
    return f"{hour:02}:{minute} {period}"

def format_date(date_str):
    # YYYYMMDD -> YYYY. MM. DD.
    return f"{date_str[:4]}. {date_str[4:6]}. {date_str[6:8]}."

def main():
    if not os.path.exists(FILE_PATH):
        print(f"Error: {FILE_PATH} not found.")
        return

    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    
    # Regex to capture the timestamp from filename: YYYYMMDD_HHMMSS inside src string
    # Example: "src": "/images/real/20251219_193047.jpg",
    src_pattern = re.compile(r'"src":\s*"/images/real/(\d{8})_(\d{6})')
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        match = src_pattern.search(line)
        if match:
            date_part = match.group(1)
            time_part = match.group(2)
            
            formatted_date = format_date(date_part)
            formatted_time = format_12hr_time(time_part)
            
            # Check if next lines already contain "date" or "time" for this item to avoid duplicates
            # We look ahead a few lines until we see '}', assuming standard formatting
            has_date = False
            has_time = False
            
            # Simple lookahead
            j = 1
            while i + j < len(lines):
                next_line = lines[i+j]
                if '}' in next_line:
                    break
                if '"date":' in next_line:
                    has_date = True
                if '"time":' in next_line:
                    has_time = True
                j += 1
            
            # Insert metadata if missing
            indent = line[:line.find('"src"')] # preserve indentation
            
            # We'll just insert/append them. If they exist, the previous logic (lookahead) 
            # might be insufficient if we want to UPDATE.
            # But simpler approach: I'm just appending. 
            # Wait, if I append and they exist, it's invalid JSON/Object (duplicate keys).
            # The user asked me to "input" it. Ideally I should REPLACE or INSERT.
            
            # Current `real.ts` basically doesn't have them except for the first 3 I added.
            # The FIRST THREE I added manually. I should probably overwrite/skip them.
            
            if not has_date:
                new_lines.append(f'{indent}"date": "{formatted_date}",\n')
            if not has_time:
                new_lines.append(f'{indent}"time": "{formatted_time}",\n')

    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("Updated real.ts with Date/Time from filenames.")

if __name__ == "__main__":
    main()
