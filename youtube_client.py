import time

from googleapiclient.errors import HttpError

from auth import get_youtube_service

class YouTubeQuotaExceededError(Exception):
    pass

SCOPES = [
    "https://www.googleapis.com/auth/youtube"
]


def get_my_playlists(youtube):
    playlists = []

    next_page_token = None

    while True:
        request = youtube.playlists().list(
            part="snippet,contentDetails",
            mine=True,
            maxResults=50,
            pageToken=next_page_token
        )

        response = request.execute()

        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            thumbnails = snippet.get("thumbnails", {})

            thumbnail = (
                thumbnails.get("medium")
                or thumbnails.get("high")
                or thumbnails.get("default")
                or {}
            ).get("url")

            playlists.append({
                "id": item["id"],
                "title": snippet.get("title", ""),
                "track_count": item["contentDetails"]["itemCount"],
                "thumbnail": thumbnail
            })

        next_page_token = response.get("nextPageToken")

        if not next_page_token:
            break

    return playlists


def get_playlist_tracks(youtube, playlist_id: str):
    tracks = []

    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )

        response = request.execute()

        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            resource_id = snippet.get("resourceId", {})

            video_id = resource_id.get("videoId")

            if not video_id:
                continue

            tracks.append({
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "video_id": video_id
            })

        next_page_token = response.get("nextPageToken")

        if not next_page_token:
            break

    return tracks


def create_playlist(youtube, title: str):
    request = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": "Created with Ramma Sorter"
            },
            "status": {
                "privacyStatus": "private"
            }
        }
    )

    response = request.execute()

    return response["id"]


def add_video_to_playlist(
    youtube,
    playlist_id: str,
    video_id: str
):
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )

    request.execute()


def add_video_to_playlist_with_retry(
    youtube,
    playlist_id: str,
    video_id: str,
    title: str,
    max_attempts: int = 4
) -> bool:

    for attempt in range(max_attempts):

        try:
            add_video_to_playlist(
                youtube,
                playlist_id,
                video_id
            )

            print(f"Added: {title}")

            return True

        except HttpError as error:

            status = error.resp.status
            error_text = str(error).lower()

            # ---------------------------------
            # Quota exceeded
            # ---------------------------------

            if (
                    status == 403
                    and "quotaexceeded" in error_text
            ):
                print(
                    "YouTube API quota exceeded."
                )

                print(
                    f"Stopping track addition: {title}"
                )

                raise YouTubeQuotaExceededError(
                    "YouTube API quota exceeded."
                )

            # ---------------------------------
            # Permanent errors
            # ---------------------------------

            if status in (400, 401, 403, 404):

                print(
                    f"Permanent YouTube API error "
                    f"for: {title}"
                )

                print(
                    f"YouTube API: {error}"
                )

                return False

            # ---------------------------------
            # Temporary errors
            # ---------------------------------

            print(
                f"Attempt "
                f"{attempt + 1}/{max_attempts} "
                f"failed for: {title}"
            )

            print(
                f"YouTube API: {error}"
            )

            if attempt == max_attempts - 1:
                break

            wait_time = 2 ** attempt

            print(
                f"Retrying in "
                f"{wait_time} seconds..."
            )

            time.sleep(wait_time)

        except Exception as error:

            print(
                f"Unexpected error "
                f"for {title}: {error}"
            )

            if attempt == max_attempts - 1:
                break

            wait_time = 2 ** attempt

            time.sleep(wait_time)

    print(
        f"Failed after "
        f"{max_attempts} attempts: {title}"
    )

    return False


def get_youtube_error_message(error: HttpError) -> str:
    status = error.resp.status
    error_text = str(error).lower()

    if status == 401:
        return (
            "Google authorization expired. "
            "Please reconnect your Google account."
        )

    if status == 403:

        if "quotaexceeded" in error_text:
            return (
                "YouTube API quota exceeded. "
                "Please check the quota of your "
                "Google Cloud project."
            )

        return (
            "YouTube API access was denied. "
            "Please check your Google Cloud "
            "project and API permissions."
        )

    if status == 404:
        return (
            "The requested YouTube resource "
            "was not found."
        )

    if status >= 500:
        return (
            "YouTube is temporarily unavailable. "
            "Please try again later."
        )

    return (
        "YouTube API request failed. "
        "Please try again."
    )


if __name__ == "__main__":
    youtube = get_youtube_service()

    print(
        "Authorization successful! "
        "Looking for playlists..."
    )

    my_playlists = get_my_playlists(youtube)

    for playlist in my_playlists:
        print(
            f"Playlist: {playlist['title']} | "
            f"Tracks: {playlist['track_count']} | "
            f"ID: {playlist['id']}"
        )