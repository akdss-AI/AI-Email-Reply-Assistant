const API_BASE_URL = "http://127.0.0.1:8000";

async function apiFetch(endpoint, options = {}) {
    const token = localStorage.getItem("access_token");
    
    const headers = {
        ...options.headers,
    };
    
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    
    const isFormData = options.body instanceof URLSearchParams;
    if (!isFormData && !headers["Content-Type"] && options.method && options.method !== 'GET') {
        headers["Content-Type"] = "application/json";
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });

        const contentType = response.headers.get("content-type");
        const isJson = contentType && contentType.includes("application/json");
        const data = isJson ? await response.json() : null;

        if (response.status === 401) {
            // Unauthorized - clear token and redirect to login
            localStorage.removeItem("access_token");
            if (!window.location.pathname.endsWith("login.html") && !window.location.pathname.endsWith("signup.html")) {
                window.location.href = "login.html";
            }
            
            // If the backend provided a specific detail message, use it
            if (data && data.detail && typeof data.detail === 'string') {
                throw new Error(data.detail);
            }
            throw new Error("Unauthorized");
        }

        if (!response.ok) {
            let errorMessage = "An unexpected error occurred.";
            
            if (data && data.detail) {

                if (typeof data.detail === 'string') {
                    errorMessage = data.detail;
                } else if (Array.isArray(data.detail)) {
                    errorMessage = "Please check the information you entered."; // 422 standard
                }
            } else if (response.status === 404) {
                errorMessage = "Resource not found.";
            } else if (response.status === 422) {
                errorMessage = "Please check the information you entered.";
            } else if (response.status === 429) {
                errorMessage = "AI request limit reached. Please try again later.";
            } else if (response.status === 502) {
                errorMessage = "The AI service returned an invalid response. Please try again.";
            } else if (response.status === 503) {
                errorMessage = "AI service is temporarily unavailable. Please try again later.";
            } else if (response.status >= 500) {
                errorMessage = "Something went wrong on the server. Please try again.";
            }
            
            throw new Error(errorMessage);
        }

        return data;
    } catch (error) {
        if (error.message === 'Failed to fetch') {
            throw new Error("Unable to connect to the server. Please try again later.");
        }
        throw error;
    }
}
