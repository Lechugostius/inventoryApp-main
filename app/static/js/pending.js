const PENDING_API_URL  = '/api/pending-purchases';
const PENDING_MARK_URL = '/api/pending-purchases/mark';
let allProducts = [];

// ── Tabs ──────────────────────────────────────────────────────────────────────
function switchTab(tab) {
    document.querySelectorAll('.cp-tab').forEach(b => b.classList.remove('active'));
    ['pending', 'purchased'].forEach(t =>
        document.getElementById('panel-' + t).classList.toggle('d-none', t !== tab)
    );
    document.getElementById('tab-' + tab).classList.add('active');
}

// ── Modal ─────────────────────────────────────────────────────────────────────
function showConfirmModal(name) {
    return new Promise(resolve => {
        const modal = document.getElementById('confirm-modal');
        document.getElementById('modal-message').innerHTML =
            `<strong>${escapeHtml(name)}</strong> volverá a la lista de Pendientes. ¿Confirmas?`;
        modal.classList.remove('d-none');
        document.getElementById('modal-confirm').onclick = () => { modal.classList.add('d-none'); resolve(true); };
        document.getElementById('modal-cancel').onclick  = () => { modal.classList.add('d-none'); resolve(false); };
    });
}

// ── Render ────────────────────────────────────────────────────────────────────
function renderProducts() {
    const pending   = allProducts.filter(p => p.status !== 'purchased');
    const purchased = allProducts.filter(p => p.status === 'purchased');
    document.getElementById('badge-pending').textContent   = pending.length;
    document.getElementById('badge-purchased').textContent = purchased.length;
    renderList('container-pending',   pending,   false);
    renderList('container-purchased', purchased, true);
}

function renderList(containerId, products, isPurchased) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (products.length === 0) {
        container.innerHTML = `
            <div class="pending-empty">
                <i class="fas ${isPurchased ? 'fa-inbox' : 'fa-check-circle'}"></i>
                <p class="mb-0 mt-2">
                    ${isPurchased ? 'Sin pedidos realizados aún' : '¡Todo en orden! Sin productos críticos'}
                </p>
            </div>`;
        return;
    }

    container.innerHTML = `
        <div class="cp-list-header">
            <span>Producto</span>
            <span>Detalles</span>
        </div>
        ${products.map(p => `
        <div class="cp-row ${isPurchased ? 'cp-row-done' : ''}" data-id="${p.id}">
            <div class="cp-row-left">
                <label class="cp-check-wrap">
                    <input type="checkbox" class="product-checkbox"
                        data-id="${p.id}" data-name="${escapeHtml(p.name)}"
                        ${isPurchased ? 'checked' : ''}>
                    <span class="cp-box">
                        <i class="fas fa-check" style="font-size:9px;color:#fff;"></i>
                    </span>
                </label>
                <span class="cp-name">${escapeHtml(p.name)}</span>
            </div>
            <div class="cp-row-right">
                <span class="cp-pill">Stock: <strong>${p.stock}</strong></span>
                <span class="cp-pill">Mín: <strong>${p.minimumStock}</strong></span>
                <span class="cp-pill cp-pill-red">-${p.deficit} uds</span>
            </div>
        </div>`).join('')}`;

    container.querySelectorAll('.product-checkbox').forEach(cb =>
        cb.addEventListener('change', handleCheckboxChange)
    );
}

// ── Checkbox ──────────────────────────────────────────────────────────────────
async function handleCheckboxChange(e) {
    const cb        = e.target;
    const id        = parseInt(cb.getAttribute('data-id'));
    const name      = cb.getAttribute('data-name');
    const newStatus = cb.checked ? 'purchased' : 'pending';

    // Si está desmarcando → pedir confirmación
    if (!cb.checked) {
        cb.checked = true;
        const ok = await showConfirmModal(name);
        if (!ok) return;
        cb.checked = false;
    }

    cb.disabled = true;
    try {
        const res    = await fetch(PENDING_MARK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ productId: id, status: newStatus })
        });
        const result = await res.json();

        if (result.success) {
            const p = allProducts.find(x => x.id === id);
            if (p) p.status = newStatus;

            // Solo re-renderiza, NO cambia de tab
            renderProducts();
        } else {
            alert('Error: ' + result.error);
            cb.checked = !cb.checked;
        }
    } catch {
        alert('Error de conexión');
        cb.checked = !cb.checked;
    } finally {
        cb.disabled = false;
    }
}

// ── Load ──────────────────────────────────────────────────────────────────────
async function loadPendingPurchases() {
    try {
        const res  = await fetch(PENDING_API_URL);
        const data = await res.json();
        if (data.error) {
            document.getElementById('container-pending').innerHTML =
                `<div class="alert alert-danger m-3">Error: ${data.error}</div>`;
            return;
        }
        allProducts = data;
        renderProducts();
    } catch {
        document.getElementById('container-pending').innerHTML =
            `<div class="alert alert-danger m-3">Error al cargar los datos</div>`;
    }
}

function escapeHtml(t) {
    if (!t) return '';
    const d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
}

document.addEventListener('DOMContentLoaded', loadPendingPurchases);