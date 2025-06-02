import sys

# For Python 3.8+ (which includes your 3.13)
if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    # Fallback for older Python versions, though not needed for you
    try:
        import importlib_metadata as metadata
    except ImportError:
        metadata = None

try:
    if metadata:
        version = metadata.version("obs-websocket-py")
        print(f"DEBUG: obs-websocket-py version installed: {version}")
    else:
        print("DEBUG: Could not determine obs-websocket-py version (importlib.metadata not available/fallback failed).")
except metadata.PackageNotFoundError:
    print("DEBUG: obs-websocket-py not found in this environment via importlib.metadata.")
except Exception as e:
    print(f"DEBUG: Error getting obs-websocket-py version: {e}")

from obswebsocket import obsws, requests
# We will not attempt to import specific OBS-related exceptions here
# as they seem to not be directly exposed in your version.
# Instead, we'll rely on general Python exceptions.

import time
import socket # Import socket to catch ConnectionRefusedError and TimeoutError

host = "192.168.1.2"  # your OBS server IP
port = 4455           # OBS WebSocket port
password = "Virat123" # your OBS WebSocket password

ws = None # Initialize ws to None for the finally block

try:
    print(f"Attempting to connect to OBS WebSocket at {host}:{port}...")
    ws = obsws(host, port, password)
    ws.connect()
    print("✅ Connected to remote OBS")

    # --- Diagnostic Steps ---

    # 1. Get Recording Status (Crucial for debugging)
    try:
        response = ws.call(requests.GetRecordingStatus())
        is_recording = response.getRecording()
        print(f"Current recording status: {'Recording' if is_recording else 'Not recording'}")
        if is_recording:
            print("Warning: OBS was already recording!")
            # Consider stopping it if you want to ensure a fresh start
            # ws.call(requests.StopRecording())
            # time.sleep(1) # Give OBS a moment to stop
    except Exception as e: # Catch any exception during this call
        print(f"Error getting recording status: {e}")

    # 2. Get Studio Mode Status (Can sometimes affect behavior)
    try:
        response = ws.call(requests.GetStudioModeStatus())
        print(f"Studio Mode enabled: {response.getStudioModeEnabled()}")
    except Exception as e: # Catch any exception during this call
        print(f"Error getting studio mode status: {e}")


    # 3. Check for specific OBS errors after starting recording
    try:
        print("Attempting to start recording...")
        start_response = ws.call(requests.StartRecording())
        print("🎥 StartRecording request sent.")

        # --- Re-check recording status immediately after the call ---
        time.sleep(1) # Give OBS a very brief moment to initiate recording
        status_after_start = ws.call(requests.GetRecordingStatus())
        if status_after_start.getRecording():
            print("✅ Recording confirmed to be started!")
        else:
            print("❌ Recording did NOT start after request. Check OBS logs for errors!")

    except Exception as e: # Catch any exception during this call
        print(f"Error starting recording: {e}")

    print("Recording for 10 seconds...")
    time.sleep(10)  # record for 10 seconds

    print("Attempting to stop recording...")
    try:
        ws.call(requests.StopRecording())
        print("🛑 StopRecording request sent.")
        # --- Re-check recording status immediately after the call ---
        time.sleep(1) # Give OBS a very brief moment to stop recording
        status_after_stop = ws.call(requests.GetRecordingStatus())
        if not status_after_stop.getRecording():
            print("✅ Recording confirmed to be stopped!")
        else:
            print("❌ Recording did NOT stop after request. Check OBS logs for errors!")

    except Exception as e: # Catch any exception during this call
        print(f"Error stopping recording: {e}")

# Catch connection-specific errors first, if they occur before ws.connect() fully succeeds
except (socket.timeout, ConnectionRefusedError) as e:
    print(f"❌ Connection failed (Network Error): {e}. Please ensure OBS is running and OBS WebSocket is enabled with the correct IP, port, and password.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    if ws:
        try:
            ws.disconnect()
            print("✅ Disconnected from OBS")
        except Exception as e:
            print(f"Error during disconnection: {e}")
    else:
        print("No active connection to disconnect.")