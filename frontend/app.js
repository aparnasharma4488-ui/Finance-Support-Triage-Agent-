document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyze-btn');
    const messageInput = document.getElementById('message-input');
    const resultsContent = document.getElementById('results-content');
    const loadingIndicator = document.getElementById('loading-indicator');
    const statusBadge = document.getElementById('conn-status');

    // Simple ping to backend to check connection
    fetch('http://127.0.0.1:8000/health')
        .then(res => res.json())
        .then(() => {
            statusBadge.textContent = 'API Connected';
            statusBadge.style.color = '#10b981';
            statusBadge.style.background = 'rgba(16, 185, 129, 0.1)';
            statusBadge.style.borderColor = 'rgba(16, 185, 129, 0.2)';
        })
        .catch(() => {
            statusBadge.textContent = 'API Offline';
            statusBadge.style.color = '#ef4444';
            statusBadge.style.background = 'rgba(239, 68, 68, 0.1)';
            statusBadge.style.borderColor = 'rgba(239, 68, 68, 0.2)';
        });

    analyzeBtn.addEventListener('click', async () => {
        const text = messageInput.value.trim();
        if (!text) {
            alert('Please enter a message to analyze.');
            return;
        }

        // Set Loading state
        analyzeBtn.disabled = true;
        loadingIndicator.classList.remove('hidden');
        resultsContent.style.opacity = '0.5';

        try {
            const response = await fetch('http://127.0.0.1:8000/api/triage', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: text })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            renderResults(data);
        } catch (error) {
            console.error('Error fetching triage analysis:', error);
            alert(`Error connecting to the backend. Is the server running? ${error.message}`);
        } finally {
            analyzeBtn.disabled = false;
            loadingIndicator.classList.add('hidden');
            resultsContent.style.opacity = '1';
        }
    });

    function renderResults(data) {
        // Clone template
        const template = document.getElementById('result-template');
        const clone = template.content.cloneNode(true);

        // Update Intent
        clone.querySelector('.intent-val .val-text').textContent = data.intent || 'Unknown';

        // Update Urgency
        const urgencyEl = clone.querySelector('.urgency-val');
        const urgencyText = clone.querySelector('.urgency-val .val-text');
        const urgency = (data.urgency || 'Low').toLowerCase();
        
        urgencyText.textContent = data.urgency;
        
        // Color based on urgency
        if (urgency === 'critical') {
            urgencyEl.style.color = '#dc2626'; // red-600
        } else if (urgency === 'high') {
            urgencyEl.style.color = '#f97316'; // orange-500
        } else if (urgency === 'medium') {
            urgencyEl.style.color = '#eab308'; // yellow-500
        } else {
            urgencyEl.style.color = '#22c55e'; // green-500
        }

        // Update Entities
        const renderEntityChips = (containerId, items) => {
            const container = clone.getElementById(containerId);
            if (items && items.length > 0) {
                container.innerHTML = '';
                items.forEach(item => {
                    const span = document.createElement('span');
                    span.className = 'entity-chip fade-in-up';
                    span.textContent = item;
                    container.appendChild(span);
                });
            } else {
                container.innerHTML = '<span style="color: #64748b; font-size: 0.85rem; font-style: italic;">None detected</span>';
            }
        };

        renderEntityChips('ent-accounts', data.entities?.account_ids);
        renderEntityChips('ent-dates', data.entities?.dates);
        renderEntityChips('ent-amounts', data.entities?.amounts);

        // Update Draft Response
        const draftEl = clone.getElementById('draft-text');
        draftEl.textContent = data.draft_response || 'No draft generated.';

        // Copy button listener
        const copyBtn = clone.querySelector('.copy-btn');
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(draftEl.textContent).then(() => {
                const icon = copyBtn.querySelector('i');
                icon.className = 'fa-solid fa-check';
                icon.style.color = '#10b981';
                setTimeout(() => {
                    icon.className = 'fa-regular fa-copy';
                    icon.style.color = '';
                }, 2000);
            });
        });

        // Insert into DOM
        resultsContent.innerHTML = '';
        resultsContent.appendChild(clone);
    }
});
