# Ramma Sorter

AI-powered YouTube Music playlist sorter.

Ramma Sorter analyzes your existing YouTube playlists using Gemini AI and creates a new playlist containing tracks that match your description.

Instead of manually searching through hundreds of songs, simply select your playlists and describe what you want to find.

## Features

* Select one or multiple YouTube playlists
* Automatically collect and deduplicate tracks
* Describe your desired music using natural language
* AI-powered track filtering with Gemini
* Create a new private YouTube playlist automatically
* Add matching tracks directly to the new playlist
* Real-time sorting progress
* YouTube Music playlist links
* Local credential and API key storage
* Windows standalone executable
* No Python installation required for end users

## How It Works

```text
Your YouTube Playlists
        |
        v
Select Playlists
        |
        v
Collect Tracks
        |
        v
Remove Duplicates
        |
        v
Gemini AI Analysis
        |
        v
Select Matching Tracks
        |
        v
Create New Playlist
        |
        v
Add Tracks
        |
        v
Open in YouTube Music
```

Gemini primarily analyzes track titles and artists. YouTube descriptions are used only as additional context when the title does not provide enough information.

## Screenshots

Screenshots will be added here.

## For Windows Users

### Requirements

* Windows 10 or newer
* Google account
* YouTube account
* Gemini API key
* Your own Google Cloud OAuth credentials

You do **not** need:

* Python
* pip
* VS Code
* FastAPI
* Git

### Installation

1. Download the latest Windows release from the GitHub Releases page.
2. Extract the downloaded ZIP archive.
3. Run `RammaSorter.exe`.
4. The application will automatically open in your default browser.
5. Follow the first-run setup instructions.
6. Configure your Google OAuth credentials.
7. Connect your YouTube account.
8. Enter your Gemini API key.
9. Select the playlists you want to analyze.
10. Describe the music you want to find.
11. Enter a name for the new playlist.
12. Start sorting.

The application stores its local configuration under:

```text
%APPDATA%\RammaSorter\
```

This includes:

```text
client_secret.json
token.json
config.json
```

Your credentials are stored locally on your computer and are not committed to the project repository.

## Google Cloud Setup

Ramma Sorter uses the YouTube Data API to access your playlists and create new playlists.

You need to create your own Google Cloud project and configure OAuth credentials for the application.

### Required API

Enable:

```text
YouTube Data API v3
```

Create OAuth credentials for a **Desktop application** and download the resulting JSON file.

Ramma Sorter validates the uploaded credentials and stores them locally in:

```text
%APPDATA%\RammaSorter\client_secret.json
```

Uploading new credentials removes the previously stored YouTube authorization token so that the account can be authorized again.

## Gemini API Setup

Ramma Sorter uses the Gemini API for music filtering.

Create your own Gemini API key and enter it in the application during setup.

The key is stored locally in:

```text
%APPDATA%\RammaSorter\config.json
```

Example:

```json
{
    "gemini_api_key": "YOUR_API_KEY"
}
```

Never commit your API key to Git.

## YouTube API Quota

YouTube Data API requests are subject to Google's quota system.

Ramma Sorter uses the YouTube API to:

* Read playlists
* Read playlist tracks
* Create playlists
* Add videos to playlists

Large playlists may require a significant number of API requests.

If you reach your project's quota limit, you may need to wait for the quota to reset or review your quota and usage in Google Cloud.

Each user should use their own Google Cloud project and OAuth credentials rather than sharing credentials with other users.

## Security

Ramma Sorter is designed so that sensitive credentials are stored outside the application directory.

Local application data is stored in:

```text
%APPDATA%\RammaSorter\
```

The following files should never be uploaded to GitHub:

```text
client_secret.json
token.json
config.json
```

The repository includes a `.gitignore` configuration to prevent sensitive files and local development artifacts from being committed accidentally.

## For Developers

### Requirements

* Python 3.12+
* Git

### Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
cd Ramma_sorter
```

### Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### Install Dependencies

```powershell
pip install -r requirements.txt
```

### Run the Application

Start the launcher:

```powershell
python launcher.py
```

The launcher starts the FastAPI server and automatically opens the application in your default browser.

The development server is available at:

```text
http://127.0.0.1:8000
```

### API Health Check

The application provides:

```text
GET /health
```

Expected response:

```json
{
    "status": "API is running"
}
```

## Project Structure

```text
Ramma_sorter/
├── auth.py
├── config.py
├── launcher.py
├── main.py
├── sorter.py
├── youtube_client.py
├── requirements.txt
├── LICENSE
├── README.md
├── .gitignore
├── static/
│   ├── app.js
│   ├── favicon.svg
│   ├── login.js
│   └── style.css
└── templates/
    ├── index.html
    └── login.html
```

### Main Components

**`main.py`**

FastAPI application and API routes.

**`auth.py`**

Google OAuth authentication and credential management.

**`config.py`**

Local Gemini API key configuration.

**`youtube_client.py`**

YouTube Data API operations.

**`sorter.py`**

Gemini-powered music filtering.

**`launcher.py`**

Starts the FastAPI server and opens the application in the browser.

**`static/`**

Frontend JavaScript, CSS and favicon.

**`templates/`**

HTML pages used by the application.

## Technology Stack

* Python
* FastAPI
* Uvicorn
* Google YouTube Data API v3
* Google OAuth 2.0
* Gemini API
* JavaScript
* HTML
* CSS
* PyInstaller

## License

Ramma Sorter is licensed under the MIT License.

See the [LICENSE](LICENSE) file for details.
