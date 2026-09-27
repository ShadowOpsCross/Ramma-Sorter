let playlists = [];


document.addEventListener("DOMContentLoaded", () => {
    loadPlaylists();
});


async function loadPlaylists() {
    const container = document.getElementById(
        "playlists-container"
    );

    const refreshButton = document.getElementById(
        "refresh-button"
    );

    refreshButton.disabled = true;

    container.innerHTML = `
        <div class="loading">
            Loading playlists...
        </div>
    `;

    try {
        const response = await fetch("/playlists");

        const data = await response.json();

        /*
         * Backend returned an error.
         */
        if (
            !response.ok ||
            !Array.isArray(data)
        ) {
            throw new Error(
                data.message ||
                "Failed to load playlists."
            );
        }

        playlists = data;

        renderPlaylists();

    } catch (error) {
        console.error(error);

        container.innerHTML = `
            <div class="error-box">
                ${escapeHtml(
                    error.message ||
                    "Failed to load playlists."
                )}
            </div>
        `;

    } finally {
        refreshButton.disabled = false;
    }
}


function renderPlaylists() {
    const container = document.getElementById(
        "playlists-container"
    );

    if (playlists.length === 0) {
        container.innerHTML = `
            <div class="empty-box">
                No playlists found.
            </div>
        `;

        return;
    }

    container.innerHTML = playlists.map(
    (playlist) => `
        <label class="playlist-card">

            <input
                type="checkbox"
                value="${playlist.id}"
                class="playlist-checkbox"
            >

            <div class="playlist-thumbnail">
                ${
                    playlist.thumbnail
                        ? `
                            <img
                                src="${playlist.thumbnail}"
                                alt=""
                                loading="lazy"
                            >
                        `
                        : `
                            <div class="thumbnail-placeholder">
                                ♪
                            </div>
                        `
                }
            </div>

            <div class="playlist-info">

                <div class="playlist-title">
                    ${escapeHtml(playlist.title)}
                </div>

                <div class="playlist-count">
                    ${playlist.track_count} tracks
                </div>

            </div>

            <div class="playlist-check">
                ✓
            </div>

        </label>
    `
).join("");
}


async function sortPlaylists() {
    const selectedPlaylists = Array.from(
        document.querySelectorAll(
            ".playlist-checkbox:checked"
        )
    ).map(
        (checkbox) => checkbox.value
    );


    const userPrompt = document
        .getElementById("user-prompt")
        .value
        .trim();


    const playlistName = document
        .getElementById("playlist-name")
        .value
        .trim();


    const status = document.getElementById("status");
    const button = document.getElementById("sort-button");


    if (selectedPlaylists.length === 0) {
        showStatus(
            "Select at least one playlist.",
            "error"
        );

        return;
    }


    if (!userPrompt) {
        showStatus(
            "Describe what kind of music you want.",
            "error"
        );

        return;
    }


    if (!playlistName) {
        showStatus(
            "Enter a name for the new playlist.",
            "error"
        );

        return;
    }


    button.disabled = true;
    button.textContent = "Sorting...";

    hideResult();
    showProgress();


    try {
        const response = await fetch(
            "/playlists/sort",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    playlist_ids: selectedPlaylists,
                    user_prompt: userPrompt,
                    new_playlist_name: playlistName
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.detail ||
                data.message ||
                "Sorting failed."
            );
        }


        if (!data.task_id) {
            throw new Error(
                "Sorting task was not created."
            );
        }


        await pollSortStatus(
            data.task_id
        );


    } catch (error) {
        console.error(error);

        hideProgress();

        showStatus(
            error.message ||
            "Something went wrong.",
            "error"
        );

    } finally {
        button.disabled = false;
        button.textContent = "Sort playlists";
    }
}

async function pollSortStatus(taskId) {
    while (true) {
        const response = await fetch(
            `/playlists/sort/status/${taskId}`
        );


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.error ||
                "Failed to get sorting status."
            );
        }


        updateProgress(data);


        if (data.done) {

            if (!data.success) {
                throw new Error(
                    data.error ||
                    "Sorting failed."
                );
            }


            hideProgress();


            showStatus(
                "Playlist created successfully!",
                "success"
            );


            showResult(
                data.result
            );


            return;
        }


        await sleep(500);
    }
}

function sleep(milliseconds) {
    return new Promise(
        (resolve) => {
            setTimeout(
                resolve,
                milliseconds
            );
        }
    );
}


function updateProgress(data) {
    const title = document.getElementById(
        "progress-title"
    );

    const percent = document.getElementById(
        "progress-percent"
    );

    const bar = document.getElementById(
        "progress-bar"
    );

    const count = document.getElementById(
        "progress-count"
    );

    const trackName = document.getElementById(
        "progress-track-name"
    );


    const progressPercent =
    Number(data.percent) || 0;

    bar.style.width =
        `${progressPercent}%`;

    percent.textContent =
        `${progressPercent}%`;


    title.textContent =
        getProgressTitle(data.stage);


    if (
        data.total > 0 &&
        data.stage === "adding"
    ) {
        count.textContent =
            `${data.current} of ${data.total} tracks`;
    } else {
        count.textContent =
            data.message || "";
    }


    if (data.current_track) {
        trackName.textContent =
            `♫ ${data.current_track}`;
    } else {
        trackName.textContent = "";
    }
}

function getProgressTitle(stage) {
    switch (stage) {
        case "collecting":
            return "Collecting your music...";

        case "analyzing":
            return "AI is analyzing your music...";

        case "creating":
            return "Creating your playlist...";

        case "adding":
            return "Adding tracks...";

        case "completed":
            return "Sorting complete!";

        default:
            return "Preparing...";
    }
}

function showProgress() {
    const progress = document.getElementById(
        "progress-panel"
    );

    progress.classList.remove("hidden");


    updateProgress({
        stage: "starting",
        message: "Starting...",
        current: 0,
        total: 0,
        percent: 0,
        current_track: ""
    });
}


function showResult(data) {
    const result = document.getElementById("result");

    result.classList.remove("hidden");


    let failedTracks = "";


    if (
        data.failed_track_names &&
        data.failed_track_names.length > 0
    ) {
        failedTracks = `
            <div class="failed-tracks">
                <h3>Failed tracks</h3>

                <ul>
                    ${data.failed_track_names
                        .map(
                            (track) =>
                                `<li>${escapeHtml(track)}</li>`
                        )
                        .join("")
                    }
                </ul>
            </div>
        `;
    }


    result.innerHTML = `
        <div class="result-header">
            <h2>Sorting complete</h2>

            <span class="success-badge">
                Done
            </span>
        </div>


        <div class="stats">

            <div class="stat">
                <span class="stat-value">
                    ${data.source_playlists}
                </span>

                <span class="stat-label">
                    Source playlists
                </span>
            </div>


            <div class="stat">
                <span class="stat-value">
                    ${data.source_tracks}
                </span>

                <span class="stat-label">
                    Source tracks
                </span>
            </div>


            <div class="stat">
                <span class="stat-value">
                    ${data.selected_tracks}
                </span>

                <span class="stat-label">
                    Selected tracks
                </span>
            </div>


            <div class="stat">
                <span class="stat-value">
                    ${data.added_tracks}
                </span>

                <span class="stat-label">
                    Added tracks
                </span>
            </div>

        </div>


        <a
            href="${data.url}"
            target="_blank"
            class="youtube-button"
        >
            Open Playlist in YouTube Music
        </a>


        ${failedTracks}
    `;
}


function showStatus(message, type) {
    const status = document.getElementById("status");

    status.textContent = message;

    status.className = `status ${type}`;
}


function hideResult() {
    const result = document.getElementById("result");

    result.classList.add("hidden");
}


async function logout() {
    const button = document.getElementById(
        "logout-button"
    );

    button.disabled = true;
    button.textContent = "Disconnecting...";


    try {
        const response = await fetch(
            "/auth/logout",
            {
                method: "POST"
            }
        );


        if (!response.ok) {
            throw new Error("Logout failed.");
        }


        window.location.href = "/";

    } catch (error) {
        console.error(error);

        button.disabled = false;
        button.textContent = "Disconnect";
    }
}


function escapeHtml(value) {
    const div = document.createElement("div");

    div.textContent = value;

    return div.innerHTML;
}