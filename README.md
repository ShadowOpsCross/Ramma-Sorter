# Ramma Sorter

AI-powered YouTube Music playlist sorter.

Ramma Sorter uses Gemini AI to analyze your existing YouTube playlists and create a new playlist containing tracks that match your description.

Instead of manually searching through hundreds of songs, select your playlists and describe what you want to find.

---

## Download for Windows

### For regular users

You **do not need Python, pip, Git, VS Code, or any development tools** to use Ramma Sorter.

**[Download the latest Windows release](https://github.com/ShadowOpsCross/Ramma-Sorter/releases/latest)**

### Installation

1. Download `RammaSorter-Windows.zip` from the latest release.
2. Extract the ZIP archive.
3. Open the extracted folder.
4. Run `RammaSorter.exe`.
5. The application will automatically open in your default browser.
6. Follow the first-run setup instructions.

That's it.

---

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

---

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

Gemini primarily analyzes track titles and artists.

YouTube playlist descriptions are used only as additional context when the title does not provide enough information.

---

# First-Run Setup

When you launch Ramma Sorter for the first time, you will need to configure:

1. Google OAuth credentials
2. Your YouTube account
3. Gemini API key

Your credentials and API key are stored locally on your computer.

Application data is stored in:

```text
%APPDATA%\RammaSorter\
```

The directory may contain:

```text
client_secret.json
token.json
config.json
```

These files are local to your computer and are not uploaded to the Ramma Sorter repository.

---

# Google Cloud Setup

Ramma Sorter uses the YouTube Data API v3 to access your playlists and create new playlists.

Each user should create and use their own Google Cloud project and OAuth credentials.

## 1. Create a Google Cloud project

Create a project in Google Cloud Console.

## 2. Enable YouTube Data API v3

Enable:

```text
YouTube Data API v3
```

for your project.

## 3. Configure OAuth

Create OAuth credentials for a:

```text
Desktop application
```

Download the generated JSON file.

Ramma Sorter expects the standard Google OAuth client configuration containing the `installed` section.

## 4. Upload the credentials

During the first-run setup, upload the downloaded JSON file.

Ramma Sorter validates the credentials and stores them locally as:

```text
%APPDATA%\RammaSorter\client_secret.json
```

If you upload new Google OAuth credentials later, the existing YouTube authorization token is removed so that the account can be authorized again.

---

# Gemini API Setup

Ramma Sorter uses Gemini AI to filter tracks according to your description.

Create your own Gemini API key and enter it during the application setup.

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

Never publish your Gemini API key or commit it to Git.

---

# YouTube API Quota

YouTube Data API requests are subject to Google's quota system.

Ramma Sorter uses the YouTube API to:

* Read playlists
* Read playlist tracks
* Create playlists
* Add videos to playlists

Large playlists may require a significant number of API requests.

If your project reaches its quota limit, you may need to wait for the quota to reset or review your API usage and quota configuration in Google Cloud.

Each user should use their own Google Cloud project and OAuth credentials rather than sharing credentials with other users.

---

# Security

Ramma Sorter stores sensitive credentials outside the application directory.

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

The project includes a `.gitignore` configuration to prevent sensitive files and local development artifacts from being committed accidentally.

Your Google OAuth credentials and Gemini API key are stored locally and are not included in the Windows release archive.

---

# Screenshots

Screenshots will be added here.

---

# For Developers

This section is intended for developers who want to run, inspect, modify, or contribute to Ramma Sorter.

## Requirements

* Windows 10 or newer
* Python 3.12+
* Git

## Clone the Repository

```powershell
git clone https://github.com/ShadowOpsCross/Ramma-Sorter.git
cd Ramma-Sorter
```

## Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Verify Python:

```powershell
python --version
```

Python 3.12 or newer is recommended.

## Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

## Run the Application

Start the launcher:

```powershell
python launcher.py
```

The launcher starts the FastAPI server and automatically opens the application in your default browser.

The local development server is available at:

```text
http://127.0.0.1:8000
```

---

# API

The application provides a basic health endpoint:

```text
GET /health
```

Expected response:

```json
{
    "status": "API is running"
}
```

---

# Building the Windows Executable

The Windows release is built using PyInstaller.

Install PyInstaller:

```powershell
python -m pip install pyinstaller
```

Build the executable:

```powershell
python -m PyInstaller --onefile --windowed --clean --name RammaSorter --icon=icon.ico --add-data "templates;templates" --add-data "static;static" launcher.py
```

The executable will be created at:

```text
dist\RammaSorter.exe
```

The executable is standalone and contains the application code and required frontend files.

---

# Creating a Windows Release

The Windows release should contain only the executable:

```text
RammaSorter-Windows/
└── RammaSorter.exe
```

Create the release ZIP:

```powershell
Compress-Archive `
    -Path .\release\RammaSorter-Windows `
    -DestinationPath .\release\RammaSorter-Windows.zip `
    -Force
```

The resulting archive can be uploaded to the GitHub Releases page.

The executable itself should not be committed to the Git repository.

---

# Project Structure

```text
Ramma-Sorter/
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
├── icon.ico
├── static/
│   ├── app.js
│   ├── favicon.svg
│   ├── login.js
│   └── style.css
└── templates/
    ├── index.html
    └── login.html
```

---

# Main Components

### `main.py`

FastAPI application and API routes.

### `auth.py`

Google OAuth authentication, token management, and credential management.

### `config.py`

Local Gemini API key configuration.

### `youtube_client.py`

YouTube Data API operations such as retrieving playlists, creating playlists, and adding videos.

### `sorter.py`

Gemini-powered music filtering and track selection.

### `launcher.py`

Starts the FastAPI server, waits for the health endpoint, and opens the application in the browser.

### `static/`

Frontend JavaScript, CSS, and favicon files.

### `templates/`

HTML pages used by the application.

---

# Technology Stack

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

---

# License

Ramma Sorter is licensed under the MIT License.

See the [LICENSE](LICENSE) file for details.

---

# Repository

Source code:

https://github.com/ShadowOpsCross/Ramma-Sorter

Windows releases:

https://github.com/ShadowOpsCross/Ramma-Sorter/releases
