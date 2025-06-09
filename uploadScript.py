# import os
# import time
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
# from google.auth.transport.requests import Request

# # Scopes for uploading videos
# SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

# def authenticate_youtube():
#     creds = None
#     if os.path.exists("token.json"):
#         creds = Credentials.from_authorized_user_file("token.json", SCOPES)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file("client.json", SCOPES)
#             creds = flow.run_local_server(port=8081)
#         with open("token.json", "w") as token:
#             token.write(creds.to_json())
#     return build("youtube", "v3", credentials=creds)

# def upload_video(video_path, title, description="", tags=[], categoryId="20", privacyStatus="public"):
#     youtube = authenticate_youtube()

#     request_body = {
#         "snippet": {
#             "title": title,
#             "description": description,
#             "tags": tags,
#             "categoryId": categoryId  # 20 = Gaming
#         },
#         "status": {
#             "privacyStatus": privacyStatus,
#         }
#     }

#     media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/*")
#     request = youtube.videos().insert(
#         part="snippet,status",
#         body=request_body,
#         media_body=media
#     )

#     response = None
#     while response is None:
#         status, response = request.next_chunk()
#         if status:
#             print(f"Uploading... {int(status.progress() * 100)}%")

#     print(f"✅ Upload successful! Video ID: {response['id']}")
#     return response

# # Example usage
# if __name__ == "__main__":
#     upload_video(
#         video_path="testUpload.mp4",
#         title="Brilliant Checkmate! ♟️ | The Eighth Rank",
#         description="A short brilliant checkmate breakdown | The Eighth Rank",
#         tags=["chess", "brilliant moves", "the eighth rank"],
#         privacyStatus="public"  # or "unlisted", "private"
#     )


import os
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Scopes for uploading videos
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def authenticate_youtube():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client.json", SCOPES)
            creds = flow.run_local_server(port=8081)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def upload_video(video_path, title, description="", tags=[], categoryId="20", privacyStatus="public"):
    youtube = authenticate_youtube()

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": categoryId
        },
        "status": {
            "privacyStatus": privacyStatus,
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/*")
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading... {int(status.progress() * 100)}%")

    print(f"✅ Upload successful! Video ID: {response['id']}")
    return response['id']

def update_video_metadata(video_id, title, description, tags, categoryId="20"):
    youtube = authenticate_youtube()

    request_body = {
        "id": video_id,
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": categoryId
        }
    }

    response = youtube.videos().update(
        part="snippet",
        body=request_body
    ).execute()

    print("✅ Metadata updated (title, description, tags)")
    return response

# Example usage
if __name__ == "__main__":
    video_id = upload_video(
        video_path="testUpload.mp4",
        title="Brilliant Checkmate! ♟️ | The Eighth Rank",
        description="Uploading first draft...",
        tags=[],
        privacyStatus="public"
    )

    time.sleep(3)  # Wait a few seconds to ensure YouTube has indexed the video

    update_video_metadata(
        video_id=video_id,
        title="Brilliant Checkmate! ♟️ | The Eighth Rank",
        description="Hell This video showcases a brilliant chess checkmate in under 60 moves! Analyzed and presented by The Eighth Rank.",
        tags=["chess", "brilliant move", "checkmate", "the eighth rank"]
    )
