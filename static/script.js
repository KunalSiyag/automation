function fetchStats() {
    fetch('/api/stats')
        .then(res => res.json())
        .then(data => {
            // Update Commits
            const commitList = document.getElementById('commit-list');
            commitList.innerHTML = '';
            data.commits.forEach(c => {
                const item = document.createElement('div');
                item.className = 'commit-item';
                item.innerHTML = `
                    <div class="commit-dot">■</div>
                    <div class="commit-info">
                        <div class="commit-hash">${c.hash}</div>
                        <div class="commit-desc">${c.msg}</div>
                    </div>
                `;
                commitList.appendChild(item);
            });

            if (data.commits.length > 0) {
                document.getElementById('last-commit-msg').innerText = `LAST_COMMIT: "${data.commits[0].msg}"`;
            }

            // Update Agent Statuses
            document.getElementById('supervisor-status').innerText = data.supervisor ? 'MONITORING' : 'OFFLINE';
            document.getElementById('openclaw-status').innerText = data.openclaw ? 'ACTIVE' : 'IDLE';
            document.getElementById('commits-today').innerText = data.commits_today;
        })
        .catch(err => console.error("Error fetching stats:", err));
}

function fetchLogs() {
    fetch('/api/logs')
        .then(res => res.json())
        .then(data => {
            const content = document.getElementById('terminal-content');

            content.innerHTML = '';
            data.logs.forEach(log => {
                const line = document.createElement('div');
                line.className = 'log-line';
                if (log.includes('ERROR') || log.includes('WARN')) {
                    line.classList.add('warn');
                } else if (log.includes('SUCCESS') || log.includes('INITIALIZING')) {
                    line.classList.add('success');
                } else if (log.includes('OpenClaw')) {
                    line.classList.add('cyan');
                } else {
                    line.classList.add('info');
                }
                line.innerText = log;
                content.appendChild(line);
            });
            content.scrollTop = content.scrollHeight;
        })
        .catch(err => console.error("Error fetching logs:", err));
}

setInterval(fetchStats, 5000);
setInterval(fetchLogs, 3000);

// Initial fetches
fetchStats();
fetchLogs();