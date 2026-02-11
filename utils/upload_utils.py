#!/usr/bin/env python3
"""Shared functions for ChatGPT upload scripts."""
import sys
import time
import subprocess
from pathlib import Path


def sleep_ms(ms):
    """Sleep for specified milliseconds."""
    time.sleep(ms / 1000)


def run_applescript(script):
    """Execute AppleScript command."""
    subprocess.run(["osascript", "-e", script], check=True)


def close_finder():
    """Close all Finder windows."""
    script = '''
tell application "Finder"
  close every window
end tell
'''
    run_applescript(script)


def select_and_copy_file(file_path):
    """Open file in Finder and copy it to clipboard."""
    script = f'''
tell application "Finder"
  activate
  select file (POSIX file "{file_path}" as alias)
  delay 0.5
end tell

tell application "System Events"
  key code 8 using {{command down}}
  delay 0.5
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
delay 1.5
'''
    run_applescript(script)


def paste_file():
    """Paste file from clipboard into ChatGPT."""
    script = '''
tell application "Google Chrome"
  activate
  delay 0.5
end tell

tell application "System Events"
  key code 9 using {command down}
  delay 1
end tell
'''
    run_applescript(script)


def send_prompt(prompt):
    """Copy prompt to clipboard and send it."""
    subprocess.run(["pbcopy"], input=prompt.encode(), check=True)
    script = '''
tell application "System Events"
  key code 9 using {command down}
  delay 0.5
  key code 36
end tell
'''
    run_applescript(script)


def upload_to_chatgpt(file_path, prompt, chatgpt_url, delay_ms, finder_wait_ms, upload_wait_ms):
    """Upload file to ChatGPT with given prompt."""
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    absolute_path = file_path.resolve()
    print(f"✅ File: {absolute_path}")
    
    print("📂 Opening file in Finder...")
    subprocess.run(["open", "-R", str(absolute_path)], check=True)
    sleep_ms(finder_wait_ms)
    
    print("🗑️  Closing Finder windows...")
    close_finder()
    sleep_ms(200)
    
    print("📋 Selecting and copying file...")
    select_and_copy_file(str(absolute_path))
    
    print("🌐 Opening ChatGPT...")
    open_chatgpt(chatgpt_url)
    sleep_ms(delay_ms)
    
    print("📎 Pasting file...")
    paste_file()
    sleep_ms(upload_wait_ms)
    
    print("📝 Sending prompt...")
    send_prompt(prompt)
    
    print("✅ Done")
