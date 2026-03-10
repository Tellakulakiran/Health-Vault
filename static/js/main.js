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

// Fetch helper that handles 401s
async function authFetch(url, options = {}) {
    const response = await fetch(url, options);
    if (response.status === 401) {
        window.location.href = '/login';
    }
    return response;
}

// Determine badge class
function getRiskBadgeClass(score) {
    if (score >= 75) return 'badge-danger';
    if (score >= 40) return 'badge-warning';
    return 'badge-normal';
}

// Dashboard Initializer
if (document.getElementById('dashboard-app')) {
    
    // Load Records
    async function loadRecords() {
        try {
            const res = await authFetch('/api/records/');
            if (!res.ok) throw new Error('Failed to load records');
            const records = await res.json();
            
            const list = document.getElementById('records-list');
            list.innerHTML = '';
            
            if (records.length === 0) {
                list.innerHTML = '<p class="text-secondary">No records found. Add one above.</p>';
            }
            
            records.forEach(r => {
                const date = new Date(r.recorded_at).toLocaleDateString();
                const badgeClass = getRiskBadgeClass(r.risk_score);
                
                list.innerHTML += `
                    <li class="data-item glass-panel">
                        <div class="data-details">
                            <strong>${date}</strong>
                            <p>HR: ${r.heart_rate} | BP: ${r.blood_pressure_systolic}/${r.blood_pressure_diastolic} | Sugar: ${r.blood_sugar} | Temp: ${r.body_temperature}</p>
                        </div>
                        <div>
                            <span class="badge ${badgeClass}">${r.risk_assessment} (Score: ${Math.round(r.risk_score)})</span>
                        </div>
                    </li>
                `;
            });
        } catch (e) {
            console.error(e);
            showToast('Failed to load records', 'error');
        }
    }

    // Load Medications
    async function loadMedications() {
        try {
            const res = await authFetch('/api/medications/');
            if (!res.ok) throw new Error('Failed to load medications');
            const meds = await res.json();
            
            const list = document.getElementById('medications-list');
            list.innerHTML = '';
            
            if (meds.length === 0) {
                list.innerHTML = '<p class="text-secondary">No medications found. Add one above.</p>';
            }
            
            meds.forEach(m => {
                list.innerHTML += `
                    <li class="data-item glass-panel" id="med-${m.id}">
                        <div class="data-details">
                            <strong>${m.name}</strong>
                            <p>${m.dosage} - ${m.frequency} at ${m.time_to_take}</p>
                        </div>
                        <button class="btn btn-danger" onclick="deleteMed(${m.id})">Del</button>
                    </li>
                `;
            });
        } catch (e) {
            console.error(e);
            showToast('Failed to load medications', 'error');
        }
    }

    // Submit Health Record
    const recordForm = document.getElementById('record-form');
    if (recordForm) {
        recordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                heart_rate: parseInt(document.getElementById('hr').value),
                blood_pressure_systolic: parseInt(document.getElementById('bp_sys').value),
                blood_pressure_diastolic: parseInt(document.getElementById('bp_dia').value),
                blood_sugar: parseFloat(document.getElementById('sugar').value),
                body_temperature: parseFloat(document.getElementById('temp').value)
            };
            
            try {
                const res = await authFetch('/api/records/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (res.ok) {
                    showToast('Record added successfully');
                    recordForm.reset();
                    loadRecords();
                } else {
                    const err = await res.json();
                    showToast(err.detail || 'Error adding record', 'error');
                }
            } catch (e) {
                showToast('Network error', 'error');
            }
        });
    }

    // Submit Medication
    const medForm = document.getElementById('med-form');
    if(medForm) {
        medForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                name: document.getElementById('med-name').value,
                dosage: document.getElementById('med-dosage').value,
                frequency: document.getElementById('med-freq').value,
                time_to_take: document.getElementById('med-time').value
            };
            
            try {
                const res = await authFetch('/api/medications/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (res.ok) {
                    showToast('Medication added successfully');
                    medForm.reset();
                    loadMedications();
                } else {
                    showToast('Error adding medication', 'error');
                }
            } catch (e) {
                showToast('Network error', 'error');
            }
        });
    }

    // Delete Med
    window.deleteMed = async (id) => {
        if(!confirm('Delete this medication?')) return;
        try {
            const res = await authFetch(`/api/medications/${id}`, { method: 'DELETE' });
            if (res.ok) {
                showToast('Deleted successfully');
                loadMedications();
            } else {
                showToast('Failed to delete', 'error');
            }
        } catch(e) {
            showToast('Network error', 'error');
        }
    }

    // Emergency Trigger
    const emBtn = document.getElementById('emergency-btn');
    const statusText = document.getElementById('emergency-status');
    const glow = document.querySelector('.radar-glow');
    
    if (emBtn) {
        emBtn.addEventListener('click', async () => {
            emBtn.disabled = true;
            statusText.innerText = "Initiating tracking...";
            glow.classList.add('active');
            
            try {
                const res = await authFetch('/api/emergency/trigger', { method: 'POST' });
                if (res.ok) {
                    const data = await res.json();
                    statusText.innerHTML = `Alert Sent!<br>Simulated Location: LAT ${data.data.simulated_location.latitude}, LNG ${data.data.simulated_location.longitude}`;
                    showToast('Emergency Services Notified', 'error'); // red toast
                } else {
                    statusText.innerText = "Error triggering emergency. Please call 911 directly.";
                    glow.classList.remove('active');
                }
            } catch (e) {
                statusText.innerText = "Network Error.";
                glow.classList.remove('active');
            }
            
            setTimeout(() => {
                emBtn.disabled = false;
                // Leave glow active for effect until page reload
            }, 3000);
        });
    }

    // Logout
    const logoutBtn = document.getElementById('logout-btn');
    if(logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            await authFetch('/api/auth/logout', { method: 'POST' });
            window.location.href = '/login';
        });
    }

    // Initialize data
    loadRecords();
    loadMedications();
}

// Login Handling
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
                const data = await res.json();
                showToast(data.detail, 'error');
            }
        } catch (e) {
            showToast('Network error', 'error');
        }
    });
}
