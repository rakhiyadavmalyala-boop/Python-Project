const API_BASE = '/api';
let currentSessionId = 'session-' + Math.random().toString(36).substring(2, 9);
let activeSearchMode = 'hybrid';
let globalDocuments = [];

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initUpload();
    initSearch();
    initChat();
    initComparison();
    initSummarizer();
    initAnalytics();
    
    // Initial fetch
    loadDocuments();
    loadAnalytics();
});

// Navigation Setup
function initNavigation() {
    const navButtons = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const pageTitle = document.getElementById('page-title');
    const pageSubtitle = document.getElementById('page-subtitle');

    const titlesMap = {
        'tab-docs': { title: 'Document Management Hub', subtitle: 'Upload, process, and classify enterprise technical papers & documentation.' },
        'tab-search': { title: 'Semantic & Vector Search', subtitle: 'Retrieve relevant information using Semantic, Keyword, or Hybrid search modes.' },
        'tab-chat': { title: 'AI Research Assistant', subtitle: 'Grounded question answering with exact page citations and context.' },
        'tab-compare': { title: 'Document Comparison', subtitle: 'Compare methodologies, pros & cons, similarities, and conclusions across papers.' },
        'tab-summarize': { title: 'Multi-Perspective Summarizer', subtitle: 'Generate Executive, Technical, Bullet, and Key Takeaway summaries.' },
        'tab-analytics': { title: 'Knowledge Base Analytics', subtitle: 'Analytical insights on documents, vector chunks, categories, and user activity.' }
    };

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            navButtons.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(targetTab).classList.add('active');

            if (titlesMap[targetTab]) {
                pageTitle.textContent = titlesMap[targetTab].title;
                pageSubtitle.textContent = titlesMap[targetTab].subtitle;
            }

            if (targetTab === 'tab-analytics') loadAnalytics();
            if (targetTab === 'tab-docs') loadDocuments();
        });
    });

    document.getElementById('btn-refresh-all').addEventListener('click', () => {
        loadDocuments();
        loadAnalytics();
        showToast('Data refreshed successfully!');
    });
}

// Toast Notification
function showToast(msg, isError = false) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.style.borderColor = isError ? 'var(--danger)' : 'var(--border-accent)';
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3500);
}

// Document Management
function initUpload() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFileUpload(e.dataTransfer.files);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFileUpload(fileInput.files);
        }
    });
}

async function handleFileUpload(files) {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('files', files[i]);
    }

    showToast('Uploading & processing document pipeline (Extraction -> Chunking -> Vector Index -> TF Classifier)...');

    try {
        const res = await fetch(`${API_BASE}/documents/upload`, {
            method: 'POST',
            body: formData
        });

        if (!res.ok) throw new Error('Upload failed');
        const data = await res.json();
        showToast(`Successfully processed ${data.length} document(s)!`);
        loadDocuments();
        loadAnalytics();
    } catch (err) {
        showToast(`Error: ${err.message}`, true);
    }
}

async function loadDocuments() {
    try {
        const res = await fetch(`${API_BASE}/documents`);
        const data = await res.json();
        globalDocuments = data.documents || [];

        renderDocumentsTable(globalDocuments);
        populateDropdowns(globalDocuments);
    } catch (err) {
        console.error('Failed to load documents', err);
    }
}

function renderDocumentsTable(docs) {
    const tbody = document.getElementById('docs-table-body');
    const badge = document.getElementById('doc-count-badge');
    badge.textContent = `${docs.length} File(s) Loaded`;

    if (!docs.length) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-cell">No documents uploaded yet. Drag & drop PDF files above.</td></tr>`;
        return;
    }

    tbody.innerHTML = docs.map(d => `
        <tr>
            <td><strong>${d.filename}</strong></td>
            <td>${d.total_pages}</td>
            <td>${d.total_chunks}</td>
            <td>
                <span class="badge badge-info">${d.category}</span>
                <span class="text-xs text-muted">(${Math.round(d.category_confidence * 100)}%)</span>
            </td>
            <td><span class="badge badge-success">${d.processing_status}</span></td>
            <td>${new Date(d.upload_timestamp).toLocaleTimeString()}</td>
            <td>
                <button class="btn btn-secondary btn-sm" onclick="reprocessDoc('${d.id}')">🔄 Reprocess</button>
                <button class="btn btn-secondary btn-sm" style="color: var(--danger);" onclick="deleteDoc('${d.id}')">🗑️ Delete</button>
            </td>
        </tr>
    `).join('');
}

async function deleteDoc(docId) {
    if (!confirm('Are you sure you want to delete this document and purge its vector chunks?')) return;
    try {
        const res = await fetch(`${API_BASE}/documents/${docId}`, { method: 'DELETE' });
        if (res.ok) {
            showToast('Document deleted.');
            loadDocuments();
            loadAnalytics();
        }
    } catch (err) {
        showToast('Failed to delete document', true);
    }
}

async function reprocessDoc(docId) {
    showToast('Reprocessing document pipeline...');
    try {
        const res = await fetch(`${API_BASE}/documents/${docId}/reprocess`, { method: 'POST' });
        if (res.ok) {
            showToast('Document reprocessed!');
            loadDocuments();
        }
    } catch (err) {
        showToast('Reprocess failed', true);
    }
}

function populateDropdowns(docs) {
    // Chat doc filter
    const chatSelect = document.getElementById('chat-doc-filter');
    chatSelect.innerHTML = `<option value="">All Uploaded Documents</option>` + 
        docs.map(d => `<option value="${d.id}">${d.filename}</option>`).join('');

    // Summarize select
    const sumSelect = document.getElementById('summarize-doc-select');
    sumSelect.innerHTML = `<option value="">-- Select Document --</option>` + 
        docs.map(d => `<option value="${d.id}">${d.filename}</option>`).join('');

    // Compare checkboxes
    const compareBox = document.getElementById('compare-checkbox-group');
    if (!docs.length) {
        compareBox.innerHTML = `<p class="text-muted">Please upload at least 2 documents to compare.</p>`;
    } else {
        compareBox.innerHTML = docs.map(d => `
            <label class="flex-row gap-4" style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; cursor: pointer;">
                <input type="checkbox" value="${d.id}" class="compare-chk">
                <span>${d.filename} <span class="badge badge-info text-xs">${d.category}</span></span>
            </label>
        `).join('');
    }
}

// Search Logic
function initSearch() {
    const segments = document.querySelectorAll('.segmented-control .segment');
    segments.forEach(s => {
        s.addEventListener('click', () => {
            segments.forEach(seg => seg.classList.remove('active'));
            s.classList.add('active');
            activeSearchMode = s.getAttribute('data-mode');
        });
    });

    document.getElementById('btn-search-exec').addEventListener('click', executeSearch);
}

async function executeSearch() {
    const q = document.getElementById('search-input').value.trim();
    if (!q) return showToast('Please enter a query.', true);

    const topK = parseInt(document.getElementById('search-top-k').value, 10);
    const container = document.getElementById('search-results-list');
    container.innerHTML = `<p class="text-muted">Searching vector index...</p>`;

    try {
        const res = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: q,
                search_mode: activeSearchMode,
                top_k: topK
            })
        });

        const data = await res.json();
        if (!data.results || !data.results.length) {
            container.innerHTML = `<div class="placeholder-state"><p>No relevant document chunks found matching query.</p></div>`;
            return;
        }

        container.innerHTML = data.results.map((item, idx) => `
            <div class="section-card mb-4" style="border-left: 4px solid var(--primary);">
                <div class="card-header" style="margin-bottom: 8px;">
                    <div>
                        <span class="badge badge-info">Chunk #${idx+1}</span>
                        <strong style="margin-left: 8px;">${item.document_name}</strong> (Page ${item.page_number})
                    </div>
                    <span class="badge badge-success">Relevance Score: ${item.score}</span>
                </div>
                <p style="font-size: 14px; color: var(--text-primary); line-height: 1.6;">${item.text}</p>
            </div>
        `).join('');
    } catch (err) {
        showToast('Search failed.', true);
    }
}

// AI Chat Logic
function initChat() {
    document.getElementById('btn-send-chat').addEventListener('click', sendChatMessage);
    document.getElementById('chat-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;

    input.value = '';
    const container = document.getElementById('chat-messages-container');

    // Append User Message
    container.innerHTML += `
        <div class="message user-msg">
            <div class="msg-avatar">👤</div>
            <div class="msg-content"><p>${text}</p></div>
        </div>
    `;
    container.scrollTop = container.scrollHeight;

    const docFilter = document.getElementById('chat-doc-filter').value;
    const docIds = docFilter ? [docFilter] : null;

    try {
        const res = await fetch(`${API_BASE}/assistant/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                question: text,
                document_ids: docIds
            })
        });

        const data = await res.json();

        // Render Citations
        let citHtml = '';
        if (data.citations && data.citations.length) {
            citHtml = `<div class="mt-4" style="border-top: 1px solid var(--border-color); padding-top: 8px;">
                <strong style="font-size: 12px; color: var(--primary);">Citations & Grounded Sources:</strong>
                <div class="flex-row gap-4 mt-4" style="flex-wrap: wrap;">
                    ${data.citations.map(c => `<span class="badge badge-info">📄 ${c.document_name} (Page ${c.page_number})</span>`).join('')}
                </div>
            </div>`;
        }

        container.innerHTML += `
            <div class="message assistant-msg">
                <div class="msg-avatar">🤖</div>
                <div class="msg-content">
                    <p>${data.answer.replace(/\n/g, '<br>')}</p>
                    ${citHtml}
                </div>
            </div>
        `;
        container.scrollTop = container.scrollHeight;

        // Update confidence meter
        const confPercent = Math.round((data.confidence_score || 0) * 100);
        document.getElementById('chat-confidence-fill').style.width = `${confPercent}%`;
        document.getElementById('chat-confidence-text').textContent = `Confidence: ${confPercent}% grounded`;

    } catch (err) {
        showToast('Chat request failed.', true);
    }
}

// Document Comparison
function initComparison() {
    document.getElementById('btn-run-compare').addEventListener('click', async () => {
        const selected = Array.from(document.querySelectorAll('.compare-chk:checked')).map(c => c.value);
        if (selected.length < 2) return showToast('Please select at least 2 documents to compare.', true);

        showToast('Running document comparison matrix...');
        try {
            const res = await fetch(`${API_BASE}/assistant/compare`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ document_ids: selected })
            });

            const data = await res.json();
            document.getElementById('compare-results-card').classList.remove('hidden');
            document.getElementById('compare-exec-box').innerHTML = `<p>${data.executive_comparison}</p>`;

            const tbody = document.getElementById('compare-matrix-body');
            tbody.innerHTML = data.matrix.map(m => `
                <tr>
                    <td><strong>${m.aspect_name}</strong></td>
                    <td style="white-space: pre-line;">${m.comparison_text}</td>
                </tr>
            `).join('');
        } catch (err) {
            showToast('Comparison failed', true);
        }
    });
}

// Summarizer Suite
function initSummarizer() {
    document.getElementById('btn-run-summarize').addEventListener('click', async () => {
        const docId = document.getElementById('summarize-doc-select').value;
        if (!docId) return showToast('Please select a document.', true);

        showToast('Generating 4-part summary...');
        try {
            const res = await fetch(`${API_BASE}/assistant/summarize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ document_id: docId })
            });

            const data = await res.json();
            document.getElementById('summary-results-container').classList.remove('hidden');

            document.getElementById('sum-exec-body').innerHTML = `<p>${data.executive_summary.replace(/\n/g, '<br>')}</p>`;
            document.getElementById('sum-tech-body').innerHTML = `<p>${data.technical_summary.replace(/\n/g, '<br>')}</p>`;

            document.getElementById('sum-bullets-list').innerHTML = data.bullet_points.map(b => `<li>${b}</li>`).join('');
            document.getElementById('sum-takeaways-list').innerHTML = data.key_takeaways.map(t => `<li>${t}</li>`).join('');
        } catch (err) {
            showToast('Summarization failed', true);
        }
    });
}

// Analytics Dashboard
async function loadAnalytics() {
    try {
        const res = await fetch(`${API_BASE}/analytics`);
        const data = await res.json();

        document.getElementById('kpi-total-docs').textContent = data.total_documents;
        document.getElementById('kpi-total-chunks').textContent = data.total_chunks;
        document.getElementById('kpi-total-embeddings').textContent = data.total_embeddings;
        document.getElementById('kpi-total-questions').textContent = data.total_questions_answered;

        // Render Category Distribution
        const catBox = document.getElementById('category-dist-container');
        if (data.category_distribution && Object.keys(data.category_distribution).length) {
            catBox.innerHTML = Object.entries(data.category_distribution).map(([cat, cnt]) => `
                <div class="flex-row justify-between mb-4" style="justify-content: space-between; border-bottom: 1px solid var(--border-color); padding-bottom: 6px;">
                    <span>${cat}</span>
                    <span class="badge badge-info">${cnt} Doc(s)</span>
                </div>
            `).join('');
        } else {
            catBox.innerHTML = `<p class="text-muted">No category data yet.</p>`;
        }

        // Render Top Queries
        const topBody = document.getElementById('top-queries-table-body');
        if (data.top_queried_documents && data.top_queried_documents.length) {
            topBody.innerHTML = data.top_queried_documents.map(d => `
                <tr>
                    <td>${d.filename}</td>
                    <td><span class="badge badge-info">${d.category}</span></td>
                    <td><strong>${d.query_count} queries</strong></td>
                </tr>
            `).join('');
        } else {
            topBody.innerHTML = `<tr><td colspan="3" class="empty-cell">No query activity recorded yet.</td></tr>`;
        }
    } catch (err) {
        console.error('Analytics load error', err);
    }
}
