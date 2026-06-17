// ── informes.js ───────────────────────────────────────────────────────────

let movementsChart = null;
let categoriesChart = null;
let currentGranularidad = 'mes';
let currentYear = null;
let currentPeriod = null;
let currentMode = 'monitor';
let compareYear = null;
let comparePeriod = null;
let chartType = 'line';

const MONTHS = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
const MONTHS_SHORT = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
const CHART_COLORS = {
    entradas:    '#6A0B93',
    salidas:     '#dc3545',
    entradasCmp: '#1D9E75',
    salidasCmp:  '#EF9F27'
};

// ── Gráfico circular ──────────────────────────────────────────────────────

async function cargarCategorias() {
    try {
        const res = await fetch('/api/categorias-data');
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        const ctx = document.getElementById('categoriesChart').getContext('2d');
        if (categoriesChart) categoriesChart.destroy();
        categoriesChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: ['#6A0B93','#FFA500','#28a745','#17a2b8','#ffc107','#dc3545'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: { font: { size: 12 }, padding: 16 }
                    },
                    tooltip: {
                        callbacks: {
                            label: c => ` ${c.label}: ${c.raw} items`
                        }
                    }
                }
            }
        });
    } catch (error) { console.error('Error categorias:', error); }
}

// ── Fetch movimientos ─────────────────────────────────────────────────────

async function obtenerDatos(granularidad, fecha = '') {
    let url = `/api/movimientos?granularidad=${granularidad}`;
    if (fecha) url += `&fecha=${fecha}`;
    const res = await fetch(url);
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    return data;
}

// ── Semanas de un mes ─────────────────────────────────────────────────────

function getWeeksOfMonth(year, month) {
    const last = new Date(year, month + 1, 0).getDate();
    const weeks = [];
    let start = 1;
    while (start <= last) {
        const end = Math.min(start + 6, last);
        weeks.push({
            label: `${start} ${MONTHS_SHORT[month]} – ${end} ${MONTHS_SHORT[month]}`,
            fecha: `${year}-${String(month + 1).padStart(2,'0')}`
        });
        start = end + 1;
    }
    return weeks;
}

// ── Leyenda ───────────────────────────────────────────────────────────────

function buildLegend(datasets) {
    const colorArr = Object.values(CHART_COLORS);
    const box = document.getElementById('chartLegend');
    if (!box) return;
    box.innerHTML = datasets.map((d, i) =>
        `<span class="legend-item">
            <span class="legend-dot" style="background:${colorArr[i]}"></span>
            ${d.label}
        </span>`
    ).join('');
}

// ── Label de período ──────────────────────────────────────────────────────

function getPeriodLabel(year, period) {
    return MONTHS_SHORT[period - 1] + ' ' + year;
}

// ── Render gráfico ────────────────────────────────────────────────────────

async function cargarMovimientos() {
    try {
        let fecha = '';
        if (currentYear && currentPeriod) {
            fecha = `${currentYear}-${String(currentPeriod).padStart(2,'0')}`;
        }

        const dataActual = await obtenerDatos(currentGranularidad, fecha);
        const p1 = currentPeriod ? getPeriodLabel(currentYear, currentPeriod) : String(currentYear);

        // FIX 2: spanGaps true y pointRadius mayor para que las líneas aparezcan
        // aunque haya pocos puntos
        const mkDs = (label, data, color, dash) => ({
            label,
            data,
            borderColor: color,
            backgroundColor: chartType === 'line' ? color + '20' : color + 'bb',
            fill: chartType === 'line',
            tension: 0.4,
            pointRadius: chartType === 'line' ? 5 : 0,
            pointHoverRadius: 7,
            borderWidth: 2,
            spanGaps: true,
            borderDash: dash || []
        });

        let datasets = [
            mkDs('Entradas · ' + p1, dataActual.entradas, CHART_COLORS.entradas),
            mkDs('Salidas · '  + p1, dataActual.salidas,  CHART_COLORS.salidas)
        ];

        if (currentMode === 'compare' && compareYear && comparePeriod) {
            const fechaCmp = `${compareYear}-${String(comparePeriod).padStart(2,'0')}`;
            const dataCmp = await obtenerDatos(currentGranularidad, fechaCmp);
            const p2 = getPeriodLabel(compareYear, comparePeriod);
            datasets.push(
                mkDs('Entradas · ' + p2, dataCmp.entradas, CHART_COLORS.entradasCmp, [5,3]),
                mkDs('Salidas · '  + p2, dataCmp.salidas,  CHART_COLORS.salidasCmp,  [5,3])
            );
        }

        buildLegend(datasets);

        if (movementsChart) movementsChart.destroy();
        const ctx = document.getElementById('movementsChart').getContext('2d');
        movementsChart = new Chart(ctx, {
            type: chartType === 'bar' ? 'bar' : 'line',
            data: { labels: dataActual.labels, datasets },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { callbacks: { label: c => c.dataset.label + ': ' + c.raw + ' uds' } }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1 },
                        title: { display: true, text: 'Cantidad', color: '#888' }
                    },
                    x: { ticks: { autoSkip: false, maxRotation: 45, font: { size: 10 } } }
                }
            }
        });

        const gran_map = { mes: 'Mensual', semana: 'Semanal', dia: 'Diario' };
        const titleEl = document.getElementById('chartTitle');
        if (titleEl) titleEl.innerText = (gran_map[currentGranularidad] || '') + (currentPeriod ? ' — ' + MONTHS[currentPeriod - 1] + ' ' + currentYear : ' — ' + currentYear);

    } catch (error) { console.error('Error cargarMovimientos:', error); }
}

// ── Chips de meses ────────────────────────────────────────────────────────

function buildChip(text, period, containerId, onClick) {
    const c = document.createElement('div');
    c.className = 'chip';
    c.dataset.period = period;
    c.textContent = text;
    c.onclick = () => {
        document.querySelectorAll(`#${containerId} .chip`).forEach(el => el.classList.remove('active'));
        c.classList.add('active');
        onClick(period);
    };
    return c;
}

function generarChipsMeses(year, containerId, onSelect) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';
    MONTHS_SHORT.forEach((m, i) => {
        container.appendChild(buildChip(m + ' ' + year, i + 1, containerId, onSelect));
    });
}

function buildWeekChips(year, monthIndex) {
    const wrap = document.getElementById('weekChipsWrap');
    const box  = document.getElementById('weekChips');
    if (!wrap || !box) return;
    box.innerHTML = '';
    const weeks = getWeeksOfMonth(year, monthIndex);
    weeks.forEach((w, i) => {
        const c = document.createElement('div');
        c.className = 'chip' + (i === 0 ? ' active' : '');
        c.textContent = w.label;
        c.onclick = () => {
            box.querySelectorAll('.chip').forEach(el => el.classList.remove('active'));
            c.classList.add('active');
            cargarMovimientos();
        };
        box.appendChild(c);
    });
    wrap.style.display = 'block';
}

// ── Años ──────────────────────────────────────────────────────────────────

async function cargarAnios() {
    try {
        const data = await obtenerDatos('mes');

        // Años de la BD
        let yearsFromDB = [...new Set(data.labels.map(l => {
            const m = l.match(/\d{4}/);
            return m ? parseInt(m[0]) : null;
        }).filter(Boolean))];

        // FIX 1: Siempre incluir al menos el año actual y el anterior
        const currentYearNow = new Date().getFullYear();
        const fallbackYears = [currentYearNow, currentYearNow - 1];
        let years = [...new Set([...yearsFromDB, ...fallbackYears])].sort((a, b) => b - a);

        const yearSel    = document.getElementById('yearSel');
        const cmpYearSel = document.getElementById('cmpYearSel');
        yearSel.innerHTML    = years.map(y => `<option value="${y}">${y}</option>`).join('');
        cmpYearSel.innerHTML = years.map(y => `<option value="${y}">${y}</option>`).join('');

        currentYear  = years[0];
        // FIX 1: compareYear siempre es un año diferente al principal
        compareYear  = years.find(y => y !== currentYear) || years[0];
        yearSel.value    = currentYear;
        cmpYearSel.value = compareYear;

        // Chips principales
        generarChipsMeses(currentYear, 'periodChips', (p) => {
            currentPeriod = parseInt(p);
            if (currentGranularidad === 'semana') buildWeekChips(currentYear, currentPeriod - 1);
            cargarMovimientos();
        });

        // Chips comparativo
        generarChipsMeses(compareYear, 'cmpMonthChips', (p) => {
            comparePeriod = parseInt(p);
            if (currentMode === 'compare') cargarMovimientos();
        });

        // Eventos de año
        yearSel.onchange = () => {
            currentYear   = parseInt(yearSel.value);
            currentPeriod = null;
            document.getElementById('weekChipsWrap').style.display = 'none';
            generarChipsMeses(currentYear, 'periodChips', (p) => {
                currentPeriod = parseInt(p);
                if (currentGranularidad === 'semana') buildWeekChips(currentYear, currentPeriod - 1);
                cargarMovimientos();
            });
            cargarMovimientos();
        };
        cmpYearSel.onchange = () => {
            compareYear   = parseInt(cmpYearSel.value);
            comparePeriod = null;
            generarChipsMeses(compareYear, 'cmpMonthChips', (p) => {
                comparePeriod = parseInt(p);
                if (currentMode === 'compare') cargarMovimientos();
            });
        };

        cargarMovimientos();
    } catch (error) { console.error('Error cargarAnios:', error); }
}

// ── Granularidad ──────────────────────────────────────────────────────────

function setGranularidad(gran) {
    currentGranularidad = gran;
    currentPeriod       = null;
    document.getElementById('weekChipsWrap').style.display = 'none';
    generarChipsMeses(currentYear, 'periodChips', (p) => {
        currentPeriod = parseInt(p);
        if (gran === 'semana') buildWeekChips(currentYear, currentPeriod - 1);
        cargarMovimientos();
    });
    if (currentMode === 'compare') {
        generarChipsMeses(compareYear, 'cmpMonthChips', (p) => {
            comparePeriod = parseInt(p);
            cargarMovimientos();
        });
    }
    cargarMovimientos();
}

// ── Modo ──────────────────────────────────────────────────────────────────

function setMode(mode) {
    currentMode = mode;
    document.getElementById('compareRow').style.display = mode === 'compare' ? 'block' : 'none';
    document.getElementById('tabMonitor').classList.toggle('active', mode === 'monitor');
    document.getElementById('tabCompare').classList.toggle('active', mode === 'compare');
    if (mode === 'compare' && !comparePeriod) {
        const firstChip = document.querySelector('#cmpMonthChips .chip');
        if (firstChip) firstChip.click();
    }
    cargarMovimientos();
}

// ── Tipo de gráfico ───────────────────────────────────────────────────────

function setChartType(type) {
    chartType = type;
    document.getElementById('btnLine').classList.toggle('active', type === 'line');
    document.getElementById('btnBar').classList.toggle('active', type === 'bar');
    cargarMovimientos();
}

// ── Exportar ──────────────────────────────────────────────────────────────

async function exportarPDF() {
    try {
        const response = await fetch('/api/export/pdf');
        if (response.ok) {
            const blob = await response.blob();
            const url  = window.URL.createObjectURL(blob);
            const a    = document.createElement('a');
            a.href     = url;
            a.download = 'reporte_inventario.pdf';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else {
            const error = await response.json();
            alert('Error al exportar PDF: ' + error.error);
        }
    } catch (error) { alert('Error al exportar PDF'); }
}

async function exportarExcel() {
    try {
        const response = await fetch('/api/export/excel');
        if (response.ok) {
            const blob = await response.blob();
            const url  = window.URL.createObjectURL(blob);
            const a    = document.createElement('a');
            a.href     = url;
            a.download = 'inventario.xlsx';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } else {
            const error = await response.json();
            alert('Error al exportar Excel: ' + error.error);
        }
    } catch (error) { alert('Error al exportar Excel'); }
}

// ── Init ──────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    cargarCategorias();
    cargarAnios();

    document.getElementById('granSel').onchange  = e => setGranularidad(e.target.value);
    document.getElementById('tabMonitor').onclick = () => setMode('monitor');
    document.getElementById('tabCompare').onclick = () => setMode('compare');
    document.getElementById('btnLine').onclick    = () => setChartType('line');
    document.getElementById('btnBar').onclick     = () => setChartType('bar');

    window.exportarPDF   = exportarPDF;
    window.exportarExcel = exportarExcel;
});