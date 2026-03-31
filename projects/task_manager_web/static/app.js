let currentFilter = 'all';

document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    document.getElementById('addTaskBtn').onclick = () => {
        document.getElementById('taskModal').style.display = 'block';
    };
    document.querySelector('.close').onclick = () => {
        document.getElementById('taskModal').style.display = 'none';
    };
    document.getElementById('taskForm').onsubmit = async (e) => {
        e.preventDefault();
        await createTask();
    };
});

async function loadTasks() {
    const tasks = await fetch('/api/tasks').then(r => r.json());
    displayTasks(tasks);
}

function displayTasks(tasks) {
    const filtered = currentFilter === 'all' ? tasks : tasks.filter(t => t.status === currentFilter);
    document.getElementById('taskList').innerHTML = filtered.map(task => `
        <div class="task-card">
            <h3>${task.title}</h3>
            <p>${task.description}</p>
            <span>Priority: ${task.priority}</span>
        </div>
    `).join('');
}

async function createTask() {
    await fetch('/api/tasks', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            title: document.getElementById('taskTitle').value,
            description: document.getElementById('taskDescription').value,
            priority: document.getElementById('taskPriority').value
        })
    });
    document.getElementById('taskModal').style.display = 'none';
    document.getElementById('taskForm').reset();
    loadTasks();
}
