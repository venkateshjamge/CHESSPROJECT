import subprocess
import pygetwindow as gw
from datetime import datetime
import os
import time
import re

# Import your chess analysis function
from automation_chess import run_chess_analysis

# Import upload functions
from uploadScript import upload_video, update_video_metadata

def start_recording(duration_sec=60):
    chrome_windows = gw.getWindowsWithTitle('Chrome')
    if not chrome_windows:
        raise Exception("Chrome window not found.")
    
    left = max(0, 0)
    top = max(0, 0)
    width = 1920
    height = 1080

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    v_output_file = f"chrome_recording_{timestamp}.mp4"
    v_output_path = os.path.join(os.getcwd(), v_output_file)

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
        "-rtbufsize", "512M",
        "-i", "audio=CABLE Output (VB-Audio Virtual Cable)",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ac", "2",
        "-vsync", "2",                     # ✅ Sync video
        "-async", "1",                     # ✅ Sync audio
        "-t", str(duration_sec),
        "-shortest",
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

def trim_video(input_path, output_path, trim_start=22):
    trimmed_cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(trim_start),      # Start at 22 seconds
        "-i", input_path,
        "-c", "copy",                # Fast cut (no re-encoding)
        output_path
    ]
    subprocess.run(trimmed_cmd, check=True)


def main(pgn):

    last_move_number = get_last_move_number(pgn)
    record_time = 6 * last_move_number + 40

    # Start screen + audio recording
    record_proc, video_path = start_recording(record_time)

    try:
        brilliant_moves = run_chess_analysis(pgn)
    finally:
        if record_proc.poll() is None:
            print("🛑 Stopping recording...")
            record_proc.terminate()
            record_proc.wait()

    print(f"✅ Recording saved to: {video_path}")

    # === Generate dynamic title and description ===
    if brilliant_moves:
        move_phrase = f"Brilliant Move on Move {brilliant_moves[0]}"
    else:
        move_phrase = "Fast Tactical Game"

    white_name = re.search(r'\[White\s+"(.*?)"\]', pgn).group(1)
    black_name = re.search(r'\[Black\s+"(.*?)"\]', pgn).group(1)

    title = f"{move_phrase} – {white_name} vs {black_name}"
    description = f"""
This video showcases a chess game between {white_name} and {black_name}.
{move_phrase} detected by Chess.com Analysis.

Full PGN:
{pgn.strip()}

Analyzed and recorded by The Eighth Rank.
    """

    tags = [
        "chess", "brilliant move", "checkmate", "chess.com", "the eighth rank", 
        white_name.lower(), black_name.lower(), "samay raina", 
        "chessbase india", "vidit gujrathi"
    ]


    #Trim the video
    trimmed_path = video_path.replace(".mp4", "_trimmed.mp4")
    trim_video(video_path, trimmed_path)


    # === Upload to YouTube ===
    video_id = upload_video(
        video_path=trimmed_path,
        title=title,
        description="Uploading first draft...",
        tags=[],  # initially empty
        privacyStatus="public"
    )

    time.sleep(3)  # give YouTube time to index video

    update_video_metadata(
        video_id=video_id,
        title=title,
        description=description.strip(),
        tags=tags
    )

    print(f"✅ Upload completed with Video ID: {video_id}")


if __name__ == "__main__":
    import chess.pgn

    with open("gchess_top_10_best_games.pgn", "r", encoding="utf-8") as f:
        games_text = f.read()

    # Split PGNs on double newlines before [Event
    pgns = re.split(r'\n(?=\[Event )', games_text.strip())

    for i, pgn in enumerate(pgns, 1):
        print(f"\n🧩 Processing game {i}")
        main(pgn)

