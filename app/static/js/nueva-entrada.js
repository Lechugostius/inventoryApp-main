console.log("Nueva entrada JS cargado!");

let itemCounter = 0;
const selectedFiles = new Set();

document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("newEntryForm");
  const dropArea = document.getElementById("dropArea");
  const fileInput = document.getElementById("fileInput");
  const previewContainer = document.getElementById("previewContainer");
  const saveDraftButton = document.getElementById("saveDraft");

  // Establecer fecha actual
  document.getElementById('invoiceDate').value = new Date().toISOString().split('T')[0];

  // Agregar un producto inicial
  addNewItem();

  // Configurar manejo de moneda
  setupCurrencyHandlers();

  // Función para mostrar vista previa de imágenes
  function handleFiles(files) {
    Array.from(files).forEach((file) => {
      if (selectedFiles.has(file.name)) return;
      
      selectedFiles.add(file.name);
      
      const reader = new FileReader();
      reader.onload = function (e) {
        const previewItem = document.createElement("div");
        previewItem.className = "position-relative";
        previewItem.style.width = "100px";
        previewItem.style.height = "100px";
        
        if (file.type.startsWith('image/')) {
          previewItem.innerHTML = `
            <img src="${e.target.result}" class="img-thumbnail" style="width: 100px; height: 100px; object-fit: cover;">
            <button type="button" class="btn btn-danger btn-sm position-absolute top-0 end-0" onclick="removeFile(this, '${file.name}')">
              <i class="fas fa-times"></i>
            </button>
          `;
        } else {
          previewItem.innerHTML = `
            <div class="border border-secondary rounded d-flex align-items-center justify-content-center" style="width: 100px; height: 100px;">
              <i class="fas fa-file fa-2x text-secondary"></i>
            </div>
            <button type="button" class="btn btn-danger btn-sm position-absolute top-0 end-0" onclick="removeFile(this, '${file.name}')">
              <i class="fas fa-times"></i>
            </button>
            <small class="text-truncate d-block">${file.name}</small>
          `;
        }
        
        previewContainer.appendChild(previewItem);
      };
      reader.readAsDataURL(file);
    });
  }

  // Event listeners para drag & drop
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ["dragenter", "dragover"].forEach((eventName) => {
    dropArea.addEventListener(eventName, () => dropArea.classList.add('bg-light'), false);
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, () => dropArea.classList.remove('bg-light'), false);
  });

  dropArea.addEventListener("drop", function (e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
  });

  // Manejar selección de archivos mediante el botón
  fileInput.addEventListener("change", function (e) {
    handleFiles(this.files);
  });

  // Guardar borrador
  saveDraftButton.addEventListener("click", function () {
    saveDraft();
  });

  // Cargar borrador si existe
  loadDraftIfExists();

  // Manejar envío del formulario
  form.addEventListener("submit", submitEntry);
});

function setupCurrencyHandlers() {
  const invoiceCurrencySelect = document.getElementById('invoiceCurrency');
  if (invoiceCurrencySelect) {
    invoiceCurrencySelect.addEventListener('change', function() {
      updateAllItemsCurrency();
      updateCostSummary();
    });
  }
}

function updateAllItemsCurrency() {
  const invoiceCurrency = document.getElementById('invoiceCurrency').value;
  const currencySymbol = invoiceCurrency === 'USD' ? '$' : '₡';
  
  // Actualizar todos los campos de costo existentes
  const itemCards = document.querySelectorAll('.item-card');
  itemCards.forEach(card => {
    const cardId = card.id.split('-')[1];
    const costSymbol = document.getElementById(`costSymbol-${cardId}`);
    const costInput = document.getElementById(`unitCost-${cardId}`);
    
    if (costSymbol) costSymbol.textContent = currencySymbol;
    
    if (costInput) {
      if (invoiceCurrency === 'USD') {
        costInput.step = '0.01';
        costInput.placeholder = '0.00';
      } else {
        costInput.step = '1';
        costInput.placeholder = '0';
      }
    }
  });
}

function addNewItem() {
  itemCounter++;
  const itemsContainer = document.getElementById('itemsContainer');
  const emptyState = document.getElementById('emptyState');
  const invoiceCurrency = document.getElementById('invoiceCurrency').value || 'USD';
  const currencySymbol = invoiceCurrency === 'USD' ? '$' : '₡';
  const step = invoiceCurrency === 'USD' ? '0.01' : '1';
  const placeholder = invoiceCurrency === 'USD' ? '0.00' : '0';
  
  emptyState.style.display = 'none';

  const itemCard = document.createElement('div');
  itemCard.className = 'item-card position-relative';
  itemCard.id = `item-${itemCounter}`;
  
  itemCard.innerHTML = `
    <button type="button" class="btn btn-outline-danger btn-sm remove-item-btn" onclick="removeItem(${itemCounter})" ${itemCounter === 1 ? 'style="display: none;"' : ''}>
      <i class="fas fa-times"></i>
    </button>
    
    <div class="row mb-3">
      <div class="col-12">
        <h6 class="text-primary">
          <i class="fas fa-box me-2"></i>Producto #${itemCounter}
        </h6>
      </div>
    </div>
    
    <div class="row mb-3">
      <div class="col-md-4">
        <label class="form-label">Nombre del Producto</label>
        <input type="text" class="form-control" id="itemName-${itemCounter}" 
               placeholder="Ej: Laptop Dell XPS 13" required onchange="updateItemCard(${itemCounter})">
      </div>
      <div class="col-md-2">
        <label class="form-label">Categoría</label>
        <select class="form-select" id="categoryId-${itemCounter}" required onchange="updateItemCard(${itemCounter})">
          <option value="">Selecciona</option>
          ${categories.map(cat => `<option value="${cat.id}">${cat.name}</option>`).join('')}
        </select>
      </div>
      <div class="col-md-2">
        <label class="form-label">Estado</label>
        <select class="form-select" id="statusId-${itemCounter}" required onchange="updateItemCard(${itemCounter})">
          <option value="">Selecciona</option>
          ${statuses.map(status => `<option value="${status.id}">${status.name}</option>`).join('')}
        </select>
      </div>
      <div class="col-md-2">
        <label class="form-label">Cantidad</label>
        <input type="number" class="form-control" id="quantity-${itemCounter}" 
               min="1" value="1" required onchange="updateSerialInputs(${itemCounter})">
      </div>
      <div class="col-md-2">
        <label class="form-label">Costo Unitario</label>
        <div class="input-group">
          <span class="input-group-text" id="costSymbol-${itemCounter}">${currencySymbol}</span>
          <input type="number" class="form-control" id="unitCost-${itemCounter}" 
                 step="${step}" min="0" placeholder="${placeholder}" required onchange="updateCostSummary()">
        </div>
      </div>
    </div>
    
    <div class="row mb-3">
      <div class="col-md-12">
        <label class="form-label">Modelo/Descripción</label>
        <input type="text" class="form-control" id="description-${itemCounter}" 
               placeholder="Ej: XPS 13 9310, Intel i7, 16GB RAM">
      </div>
    </div>
    
    <div class="row">
      <div class="col-12">
        <label class="form-label d-flex justify-content-between align-items-center">
          <span>Números de Serie</span>
          <span class="serial-counter bg-warning" id="serialCounter-${itemCounter}">0 / 0</span>
        </label>
        <div id="serialContainer-${itemCounter}">
          <!-- Los inputs de serie se generarán aquí -->
        </div>
      </div>
    </div>
  `;
  
  itemsContainer.appendChild(itemCard);
  updateSerialInputs(itemCounter);
  updateCostSummary();
  renumberProducts();
}

function renumberProducts() {
  // Renumera el texto "Producto #N" en todas las tarjetas existentes
  // según su posición actual, sin tocar los IDs internos.
  const cards = document.querySelectorAll('.item-card');
  cards.forEach((card, index) => {
    const title = card.querySelector('h6.text-primary');
    if (title) {
      title.innerHTML = `<i class="fas fa-box me-2"></i>Producto #${index + 1}`;
    }
  });
}

function removeItem(itemId) {
  const itemCard = document.getElementById(`item-${itemId}`);
  itemCard.remove();
  renumberProducts();
  
  const remainingItems = document.querySelectorAll('.item-card').length;
  if (remainingItems === 0) {
    document.getElementById('emptyState').style.display = 'block';
    document.getElementById('costSummary').style.display = 'none';
  }
  
  updateCostSummary();
}

function updateItemCard(itemId) {
  const itemCard = document.getElementById(`item-${itemId}`);
  const itemName = document.getElementById(`itemName-${itemId}`).value;
  const categoryId = document.getElementById(`categoryId-${itemId}`).value;
  const statusId = document.getElementById(`statusId-${itemId}`).value;
  
  if (itemName && categoryId && statusId) {
    itemCard.classList.add('filled');
  } else {
    itemCard.classList.remove('filled');
  }
  
  updateCostSummary();
}

function updateSerialInputs(itemId) {
  const quantity = parseInt(document.getElementById(`quantity-${itemId}`).value) || 1;
  const serialContainer = document.getElementById(`serialContainer-${itemId}`);
  
  serialContainer.innerHTML = '';
  
  for (let i = 1; i <= quantity; i++) {
    const serialGroup = document.createElement('div');
    serialGroup.className = 'serial-input-group';
    
    serialGroup.innerHTML = `
      <div class="input-group input-group-sm">
        <span class="input-group-text">Unidad ${i}</span>
        <input type="text" class="form-control serial-input" 
               id="serial-${itemId}-${i}" 
               placeholder="Número de serie único"
               onchange="updateSerialCounter(${itemId})"
               maxlength="50" required>
        <button class="btn btn-outline-secondary" type="button" onclick="generateSerial(${itemId}, ${i})">
          <i class="fas fa-random"></i>
        </button>
      </div>
    `;
    
    serialContainer.appendChild(serialGroup);
  }
  
  updateSerialCounter(itemId);
  updateCostSummary();
}

function updateSerialCounter(itemId) {
  const serialInputs = document.querySelectorAll(`#serialContainer-${itemId} .serial-input`);
  const filled = Array.from(serialInputs).filter(input => input.value.trim() !== '').length;
  const total = serialInputs.length;
  
  const counter = document.getElementById(`serialCounter-${itemId}`);
  counter.textContent = `${filled} / ${total}`;
  counter.className = `serial-counter ${filled === total ? 'bg-success' : 'bg-warning'}`;
  
  updateCostSummary();
}

function generateSerial(itemId, unitNumber) {
  const serialInput = document.getElementById(`serial-${itemId}-${unitNumber}`);
  const timestamp = Date.now().toString().slice(-6);
  const random = Math.random().toString(36).substr(2, 4).toUpperCase();
  serialInput.value = `SN${timestamp}${random}`;
  updateSerialCounter(itemId);
}

function formatCurrency(amount, currency) {
  if (currency === 'USD') {
    return `$${parseFloat(amount).toFixed(2)}`;
  } else if (currency === 'CRC') {
    return `₡${parseInt(amount).toLocaleString()}`;
  }
  return `${currency} ${amount}`;
}

function updateCostSummary() {
  const itemCards = document.querySelectorAll('.item-card');
  const costSummary = document.getElementById('costSummary');
  const invoiceCurrency = document.getElementById('invoiceCurrency').value || 'USD';
  
  if (itemCards.length === 0) {
    costSummary.style.display = 'none';
    return;
  }
  
  costSummary.style.display = 'block';
  
  let totalProducts = itemCards.length;
  let totalUnits = 0;
  let totalCost = 0;
  let totalSeries = 0;
  let filledSeries = 0;
  
  itemCards.forEach(card => {
    const cardId = card.id.split('-')[1];
    const quantity = parseInt(document.getElementById(`quantity-${cardId}`)?.value) || 0;
    const unitCost = parseFloat(document.getElementById(`unitCost-${cardId}`)?.value) || 0;
    const serialInputs = card.querySelectorAll('.serial-input');
    const filledSerials = Array.from(serialInputs).filter(input => input.value.trim() !== '').length;
    
    totalUnits += quantity;
    totalCost += quantity * unitCost;
    totalSeries += serialInputs.length;
    filledSeries += filledSerials;
  });
  
  const completionPercentage = totalSeries > 0 ? Math.round((filledSeries / totalSeries) * 100) : 0;
  
  document.getElementById('totalProducts').textContent = totalProducts;
  document.getElementById('totalUnits').textContent = totalUnits;
  document.getElementById('totalCost').textContent = formatCurrency(totalCost, invoiceCurrency);
  document.getElementById('completionPercentage').textContent = `${completionPercentage}%`;
}

function previewSummary() {
  const previewContent = document.getElementById('previewContent');
  const invoiceNumber = document.getElementById('invoiceNumber').value;
  const invoiceDate = document.getElementById('invoiceDate').value;
  const supplierId = document.getElementById('supplierId').value;
  const supplierName = suppliers.find(s => s.id == supplierId)?.name || 'No seleccionado';
  const warehouseLocation = document.getElementById('warehouseLocation').value;
  const invoiceCurrency = document.getElementById('invoiceCurrency').value || 'USD';
  
  let html = `
    <div class="row mb-4">
      <div class="col-md-6">
        <h6><i class="fas fa-receipt me-2"></i>Información de la Factura</h6>
        <p><strong>Número:</strong> ${invoiceNumber || 'No especificado'}</p>
        <p><strong>Fecha:</strong> ${invoiceDate || 'No especificada'}</p>
        <p><strong>Proveedor:</strong> ${supplierName}</p>
        <p><strong>Ubicación:</strong> ${warehouseLocation || 'No especificada'}</p>
        <p><strong>Moneda:</strong> ${invoiceCurrency === 'USD' ? 'Dólares (USD)' : 'Colones (CRC)'}</p>
      </div>
      <div class="col-md-6">
        <h6><i class="fas fa-calculator me-2"></i>Resumen de Costos</h6>
        <p><strong>Total Productos:</strong> ${document.getElementById('totalProducts').textContent}</p>
        <p><strong>Total Unidades:</strong> ${document.getElementById('totalUnits').textContent}</p>
        <p><strong>Costo Total:</strong> ${document.getElementById('totalCost').textContent}</p>
      </div>
    </div>
    <hr>
    <h6><i class="fas fa-boxes me-2"></i>Productos a Registrar</h6>
    <div class="table-responsive">
      <table class="table table-sm">
        <thead>
          <tr>
            <th>Producto</th>
            <th>Cantidad</th>
            <th>Costo Unit.</th>
            <th>Costo Total</th>
            <th>Series Completas</th>
          </tr>
        </thead>
        <tbody>
  `;
  
  const itemCards = document.querySelectorAll('.item-card');
  itemCards.forEach(card => {
    const cardId = card.id.split('-')[1];
    const itemName = document.getElementById(`itemName-${cardId}`)?.value || 'Sin nombre';
    const quantity = parseInt(document.getElementById(`quantity-${cardId}`)?.value) || 0;
    const unitCost = parseFloat(document.getElementById(`unitCost-${cardId}`)?.value) || 0;
    const totalCost = quantity * unitCost;
    
    const serialInputs = card.querySelectorAll('.serial-input');
    const filledSerials = Array.from(serialInputs).filter(input => input.value.trim() !== '').length;
    const isComplete = filledSerials === quantity;
    
    html += `
      <tr class="${isComplete ? 'table-success' : 'table-warning'}">
        <td>${itemName}</td>
        <td>${quantity}</td>
        <td>${formatCurrency(unitCost, invoiceCurrency)}</td>
        <td>${formatCurrency(totalCost, invoiceCurrency)}</td>
        <td>
          <span class="badge ${isComplete ? 'bg-success' : 'bg-warning'}">
            ${filledSerials}/${quantity}
          </span>
        </td>
      </tr>
    `;
  });
  
  html += `
        </tbody>
      </table>
    </div>
  `;
  
  previewContent.innerHTML = html;
  new bootstrap.Modal(document.getElementById('previewModal')).show();
}

function clearAll() {
  if (confirm('¿Estás seguro de que deseas limpiar todos los productos?')) {
    document.getElementById('itemsContainer').innerHTML = '';
    document.getElementById('emptyState').style.display = 'block';
    document.getElementById('costSummary').style.display = 'none';
    document.getElementById('previewContainer').innerHTML = '';
    selectedFiles.clear();
    itemCounter = 0;
    
    // Limpiar campos de factura
    document.getElementById('invoiceNumber').value = '';
    document.getElementById('invoiceDate').value = new Date().toISOString().split('T')[0];
    document.getElementById('supplierId').value = '';
    document.getElementById('warehouseLocation').value = '';
    document.getElementById('invoiceCurrency').value = 'USD';
    
    // Agregar un producto inicial
    addNewItem();
  }
}

function removeFile(button, fileName) {
  selectedFiles.delete(fileName);
  button.parentElement.remove();
}

function viewInventory() {
  window.parent.location.href = '/inventario';
}

async function submitEntry(e) {
  if (e) e.preventDefault();
  
  const itemCards = document.querySelectorAll('.item-card');
  
  if (itemCards.length === 0) {
    alert('Debes agregar al menos un producto');
    return;
  }
  
  // Validar campos básicos
  const invoiceNumber = document.getElementById('invoiceNumber').value;
  const invoiceDate = document.getElementById('invoiceDate').value;
  const supplierId = document.getElementById('supplierId').value;
  const warehouseLocation = document.getElementById('warehouseLocation').value;
  const invoiceCurrency = document.getElementById('invoiceCurrency').value;
  
  if (!supplierId || !warehouseLocation) {
    alert('Por favor completa la información del proveedor y ubicación');
    return;
  }
  
  // Validar productos y recopilar datos
  let isValid = true;
  const entries = [];
  const allSerials = [];
  
  itemCards.forEach(card => {
    const cardId = card.id.split('-')[1];
    const itemName = document.getElementById(`itemName-${cardId}`)?.value;
    const categoryId = document.getElementById(`categoryId-${cardId}`)?.value;
    const statusId = document.getElementById(`statusId-${cardId}`)?.value;
    const quantity = parseInt(document.getElementById(`quantity-${cardId}`)?.value) || 0;
    const unitCost = parseFloat(document.getElementById(`unitCost-${cardId}`)?.value) || 0;
    const description = document.getElementById(`description-${cardId}`)?.value || '';
    
    if (!itemName || !categoryId || !statusId || !quantity || !unitCost) {
      isValid = false;
      alert(`Por favor completa todos los campos del Producto #${cardId}, incluyendo el costo unitario`);
      return;
    }
    
    const serialInputs = card.querySelectorAll('.serial-input');
    const serials = Array.from(serialInputs).map(input => input.value.trim()).filter(serial => serial !== '');
    
    if (serials.length !== quantity) {
      isValid = false;
      alert(`El Producto #${cardId} debe tener ${quantity} números de serie completos`);
      return;
    }
    
    // Verificar duplicados
    serials.forEach(serial => {
      if (allSerials.includes(serial)) {
        isValid = false;
        alert(`El número de serie "${serial}" está duplicado`);
        return;
      }
      allSerials.push(serial);
    });
    
    // Agregar cada unidad como entrada individual
    serials.forEach(serial => {
      entries.push({
        itemName,
        categoryId,
        statusId,
        serial,
        unitCost,
        currency: invoiceCurrency,
        description,
        supplierId,
        location: warehouseLocation,
        invoiceNumber: invoiceNumber || '',
        invoiceDate: invoiceDate || ''
      });
    });
  });
  
  if (!isValid) {
    return;
  }
  
  // Calcular costo total
  const totalCost = entries.reduce((sum, entry) => sum + entry.unitCost, 0);
  
  // Mostrar confirmación
  const confirmMessage = `¿Confirmas el registro de ${entries.length} unidades de ${itemCards.length} productos diferentes?\n\nCosto Total: ${formatCurrency(totalCost, invoiceCurrency)}`;
  
  if (!confirm(confirmMessage)) {
    return;
  }
  
  // Deshabilitar botón y mostrar loading
  const submitBtn = document.querySelector('button[type="submit"]');
  const originalText = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';
  
  try {
    // Si solo hay un producto, usar la ruta original
    if (entries.length === 1) {
      const formData = new FormData();
      const entry = entries[0];
      
      formData.append('device_name', entry.itemName);
      formData.append('device_id', entry.serial);
      formData.append('category_id', entry.categoryId);
      formData.append('status_id', entry.statusId);
      formData.append('supplier_id', entry.supplierId);
      formData.append('location', entry.location);
      formData.append('quantity', '1');
      formData.append('unit_cost', entry.unitCost);
      formData.append('currency', entry.currency);
      formData.append('model', entry.description);
      formData.append('invoice_number', entry.invoiceNumber);
      formData.append('notes', document.querySelector('textarea[name="general_notes"]')?.value || '');
      
      // Agregar archivos
      const fileInput = document.getElementById('fileInput');
      Array.from(fileInput.files).forEach(file => {
        formData.append('files', file);
      });
      
      const response = await fetch('/nueva-entrada', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (response.ok) {
        showSuccessResult(result);
        localStorage.removeItem('entryDraft');
      } else {
        throw new Error(result.error || 'Error al registrar la entrada');
      }
    } else {
      // Múltiples productos
      const response = await fetch('/nueva-entrada-multiple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          invoiceNumber: invoiceNumber || '',
          invoiceDate: invoiceDate || '',
          supplierId,
          warehouseLocation,
          invoiceCurrency,
          entries
        })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        showMultipleResults(result);
        localStorage.removeItem('entryDraft');
      } else {
        throw new Error(result.error || 'Error al procesar la entrada');
      }
    }
    
  } catch (error) {
    console.error('Error:', error);
    alert('Error al procesar la entrada: ' + error.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;
  }
}

function showSuccessResult(result) {
  const modalHeader = document.getElementById('resultsModalHeader');
  const modalTitle = document.getElementById('resultsModalTitle');
  const modalBody = document.getElementById('resultsModalBody');
  const viewBtn = document.getElementById('viewInventoryBtn');
  
  modalHeader.className = 'modal-header bg-success text-white';
  modalTitle.innerHTML = '<i class="fas fa-check-circle me-2"></i>Entrada Registrada Exitosamente';
  
  const currency = result.currency || 'USD';
  
  modalBody.innerHTML = `
    <div class="text-center mb-4">
      <i class="fas fa-check-circle fa-4x text-success mb-3"></i>
      <h4>¡Producto registrado correctamente!</h4>
      <p class="text-muted">El producto ha sido agregado al inventario</p>
    </div>
    <div class="row text-center">
      <div class="col-md-4">
        <h5 class="text-success">#${result.item_id}</h5>
        <small class="text-muted">ID del Item</small>
      </div>
      <div class="col-md-4">
        <h5 class="text-primary">${formatCurrency(result.unit_cost || 0, currency)}</h5>
        <small class="text-muted">Costo Unitario</small>
      </div>
      <div class="col-md-4">
        <h5 class="text-info">${formatCurrency(result.total_cost || 0, currency)}</h5>
        <small class="text-muted">Costo Total</small>
      </div>
    </div>
  `;
  
  viewBtn.style.display = 'block';
  new bootstrap.Modal(document.getElementById('resultsModal')).show();
}

function showMultipleResults(result) {
  const modalHeader = document.getElementById('resultsModalHeader');
  const modalTitle = document.getElementById('resultsModalTitle');
  const modalBody = document.getElementById('resultsModalBody');
  const viewBtn = document.getElementById('viewInventoryBtn');
  
  modalHeader.className = `modal-header bg-${result.failed_count === 0 ? 'success' : 'warning'} text-white`;
  modalTitle.innerHTML = `<i class="fas fa-${result.failed_count === 0 ? 'check-circle' : 'exclamation-triangle'} me-2"></i>Resultado del Procesamiento`;
  
  const currency = result.currency || 'USD';
  
  let html = `
    <div class="row text-center mb-4">
      <div class="col-md-3">
        <h3 class="text-success">${result.successful_count}</h3>
        <small class="text-muted">Exitosas</small>
      </div>
      <div class="col-md-3">
        <h3 class="text-danger">${result.failed_count}</h3>
        <small class="text-muted">Fallidas</small>
      </div>
      <div class="col-md-3">
        <h3 class="text-info">${result.successful_count + result.failed_count}</h3>
        <small class="text-muted">Total Procesadas</small>
      </div>
      <div class="col-md-3">
        <h3 class="text-primary">${formatCurrency(result.total_cost || 0, currency)}</h3>
        <small class="text-muted">Costo Total</small>
      </div>
    </div>
  `;
  
  if (result.successful_entries && result.successful_entries.length > 0) {
    html += `
      <h6 class="text-success">✅ Entradas Exitosas:</h6>
      <div class="table-responsive mb-3">
        <table class="table table-sm">
          <thead>
            <tr>
              <th>ID</th>
              <th>Producto</th>
              <th>Serie</th>
              <th>Costo</th>
            </tr>
          </thead>
          <tbody>
            ${result.successful_entries.map(entry => `
              <tr>
                <td>#${entry.item_id}</td>
                <td>${entry.name}</td>
                <td><code>${entry.serial}</code></td>
                <td>${formatCurrency(entry.cost || 0, currency)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  }
  
  if (result.failed_entries && result.failed_entries.length > 0) {
    html += `
      <h6 class="text-danger">❌ Entradas Fallidas:</h6>
      <div class="table-responsive">
        <table class="table table-sm">
          <thead>
            <tr>
              <th>Serie</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            ${result.failed_entries.map(entry => `
              <tr>
                <td><code>${entry.serial}</code></td>
                <td class="text-danger">${entry.error}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  }
  
  modalBody.innerHTML = html;
  viewBtn.style.display = result.successful_count > 0 ? 'block' : 'none';
  new bootstrap.Modal(document.getElementById('resultsModal')).show();
}

function saveDraft() {
  try {
    const draftData = {
      invoiceNumber: document.getElementById('invoiceNumber').value,
      invoiceDate: document.getElementById('invoiceDate').value,
      supplierId: document.getElementById('supplierId').value,
      warehouseLocation: document.getElementById('warehouseLocation').value,
      invoiceCurrency: document.getElementById('invoiceCurrency').value,
      items: []
    };
    
    const itemCards = document.querySelectorAll('.item-card');
    itemCards.forEach(card => {
      const cardId = card.id.split('-')[1];
      const itemData = {
        itemName: document.getElementById(`itemName-${cardId}`)?.value || '',
        categoryId: document.getElementById(`categoryId-${cardId}`)?.value || '',
        statusId: document.getElementById(`statusId-${cardId}`)?.value || '',
        quantity: document.getElementById(`quantity-${cardId}`)?.value || '',
        unitCost: document.getElementById(`unitCost-${cardId}`)?.value || '',
        description: document.getElementById(`description-${cardId}`)?.value || '',
        serials: []
      };
      
      const serialInputs = card.querySelectorAll('.serial-input');
      serialInputs.forEach(input => {
        if (input.value.trim()) {
          itemData.serials.push(input.value.trim());
        }
      });
      
      draftData.items.push(itemData);
    });
    
    localStorage.setItem('entryDraft', JSON.stringify(draftData));
    alert('¡Borrador guardado correctamente!');
  } catch (error) {
    console.error('Error al guardar borrador:', error);
    alert('Error al guardar el borrador');
  }
}

function loadDraftIfExists() {
  setTimeout(() => {
    const savedDraft = localStorage.getItem('entryDraft');
    if (savedDraft) {
      try {
        const draftData = JSON.parse(savedDraft);
        
        if (confirm('Se encontró un borrador guardado. ¿Deseas cargarlo?')) {
          // Cargar datos básicos
          document.getElementById('invoiceNumber').value = draftData.invoiceNumber || '';
          document.getElementById('invoiceDate').value = draftData.invoiceDate || '';
          document.getElementById('supplierId').value = draftData.supplierId || '';
          document.getElementById('warehouseLocation').value = draftData.warehouseLocation || '';
          document.getElementById('invoiceCurrency').value = draftData.invoiceCurrency || 'USD';
          
          // Limpiar items existentes
          document.getElementById('itemsContainer').innerHTML = '';
          itemCounter = 0;
          
          // Cargar items guardados
          if (draftData.items && draftData.items.length > 0) {
            draftData.items.forEach(itemData => {
              addNewItem();
              const currentId = itemCounter;
              
              document.getElementById(`itemName-${currentId}`).value = itemData.itemName || '';
              document.getElementById(`categoryId-${currentId}`).value = itemData.categoryId || '';
              document.getElementById(`statusId-${currentId}`).value = itemData.statusId || '';
              document.getElementById(`quantity-${currentId}`).value = itemData.quantity || '';
              document.getElementById(`unitCost-${currentId}`).value = itemData.unitCost || '';
              document.getElementById(`description-${currentId}`).value = itemData.description || '';
              
              // Actualizar series después de cambiar cantidad
              updateSerialInputs(currentId);
              
              // Cargar números de serie
              if (itemData.serials) {
                itemData.serials.forEach((serial, index) => {
                  const serialInput = document.getElementById(`serial-${currentId}-${index + 1}`);
                  if (serialInput) {
                    serialInput.value = serial;
                  }
                });
              }
              
              updateItemCard(currentId);
              updateSerialCounter(currentId);
            });
          } else {
            addNewItem();
          }
          
          // Actualizar la moneda de todos los items
          updateAllItemsCurrency();
          updateCostSummary();
          console.log('Borrador cargado exitosamente');
        } else {
          localStorage.removeItem('entryDraft');
        }
      } catch (error) {
        console.error('Error al cargar el borrador:', error);
        localStorage.removeItem('entryDraft');
      }
    }
  }, 500);
}