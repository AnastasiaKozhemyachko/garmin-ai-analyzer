#!/usr/bin/env python3
import sys
import time
import subprocess
from pathlib import Path
from config import DATA_FILE, CHATGPT_URL, DELAY_MS, FINDER_WAIT_MS, UPLOAD_WAIT_MS, ANALYSIS_PROMPT


def sleep_ms(ms):
    """Sleep for specified milliseconds."""
    time.sleep(ms / 1000)


def run_applescript(script):
    """Execute AppleScript command."""
    subprocess.run(["osascript", "-e", script], check=True)


def select_and_copy_file(file_path):
    """Open file in Finder and copy it to clipboard."""
    script = f'''
tell application "Finder"
  activate
  select file (POSIX file "{file_path}" as alias)
  delay 1
end tell

tell application "System Events"
  keystroke "c" using {{command down}}
  delay 1
end tell
'''
    run_applescript(script)


def open_chatgpt(url):
    """Open ChatGPT in Chrome."""
    script = f'''
tell application "Google Chrome"
  activate
  open location "{url}"
end tell
delay 3
'''
    run_applescript(script)


def paste_file():
    """Paste file from clipboard into ChatGPT."""
    script = '''
tell application "Google Chrome"
  activate
  delay 1
end tell

tell application "System Events"
  keystroke "v" using {command down}
  delay 2
end tell
'''
    run_applescript(script)


def send_prompt(prompt):
    """Copy prompt to clipboard and send it."""
    subprocess.run(["pbcopy"], input=prompt.encode(), check=True)
    script = '''
tell application "System Events"
  keystroke "v" using {command down}
  delay 1
  key code 36
end tell
'''
    run_applescript(script)


def main():
    file_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_FILE
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    absolute_path = file_path.resolve()
    print(f"✅ File: {absolute_path}")
    
    print("📂 Opening file in Finder...")
    subprocess.run(["open", "-R", str(absolute_path)], check=True)
    sleep_ms(FINDER_WAIT_MS)
    
    print("📋 Selecting and copying file...")
    select_and_copy_file(str(absolute_path))
    
    print("🌐 Opening ChatGPT...")
    open_chatgpt(CHATGPT_URL)
    sleep_ms(DELAY_MS)
    
    print("📎 Pasting file...")
    paste_file()
    sleep_ms(UPLOAD_WAIT_MS)
    
    print("📝 Sending prompt...")
    send_prompt(ANALYSIS_PROMPT)
    
    print("✅ Done")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
