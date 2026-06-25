let token = localStorage.getItem('token');
if (!token) window.location.href = '/';

const headers    = () => ({ 'Authorization': `Bearer ${token}` });
const jsonHeaders = () => ({ ...headers(), 'Content-Type': 'application/json' });

// ── Token refresh ────────────────────────────────────────────────
async function apiFetch(url, opts = {}) {
    // Inyectar siempre el token más reciente
    opts.headers = { ...opts.headers, 'Authorization': `Bearer ${token}` };
    let res = await fetch(url, opts);

    if (res.status === 401) {
        const refreshed = await tryRefresh();
        if (!refreshed) { logout(); return res; }
        opts.headers['Authorization'] = `Bearer ${token}`;
        res = await fetch(url, opts);
    }
    return res;
}

async function tryRefresh() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return false;
    try {
        const res = await fetch('/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (!res.ok) return false;
        const data = await res.json();
        token = data.access_token;
        localStorage.setItem('token', token);
        localStorage.setItem('refresh_token', data.refresh_token);
        return true;
    } catch {
        return false;
    }
}

let activeStatus = '';
let searchTimeout = null;

// ── Bootstrap ────────────────────────────────────────────────────
const payload = JSON.parse(atob(token.split('.')[1]));
document.getElementById('nav-username').textContent = payload.sub;
if (payload.role === 'admin') {
    document.getElementById('admin-card').style.display = 'block';
    loadUsers();
}

// Status tabs
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        activeStatus = tab.dataset.status;
        loadTasks();
    });
});

loadStats();
loadCategories();
loadTasks();

// ── Stats ────────────────────────────────────────────────────────
async function loadStats() {
    const res = await apiFetch('/tasks/stats');
    if (!res.ok) return;
    const s = await res.json();
    document.getElementById('stat-total').textContent      = s.total;
    document.getElementById('stat-pending').textContent    = s.pending;
    document.getElementById('stat-inprogress').textContent = s.in_progress;
    document.getElementById('stat-done').textContent       = s.done;
    document.getElementById('stat-overdue').textContent    = s.overdue;
}

// ── Tasks ────────────────────────────────────────────────────────
async function loadTasks() {
    const params = new URLSearchParams();
    if (activeStatus) params.set('status', activeStatus);

    const priority = document.getElementById('priority-filter').value;
    if (priority) params.set('priority', priority);

    const catId = document.getElementById('category-filter').value;
    if (catId) params.set('category_id', catId);

    const search = document.getElementById('search-input').value.trim();
    if (search) params.set('search', search);

    const sortBy = document.getElementById('sort-select').value;
    params.set('sort_by', sortBy);
    params.set('order', 'desc');
    params.set('limit', '100');

    const res = await apiFetch(`/tasks/?${params}`);
    if (!res.ok) return;

    const tasks = await res.json();
    renderTasks(tasks);
}

function renderTasks(tasks) {
    const container = document.getElementById('tasks-list');
    if (!tasks.length) {
        container.innerHTML = '<div class="empty-msg">No hay tareas que coincidan.</div>';
        return;
    }
    container.innerHTML = tasks.map(t => taskCard(t)).join('');
}

function taskCard(t) {
    const today = new Date().toISOString().split('T')[0];
    const isOverdue = t.due_date && t.due_date < today && t.status !== 'done';
    const dueDateHtml = t.due_date
        ? `<span class="due-date${isOverdue ? ' overdue' : ''}">📅 ${formatDate(t.due_date)}${isOverdue ? ' · Vencida' : ''}</span>`
        : '';

    const catHtml = t.category_id ? categoryBadge(t.category_id) : '';

    const priorityLabels = { high: 'Alta', medium: 'Media', low: 'Baja' };
    const statusLabels   = { pending: 'Pendiente', in_progress: 'En progreso', done: 'Completada' };

    const nextBtn = t.status !== 'done'
        ? `<button class="btn-action btn-next" onclick="advanceTask(${t.id}, '${t.status}')">
               ${t.status === 'pending' ? '▶ Iniciar' : '✓ Completar'}
           </button>`
        : '';

    return `
    <div class="task-card priority-${t.priority} status-${t.status}" id="task-${t.id}">
        <div class="task-body">
            <div class="task-title">${escHtml(t.title)}</div>
            ${t.description ? `<div class="task-desc">${escHtml(t.description)}</div>` : ''}
            <div class="task-meta">
                <span class="badge badge-priority-${t.priority}">${priorityLabels[t.priority]}</span>
                <span class="badge badge-status-${t.status}">${statusLabels[t.status]}</span>
                ${catHtml}
                ${dueDateHtml}
            </div>
        </div>
        <div class="task-actions">
            ${nextBtn}
            <button class="btn-action btn-delete" onclick="deleteTask(${t.id})">✕</button>
        </div>
    </div>`;
}

function categoryBadge(catId) {
    const cat = window._categories?.find(c => c.id === catId);
    if (!cat) return '';
    return `<span class="badge-cat" style="background:${cat.color}">${escHtml(cat.name)}</span>`;
}

async function advanceTask(id, currentStatus) {
    const next = currentStatus === 'pending' ? 'in_progress' : 'done';
    const res = await apiFetch(`/tasks/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: next }),
    });
    if (res.ok) { loadTasks(); loadStats(); }
}

async function deleteTask(id) {
    const res = await apiFetch(`/tasks/${id}`, { method: 'DELETE' });
    if (res.ok) { loadTasks(); loadStats(); }
}

async function createTask() {
    const title = document.getElementById('task-title').value.trim();
    const msg   = document.getElementById('task-msg');
    if (!title) { msg.textContent = 'El título es obligatorio.'; return; }

    const priority    = document.getElementById('task-priority').value;
    const due_date    = document.getElementById('task-due').value || null;
    const catVal      = document.getElementById('task-category').value;
    const category_id = catVal ? parseInt(catVal) : null;
    const description = document.getElementById('task-desc').value.trim() || null;

    const res = await apiFetch('/tasks/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description, priority, due_date, category_id }),
    });

    if (res.ok) {
        msg.textContent = 'Tarea creada';
        document.getElementById('task-title').value = '';
        document.getElementById('task-desc').value  = '';
        document.getElementById('task-due').value   = '';
        setTimeout(() => msg.textContent = '', 2500);
        loadTasks();
        loadStats();
    } else {
        msg.textContent = 'Error al crear la tarea.';
    }
}

// ── Categories ───────────────────────────────────────────────────
async function loadCategories() {
    const res = await apiFetch('/categories/');
    if (!res.ok) return;
    window._categories = await res.json();
    renderCategories();
    populateCategorySelects();
}

function renderCategories() {
    const cats = window._categories || [];
    document.getElementById('categories-list').innerHTML = cats.map(c => `
        <span class="cat-chip" style="background:${c.color}">
            ${escHtml(c.name)}
            <button class="cat-chip-del" onclick="deleteCategory(${c.id})" title="Eliminar">×</button>
        </span>
    `).join('') || '<span style="font-size:0.8rem;color:#94a3b8">Sin categorías</span>';
}

function populateCategorySelects() {
    const cats = window._categories || [];
    const options = cats.map(c => `<option value="${c.id}">${escHtml(c.name)}</option>`).join('');

    const filterSel = document.getElementById('category-filter');
    const currentFilter = filterSel.value;
    filterSel.innerHTML = `<option value="">Categoría</option>${options}`;
    filterSel.value = currentFilter;

    const taskSel = document.getElementById('task-category');
    const currentTask = taskSel.value;
    taskSel.innerHTML = `<option value="">Sin categoría</option>${options}`;
    taskSel.value = currentTask;
}

async function createCategory() {
    const name = document.getElementById('cat-name').value.trim();
    const color = document.getElementById('cat-color').value;
    const msg = document.getElementById('cat-msg');
    if (!name) { msg.textContent = 'Ingresá un nombre.'; return; }

    const res = await apiFetch('/categories/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, color }),
    });
    if (res.ok) {
        document.getElementById('cat-name').value = '';
        msg.textContent = '';
        await loadCategories();
    } else if (res.status === 409) {
        msg.textContent = 'Ya existe esa categoría.';
    } else {
        msg.textContent = 'Error al crear.';
    }
}

async function deleteCategory(id) {
    const res = await apiFetch(`/categories/${id}`, { method: 'DELETE' });
    if (res.ok) { await loadCategories(); loadTasks(); }
}

// ── Users (admin) ────────────────────────────────────────────────
async function loadUsers() {
    const res = await apiFetch('/users/');
    if (!res.ok) return;
    const users = await res.json();
    document.getElementById('users-list').innerHTML = users.map(u => `
        <div class="user-row">
            <span>${u.username} <span style="color:#94a3b8">#${u.id}</span></span>
            ${u.role === 'admin' ? '<span class="user-badge-admin">admin</span>' : ''}
        </div>
    `).join('');
}

async function deleteUser() {
    const userId = document.getElementById('delete-user-id').value.trim();
    const msg = document.getElementById('delete-user-msg');
    if (!userId) { msg.textContent = 'Ingresá un ID.'; return; }

    const res = await apiFetch(`/users/${userId}`, { method: 'DELETE' });
    if (res.ok) {
        msg.textContent = 'Usuario eliminado.';
        document.getElementById('delete-user-id').value = '';
        loadUsers();
    } else if (res.status === 404) {
        msg.textContent = 'Usuario no encontrado.';
    } else if (res.status === 400) {
        msg.textContent = 'No podés eliminarte a vos mismo.';
    } else {
        msg.textContent = 'Sin permisos.';
    }
}

// ── Utils ────────────────────────────────────────────────────────
function onSearchInput() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(loadTasks, 300);
}

function formatDate(iso) {
    const [y, m, d] = iso.split('-');
    return `${d}/${m}/${y}`;
}

function escHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/';
}

// ── WebSocket ────────────────────────────────────────────────────
(function initWebSocket() {
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    const url   = `${proto}://${location.host}/ws?token=${encodeURIComponent(token)}`;
    let ws, reconnectDelay = 1000;

    function connect() {
        ws = new WebSocket(url);

        ws.onopen = () => {
            reconnectDelay = 1000;
        };

        ws.onmessage = ({ data }) => {
            const msg = JSON.parse(data);
            handleWsEvent(msg);
        };

        ws.onclose = () => {
            // Reconectar con backoff exponencial (máx 30s)
            setTimeout(connect, reconnectDelay);
            reconnectDelay = Math.min(reconnectDelay * 2, 30000);
        };
    }

    connect();
})();

function handleWsEvent(msg) {
    const myUsername = payload.sub;
    const isOwnAction = msg.username === myUsername;

    // Siempre refrescar stats y lista al recibir cualquier evento
    loadStats();
    loadTasks();

    // Solo mostrar toast si la acción fue de otro usuario
    if (!isOwnAction) {
        const configs = {
            task_created: { cls: 'created', icon: '✦', label: 'Nueva tarea creada' },
            task_updated: { cls: 'updated', icon: '↻', label: 'Tarea actualizada'  },
            task_deleted: { cls: 'deleted', icon: '✕', label: 'Tarea eliminada'    },
        };
        const cfg = configs[msg.event];
        if (cfg) showToast(cfg.cls, cfg.icon, cfg.label, `${msg.username}: "${msg.title}"`);
    }
}

function showToast(cls, icon, title, message) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${cls}`;
    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <div class="toast-body">
            <div class="toast-title">${escHtml(title)}</div>
            <div class="toast-msg">${escHtml(message)}</div>
        </div>
        <button class="toast-close" onclick="dismissToast(this.parentElement)">×</button>
    `;
    container.appendChild(toast);

    // Auto-dismiss después de 4 segundos
    setTimeout(() => dismissToast(toast), 4000);
}

function dismissToast(el) {
    if (!el || !el.parentElement) return;
    el.classList.add('hiding');
    el.addEventListener('animationend', () => el.remove(), { once: true });
}
