let currentSessionId = null;

document.addEventListener('DOMContentLoaded', () => {
    // Check if on dashboard
    if (!document.getElementById('dashboard-container')) return;

    const newSessionBtn = document.getElementById('new-session-btn');
    const generateBtn = document.getElementById('generate-btn');
    const copyBtn = document.getElementById('copy-btn');
    const sessionList = document.getElementById('session-list');

    loadSessions();

    newSessionBtn.addEventListener('click', async () => {
        try {
            setLoading('new-session-btn', true, 'Creating...');
            const session = await apiFetch('/sessions', {
                method: 'POST'
            });
            await loadSessions();
            selectSession(session.id);
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            setLoading('new-session-btn', false);
        }
    });

    generateBtn.addEventListener('click', async () => {
        if (!currentSessionId) {
            showToast('Please select or create a session first', 'error');
            return;
        }

        clearValidationErrors();
        
        const incomingEmail = document.getElementById('incoming-email').value;
        const instruction = document.getElementById('instruction').value;
        const tone = document.getElementById('tone').value;

        if (!incomingEmail) showValidationError('incoming-email', 'Incoming email is required');
        if (!instruction) showValidationError('instruction', 'Instruction is required');
        if (!tone) showValidationError('tone', 'Tone is required');
        
        if (!incomingEmail || !instruction || !tone) return;

        try {
            setLoading('generate-btn', true, 'Generating reply...');
            
            const reply = await apiFetch(`/sessions/${currentSessionId}/messages`, {
                method: 'POST',
                body: JSON.stringify({
                    incoming_email: incomingEmail,
                    instruction: instruction,
                    tone: tone
                })
            });
            
            displayReply(reply);
            // Reload history to show the new interaction
            loadMessageHistory(currentSessionId);
            
            // Clear inputs
            document.getElementById('incoming-email').value = '';
            document.getElementById('instruction').value = '';
            
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            setLoading('generate-btn', false);
        }
    });

    copyBtn.addEventListener('click', () => {
        const subject = document.getElementById('reply-subject').textContent;
        const greeting = document.getElementById('reply-greeting').textContent;
        const body = document.getElementById('reply-body').textContent;
        const closing = document.getElementById('reply-closing').textContent;

        if (!subject && !body) return;

        const textToCopy = `Subject: ${subject}\n\n${greeting}\n\n${body}\n\n${closing}`;
        
        navigator.clipboard.writeText(textToCopy).then(() => {
            showToast('Copied!', 'success');
        }).catch(err => {
            showToast('Failed to copy', 'error');
        });
    });
});

async function loadSessions() {
    try {
        const sessions = await apiFetch('/sessions');
        const sessionList = document.getElementById('session-list');
        sessionList.innerHTML = '';
        
        if (sessions.length === 0) {
            sessionList.innerHTML = '<div class="empty-state">No sessions yet.</div>';
            return;
        }

        sessions.forEach(session => {
            const date = new Date(session.created_at).toLocaleString();
            const el = document.createElement('div');
            el.className = 'session-item';
            el.dataset.id = session.id;
            el.innerHTML = `
                <div class="session-title">Session ${session.id}</div>
                <div class="session-date">${date}</div>
            `;
            el.addEventListener('click', () => selectSession(session.id));
            sessionList.appendChild(el);
        });

        // Highlight current if it exists
        if (currentSessionId) {
            highlightSession(currentSessionId);
        }
    } catch (error) {
        showToast('Failed to load sessions', 'error');
    }
}

async function selectSession(sessionId) {
    currentSessionId = sessionId;
    highlightSession(sessionId);
    clearDraftArea();
    await loadMessageHistory(sessionId);
}

function highlightSession(sessionId) {
    document.querySelectorAll('.session-item').forEach(el => {
        el.classList.toggle('active', parseInt(el.dataset.id) === parseInt(sessionId));
    });
}

async function loadMessageHistory(sessionId) {
    try {
        const historyContainer = document.getElementById('message-history');
        historyContainer.innerHTML = '<div class="loading-history">Loading history...</div>';
        
        const messages = await apiFetch(`/sessions/${sessionId}/messages`);
        historyContainer.innerHTML = '';
        
        if (messages.length === 0) {
            historyContainer.innerHTML = '<div class="empty-state">No history yet. Draft your first reply!</div>';
            return;
        }

        messages.forEach(msg => {
            const msgEl = document.createElement('div');
            msgEl.className = `message ${msg.role === 'user' ? 'message-user' : 'message-assistant'}`;
            
            if (msg.role === 'user') {
                msgEl.innerHTML = `
                    <div class="message-header">You requested a <strong>${msg.content.tone}</strong> reply</div>
                    <div class="message-body">
                        <strong>Instruction:</strong> ${msg.content.instruction}
                    </div>
                `;
            } else {
                msgEl.innerHTML = `
                    <div class="message-header">AI Reply</div>
                    <div class="message-body">
                        <strong>Subject:</strong> ${msg.content.subject}<br/><br/>
                        ${msg.content.greeting}<br/><br/>
                        ${msg.content.body}<br/><br/>
                        ${msg.content.closing}
                    </div>
                `;
            }
            historyContainer.appendChild(msgEl);
        });
        
        // Scroll to bottom
        historyContainer.scrollTop = historyContainer.scrollHeight;
        
    } catch (error) {
        showToast('Failed to load history', 'error');
        document.getElementById('message-history').innerHTML = '<div class="error-text">Failed to load history.</div>';
    }
}

function displayReply(reply) {
    document.getElementById('reply-container').style.display = 'block';
    document.getElementById('reply-subject').textContent = reply.subject;
    document.getElementById('reply-greeting').textContent = reply.greeting;
    document.getElementById('reply-body').textContent = reply.body;
    document.getElementById('reply-closing').textContent = reply.closing;
}

function clearDraftArea() {
    document.getElementById('reply-container').style.display = 'none';
    document.getElementById('incoming-email').value = '';
    document.getElementById('instruction').value = '';
    document.getElementById('tone').value = 'professional';
}
