import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# Auth
flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
creds = flow.run_local_server(port=0)

youtube = build("youtube", "v3", credentials=creds)

# Upload
request_body = {
    "snippet": {
        "title": "Kasparov Immortal - Automated Analysis",
        "description": "Auto-analyzed using Selenium on chess.com",
        "tags": ["chess", "kasparov", "automation"]
    },
    "status": {
        "privacyStatus": "public"
    }
}

media_file = MediaFileUpload("recorded_video.mp4")

upload = youtube.videos().insert(
    part="snippet,status",
    body=request_body,
    media_body=media_file
).execute()

print(f"✅ Video uploaded: https://www.youtube.com/watch?v={upload['id']}")
