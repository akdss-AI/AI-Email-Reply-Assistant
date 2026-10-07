const API_BASE_URL = "https://ai-email-reply-assistant-df6a9.containers.snapdeploy.app";

async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem("access_token");

    const headers = {
        ...options.headers,
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const isFormData = options.body instanceof URLSearchParams;

    if (
        !isFormData &&
        !headers["Content-Type"] &&
        options.method &&
        options.method !== "GET"
    ) {
        headers["Content-Type"] = "application/json";
    }

    const MAX_RETRIES = 4;
    const RETRY_DELAY = 3000;

    const serverStatus = document.getElementById("server-status");

    function showServerStatus(message) {
        if (serverStatus) {
            serverStatus.textContent = message;
            serverStatus.classList.remove("hidden");
        }
    }

    function hideServerStatus() {
        if (serverStatus) {
            serverStatus.classList.add("hidden");
        }
    }

    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                ...options,
                headers
            });

            const contentType = response.headers.get("content-type");
            const isJson =
                contentType && contentType.includes("application/json");

            const data = isJson ? await response.json() : null;

            // -----------------------------
            // AUTHENTICATION
            // -----------------------------
            if (response.status === 401) {
                localStorage.removeItem("access_token");

                if (
                    !window.location.pathname.endsWith("login.html") &&
                    !window.location.pathname.endsWith("signup.html")
                ) {
                    window.location.href = "login.html";
                }

                if (
                    data &&
                    data.detail &&
                    typeof data.detail === "string"
                ) {
                    throw new Error(data.detail);
                }

                throw new Error("Unauthorized");
            }

            // -----------------------------
            // NORMAL API ERRORS
            // -----------------------------
            if (!response.ok) {
                let errorMessage = "An unexpected error occurred.";

                if (data && data.detail) {
                    if (typeof data.detail === "string") {
                        errorMessage = data.detail;
                    } else if (Array.isArray(data.detail)) {
                        errorMessage =
                            "Please check the information you entered.";
                    }
                } else if (response.status === 404) {
                    errorMessage = "Resource not found.";
                } else if (response.status === 422) {
                    errorMessage =
                        "Please check the information you entered.";
                } else if (response.status === 429) {
                    errorMessage =
                        "AI request limit reached. Please try again later.";
                } else if (response.status === 502) {
                    errorMessage =
                        "The AI service returned an invalid response. Please try again.";
                } else if (response.status === 503) {
                    errorMessage =
                        "AI service is temporarily unavailable. Please try again later.";
                } else if (response.status >= 500) {
                    errorMessage =
                        "Something went wrong on the server. Please try again.";
                }

                throw new Error(errorMessage);
            }

            // -----------------------------
            // SUCCESS
            // -----------------------------
            hideServerStatus();
            return data;

        } catch (error) {
            const isConnectionError =
                error.message === "Failed to fetch"
            if (isConnectionError && attempt < MAX_RETRIES) {
                const retryNumber = attempt;

                showServerStatus(
                    `⏳ Waking up the server... Retrying (${retryNumber}/3)`
                );

                console.log(
                    `Server connection failed. Retry ${retryNumber}/3...`
                );

                await new Promise(resolve =>
                    setTimeout(resolve, RETRY_DELAY)
                );

                continue;
            }

            if (isConnectionError) {
                showServerStatus(
                    "⚠️ The server is taking longer than expected. Please try again."
                );

                throw new Error(
                    "Unable to connect to the server. The server may be waking up. Please try again in a few moments."
                );
            }

            throw error;
        }
    }
}

