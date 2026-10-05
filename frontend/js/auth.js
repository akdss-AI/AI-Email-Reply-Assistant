document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const logoutBtn = document.getElementById('logout-btn');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearValidationErrors();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email) showValidationError('email', 'Email is required');
            if (!password) showValidationError('password', 'Password is required');
            if (!email || !password) return;

            setLoading('login-btn', true, 'Logging in...');
            
            try {
                // OAuth2 expects x-www-form-urlencoded
                const formData = new URLSearchParams();
                formData.append('username', email);
                formData.append('password', password);
                
                const data = await apiFetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: formData
                });
                
                localStorage.setItem('access_token', data.access_token);
                window.location.href = 'index.html';
            } catch (error) {
                showToast(error.message, 'error');
            } finally {
                setLoading('login-btn', false);
            }
        });
    }

    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearValidationErrors();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email) showValidationError('email', 'Email is required');
            if (!password) showValidationError('password', 'Password is required');
            if (!email || !password) return;

            setLoading('signup-btn', true, 'Signing up...');
            
            try {
                await apiFetch('/signup', {
                    method: 'POST',
                    body: JSON.stringify({ email, password })
                });
                
                showToast('Signup successful! Please log in.', 'success');
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1500);
            } catch (error) {
                showToast(error.message, 'error');
            } finally {
                setLoading('signup-btn', false);
            }
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            localStorage.removeItem('access_token');
            window.location.href = 'login.html';
        });
    }
    
    // Auth guard for protected pages
    const isAuthPage = window.location.pathname.endsWith('login.html') || window.location.pathname.endsWith('signup.html');
    const token = localStorage.getItem('access_token');
    
    if (!isAuthPage && !token) {
        window.location.href = 'login.html';
    } else if (isAuthPage && token) {
        window.location.href = 'index.html';
    }
});
