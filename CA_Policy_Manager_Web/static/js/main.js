// JavaScript for CA Policy Manager Web App

let selectedPolicyIds = new Set();
let selectedRecommendations = new Set();
let allPolicies = [];
let allRecommendations = [];
let currentSortColumn = null;
let currentSortDirection = 'asc';

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadTemplates();
    checkConnection();
    loadAIStats();
    
    // Refresh AI stats periodically
    setInterval(loadAIStats, 30000); // Every 30 seconds
    
    // Check for auth callback parameters
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('auth') === 'success') {
        const count = urlParams.get('count') || 0;
        showToast(`Successfully authenticated! Retrieved ${count} policies.`, 'success');
        updateConnectionStatus(true);
        refreshPolicies();
        // Clean up URL
        window.history.replaceState({}, document.title, '/');
    } else if (urlParams.get('auth') === 'error') {
        const message = urlParams.get('message') || 'Authentication failed';
        showToast(`Authentication error: ${message}`, 'danger');
        // Clean up URL
        window.history.replaceState({}, document.title, '/');
    }
    
    // Add event listener for Entra ID sign-in card (backup for onclick)
    setTimeout(() => {
        const entraSignInCard = document.querySelector('.auth-method-card:has(.bi-person-circle)');
        if (entraSignInCard) {
            console.log('Adding click listener to Entra ID card');
            entraSignInCard.addEventListener('click', function(e) {
                console.log('Card clicked via event listener');
                signInWithEntraID();
            });
        } else {
            console.warn('Entra ID sign-in card not found');
        }
    }, 500);
});

// Show/hide client credentials form
function showClientCredsAuth() {
    document.getElementById('clientCredsForm').style.display = 'block';
    document.querySelectorAll('.auth-method-card').forEach(card => {
        card.style.display = 'none';
    });
}

function hideClientCredsAuth() {
    document.getElementById('clientCredsForm').style.display = 'none';
    document.querySelectorAll('.auth-method-card').forEach(card => {
        card.style.display = 'block';
    });
}

// Sign in with Entra ID (delegated authentication)
async function signInWithEntraID() {
    console.log('signInWithEntraID called');
    try {
        const response = await fetch('/auth/login');
        const data = await response.json();
        console.log('Auth response:', data, 'Status:', response.status);
        
        // Handle demo mode (400 status with demo_mode flag)
        if (data.demo_mode || (!response.ok && data.error && data.error.includes('Demo mode'))) {
            console.log('Demo mode detected, showing modal');
            // Close the connect modal first
            const connectModal = bootstrap.Modal.getInstance(document.getElementById('connectModal'));
            if (connectModal) {
                connectModal.hide();
            }
            showDemoModeModal();
            return;
        }
        
        if (data.success && data.auth_url) {
            // Redirect to Microsoft login page
            window.location.href = data.auth_url;
        } else {
            showToast('Failed to initiate sign-in: ' + (data.error || 'Unknown error'), 'danger');
        }
    } catch (error) {
        console.error('Sign-in error:', error);
        showToast('Error initiating sign-in: ' + error.message, 'danger');
    }
}

// Show demo mode modal with setup options
function showDemoModeModal() {
    const modalHtml = `
        <div class="modal fade" id="demoModeModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title">
                            <i class="bi bi-exclamation-triangle"></i> Demo Mode Active
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>The app is running in <strong>Demo Mode</strong>. To use authentication and connect to Azure AD/Microsoft Graph, you need to:</p>
                        
                        <h6>Option 1: Automatic Setup (Recommended)</h6>
                        <p>Let the app automatically create an Azure App Registration for you.</p>
                        <a href="/setup/azure" class="btn btn-primary mb-3">
                            <i class="bi bi-magic"></i> Start Automatic Setup
                        </a>
                        
                        <h6>Option 2: Manual Setup</h6>
                        <p>Set up Azure App Registration manually through the Azure Portal.</p>
                        <a href="/docs/QUICK_SETUP.md" target="_blank" class="btn btn-outline-secondary">
                            <i class="bi bi-book"></i> Manual Setup Guide
                        </a>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if present
    const existingModal = document.getElementById('demoModeModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('demoModeModal'));
    modal.show();
}

// Existing function continues...
async function signInWithEntraIDOld() {
    try {
        const response = await fetch('/auth/login');
        const data = await response.json();
        
        if (data.success && data.auth_url) {
            // Redirect to Microsoft login page
            window.location.href = data.auth_url;
        } else {
            showToast('Failed to initiate sign-in: ' + (data.error || 'Unknown error'), 'danger');
        }
    } catch (error) {
        showToast('Error initiating sign-in: ' + error.message, 'danger');
    }
}

// Toast notification helper
function showToast(message, type = 'info') {
    const toastEl = document.getElementById('liveToast');
    const toastBody = document.getElementById('toastBody');
    const toast = new bootstrap.Toast(toastEl);
    
    toastBody.textContent = message;
    toastEl.className = `toast bg-${type} text-white`;
    toast.show();
}

// Check connection status
async function checkConnection() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (data.connected) {
            updateConnectionStatus(true);
            refreshPolicies();
        }
    } catch (error) {
        console.error('Health check failed:', error);
    }
}

// Update connection status badge
function updateConnectionStatus(connected) {
    const badge = document.getElementById('connectionStatus');
    const connectBtn = document.getElementById('connectBtn');
    const disconnectBtn = document.getElementById('disconnectBtn');
    const userInfoCard = document.getElementById('userInfoCard');
    
    if (connected) {
        badge.className = 'badge bg-success me-3';
        badge.textContent = 'Connected';
        connectBtn.classList.add('d-none');
        disconnectBtn.classList.remove('d-none');
        
        // Load and display user info
        loadUserInfo();
    } else {
        badge.className = 'badge bg-secondary me-3';
        badge.textContent = 'Not Connected';
        connectBtn.classList.remove('d-none');
        disconnectBtn.classList.add('d-none');
        
        // Hide user info card
        if (userInfoCard) {
            userInfoCard.classList.add('d-none');
        }
    }
}

// Load user information
async function loadUserInfo() {
    try {
        const response = await fetch('/api/user/info');
        const data = await response.json();
        
        if (data.success && data.user) {
            const userInfoCard = document.getElementById('userInfoCard');
            const userDisplayName = document.getElementById('userDisplayName');
            const userTenantInfo = document.getElementById('userTenantInfo');
            
            // Update display
            userDisplayName.textContent = data.user.displayName || data.user.userPrincipalName || 'User';
            userDisplayName.title = data.user.userPrincipalName || '';
            
            const tenantName = data.tenant?.displayName || 'Unknown Tenant';
            const tenantId = data.tenant?.id ? data.tenant.id.substring(0, 8) + '...' : '';
            userTenantInfo.textContent = `${tenantName} ${tenantId}`;
            userTenantInfo.title = `Tenant: ${data.tenant?.displayName || 'Unknown'}\nID: ${data.tenant?.id || 'N/A'}`;
            
            // Show card
            userInfoCard.classList.remove('d-none');
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

// Disconnect
async function disconnect() {
    if (!confirm('Are you sure you want to disconnect?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/disconnect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateConnectionStatus(false);
            showToast('Disconnected successfully', 'success');
            
            // Clear the policies table
            document.getElementById('policiesTableBody').innerHTML = 
                '<tr><td colspan="6" class="text-center text-muted">Not connected. Click Connect to sign in.</td></tr>';
            
            // Hide the connect modal if open
            const modalEl = document.getElementById('connectModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) {
                modal.hide();
            }
            
            // Reset auth form
            hideClientCredsAuth();
        } else {
            showToast('Disconnect failed: ' + data.error, 'danger');
        }
    } catch (error) {
        showToast('Error disconnecting: ' + error.message, 'danger');
    }
}

// Connect to Microsoft Graph
async function connect() {
    const tenantId = document.getElementById('tenantId').value;
    const clientId = document.getElementById('clientId').value;
    const clientSecret = document.getElementById('clientSecret').value;
    const verifySsl = document.getElementById('verifySsl').checked;
    
    if (!tenantId || !clientId || !clientSecret) {
        showToast('Please fill in all credentials', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/connect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tenant_id: tenantId,
                client_id: clientId,
                client_secret: clientSecret,
                verify_ssl: verifySsl
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message, 'success');
            updateConnectionStatus(true);
            bootstrap.Modal.getInstance(document.getElementById('connectModal')).hide();
            refreshPolicies();
        } else {
            showToast('Connection failed: ' + data.error, 'danger');
        }
    } catch (error) {
        showToast('Connection error: ' + error.message, 'danger');
    }
}

// Refresh policies list
async function refreshPolicies() {
    const loader = document.getElementById('policiesLoader');
    const tbody = document.getElementById('policiesTableBody');
    
    loader.classList.remove('d-none');
    
    try {
        const response = await fetch('/api/policies');
        const data = await response.json();
        
        if (data.success) {
            allPolicies = data.policies;
            displayPolicies(data.policies);
            showToast(`Loaded ${data.count} policies`, 'success');
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Failed to load policies: ' + data.error + '</td></tr>';
        }
    } catch (error) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Error loading policies: ' + error.message + '</td></tr>';
    } finally {
        loader.classList.add('d-none');
    }
}

// Sort policies by column
function sortPolicies(column) {
    // Toggle sort direction if same column, otherwise default to ascending
    if (currentSortColumn === column) {
        currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortColumn = column;
        currentSortDirection = 'asc';
    }
    
    // Sort the policies array
    const sortedPolicies = [...allPolicies].sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];
        
        // Handle null/undefined values
        if (aVal === null || aVal === undefined) aVal = '';
        if (bVal === null || bVal === undefined) bVal = '';
        
        // For dates, convert to timestamp
        if (column === 'createdDateTime' || column === 'modifiedDateTime') {
            aVal = aVal ? new Date(aVal).getTime() : 0;
            bVal = bVal ? new Date(bVal).getTime() : 0;
        }
        
        // For strings, case-insensitive comparison
        if (typeof aVal === 'string') {
            aVal = aVal.toLowerCase();
            bVal = bVal.toLowerCase();
        }
        
        // Compare values
        if (aVal < bVal) return currentSortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return currentSortDirection === 'asc' ? 1 : -1;
        return 0;
    });
    
    // Update sort icons
    updateSortIcons(column, currentSortDirection);
    
    // Display sorted policies
    displayPolicies(sortedPolicies);
}

// Update sort direction icons
function updateSortIcons(column, direction) {
    // Reset all icons
    document.querySelectorAll('th i[id^="sort-"]').forEach(icon => {
        icon.className = 'bi bi-arrow-down-up';
    });
    
    // Set active icon
    const icon = document.getElementById(`sort-${column}`);
    if (icon) {
        icon.className = direction === 'asc' ? 'bi bi-sort-up' : 'bi bi-sort-down';
    }
}

// Display policies in table
function displayPolicies(policies) {
    const tbody = document.getElementById('policiesTableBody');
    
    if (policies.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No policies found</td></tr>';
        return;
    }
    
    tbody.innerHTML = policies.map(policy => `
        <tr>
            <td>
                <input type="checkbox" class="policy-checkbox" data-policy-id="${policy.id}" 
                       onchange="togglePolicySelection('${policy.id}')" 
                       ${selectedPolicyIds.has(policy.id) ? 'checked' : ''}>
            </td>
            <td><a href="#" onclick="viewPolicy('${policy.id}'); return false;">${policy.displayName || 'Unnamed Policy'}</a></td>
            <td>
                <span class="badge ${getStateBadgeClass(policy.state)}">
                    ${policy.state || 'Unknown'}
                </span>
            </td>
            <td>${formatDate(policy.createdDateTime)}</td>
            <td>${formatDate(policy.modifiedDateTime)}</td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button class="btn btn-info" onclick="viewPolicy('${policy.id}')" title="View JSON">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-primary" onclick="explainPolicy('${policy.id}', '${escapeHtml(policy.displayName)}')" title="AI Explanation">
                        <i class="bi bi-lightbulb"></i>
                    </button>
                    <button class="btn btn-danger" onclick="deletePolicy('${policy.id}', '${escapeHtml(policy.displayName)}')" title="Delete">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Get badge class for policy state
function getStateBadgeClass(state) {
    const stateMap = {
        'enabled': 'bg-success',
        'disabled': 'bg-secondary',
        'enabledForReportingButNotEnforced': 'bg-warning'
    };
    return stateMap[state] || 'bg-secondary';
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Toggle policy selection
function togglePolicySelection(policyId) {
    if (selectedPolicyIds.has(policyId)) {
        selectedPolicyIds.delete(policyId);
    } else {
        selectedPolicyIds.add(policyId);
    }
    updateBulkOperationsBar();
}

// Select all policies
function toggleSelectAll() {
    const checkbox = document.getElementById('selectAllPolicies');
    const checkboxes = document.querySelectorAll('.policy-checkbox');
    
    selectedPolicyIds.clear();
    
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
        if (checkbox.checked) {
            selectedPolicyIds.add(cb.dataset.policyId);
        }
    });
    
    updateBulkOperationsBar();
}

// Update bulk operations bar visibility and count
function updateBulkOperationsBar() {
    const bulkBar = document.getElementById('bulkOperationsBar');
    const selectedCount = document.getElementById('selectedCount');
    const count = selectedPolicyIds.size;
    
    if (count > 0) {
        bulkBar.classList.remove('d-none');
        selectedCount.textContent = `${count} ${count === 1 ? 'policy' : 'policies'} selected`;
    } else {
        bulkBar.classList.add('d-none');
    }
}

// View policy details
async function viewPolicy(policyId) {
    try {
        const response = await fetch(`/api/policies/${policyId}`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('policyModalTitle').textContent = data.policy.displayName || 'Policy Details';
            document.getElementById('policyModalContent').textContent = JSON.stringify(data.policy, null, 2);
            new bootstrap.Modal(document.getElementById('policyModal')).show();
        } else {
            showToast('Failed to load policy: ' + data.error, 'danger');
        }
    } catch (error) {
        showToast('Error loading policy: ' + error.message, 'danger');
    }
}

// View template preview
function viewTemplatePreview(template, displayName) {
    document.getElementById('policyModalTitle').textContent = `Template: ${displayName}`;
    document.getElementById('policyModalContent').textContent = JSON.stringify(template, null, 2);
    new bootstrap.Modal(document.getElementById('policyModal')).show();
}

// Explain policy with AI
async function explainPolicy(policyId, policyName) {
    try {
        showToast(`Getting AI explanation for ${policyName}...`, 'info');
        
        const response = await fetch(`/api/policies/${policyId}/explain`);
        const data = await response.json();
        
        if (response.ok) {
            showPolicyExplanation(policyName, data);
            
            // Update AI stats if available
            if (data.session_stats) {
                updateAIStatsDisplay(data.session_stats);
            } else {
                // Refresh stats from server
                loadAIStats();
            }
        } else {
            showToast(`Failed to explain policy: ${data.error}`, 'danger');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'danger');
    }
}

function showPolicyExplanation(policyName, explanation) {
    const modalTitle = document.getElementById('policyModalTitle');
    const modalContent = document.getElementById('policyModalContent');
    
    modalTitle.textContent = `🤖 AI Explanation: ${policyName}`;
    
    let html = '<div class="ai-explanation">';
    
    if (!explanation.ai_enabled) {
        html += `
            <div class="alert alert-info border-info">
                <h5 class="alert-heading"><i class="bi bi-info-circle"></i> AI Features Not Enabled</h5>
                <div class="explanation-content">${formatExplanationText(explanation.explanation)}</div>
            </div>
        `;
    } else {
        html += `
            <div class="card mb-3 border-primary">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0"><i class="bi bi-chat-dots"></i> Explanation</h5>
                </div>
                <div class="card-body">
                    <div class="explanation-content">${formatExplanationText(explanation.explanation)}</div>
                </div>
            </div>
        `;
        
        if (explanation.impact) {
            html += `
                <div class="card mb-3 border-warning">
                    <div class="card-header bg-warning">
                        <h5 class="mb-0"><i class="bi bi-people"></i> User Impact</h5>
                    </div>
                    <div class="card-body">
                        <div class="impact-content">${formatExplanationText(explanation.impact)}</div>
                    </div>
                </div>
            `;
        }
        
        if (explanation.recommendations && explanation.recommendations.length > 0) {
            html += `
                <div class="card mb-3 border-success">
                    <div class="card-header bg-success text-white">
                        <h5 class="mb-0"><i class="bi bi-lightbulb"></i> Recommendations</h5>
                    </div>
                    <div class="card-body">
                        <ul class="recommendations-list mb-0">
                            ${explanation.recommendations.map(rec => `<li>${escapeHtml(rec)}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }
        
        html += `
            <div class="alert alert-light border mb-0">
                <small class="text-muted"><i class="bi bi-stars"></i> Generated by AI Assistant</small>
            </div>
        `;
    }
    
    html += '</div>';
    
    modalContent.innerHTML = html;
    new bootstrap.Modal(document.getElementById('policyModal')).show();
}

function formatExplanationText(text) {
    if (!text) return '';
    // Convert markdown-style formatting to HTML
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        .replace(/^- (.*?)(<br>|$)/gm, '<li>$1</li>')
        .replace(/(<li>.*?<\/li>)+/g, '<ul>$&</ul>')
        .split('<p>').map(p => p ? `<p>${p}</p>` : '').join('');
}

// Delete policy
async function deletePolicy(policyId, policyName) {
    if (!confirm(`Are you sure you want to delete "${policyName}"?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/policies/${policyId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Policy deleted successfully', 'success');
            refreshPolicies();
        } else {
            showToast('Failed to delete policy: ' + data.error, 'danger');
        }
    } catch (error) {
        showToast('Error deleting policy: ' + error.message, 'danger');
    }
}

// Bulk delete policies
async function bulkDeletePolicies() {
    if (selectedPolicyIds.size === 0) {
        showToast('No policies selected', 'warning');
        return;
    }
    
    if (!confirm(`Delete ${selectedPolicyIds.size} selected policies?`)) {
        return;
    }
    
    const progressBar = document.getElementById('bulkProgressBar');
    const progress = document.getElementById('bulkProgress');
    const status = document.getElementById('bulkStatus');
    
    const policyIds = Array.from(selectedPolicyIds);
    const total = policyIds.length;
    let completed = 0;
    let succeeded = 0;
    let failed = 0;
    
    progress.classList.remove('d-none');
    progressBar.style.width = '0%';
    
    // Create console-style output
    status.innerHTML = '<div class="bg-dark text-light p-3 rounded" style="max-height: 300px; overflow-y: auto; font-family: monospace; font-size: 0.85rem;" id="consoleOutput"></div>';
    const consoleOutput = document.getElementById('consoleOutput');
    
    const addLog = (message, type = 'info') => {
        const colors = {
            'info': 'text-info',
            'success': 'text-success',
            'error': 'text-danger',
            'warning': 'text-warning'
        };
        const timestamp = new Date().toLocaleTimeString();
        consoleOutput.innerHTML += `<div class="${colors[type]}">[${timestamp}] ${message}</div>`;
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    };
    
    addLog(`Starting bulk delete of ${total} policies...`, 'info');
    
    try {
        // Process policies one at a time for better progress tracking
        for (let i = 0; i < policyIds.length; i++) {
            const policyId = policyIds[i];
            const policyName = allPolicies.find(p => p.id === policyId)?.displayName || policyId.substring(0, 8);
            
            try {
                addLog(`Deleting: ${policyName}...`, 'info');
                
                const response = await fetch(`/api/policies/${policyId}`, {
                    method: 'DELETE'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    succeeded++;
                    addLog(`✓ Successfully deleted: ${policyName}`, 'success');
                } else {
                    failed++;
                    addLog(`✗ Failed to delete ${policyName}: ${data.error}`, 'error');
                }
            } catch (error) {
                failed++;
                addLog(`✗ Error deleting ${policyName}: ${error.message}`, 'error');
            }
            
            completed++;
            const percentComplete = Math.round((completed / total) * 100);
            progressBar.style.width = `${percentComplete}%`;
            progressBar.textContent = `${percentComplete}%`;
        }
        
        // Final summary
        addLog(`\n=== Bulk Delete Complete ===`, 'info');
        addLog(`Total: ${total} | Succeeded: ${succeeded} | Failed: ${failed}`, succeeded === total ? 'success' : 'warning');
        
        if (succeeded > 0) {
            showToast(`Deleted ${succeeded} of ${total} policies`, succeeded === total ? 'success' : 'warning');
            selectedPolicyIds.clear();
            updateBulkOperationsBar();
            refreshPolicies();
        }
        
    } catch (error) {
        addLog(`Fatal error: ${error.message}`, 'error');
        showToast('Error during bulk delete: ' + error.message, 'danger');
    }
}

// Global select/deselect
function selectAllPoliciesGlobal() {
    document.getElementById('selectAllPolicies').checked = true;
    toggleSelectAll();
}

function deselectAllPoliciesGlobal() {
    document.getElementById('selectAllPolicies').checked = false;
    toggleSelectAll();
}

// Load templates
async function loadTemplates() {
    try {
        const response = await fetch('/api/templates');
        const data = await response.json();
        
        if (data.success) {
            displayTemplates(data.templates, data.categories);
        }
    } catch (error) {
        console.error('Error loading templates:', error);
    }
}

// Display templates
function displayTemplates(templates, categories) {
    const container = document.getElementById('templatesContainer');
    
    // Group templates by category
    const grouped = {};
    templates.forEach(template => {
        if (!grouped[template.category]) {
            grouped[template.category] = [];
        }
        grouped[template.category].push(template);
    });
    
    container.innerHTML = categories.map(category => `
        <div class="col-12 template-category">
            <h5 class="template-category-title">${category.toUpperCase()}</h5>
            <div class="row">
                ${grouped[category] ? grouped[category].map(template => `
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card template-card h-100">
                            <div class="card-body">
                                <h6 class="card-title">${template.display_name}</h6>
                                <p class="card-text small text-muted">
                                    <span class="badge ${getStateBadgeClass(template.state)}">${template.state}</span>
                                </p>
                                <div class="d-flex gap-2">
                                    <button class="btn btn-sm btn-outline-secondary" onclick='viewTemplatePreview(${JSON.stringify(template.template)}, "${template.display_name}")' title="Preview configuration">
                                        <i class="bi bi-eye"></i> Preview
                                    </button>
                                    <button class="btn btn-sm btn-primary" onclick='deployTemplate(${JSON.stringify(template.template)}, "${template.display_name}")'>
                                        <i class="bi bi-download"></i> Deploy
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('') : ''}
            </div>
        </div>
    `).join('');
}

// Deploy template
async function deployTemplate(template, displayName) {
    if (!confirm(`Deploy template: ${displayName}?`)) {
        return;
    }
    
    // Show a loading toast
    const loadingToast = showToast(`Deploying ${displayName}...`, 'info');
    
    try {
        const response = await fetch('/api/templates/deploy', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ template })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`✓ Successfully deployed: ${displayName}`, 'success');
            refreshPolicies();
        } else {
            showToast(`✗ Failed to deploy ${displayName}: ${data.error}`, 'danger');
        }
    } catch (error) {
        showToast(`✗ Error deploying ${displayName}: ${error.message}`, 'danger');
    }
}

// Deploy all templates
async function deployAllTemplates() {
    if (!confirm('Deploy ALL templates? This will create many policies.')) {
        return;
    }
    
    // Show progress modal
    const modal = new bootstrap.Modal(document.getElementById('progressModal'));
    const modalTitle = document.getElementById('progressModalTitle');
    const progressBar = document.getElementById('progressModalBar');
    const consoleOutput = document.getElementById('progressModalConsole');
    const closeButton = document.getElementById('progressModalClose');
    
    modalTitle.textContent = 'Deploying Templates';
    progressBar.style.width = '0%';
    progressBar.textContent = '0%';
    consoleOutput.innerHTML = '';
    closeButton.disabled = true;
    modal.show();
    
    const addLog = (message, type = 'info') => {
        const colors = {
            'info': 'text-info',
            'success': 'text-success',
            'error': 'text-danger',
            'warning': 'text-warning'
        };
        const timestamp = new Date().toLocaleTimeString();
        consoleOutput.innerHTML += `<div class="${colors[type]}">[${timestamp}] ${message}</div>`;
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    };
    
    try {
        // Get all templates
        const templatesResponse = await fetch('/api/templates');
        const templatesData = await templatesResponse.json();
        
        if (!templatesData.success) {
            addLog('Failed to load templates', 'error');
            closeButton.disabled = false;
            return;
        }
        
        // templatesData.templates is already an array of template objects
        const allTemplates = templatesData.templates;
        
        const total = allTemplates.length;
        let completed = 0;
        let succeeded = 0;
        let failed = 0;
        
        addLog(`Starting deployment of ${total} templates...`, 'info');
        
        // Deploy templates one at a time
        for (const item of allTemplates) {
            try {
                addLog(`Deploying: ${item.display_name || item.name}...`, 'info');
                
                const response = await fetch('/api/templates/deploy', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ template: item.template })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    succeeded++;
                    addLog(`✓ Successfully deployed: ${item.display_name || item.name}`, 'success');
                } else {
                    failed++;
                    addLog(`✗ Failed to deploy ${item.display_name || item.name}: ${data.error}`, 'error');
                }
            } catch (error) {
                failed++;
                addLog(`✗ Error deploying ${item.display_name || item.name}: ${error.message}`, 'error');
            }
            
            completed++;
            const percentComplete = Math.round((completed / total) * 100);
            progressBar.style.width = `${percentComplete}%`;
            progressBar.textContent = `${percentComplete}%`;
        }
        
        // Final summary
        addLog(`\n=== Deployment Complete ===`, 'info');
        addLog(`Total: ${total} | Succeeded: ${succeeded} | Failed: ${failed}`, succeeded === total ? 'success' : 'warning');
        
        if (succeeded > 0) {
            showToast(`Deployed ${succeeded} of ${total} templates`, succeeded === total ? 'success' : 'warning');
            refreshPolicies();
        }
        
    } catch (error) {
        addLog(`Fatal error: ${error.message}`, 'error');
        showToast('Error deploying templates: ' + error.message, 'danger');
    } finally {
        closeButton.disabled = false;
    }
}

// Create all CA policy groups
async function createCAGroups() {
    // Show progress modal
    const modal = new bootstrap.Modal(document.getElementById('progressModal'));
    document.getElementById('progressModalTitle').textContent = 'Creating Framework Groups';
    document.getElementById('progressModalConsole').innerHTML = '';
    
    const progressBar = document.getElementById('progressModalBar');
    progressBar.style.width = '0%';
    progressBar.textContent = '0%';
    
    const closeButton = modal._element.querySelector('.btn-secondary');
    closeButton.disabled = true;
    
    modal.show();
    
    function addLog(message, type = 'info') {
        const console = document.getElementById('progressModalConsole');
        const color = {
            'success': '#28a745',
            'error': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8'
        }[type] || '#ffffff';
        
        const timestamp = new Date().toLocaleTimeString();
        console.innerHTML += `<div style="color: ${color};">[${timestamp}] ${message}</div>`;
        console.scrollTop = console.scrollHeight;
    }
    
    try {
        addLog('Starting group creation...', 'info');
        addLog('This will create approximately 66 security groups', 'info');
        addLog('', 'info');
        
        progressBar.style.width = '10%';
        progressBar.textContent = '10%';
        
        const response = await fetch('/api/groups/create-ca-groups', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        progressBar.style.width = '90%';
        progressBar.textContent = '90%';
        
        const data = await response.json();
        
        if (data.success) {
            addLog(`\n=== Group Creation Complete ===`, 'success');
            addLog(`Total Groups: ${data.total}`, 'info');
            addLog(`Created: ${data.created}`, 'success');
            addLog(`Already Existed: ${data.skipped}`, 'warning');
            
            if (data.errors && data.errors.length > 0) {
                addLog(`\nErrors (${data.errors.length}):`, 'error');
                data.errors.forEach(err => addLog(err, 'error'));
            }
            
            progressBar.style.width = '100%';
            progressBar.textContent = '100%';
            progressBar.classList.remove('bg-primary');
            progressBar.classList.add('bg-success');
            
            showToast(data.message, 'success');
        } else {
            addLog(`\nError: ${data.error}`, 'error');
            progressBar.classList.remove('bg-primary');
            progressBar.classList.add('bg-danger');
            showToast('Failed to create groups: ' + data.error, 'danger');
        }
        
    } catch (error) {
        addLog(`\nFatal error: ${error.message}`, 'error');
        progressBar.classList.remove('bg-primary');
        progressBar.classList.add('bg-danger');
        showToast('Error creating groups: ' + error.message, 'danger');
    } finally {
        closeButton.disabled = false;
    }
}

// Upload and analyze report
async function uploadReport() {
    const fileInput = document.getElementById('reportFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showToast('Please select a file', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showToast('Uploading and analyzing report...', 'info');
    
    try {
        // Upload file
        const uploadResponse = await fetch('/api/report/upload', {
            method: 'POST',
            body: formData
        });
        
        const uploadData = await uploadResponse.json();
        
        if (!uploadData.success) {
            showToast('Upload failed: ' + uploadData.error, 'danger');
            return;
        }
        
        // Analyze report
        const analyzeResponse = await fetch('/api/report/analyze', {
            method: 'POST'
        });
        
        const analyzeData = await analyzeResponse.json();
        
        if (analyzeData.success) {
            displayReportResults(analyzeData);
            showToast(analyzeData.message, 'success');
        } else {
            showToast('Analysis failed: ' + analyzeData.error, 'danger');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'danger');
    }
}

// Display report results
function displayReportResults(data) {
    // Show statistics
    document.getElementById('reportStats').classList.remove('d-none');
    document.getElementById('statTotal').textContent = data.stats.total_findings;
    document.getElementById('statHigh').textContent = data.stats.by_severity.High || 0;
    document.getElementById('statMedium').textContent = data.stats.by_severity.Medium || 0;
    document.getElementById('statLow').textContent = data.stats.by_severity.Low || 0;
    document.getElementById('statFailed').textContent = data.stats.by_status.Failed || 0;
    document.getElementById('statMapped').textContent = data.stats.mapped_policy_types;
    
    // Display findings (failed only)
    const failedFindings = data.findings.filter(f => f.status === 'Failed');
    const findingsList = document.getElementById('findingsList');
    findingsList.innerHTML = failedFindings.map(finding => `
        <div class="finding-item severity-${finding.severity.toLowerCase()}">
            <strong>${finding.title}</strong>
            <div class="small text-muted mt-1">
                <span class="badge bg-${finding.severity === 'High' ? 'danger' : finding.severity === 'Medium' ? 'warning' : 'info'}">
                    ${finding.severity}
                </span>
                <span class="badge bg-secondary">${finding.status}</span>
            </div>
            ${finding.mapped_policies && finding.mapped_policies.length > 0 ? 
                `<div class="small mt-1">Mapped: ${finding.mapped_policies.join(', ')}</div>` : ''}
        </div>
    `).join('');
    
    // Display recommendations
    allRecommendations = data.recommendations;
    const recommendationsList = document.getElementById('recommendationsList');
    recommendationsList.innerHTML = data.recommendations.map((rec, index) => `
        <div class="recommendation-item" onclick="toggleRecommendation(${index})" id="rec-${index}">
            <div class="form-check">
                <input class="form-check-input" type="checkbox" id="rec-check-${index}">
                <label class="form-check-label w-100" for="rec-check-${index}">
                    <strong>${rec.policy_display_name}</strong>
                    <div class="small text-muted mt-1">
                        <span class="badge bg-primary">${rec.policy_category}</span>
                        <span class="badge bg-success">${Math.round(rec.relevance_score * 100)}% match</span>
                    </div>
                    <div class="small mt-1">Addresses: ${rec.finding_title.substring(0, 60)}...</div>
                </label>
            </div>
        </div>
    `).join('');
    
    // Show results
    document.getElementById('reportResults').classList.remove('d-none');
}

// Toggle recommendation selection
function toggleRecommendation(index) {
    const item = document.getElementById(`rec-${index}`);
    const checkbox = document.getElementById(`rec-check-${index}`);
    
    checkbox.checked = !checkbox.checked;
    
    if (checkbox.checked) {
        selectedRecommendations.add(index);
        item.classList.add('selected');
    } else {
        selectedRecommendations.delete(index);
        item.classList.remove('selected');
    }
}

// Deploy selected recommendations
async function deploySelectedRecommendations() {
    if (selectedRecommendations.size === 0) {
        showToast('No recommendations selected', 'warning');
        return;
    }
    
    if (!confirm(`Deploy ${selectedRecommendations.size} selected policies?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/report/deploy-recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                indices: Array.from(selectedRecommendations)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message, 'success');
            selectedRecommendations.clear();
            refreshPolicies();
        } else {
            showToast('Deployment failed: ' + data.error, 'danger');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'danger');
    }
}

// Deploy all recommendations
async function deployAllRecommendations() {
    if (!allRecommendations || allRecommendations.length === 0) {
        showToast('No recommendations available', 'warning');
        return;
    }
    
    if (!confirm(`Deploy ALL ${allRecommendations.length} recommended policies?`)) {
        return;
    }
    
    const indices = Array.from({length: allRecommendations.length}, (_, i) => i);
    
    try {
        const response = await fetch('/api/report/deploy-recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ indices })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(data.message, 'success');
            refreshPolicies();
        } else {
            showToast('Deployment failed: ' + data.error, 'danger');
        }
    } catch (error) {
        showToast('Error: ' + error.message, 'danger');
    }
}

// Export findings to Excel
function exportFindings() {
    window.location.href = '/api/report/export';
}

// AI Statistics Functions
async function loadAIStats() {
    try {
        const response = await fetch('/api/ai/stats');
        const data = await response.json();
        
        if (response.ok && data.ai_enabled) {
            updateAIStatsDisplay(data);
        }
    } catch (error) {
        console.error('Error loading AI stats:', error);
    }
}

function updateAIStatsDisplay(stats) {
    // Show the stats card
    const statsCard = document.getElementById('aiStatsCard');
    if (statsCard) {
        statsCard.classList.remove('d-none');
    }
    
    // Update individual stat displays
    document.getElementById('aiExplanationsCount').textContent = stats.explanations || stats.total_explanations || 0;
    document.getElementById('aiTokensUsed').textContent = (stats.tokens_used || stats.total_tokens || 0).toLocaleString();
    document.getElementById('aiCostEstimate').textContent = '$' + (stats.total_cost || 0).toFixed(4);
    document.getElementById('aiAvgResponseTime').textContent = (stats.avg_response_time || stats.avg_response_time || 0).toFixed(1) + 's';
    
    // Update navbar badge
    const costBadge = document.getElementById('aiCostBadge');
    const costAmount = document.getElementById('aiCostAmount');
    if (costBadge && costAmount && stats.total_cost > 0) {
        costBadge.classList.remove('d-none');
        costAmount.textContent = '$' + (stats.total_cost || 0).toFixed(4);
    }
}

// Named Locations Functions
async function loadNamedLocations() {
    const container = document.getElementById('namedLocationsContainer');
    container.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Loading named locations...</p></div>';
    
    try {
        const response = await fetch('/api/named-locations');
        const data = await response.json();
        
        if (!response.ok) {
            container.innerHTML = `<div class="alert alert-danger">Error: ${escapeHtml(data.error || 'Failed to load locations')}</div>`;
            return;
        }
        
        if (!data.locations || data.locations.length === 0) {
            container.innerHTML = '<div class="text-center text-muted py-4"><p>No named locations found</p></div>';
            return;
        }
        
        container.innerHTML = renderNamedLocationsTable(data.locations);
    } catch (error) {
        container.innerHTML = `<div class="alert alert-danger">Exception: ${escapeHtml(error.message)}</div>`;
    }
}

function renderNamedLocationsTable(locations) {
    const rows = locations.map(loc => `
        <tr>
            <td><strong>${escapeHtml(loc.displayName || 'Unnamed')}</strong></td>
            <td><span class="badge bg-secondary">${escapeHtml(loc.type)}</span></td>
            <td>
                ${loc.isTrusted 
                    ? '<span class="badge bg-success"><i class="bi bi-shield-check"></i> Trusted</span>' 
                    : '<span class="badge bg-light text-dark"><i class="bi bi-shield-x"></i> Untrusted</span>'}
            </td>
            <td>
                ${loc.ipRanges.length > 0 
                    ? loc.ipRanges.map(ip => `<code class="ip-range">${escapeHtml(ip)}</code>`).join(' ')
                    : '<span class="text-muted">-</span>'}
            </td>
            <td>
                ${loc.countriesAndRegions.length > 0
                    ? loc.countriesAndRegions.map(c => `<span class="badge bg-info text-dark">${escapeHtml(c)}</span>`).join(' ')
                    : '<span class="text-muted">-</span>'}
            </td>
            <td class="text-center">
                ${loc.includeUnknownCountriesAndRegions 
                    ? '<i class="bi bi-check-circle-fill text-warning"></i>' 
                    : '<span class="text-muted">-</span>'}
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewNamedLocation('${loc.id}')" title="View Details">
                    <i class="bi bi-eye"></i>
                </button>
            </td>
        </tr>
    `).join('');
    
    return `
        <div class="table-responsive">
            <table class="table table-hover align-middle">
                <thead class="table-light">
                    <tr>
                        <th>Display Name</th>
                        <th>Type</th>
                        <th>Trust Status</th>
                        <th>IP Ranges (CIDR)</th>
                        <th>Countries/Regions</th>
                        <th class="text-center">Include Unknown</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>
        <div class="small text-muted mt-2">
            <i class="bi bi-info-circle"></i> Requires Graph permission: <code>Policy.Read.All</code>
        </div>
    `;
}

async function viewNamedLocation(locationId) {
    const modal = document.getElementById('policyModal');
    const title = document.getElementById('policyModalLabel');
    const body = document.getElementById('policyDetails');
    
    title.textContent = 'Named Location Details';
    body.innerHTML = '<div class="text-center"><div class="spinner-border"></div><p class="mt-2">Loading...</p></div>';
    new bootstrap.Modal(modal).show();
    
    try {
        const response = await fetch('/api/named-locations');
        const data = await response.json();
        
        if (!response.ok) {
            body.innerHTML = `<div class="alert alert-danger">Error: ${escapeHtml(data.error)}</div>`;
            return;
        }
        
        const location = data.locations.find(l => l.id === locationId);
        
        if (!location) {
            body.innerHTML = '<div class="alert alert-warning">Location not found</div>';
            return;
        }
        
        title.textContent = `Named Location: ${location.displayName}`;
        body.innerHTML = `
            <div class="mb-3">
                <h6>Location Type:</h6>
                <span class="badge bg-secondary">${escapeHtml(location.type)}</span>
            </div>
            ${location.isTrusted ? `
                <div class="mb-3">
                    <h6>Trust Status:</h6>
                    <span class="badge bg-success"><i class="bi bi-shield-check"></i> Trusted Location</span>
                </div>
            ` : ''}
            ${location.ipRanges.length > 0 ? `
                <div class="mb-3">
                    <h6>IP Ranges (CIDR):</h6>
                    <div class="d-flex flex-wrap gap-2">
                        ${location.ipRanges.map(ip => `<code class="ip-range">${escapeHtml(ip)}</code>`).join('')}
                    </div>
                </div>
            ` : ''}
            ${location.countriesAndRegions.length > 0 ? `
                <div class="mb-3">
                    <h6>Countries/Regions:</h6>
                    <div class="d-flex flex-wrap gap-2">
                        ${location.countriesAndRegions.map(c => `<span class="badge bg-info text-dark">${escapeHtml(c)}</span>`).join('')}
                    </div>
                </div>
            ` : ''}
            ${location.includeUnknownCountriesAndRegions ? `
                <div class="mb-3">
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i> Includes unknown countries and regions
                    </div>
                </div>
            ` : ''}
            <hr>
            <h6>Full JSON:</h6>
            <pre class="bg-light p-3 rounded" style="max-height: 300px; overflow-y: auto;">${escapeHtml(JSON.stringify(location, null, 2))}</pre>
        `;
    } catch (error) {
        body.innerHTML = `<div class="alert alert-danger">Exception: ${escapeHtml(error.message)}</div>`;
    }
}
