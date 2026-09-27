console.log("Ramma Sorter login.js loaded");
const fileInput = document.getElementById("credentials-file");
const fileName = document.getElementById("file-name");

const uploadButton = document.getElementById("upload-button");
const connectButton = document.getElementById("connect-button");

const uploadStep = document.querySelector(".upload-step");
const status = document.getElementById("status");


document.addEventListener(
    "DOMContentLoaded",
    checkAuthStatus
);


async function checkAuthStatus() {
    console.log("Checking authentication status...");

    try {
        const response = await fetch(
            "/auth/status"
        );

        const data = await response.json();

        console.log("Auth status:", data);

        if (data.authenticated) {
            console.log("User authenticated. Redirecting...");

            window.location.replace("/");
            return;
        }

        if (data.credentials_configured) {
            console.log("Credentials configured.");

            showCredentialsReady();
        }

    } catch (error) {
        console.error(
            "Failed to check authentication status:",
            error
        );
    }
}


function showCredentialsReady() {
    if (uploadStep) {
        uploadStep.innerHTML = `
            <div class="step-number">
                ✓
            </div>

            <div class="step-content">
                <strong>
                    Google credentials ready
                </strong>

                <span>
                    Your OAuth credentials are already
                    configured on this computer.
                </span>
            </div>
        `;
    }

    connectButton.disabled = false;

    showStatus(
        "Google credentials are ready.",
        "success"
    );
}


fileInput.addEventListener(
    "change",
    () => {
        const file = fileInput.files[0];

        if (!file) {
            fileName.textContent =
                "No file selected";

            return;
        }

        fileName.textContent =
            file.name;
    }
);


uploadButton.addEventListener(
    "click",
    uploadCredentials
);


async function uploadCredentials() {
    const file = fileInput.files[0];

    if (!file) {
        showStatus(
            "Please select your Google OAuth JSON file.",
            "error"
        );

        return;
    }

    if (
        !file.name
            .toLowerCase()
            .endsWith(".json")
    ) {
        showStatus(
            "Please select a JSON file.",
            "error"
        );

        return;
    }

    const formData = new FormData();

    formData.append(
        "file",
        file
    );

    uploadButton.disabled = true;

    showStatus(
        "Uploading credentials...",
        "loading"
    );

    try {
        const response = await fetch(
            "/auth/credentials",
            {
                method: "POST",
                body: formData
            }
        );

        const data = await response.json();

        if (
            !response.ok ||
            !data.success
        ) {
            throw new Error(
                data.message ||
                "Failed to upload credentials."
            );
        }

        showCredentialsReady();

    } catch (error) {
        console.error(error);

        showStatus(
            error.message ||
            "Failed to upload credentials.",
            "error"
        );

    } finally {
        uploadButton.disabled = false;
    }
}


connectButton.addEventListener(
    "click",
    connectGoogle
);


async function connectGoogle() {
    connectButton.disabled = true;

    showStatus(
        "Connecting to Google...",
        "loading"
    );

    try {
        const response = await fetch(
            "/auth/login"
        );

        const data = await response.json();

        if (
            !response.ok ||
            !data.authenticated
        ) {
            throw new Error(
                data.message ||
                "Google authentication failed."
            );
        }

        showStatus(
            "Connected successfully!",
            "success"
        );

        window.location.replace("/");

    } catch (error) {
        console.error(error);

        showStatus(
            error.message ||
            "Google authentication failed.",
            "error"
        );

        connectButton.disabled = false;
    }
}


function showStatus(
    message,
    type
) {
    status.textContent = message;

    status.className =
        `status ${type}`;
}