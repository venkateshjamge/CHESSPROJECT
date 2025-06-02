import subprocess
import pygetwindow as gw
from datetime import datetime
import os
import time

# Import your chess analysis function (make sure this is correct)
from automation_chess import run_chess_analysis

def start_recording(duration_sec=60):
    chrome_windows = gw.getWindowsWithTitle('Chrome')
    if not chrome_windows:
        raise Exception("Chrome window not found.")
    
    win = chrome_windows[0]
    left = max(0, 20)
    top = max(0, 200)
    width = 1300
    height = win.height -30
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"chrome_recording_{timestamp}.mp4"
    output_path = os.path.join(os.getcwd(), output_file)

    cmd = [
        "ffmpeg",
        "-y",
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
        output_path
    ]

    print(f"📹 Recording Chrome window ({width}x{height}) at ({left},{top}) with audio...")
    proc = subprocess.Popen(cmd)
    return proc, output_path

def main():
    # Example PGN to analyze
    pgn = """
    [Event "Fool's Mate"]
    [Site "?"]
    [Date "????.??.??"]
    [Round "?"]
    [White "White"]
    [Black "Black"]
    [Result "0-1"]

    1. f3 e5 2. g4 Qh4#
    """

    # Start recording for 60 seconds (adjust as needed)
    record_proc, video_path = start_recording(duration_sec=20)

    try:
        # Run your chess analysis function (blocking call)
        run_chess_analysis(pgn)
    finally:
        # Wait a few seconds to capture final moments after analysis finishes
        time.sleep(5)
        # Stop recording if still running
        if record_proc.poll() is None:
            print("Stopping recording...")
            record_proc.terminate()
            record_proc.wait()

    print(f"✅ Recording saved to: {video_path}")

if __name__ == "__main__":
    main()
