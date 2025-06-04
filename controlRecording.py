import subprocess
import pygetwindow as gw
from datetime import datetime
import os
from moviepy.editor import VideoFileClip, AudioFileClip
import time
import re

# Import your chess analysis function (make sure this is correct)
from automation_chess import run_chess_analysis

def start_recording(duration_sec=60):
    chrome_windows = gw.getWindowsWithTitle('Chrome')
    if not chrome_windows:
        raise Exception("Chrome window not found.")
    
    win = chrome_windows[0]
    left = max(0, 280)
    top = max(0, 180)
    width = 1600
    height = 900

    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    v_output_file = f"chrome_recording_{timestamp}.mp4"
    v_output_path = os.path.join(os.getcwd(), v_output_file)

    cmd = [
        "ffmpeg",
        "-y",
        "-ss", "7", 
        "-f", "gdigrab",
        "-framerate", "30",
        "-offset_x", str(left),
        "-offset_y", str(top),
        "-video_size", f"{width}x{height}",
        "-i", "desktop",
        "-f", "dshow",
        "-i", "audio=CABLE Output (VB-Audio Virtual Cable)",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-t", str(duration_sec),
        v_output_path
    ]

    print(f"📹 Recording Chrome window ({width}x{height}) at ({left},{top}) with audio...")
    proc = subprocess.Popen(cmd)
    return proc, v_output_path

def get_last_move_number(pgn_text):
    moves_section = pgn_text.strip().split('\n\n', 1)[1].strip()
    move_numbers = re.findall(r'(\d+)\.', moves_section)
    if move_numbers:
        return int(move_numbers[-1])
    return None

def main():
    # Example PGN to analyze
    pgn = """
    [Event "Fool's Mate"]
    [Site "India"]
    [Date "2025.24.06"]
    [Round "?"]
    [White "Magnus"]
    [Black "Vicky"]
    [Result "0-1"]

    1. f3 e5
    2. g4 Qh4#

    """

    last_move_number = get_last_move_number(pgn)
    time = 6 * last_move_number + 20

    # Start recording for 60 seconds (adjust as needed)
    record_proc, video_path = start_recording(time)

    try:
        # Run your chess analysis function (blocking call)
        run_chess_analysis(pgn)
    finally:
        # Wait a few seconds to capture final moments after analysis finishes
        # Stop recording if still running
        if record_proc.poll() is None:
            print("Stopping recording...")
            record_proc.terminate()
            record_proc.wait()

    print(f"✅ Recording saved to: {video_path}")

if __name__ == "__main__":
    main()
