// Global state
let currentUser = null;
let authToken = null;

// API configuration
const API_BASE = window.location.origin;

// Utility functions
function showMessage(message, type = 'success') {
    const messageEl = document.getElementById('message');
    if (messageEl) {
        messageEl.textContent = message;
        messageEl.className = `message ${type}`;
        setTimeout(() => {
            messageEl.textContent = '';
            messageEl.className = 'message';
        }, 5000);
    }
}

function setAuthToken(token) {
    authToken = token;
    localStorage.setItem('authToken', token);
}

function getAuthToken() {
    return authToken || localStorage.getItem('authToken');
}

function clearAuth() {
    authToken = null;
    localStorage.removeItem('authToken');
    currentUser = null;
}

async function apiCall(endpoint, options = {}) {
    const token = getAuthToken();
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
            ...options.headers
        },
        ...options
    };
    
    const response = await fetch(`${API_BASE}${endpoint}`, config);
    
    if (response.status === 401) {
        clearAuth();
        window.location.href = '/';
        return;
    }
    
    if (!response.ok) {
        const error = await response.text();
        throw new Error(error);
    }
    
    return response.json();
}

// Auth functions
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
    
    document.querySelector(`[onclick="switchTab('${tab}')"]`).classList.add('active');
    document.getElementById(`${tab}Form`).classList.add('active');
}

async function login(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        username: formData.get('email'),
        password: formData.get('password')
    };
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams(data)
        });
        
        if (response.ok) {
            const result = await response.json();
            setAuthToken(result.access_token);
            window.location.href = '/dashboard';
        } else {
            const error = await response.text();
            showMessage(error, 'error');
        }
    } catch (error) {
        showMessage('Login failed: ' + error.message, 'error');
    }
}

async function register(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {
        email: formData.get('email'),
        full_name: formData.get('full_name'),
        password: formData.get('password'),
        role: formData.get('role')
    };
    
    try {
        const result = await apiCall('/auth/register', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        showMessage('Registration successful! You can now login.');
        switchTab('login');
    } catch (error) {
        showMessage('Registration failed: ' + error.message, 'error');
    }
}

function logout() {
    clearAuth();
    window.location.href = '/';
}

// Dashboard functions
function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(`${tabName}Content`).classList.add('active');
    document.querySelector(`[onclick="showTab('${tabName}')"]`).classList.add('active');
    
    // Load content based on tab
    if (tabName === 'review') {
        loadPendingQAs();
    } else if (tabName === 'ready') {
        loadReadyQAs();
    }
}

async function loadUserInfo() {
    try {
        // Get user info
        const userInfo = await apiCall('/auth/me');
        console.log('Raw user info from API:', userInfo); // Debug log
        
        const userName = userInfo.full_name || userInfo.email.split('@')[0];
        const role = userInfo.role;
        const initials = userName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
        
        console.log('Processed user info:', { userName, role, initials }); // Debug log
        
        document.getElementById('userName').textContent = userName;
        
        // Only set role badge if element exists (not commented out)
        const roleBadge = document.getElementById('userRole');
        if (roleBadge) {
            roleBadge.textContent = initials;
            roleBadge.title = role;
        }
        
        // Show/hide tabs based on role
        console.log('Checking role:', role, 'Type:', typeof role); // Debug log
        if (role === 'provider') {
            console.log('Showing provider tabs'); // Debug log
            document.getElementById('uploadTab').style.display = 'block';
            document.getElementById('readyTab').style.display = 'block';
            
            // Auto-switch to Upload tab for providers
            showTab('upload');
        } 
        else {
            console.log('Hiding provider tabs for role:', role); // Debug log
            document.getElementById('uploadTab').style.display = 'none';
            document.getElementById('readyTab').style.display = 'none';
            
            // Keep Review tab active for annotators
            showTab('review');
        }
        
        // Load annotation count
        await loadAnnotationCount();
        
        currentUser = { role, name: userName, id: userInfo.id };
    } catch (error) {
        console.error('Failed to load user info:', error);
        showMessage('Failed to load user information: ' + error.message, 'error');
    }
}

async function loadAnnotationCount() {
    try {
        const stats = await apiCall('/review/stats');
        // This is a simple count - in a real app you'd want user-specific annotation count
        document.getElementById('annotationCount').textContent = stats.total;
    } catch (error) {
        console.error('Failed to load annotation count:', error);
    }
}

async function loadPendingQAs() {
    const qaList = document.getElementById('qaList');
    qaList.innerHTML = '<div class="loading">Loading QAs...</div>';
    
    try {
        const qas = await apiCall('/review/pending');
        const countEl = document.getElementById('qaCount');
        countEl.textContent = `${qas.length} pending QAs`;
        
        if (qas.length === 0) {
            qaList.innerHTML = '<div class="loading">No pending QAs found.</div>';
            return;
        }
        
        qaList.innerHTML = qas.map(qa => {
            const annotatorHistory = qa.annotators && qa.annotators.length > 0 ? `
                <div class="annotator-history">
                    <strong>Annotated by:</strong>
                    ${qa.annotators.map(ann => `
                        <div class="annotator-item">
                            <span class="annotator-name">${ann.name}</span>
                            <span class="annotator-date">${new Date(ann.date).toLocaleDateString()}</span>
                            <span class="annotator-score">${ann.score}</span>
                        </div>
                    `).join('')}
                </div>
            ` : '';
            
            return `
                <div class="qa-item">
                    <div class="qa-question">${qa.question}</div>
                    <div class="qa-answer">${qa.answer}</div>
                    <div class="qa-meta">
                        <span>ID: ${qa.id}</span>
                        <span>Created: ${new Date(qa.created_at).toLocaleDateString()}</span>
                    </div>
                    ${annotatorHistory}
                    <div class="qa-actions">
                        <button class="btn btn-primary btn-sm" onclick="openReviewModal(${qa.id}, '${qa.question.replace(/'/g, "\\'")}', '${qa.answer.replace(/'/g, "\\'")}')">
                            <i class="fas fa-edit"></i> Review
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        qaList.innerHTML = `<div class="loading">Error loading QAs: ${error.message}</div>`;
    }
}

async function loadReadyQAs() {
    const readyList = document.getElementById('readyList');
    readyList.innerHTML = '<div class="loading">Loading ready QAs...</div>';
    
    try {
        // Load stats first
        const stats = await apiCall('/review/stats');
        document.getElementById('totalQAs').textContent = stats.total;
        document.getElementById('pendingQAs').textContent = stats.pending;
        document.getElementById('readyQAs').textContent = stats.ready;
        document.getElementById('rejectedQAs').textContent = stats.rejected;
        
        // Load ready QAs
        const qas = await apiCall('/provider/ready');
        
        if (qas.length === 0) {
            readyList.innerHTML = '<div class="loading">No ready QAs found.</div>';
            return;
        }
        
        readyList.innerHTML = qas.map(qa => `
            <div class="qa-item">
                <div class="qa-question">${qa.question}</div>
                <div class="qa-answer">${qa.answer}</div>
                <div class="qa-meta">
                    <span>ID: ${qa.id}</span>
                    <span>Created: ${new Date(qa.created_at).toLocaleDateString()}</span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        readyList.innerHTML = `<div class="loading">Error loading ready QAs: ${error.message}</div>`;
    }
}

// Upload functions
async function uploadFile(event) {
    event.preventDefault();
    const fileInput = document.getElementById('fileInput');
    const resultBox = document.getElementById('uploadResult');
    
    if (!fileInput.files[0]) {
        showMessage('Please select a file', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('f', fileInput.files[0]);
    
    resultBox.innerHTML = '<div class="loading">Processing file...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/upload/file`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${getAuthToken()}` },
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            resultBox.innerHTML = `
                <div class="message success">
                    <strong>Success!</strong><br>
                    Created ${result.chunks} chunks<br>
                    Generated ${result.qa_generated} QAs
                </div>
            `;
            fileInput.value = '';
        } else {
            const error = await response.text();
            resultBox.innerHTML = `<div class="message error">Error: ${error}</div>`;
        }
    } catch (error) {
        resultBox.innerHTML = `<div class="message error">Upload failed: ${error.message}</div>`;
    }
}

// Modal functions
function openReviewModal(qaId, question, answer) {
    document.getElementById('qaId').value = qaId;
    document.getElementById('editQuestion').value = question;
    document.getElementById('editAnswer').value = answer;
    document.getElementById('score').value = 0.7;
    document.getElementById('scoreValue').textContent = '0.7';
    document.getElementById('comment').value = '';
    document.getElementById('validated').checked = true;
    
    document.getElementById('qaModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('qaModal').style.display = 'none';
}

async function saveAnnotation(event) {
    event.preventDefault();
    
    const data = {
        qa_item_id: parseInt(document.getElementById('qaId').value),
        edited_question: document.getElementById('editQuestion').value,
        edited_answer: document.getElementById('editAnswer').value,
        score: parseFloat(document.getElementById('score').value),
        comment: document.getElementById('comment').value,
        validated: document.getElementById('validated').checked
    };
    
    try {
        await apiCall('/review/annotate', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        closeModal();
        showMessage('Annotation saved successfully!');
        loadPendingQAs();
    } catch (error) {
        showMessage('Failed to save annotation: ' + error.message, 'error');
    }
}

function exportQAs(format) {
    const url = `/provider/export/${format}`;
    const link = document.createElement('a');
    link.href = url;
    link.download = `ready_qas.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showMessage(`Exporting QAs as ${format.toUpperCase()}...`);
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on dashboard and user is logged in
    if (window.location.pathname === '/dashboard') {
        if (!getAuthToken()) {
            window.location.href = '/';
            return;
        }
        loadUserInfo();
    }
    
    // Form event listeners
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', login);
    }
    
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', register);
    }
    
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', uploadFile);
    }
    
    const annotationForm = document.getElementById('annotationForm');
    if (annotationForm) {
        annotationForm.addEventListener('submit', saveAnnotation);
    }
    
    // Score slider
    const scoreSlider = document.getElementById('score');
    const scoreValue = document.getElementById('scoreValue');
    if (scoreSlider && scoreValue) {
        scoreSlider.addEventListener('input', function() {
            scoreValue.textContent = this.value;
        });
    }
    
    // Modal close on outside click
    const modal = document.getElementById('qaModal');
    if (modal) {
        window.addEventListener('click', function(event) {
            if (event.target === modal) {
                closeModal();
            }
        });
    }
});
