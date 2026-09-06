const API_BASE = window.location.origin;

const statusBadge = document.getElementById('statusBadge');
const logContainer = document.getElementById('logContainer');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const targetInput = document.getElementById('targetInput');
const dailyLimit = document.getElementById('dailyLimit');

let campaignId = null;

async function checkStatus() {
    try {
        const res = await fetch(`${API_BASE}/`);
        const data = await res.json();
        statusBadge.textContent = '● online';
        statusBadge.className = 'status-badge online';
    } catch {
        statusBadge.textContent = '● offline';
        statusBadge.className = 'status-badge';
    }
}

async function fetchLogs() {
    try {
        const res = await fetch(`${API_BASE}/logs?limit=10`);
        const logs = await res.json();
        logContainer.innerHTML = logs.map(log => 
            `<div class="line">${log}</div>`
        ).join('');
    } catch {}
}

startBtn.addEventListener('click', async () => {
    const targets = targetInput.value.split(',').map(s => s.trim());
    const limit = parseInt(dailyLimit.value) || 35;
    
    try {
        const res = await fetch(`${API_BASE}/campaign/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ targets, daily_limit: limit })
        });
        const data = await res.json();
        campaignId = data.id;
        logContainer.innerHTML = `<div class="line">[${new Date().toLocaleTimeString()}] campaign ${campaignId} started</div>` + logContainer.innerHTML;
    } catch (e) {
        logContainer.innerHTML = `<div class="line">error: ${e.message}</div>` + logContainer.innerHTML;
    }
});

stopBtn.addEventListener('click', async () => {
    if (!campaignId) return;
    try {
        await fetch(`${API_BASE}/campaign/${campaignId}/stop`, { method: 'POST' });
        logContainer.innerHTML = `<div class="line">[${new Date().toLocaleTimeString()}] campaign stopped</div>` + logContainer.innerHTML;
        campaignId = null;
    } catch {}
});

setInterval(() => {
    checkStatus();
    fetchLogs();
}, 5000);

checkStatus();
fetchLogs();