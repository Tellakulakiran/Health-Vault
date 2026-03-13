// Utility for Toasts
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerText = message;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3300);
}

// Fetch helper that handles 401s and non-JSON errors
async function authFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (response.status === 401) {
            window.location.href = '/login';
            return response;
        }
        return response;
    } catch (e) {
        console.error("Network or fetch error:", e);
        throw e;
    }
}

// Global helper to safely parse JSON or return a friendly error
async function safeParseJson(response) {
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.indexOf("application/json") !== -1) {
        return await response.json();
    } else {
        // Handle non-JSON (like 500 HTML pages)
        const text = await response.text();
        console.error("Non-JSON response received:", text);
        return { detail: "Server error: Received invalid response format." };
    }
}

// ... existing badge/initializer code ...

// login.js snippets (integrated into main.js)
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(loginForm);
        
        try {
            const res = await fetch('/api/auth/token', {
                method: 'POST',
                body: fd
            });
            
            if (res.ok) {
                window.location.href = '/';
            } else {
                const data = await safeParseJson(res);
                showToast(data.detail || 'Login failed', 'error');
            }
        } catch (e) {
            showToast('Network error or server unreachable', 'error');
        }
    });
}
