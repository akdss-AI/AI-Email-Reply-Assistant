function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Trigger reflow to ensure animation works
    void toast.offsetWidth;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
    return container;
}

function clearValidationErrors() {
    document.querySelectorAll('.error-text').forEach(el => el.remove());
    document.querySelectorAll('.input-error').forEach(el => el.classList.remove('input-error'));
}

function showValidationError(inputId, message) {
    const inputEl = document.getElementById(inputId);
    if (!inputEl) return;
    
    inputEl.classList.add('input-error');
    
    const errorEl = document.createElement('span');
    errorEl.className = 'error-text';
    errorEl.textContent = message;
    
    inputEl.parentNode.appendChild(errorEl);
}

function setLoading(buttonId, isLoading, loadingText = 'Loading...') {
    const button = document.getElementById(buttonId);
    if (!button) return;
    
    if (isLoading) {
        button.dataset.originalText = button.textContent;
        button.textContent = loadingText;
        button.disabled = true;
    } else {
        if (button.dataset.originalText) {
            button.textContent = button.dataset.originalText;
        }
        button.disabled = false;
    }
}
