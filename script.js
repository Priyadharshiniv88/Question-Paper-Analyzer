// API Configuration
const API_URL = 'http://localhost:5000';

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const loadingModal = document.getElementById('loadingModal');
const errorModal = document.getElementById('errorModal');
const errorMessage = document.getElementById('errorMessage');
const resultsSection = document.getElementById('results');
const fileName = document.getElementById('fileName');
const summaryGrid = document.getElementById('summaryGrid');
const superRepeatersList = document.getElementById('superRepeatersList');
const hotTopicsList = document.getElementById('hotTopicsList');
const patternsGrid = document.getElementById('patternsGrid');
const timeline = document.getElementById('timeline');
const exportBtn = document.getElementById('exportBtn');

// Add subject badge to results
const subjectBadge = document.createElement('div');
subjectBadge.className = 'subject-badge';
fileName.parentNode.insertBefore(subjectBadge, fileName.nextSibling);

// Navigation
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelectorAll('.nav-links a').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        
        const targetId = link.getAttribute('href');
        if (targetId === '#home') {
            document.getElementById('home').scrollIntoView({ behavior: 'smooth' });
        } else if (targetId === '#how-it-works') {
            document.getElementById('how-it-works').scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// File Upload Handlers
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

browseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// Handle File Upload
async function handleFile(file) {
    // Validate file
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showError('Please upload a PDF file');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
        showError('File size must be less than 10MB');
        return;
    }
    
    // Show progress
    uploadArea.style.display = 'none';
    progressContainer.style.display = 'block';
    updateProgress(10, 'Uploading file...');
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        // Show loading modal
        loadingModal.classList.add('show');
        
        // Update loading steps
        setTimeout(() => {
            document.getElementById('step1').classList.add('active');
            updateProgress(30, 'Reading file...');
        }, 1000);
        
        // Upload and analyze
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            body: formData
        });
        
        updateProgress(60, 'Analyzing patterns...');
        
        setTimeout(() => {
            document.getElementById('step2').classList.add('active');
        }, 2000);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }
        
        const data = await response.json();
        
        if (data.success) {
            updateProgress(90, 'Creating your plan...');
            
            setTimeout(() => {
                document.getElementById('step3').classList.add('active');
            }, 3000);
            
            setTimeout(() => {
                loadingModal.classList.remove('show');
                displayResults(data);
                updateProgress(100, 'Complete!');
            }, 4000);
        } else {
            throw new Error(data.error || 'Unknown error');
        }
        
    } catch (error) {
        console.error('Error:', error);
        loadingModal.classList.remove('show');
        showError(error.message || 'Failed to process file');
        
        // Reset upload area
        uploadArea.style.display = 'block';
        progressContainer.style.display = 'none';
    }
}

// Update Progress Bar
function updateProgress(percent, text) {
    progressFill.style.width = `${percent}%`;
    progressText.textContent = text;
}

// Display Results
function displayResults(data) {
    const analysis = data.analysis;
    const filename = data.filename;
    const subject = data.subject || 'OOP';
    
    // Store for export
    window.currentAnalysis = analysis;
    
    fileName.textContent = `📄 ${filename}`;
    
    // Add subject badge
    subjectBadge.innerHTML = `<span class="subject-tag">📚 ${subject}</span>`;
    
    // Summary Cards
    summaryGrid.innerHTML = `
        <div class="summary-card">
            <div class="number">${analysis.summary.total_questions || 0}</div>
            <div class="label">Total Questions</div>
        </div>
        <div class="summary-card">
            <div class="number">${analysis.summary.unique_topics || 0}</div>
            <div class="label">Topics Found</div>
        </div>
        <div class="summary-card">
            <div class="number">${analysis.summary.repeated_questions || 0}</div>
            <div class="label">Repeated Questions</div>
        </div>
        <div class="summary-card">
            <div class="number">${Object.keys(analysis.patterns).length || 0}</div>
            <div class="label">Question Types</div>
        </div>
    `;
    
    // Super Repeaters (High Priority)
    if (analysis.revision_plan.super_repeaters && analysis.revision_plan.super_repeaters.length > 0) {
        superRepeatersList.innerHTML = analysis.revision_plan.super_repeaters
            .map(item => {
                const topics = item.main_topics && item.main_topics.length > 0 
                    ? `<br><small style="color: #6366f1; margin-left: 20px;">📌 Topics: ${item.main_topics.join(', ')}</small>` 
                    : '';
                const frequency = `<span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; margin-left: 10px;">Appeared ${item.frequency} times</span>`;
                return `<div class="timeline-item" style="flex-direction: column; align-items: flex-start;">
                    <div style="display: flex; align-items: center; width: 100%;">
                        <span style="font-size: 1.2rem; margin-right: 10px;">⭐</span>
                        <span style="flex: 1;">${item.sample_question}</span>
                        ${frequency}
                    </div>
                    ${topics}
                </div>`;
            })
            .join('');
    } else {
        superRepeatersList.innerHTML = '<div class="timeline-item">No super repeaters found yet.</div>';
    }
    
    // Hot Topics
    if (analysis.revision_plan.hot_topics && analysis.revision_plan.hot_topics.length > 0) {
        hotTopicsList.innerHTML = analysis.revision_plan.hot_topics
            .map(item => {
                const topics = item.main_topics && item.main_topics.length > 0 
                    ? `<br><small style="color: #f59e0b; margin-left: 20px;">📌 Topics: ${item.main_topics.join(', ')}</small>` 
                    : '';
                return `<div class="timeline-item" style="flex-direction: column; align-items: flex-start;">
                    <div style="display: flex; align-items: center;">
                        <span style="font-size: 1.2rem; margin-right: 10px;">🔥</span>
                        <span>${item.sample_question}</span>
                    </div>
                    ${topics}
                </div>`;
            })
            .join('');
    } else {
        hotTopicsList.innerHTML = '<div class="timeline-item">No hot topics found yet.</div>';
    }
    
    // Patterns Grid
    if (analysis.patterns && Object.keys(analysis.patterns).length > 0) {
        patternsGrid.innerHTML = Object.entries(analysis.patterns)
            .map(([pattern, count]) => {
                const total = analysis.summary.total_questions;
                const percentage = ((count / total) * 100).toFixed(1);
                return `
                    <div class="pattern-item">
                        <div class="pattern-name">${pattern.charAt(0).toUpperCase() + pattern.slice(1)}</div>
                        <div class="pattern-count">${count}</div>
                        <div style="font-size: 0.8rem; color: #6b7280;">${percentage}%</div>
                    </div>
                `;
            })
            .join('');
    } else {
        patternsGrid.innerHTML = '<div class="pattern-item">No patterns detected</div>';
    }
    
    // Timeline (Hourly Plan)
    if (analysis.revision_plan.hourly_plan && analysis.revision_plan.hourly_plan.length > 0) {
        timeline.innerHTML = analysis.revision_plan.hourly_plan
            .map(plan => {
                if (plan.startsWith('  •')) {
                    // Indented items (sub-points)
                    return `<div class="timeline-item" style="margin-left: 2rem; background: #f3f4f6; padding: 0.5rem 1rem;">
                        <span class="timeline-text" style="font-size: 0.95rem;">${plan}</span>
                    </div>`;
                } else {
                    // Main timeline items
                    const match = plan.match(/(Hour \d+-\d+):/);
                    const timeSlot = match ? match[1] : '';
                    const description = plan.replace(timeSlot + ':', '').trim();
                    return `
                        <div class="timeline-item">
                            <span class="timeline-time">${timeSlot}</span>
                            <span class="timeline-text">${description}</span>
                        </div>
                    `;
                }
            })
            .join('');
    }
    
    // Add Top Topics section if available
    if (analysis.revision_plan.top_topics && analysis.revision_plan.top_topics.length > 0) {
        const topTopicsHTML = `
            <div class="result-card" style="margin-top: 1rem;">
                <div class="card-header">
                    <span class="card-icon">🏆</span>
                    <h3>Most Important Topics</h3>
                </div>
                <div class="patterns-grid">
                    ${analysis.revision_plan.top_topics.map(([topic, count]) => `
                        <div class="pattern-item">
                            <div class="pattern-name">${topic}</div>
                            <div class="pattern-count">${count}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        patternsGrid.insertAdjacentHTML('afterend', topTopicsHTML);
    }
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    // Reset upload area
    uploadArea.style.display = 'block';
    progressContainer.style.display = 'none';
}

// Export as PDF
exportBtn.addEventListener('click', async () => {
    try {
        showError('📥 PDF Export feature coming soon!');
    } catch (error) {
        showError('Failed to export PDF');
    }
});

// Show Error
function showError(message) {
    errorMessage.textContent = message;
    errorModal.classList.add('show');
}

// Close Error Modal
window.closeErrorModal = function() {
    errorModal.classList.remove('show');
};

// Close modal on outside click
window.addEventListener('click', (e) => {
    if (e.target === errorModal) {
        closeErrorModal();
    }
    if (e.target === loadingModal) {
        loadingModal.classList.remove('show');
    }
});

// Check backend health on load
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            console.log('✅ Backend connected');
            
            // Show success message
            const healthDiv = document.createElement('div');
            healthDiv.className = 'health-status';
            healthDiv.innerHTML = '✅ Connected to server';
            healthDiv.style.cssText = 'position: fixed; bottom: 20px; right: 20px; background: #10b981; color: white; padding: 10px 20px; border-radius: 30px; font-size: 0.9rem; z-index: 1000;';
            document.body.appendChild(healthDiv);
            
            setTimeout(() => healthDiv.remove(), 3000);
        } else {
            console.warn('⚠️ Backend health check failed');
            showError('Cannot connect to server. Please start the backend first.');
        }
    } catch (error) {
        console.error('❌ Cannot connect to backend. Make sure it\'s running on port 5000');
        showError('Cannot connect to server. Please start the backend first.');
    }
}

// Add some CSS for new elements
const style = document.createElement('style');
style.textContent = `
    .subject-badge {
        text-align: center;
        margin: 1rem 0;
    }
    .subject-tag {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        padding: 0.5rem 2rem;
        border-radius: 30px;
        font-size: 1.1rem;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 4px 6px rgba(99, 102, 241, 0.3);
    }
    .pattern-item {
        text-align: center;
        padding: 1rem;
        background: #f9fafb;
        border-radius: 0.5rem;
        transition: transform 0.2s;
    }
    .pattern-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .timeline-item {
        transition: transform 0.2s;
    }
    .timeline-item:hover {
        transform: translateX(5px);
    }
`;
document.head.appendChild(style);

// Initialize
checkBackendHealth();
