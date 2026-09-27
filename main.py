from pathlib import Path
from typing import List
import sys
import uuid
from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    UploadFile
)
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from googleapiclient.errors import HttpError
from pydantic import BaseModel

import auth
import config
import youtube_client
import sorter


if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS"))
else:
    BASE_DIR = Path(__file__).resolve().parent

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


app = FastAPI()
sort_tasks = {}

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

class SortRequest(BaseModel):
    playlist_ids: List[str]
    user_prompt: str
    new_playlist_name: str

class GeminiKeyRequest(BaseModel):
    api_key: str

@app.post("/auth/credentials")
async def upload_credentials(
    file: UploadFile = File(...)
):
    if not file.filename:
        return {
            "success": False,
            "message": "Please select a JSON file."
        }

    if not file.filename.lower().endswith(".json"):
        return {
            "success": False,
            "message": "Please upload a JSON file."
        }

    content = await file.read()

    if not auth.validate_credentials_file(content):
        return {
            "success": False,
            "message": (
                "Invalid Google OAuth credentials file. "
                "Please upload a Desktop app OAuth JSON file."
            )
        }

    auth.save_credentials(content)

    # Force a new Google authorization
    # when new credentials are uploaded.
    auth.remove_token()

    return {
        "success": True,
        "message": "Google OAuth credentials saved successfully."
    }


@app.get("/")
async def home():
    authenticated = auth.is_authenticated()

    print(
        f"[HOME] authenticated={authenticated}"
    )

    if authenticated:
        print("[HOME] Serving index.html")

        return FileResponse(
            TEMPLATES_DIR / "index.html"
        )

    print("[HOME] Serving login.html")

    return FileResponse(
        TEMPLATES_DIR / "login.html"
    )

@app.get("/health")
async def health():
    return {
        "status": "API is running"
    }


@app.get("/auth/status")
async def auth_status():
    return {
        "authenticated": auth.is_authenticated(),
        "credentials_configured": auth.has_credentials()
    }


@app.get("/auth/login")
async def login():
    if not auth.has_credentials():
        return {
            "authenticated": False,
            "message": "Google OAuth credentials are not configured."
        }

    try:
        auth.authenticate()

        return {
            "authenticated": auth.is_authenticated()
        }

    except Exception as error:
        print(f"Authentication error: {error}")

        return {
            "authenticated": False,
            "message": str(error)
        }

@app.post("/auth/logout")
async def logout():
    auth.remove_token()

    return {
        "authenticated": False
    }


@app.get("/config/gemini")
async def get_gemini_config():
    return {
        "configured": config.get_gemini_api_key() is not None
    }


@app.post("/config/gemini")
async def save_gemini_config(
    body: GeminiKeyRequest
):
    api_key = body.api_key.strip()

    if not api_key:
        return {
            "success": False,
            "message": "Please enter a Gemini API key."
        }

    config.save_gemini_api_key(api_key)

    return {
        "success": True,
        "message": "Gemini API key saved successfully."
    }


@app.get("/playlists")
async def get_playlists():
    try:
        youtube = auth.get_youtube_service()

        raw_playlists = youtube_client.get_my_playlists(
            youtube
        )

        clean_playlists = []

        for playlist in raw_playlists:
            clean_playlists.append({
                "id": playlist["id"],
                "title": playlist["title"],
                "track_count": playlist["track_count"],
                "thumbnail": playlist["thumbnail"]
            })

        return clean_playlists

    except HttpError as error:
        print(
            f"YouTube API error: {error}"
        )

        return {
            "success": False,
            "message": (
                youtube_client
                .get_youtube_error_message(error)
            )
        }

    except Exception as error:
        print(
            f"Failed to load playlists: {error}"
        )

        return {
            "success": False,
            "message": (
                "Failed to load playlists. "
                "Please try again."
            )
        }


@app.post("/playlists/sort")
async def sort_playlists(
    body: SortRequest,
    background_tasks: BackgroundTasks
):
    task_id = str(uuid.uuid4())

    sort_tasks[task_id] = {
        "stage": "starting",
        "message": "Starting...",
        "current": 0,
        "total": 0,
        "percent": 0,
        "current_track": "",
        "done": False,
        "success": False
    }

    background_tasks.add_task(
        run_sort_task,
        task_id,
        body.playlist_ids,
        body.user_prompt,
        body.new_playlist_name
    )

    return {
        "task_id": task_id
    }

@app.get("/playlists/sort/status/{task_id}")
async def sort_status(task_id: str):
    task = sort_tasks.get(task_id)

    if not task:
        return {
            "done": True,
            "success": False,
            "error": "Sorting task was not found."
        }

    return task


def run_sort_task(
    task_id: str,
    playlist_ids: List[str],
    user_prompt: str,
    new_playlist_name: str
):
    global current_track
    task = sort_tasks[task_id]

    youtube = None
    new_playlist_id = None

    try:
        # =====================================
        # COLLECTING
        # =====================================

        task.update({
            "stage": "collecting",
            "message": "Collecting tracks...",
            "current": 0,
            "total": len(playlist_ids),
            "percent": 0,
            "current_track": ""
        })

        youtube = auth.get_youtube_service()

        all_tracks = []

        total_playlists = len(playlist_ids)

        for index, playlist_id in enumerate(
            playlist_ids,
            start=1
        ):
            tracks = youtube_client.get_playlist_tracks(
                youtube,
                playlist_id
            )

            all_tracks.extend(tracks)

            task.update({
                "stage": "collecting",
                "message": (
                    f"Collecting playlist "
                    f"{index} of {total_playlists}..."
                ),
                "current": index,
                "total": total_playlists,
                "percent": int(
                    index / total_playlists * 100
                ),
                "current_track": ""
            })

        # =====================================
        # REMOVE DUPLICATES
        # =====================================

        unique_tracks = []
        seen_ids = set()

        for track in all_tracks:
            video_id = track.get("video_id")

            if not video_id:
                continue

            if video_id in seen_ids:
                continue

            seen_ids.add(video_id)
            unique_tracks.append(track)

        print(
            f"Collected tracks: {len(unique_tracks)}"
        )

        # =====================================
        # AI ANALYSIS
        # =====================================

        task.update({
            "stage": "analyzing",
            "message": "AI is analyzing your music...",
            "current": 0,
            "total": len(unique_tracks),
            "percent": 0,
            "current_track": ""
        })

        filtered_tracks = sorter.filter_tracks_with_ai(
            unique_tracks,
            user_prompt
        )

        # =====================================
        # NO MATCHES
        # =====================================

        if not filtered_tracks:
            task.update({
                "stage": "completed",
                "message": (
                    "AI did not find any matching tracks."
                ),
                "current": 0,
                "total": 0,
                "percent": 100,
                "current_track": "",
                "done": True,
                "success": True,
                "result": {
                    "message": (
                        "AI did not find any tracks "
                        "matching your request."
                    ),
                    "source_playlists": len(playlist_ids),
                    "source_tracks": len(unique_tracks),
                    "selected_tracks": 0,
                    "added_tracks": 0,
                    "failed_tracks": 0,
                    "failed_track_names": [],
                    "url": None
                }
            })

            return

        # =====================================
        # CREATE PLAYLIST
        # =====================================

        task.update({
            "stage": "creating",
            "message": "Creating your playlist...",
            "current": 0,
            "total": 1,
            "percent": 0,
            "current_track": ""
        })

        new_playlist_id = youtube_client.create_playlist(
            youtube,
            new_playlist_name
        )

        # =====================================
        # ADD TRACKS
        # =====================================

        total_tracks = len(filtered_tracks)

        task.update({
            "stage": "adding",
            "message": "Adding tracks...",
            "current": 0,
            "total": total_tracks,
            "percent": 0,
            "current_track": ""
        })

        added_count = 0
        failed_tracks = []
        current_track = None

        for index, track in enumerate(
            filtered_tracks,
            start=1
        ):
            track_title = track.get(
                "title",
                "Unknown"
            )
            current_track = track

            task.update({
                "stage": "adding",
                "message": "Adding tracks...",
                "current": index - 1,
                "total": total_tracks,
                "percent": int(
                    (index - 1) / total_tracks * 100
                ),
                "current_track": track_title
            })

            success = (
                youtube_client
                .add_video_to_playlist_with_retry(
                    youtube=youtube,
                    playlist_id=new_playlist_id,
                    video_id=track["video_id"],
                    title=track_title
                )
            )

            if success:
                added_count += 1
            else:
                failed_tracks.append(track)

            task.update({
                "stage": "adding",
                "message": "Adding tracks...",
                "current": index,
                "total": total_tracks,
                "percent": int(
                    index / total_tracks * 100
                ),
                "current_track": track_title
            })

        # =====================================
        # SUCCESS
        # =====================================

        result = {
            "message": "Playlist created successfully!",
            "source_playlists": len(playlist_ids),
            "source_tracks": len(unique_tracks),
            "selected_tracks": len(filtered_tracks),
            "added_tracks": added_count,
            "failed_tracks": len(failed_tracks),
            "failed_track_names": [
                track.get(
                    "title",
                    "Unknown"
                )
                for track in failed_tracks
            ],
            "url": (
                "https://music.youtube.com/playlist"
                f"?list={new_playlist_id}"
            )
        }

        task.update({
            "stage": "completed",
            "message": "Sorting complete!",
            "current": total_tracks,
            "total": total_tracks,
            "percent": 100,
            "current_track": "",
            "done": True,
            "success": True,
            "result": result
        })

    # =====================================
    # QUOTA EXCEEDED
    # =====================================

    except youtube_client.YouTubeQuotaExceededError:
        print(
            "Sorting stopped because "
            "YouTube API quota was exceeded."
        )

        added_count = 0

        if new_playlist_id:
            # Count successfully added tracks
            # from the progress state.
            added_count = task.get(
                "current",
                0
            )

        failed_track_names = []

        if current_track:
            failed_track_names.append(
                current_track.get(
                    "title",
                    "Unknown"
                )
            )

        task.update({
            "stage": "completed",
            "message": (
                "YouTube API quota exceeded."
            ),
            "current": task.get("current", 0),
            "total": task.get("total", 0),
            "percent": 100,
            "current_track": "",
            "done": True,
            "success": True,
            "result": {
                "message": (
                    "YouTube API quota was exceeded "
                    "while adding tracks. "
                    "The playlist was created with "
                    "the tracks added before the quota "
                    "was reached."
                ),
                "source_playlists": len(playlist_ids),
                "source_tracks": len(unique_tracks),
                "selected_tracks": len(filtered_tracks),
                "added_tracks": added_count,
                "failed_tracks": (
                    len(filtered_tracks) - added_count
                ),
                "failed_track_names": failed_track_names,
                "url": (
                    "https://music.youtube.com/playlist"
                    f"?list={new_playlist_id}"
                    if new_playlist_id
                    else None
                ),
                "quota_exceeded": True
            }
        })

    # =====================================
    # YOUTUBE API ERROR
    # =====================================
    except sorter.GeminiSortingError as error:

        task.update({
            "stage": "error",
            "message": str(error),
            "current": 0,
            "total": 0,
            "percent": 0,
            "current_track": "",
            "done": True,
            "success": False,
            "error": str(error)
        })

    except HttpError as error:
        print(
            f"YouTube API error: {error}"
        )

        task.update({
            "stage": "error",
            "message": (
                youtube_client
                .get_youtube_error_message(error)
            ),
            "current_track": "",
            "done": True,
            "success": False,
            "error": (
                youtube_client
                .get_youtube_error_message(error)
            )
        })

    # =====================================
    # UNKNOWN ERROR
    # =====================================

    except Exception as error:
        print(
            f"Sort task failed: {error}"
        )

        task.update({
            "stage": "error",
            "message": (
                "Something went wrong "
                "while sorting your music."
            ),
            "current_track": "",
            "done": True,
            "success": False,
            "error": (
                "Something went wrong "
                "while sorting your music. "
                "Please try again."
            )
        })
