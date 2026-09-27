# Ramma Sorter

Ramma Sorter is an AI-powered local application for organizing YouTube playlists.

It lets you:

* Connect your own Google / YouTube account.
* Select one or multiple playlists.
* Describe the kind of music you want using natural language.
* Let AI analyze your tracks.
* Automatically create a new private playlist containing the selected tracks.
* Open the resulting playlist directly in YouTube Music.

The application is designed to run locally on your computer.

---

## How authentication works

Ramma Sorter does **not** use the developer's Google OAuth credentials.

Each user creates their own Google Cloud project and OAuth credentials.

The authentication flow is:

```text
Your Google Cloud Project
        │
        │ OAuth credentials
        ▼
   Ramma Sorter
        │
        │ OAuth authorization
        ▼
 Your Google / YouTube account
```

This means you use your own Google Cloud project for YouTube Data API requests and quota accounting.

Your `client_secret.json` and generated `token.json` stay on your local machine.

---

# Requirements

Before installing Ramma Sorter, make sure you have:

* Python 3.8 or newer
* A Google account
* A Google Cloud project
* YouTube Data API v3 enabled
* Google OAuth 2.0 Desktop credentials
* A Gemini API key

---

# 1. Clone the repository

Clone the repository:

```bash
git clone <YOUR_REPOSITORY_URL>
cd Ramma_sorter
```

---

# 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

You should see:

```text
(venv)
```

at the beginning of your terminal prompt.

---

# 3. Install dependencies

Install the required packages:

```powershell
pip install -r requirements.txt
```

If `requirements.txt` does not contain `python-multipart`, install it manually:

```powershell
pip install python-multipart
```

---

# 4. Create your Google Cloud project

Open the Google Cloud Console:

https://console.cloud.google.com/

Create a new project for Ramma Sorter.

You can use any project name, for example:

```text
Ramma Sorter
```

It is recommended to create a separate project for this application.

---

# 5. Enable YouTube Data API v3

Open the API Library:

https://console.cloud.google.com/apis/library

Search for:

```text
YouTube Data API v3
```

Open it and click:

```text
Enable
```

Google's official YouTube API documentation also provides the API setup instructions:

https://developers.google.com/youtube/v3/getting-started

---

# 6. Configure Google OAuth

Open Google Auth Platform:

https://console.cloud.google.com/auth/overview

You may be asked to configure your OAuth application.

Configure the application information / branding.

Google's OAuth documentation:

https://developers.google.com/workspace/guides/configure-oauth-consent

For a personal/local application, follow Google's current OAuth setup flow and provide the required application information.

If Google asks you to configure test users, add the Google account that you will use with Ramma Sorter.

---

# 7. Create OAuth credentials

Open the Google Cloud Credentials page:

https://console.cloud.google.com/apis/credentials

Create a new OAuth client.

For the current local Ramma Sorter setup, create:

```text
OAuth Client ID
Application type: Desktop app
```

Give it a recognizable name, for example:

```text
Ramma Sorter Desktop
```

Google's documentation for installed / desktop applications:

https://developers.google.com/youtube/v3/guides/auth/installed-apps

---

# 8. Download client_secret.json

After creating the OAuth client, download the credentials JSON file.

Google will provide a JSON file containing your OAuth client configuration.

Rename it to:

```text
client_secret.json
```

Do **not** publish this file to GitHub.

Do **not** send your credentials to other people.

---

# 9. Create a Gemini API key

Ramma Sorter uses Gemini to analyze music according to the user's description.

Create your Gemini API key using Google's Gemini / AI Studio:

https://aistudio.google.com/apikey

Create a new API key.

Then create a `.env` file in the Ramma Sorter project directory:

```text
.env
```

Add:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Replace:

```text
YOUR_GEMINI_API_KEY
```

with your actual key.

Never commit `.env` to GitHub.

---

# 10. Start Ramma Sorter

Start the FastAPI server:

```powershell
uvicorn main:app --reload
```

You should see something similar to:

```text
Uvicorn running on http://127.0.0.1:8000
```

Open:

https://127.0.0.1:8000

Or:

```text
http://127.0.0.1:8000
```

---

# 11. Connect your Google account

When you open Ramma Sorter for the first time, you will see the authentication page.

Upload:

```text
client_secret.json
```

Then click:

```text
Connect Google Account
```

Your browser will open Google's authorization page.

Sign in with the Google account whose YouTube playlists you want to manage.

Review the requested permissions and allow access.

After successful authentication, Ramma Sorter will store the authorization token locally.

---

# 12. Using Ramma Sorter

After authentication:

### Select playlists

Select one or multiple playlists from your YouTube library.

### Describe the music

Enter a natural-language request.

For example:

```text
Dark and aggressive rap for the gym.
Heavy bass, energetic tracks and a hard atmosphere.
```

You can write the request in any language supported by the AI model.

### Name the new playlist

For example:

```text
Gym Rage
```

### Start sorting

Click:

```text
Sort my music
```

Ramma Sorter will:

1. Fetch tracks from the selected playlists.
2. Remove duplicate videos.
3. Send the track information and your request to Gemini.
4. Select matching tracks.
5. Create a new private YouTube playlist.
6. Add the selected tracks.
7. Provide a link to the resulting playlist in YouTube Music.

---

# API quota

YouTube Data API uses project-based quota.

Different API operations consume different amounts of quota.

For example, playlist operations such as inserting playlist items consume quota units.

Because Ramma Sorter is designed to use your own Google Cloud project, you should create and use your own OAuth credentials instead of sharing credentials from another project.

You can monitor your project's API usage in Google Cloud Console:

https://console.cloud.google.com/apis/dashboard

YouTube Data API documentation:

https://developers.google.com/youtube/v3/getting-started

API reference:

https://developers.google.com/youtube/v3/docs

---

# Security

Never commit these files to GitHub:

```text
client_secret.json
token.json
.env
```

Your `.gitignore` should contain:

```gitignore
venv/
.venv/
__pycache__/
*.pyc

.env

client_secret.json
token.json

credentials/
```

OAuth credentials and tokens are sensitive.

Do not post them in screenshots, GitHub issues, Discord, Telegram, or public repositories.

---

# Logging out

Use the:

```text
Disconnect
```

button inside Ramma Sorter.

This removes the locally stored authentication token.

The next time you connect an account, Google authentication will be performed again.

---

# Troubleshooting

## `client_secret.json was not found`

Make sure you have uploaded your OAuth credentials through the Ramma Sorter login page.

The file must be named:

```text
client_secret.json
```

---

## YouTube Data API is not enabled

Open:

https://console.cloud.google.com/apis/library

Search for:

```text
YouTube Data API v3
```

Make sure it is enabled in the same Google Cloud project that owns your OAuth credentials.

---

## OAuth authentication fails

Check that:

* You created an OAuth 2.0 Client ID.
* The OAuth client is configured for a desktop application.
* You are using the correct Google account.
* The YouTube Data API is enabled.
* Your Google account is allowed as a test user if your OAuth application is in testing mode.

---

## `quotaExceeded`

YouTube Data API has project-based quota limits.

Check your Google Cloud project:

https://console.cloud.google.com/apis/dashboard

If you are repeatedly adding a large number of tracks, remember that playlist item insertion consumes quota.

---

## Gemini errors

Check your `.env` file:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Make sure the key is valid and that the corresponding Gemini service is available for your account/project.

---

# Development

Start the development server:

```powershell
uvicorn main:app --reload
```

The `--reload` option automatically restarts the server when Python source files change.

---

# Project structure

```text
Ramma_sorter/
│
├── main.py
├── auth.py
├── youtube_client.py
├── sorter.py
│
├── templates/
│   ├── index.html
│   └── login.html
│
├── static/
│   ├── style.css
│   ├── app.js
│   └── login.js
│
├── .env
├── client_secret.json
├── token.json
├── requirements.txt
├── .gitignore
└── README.md
```

---

# Official documentation

### Google Cloud Console

https://console.cloud.google.com/

### Google Cloud API Library

https://console.cloud.google.com/apis/library

### Google Cloud Credentials

https://console.cloud.google.com/apis/credentials

### Google Auth Platform

https://console.cloud.google.com/auth/overview

### YouTube Data API

https://developers.google.com/youtube/v3/getting-started

### YouTube Data API Reference

https://developers.google.com/youtube/v3/docs

### YouTube OAuth for Desktop Apps

https://developers.google.com/youtube/v3/guides/auth/installed-apps

### Google OAuth documentation

https://developers.google.com/workspace/guides/configure-oauth-consent

### Gemini API Key

https://aistudio.google.com/apikey

---

# License

Add your preferred license here.
