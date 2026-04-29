document.addEventListener("DOMContentLoaded", function () {
  // Variables globales - MANTENER TUS VARIABLES ORIGINALES
  const searchInput = document.getElementById("searchInput");
  const searchButton = document.getElementById("searchButton");
  const searchResults = document.getElementById("searchResults");
  const selectedItemsContainer = document.getElementById("selectedProducts");
  const itemsList = document.getElementById("productsList");
  const itemCount = document.getElementById("productCount");
  const summaryContent = document.getElementById("summaryContent");
  const submitButton = document.getElementById("submitButton");
  const fileInput = document.getElementById("fileInput");
  const fileList = document.getElementById("fileList");
  const form = document.getElementById("salidaForm");
  const saveDraftButton = document.getElementById("saveDraft");
  
  // Verificar que los elementos esenciales existen
  if (!searchInput || !form) {
    console.error('Elementos esenciales no encontrados en el DOM');
    return;
  }
  
  let selectedItems = [];
  let selectedFiles = new Set();
  let searchTimeout;
  let lastSearchResults = [];

  // Establecer la fecha actual en el campo de fecha
  const today = new Date().toISOString().split("T")[0];
  const movementDateInput = document.getElementById('movement_date');
  if (movementDateInput) {
    movementDateInput.value = today;
  }

  // MANTENER TODAS TUS FUNCIONES ORIGINALES
  function groupItemsBySpecs(items) {
    const grouped = {};
    
    items.forEach(item => {
      const key = item.Name.toLowerCase().trim();
      
      if (!grouped[key]) {
        grouped[key] = {
          Name: item.Name,
          Description: item.Description || '',
          CategoryID: item.CategoryID,
          SupplierID: item.SupplierID,
          StatusID: item.StatusID,
          variants: [],
          totalStock: 0,
          serials: []
        };
      }
      
      grouped[key].variants.push(item);
      grouped[key].totalStock += item.Stock || 0;
      
      if (item.UniqueIdentifier) {
        grouped[key].serials.push({
          serial: item.UniqueIdentifier,
          itemId: item.ID,
          stock: item.Stock || 0,
          location: item.Location || 'No especificada'
        });
      }
    });
    
    return Object.values(grouped);
  }

  async function searchItems(query) {
    try {
      const response = await fetch(`/api/items/search?q=${encodeURIComponent(query || '')}`);
      if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
      
      const items = await response.json() || [];
      lastSearchResults = items;
      
      const groupedItems = groupItemsBySpecs(items);
      
      if (query.trim()) {
        showSearchResults(groupedItems);
      } else {
        hideSearchResults();
      }
      
      return items;
      
    } catch (error) {
      console.error("Error en búsqueda:", error);
      hideSearchResults();
      lastSearchResults = [];
      return [];
    }
  }

  async function loadAllItems() {
    console.log('Usando búsqueda directa con API');
  }

  function showSearchResults(groupedItems) {
    if (!searchResults) return;
    
    if (groupedItems.length === 0) {
      searchResults.innerHTML = '<div class="search-item text-center"><i class="fas fa-search text-muted"></i><br><small class="text-muted">No se encontraron items</small></div>';
    } else {
      searchResults.innerHTML = groupedItems.map(group => {
        const locations = [...new Set(group.variants.map(v => v.Location))].join(', ');
        const hasMultipleVariants = group.variants.length > 1;
        
        return `
          <div class="search-item" onclick="selectItemGroup('${group.Name.replace(/'/g, "\\'")}', '${(group.Description || '').replace(/'/g, "\\'")}')">
            <div class="item-info">
              <div class="item-details">
                <h6><i class="fas fa-layer-group me-2 text-primary"></i>${group.Name}</h6>
                <small><strong>Especificaciones:</strong> ${group.Description || 'Sin descripción específica'}</small><br>
                <small><strong>${group.serials.length} números de serie disponibles</strong> ${hasMultipleVariants ? '(' + group.variants.length + ' variantes)' : ''}</small><br>
                <small><strong>Ubicaciones:</strong> ${locations}</small>
              </div>
              <div class="item-stock">
                <span class="stock-badge ${getStockClass(group.totalStock)}">${group.totalStock} unidades</span>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }
    
    searchResults.style.display = 'block';
  }

  function hideSearchResults() {
    if (searchResults) {
      searchResults.style.display = 'none';
    }
  }

  function getStockClass(stock) {
    if (stock > 10) return 'stock-high';
    if (stock > 5) return 'stock-medium';
    return 'stock-low';
  }

  window.selectItemGroup = function(itemName, itemDescription) {
    console.log('Seleccionando grupo:', itemName, itemDescription);
    
    const groupItems = lastSearchResults.filter(item => 
      item.Name.toLowerCase().trim() === itemName.toLowerCase().trim()
    );
    
    console.log('Items encontrados para el grupo:', groupItems.length);
    
    if (groupItems.length === 0) {
      alert('Error: No se encontraron items de este grupo');
      return;
    }
    
    showSerialSelectionModal(groupItems);
    hideSearchResults();
    searchInput.value = '';
  };

  function showSerialSelectionModal(groupItems) {
    const totalStock = groupItems.reduce((sum, item) => sum + (item.Stock || 0), 0);
    
    console.log('Mostrando modal para:', groupItems.length, 'items');
    
    const modalHtml = `
      <div class="modal fade" id="serialSelectionModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                <i class="fas fa-list me-2"></i>Seleccionar ${groupItems[0].Name}
              </h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <h6>Especificaciones:</h6>
                <p class="text-muted">${groupItems[0].Description || 'Sin descripción específica'}</p>
                <small class="text-info"><strong>${groupItems.length} variantes disponibles</strong></small>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Cantidad total a retirar:</label>
                <div class="input-group" style="max-width: 200px;">
                  <button type="button" class="btn btn-outline-secondary" onclick="changeModalQuantity(-1)">
                    <i class="fas fa-minus"></i>
                  </button>
                  <input type="number" class="form-control text-center" id="modalQuantity" value="1" min="1" max="${totalStock}">
                  <button type="button" class="btn btn-outline-secondary" onclick="changeModalQuantity(1)">
                    <i class="fas fa-plus"></i>
                  </button>
                </div>
                <small class="text-muted">Máximo: ${totalStock} unidades disponibles</small>
              </div>
              
              <div class="mb-3">
                <h6>Seleccionar números de serie específicos:</h6>
                <div class="serial-numbers" id="serialNumbersList">
                  ${groupItems.map(item => `
                    <div class="serial-item ${(item.Stock || 0) <= 0 ? 'disabled' : ''}" 
                         data-item-id="${item.ID}" 
                         data-stock="${item.Stock || 0}"
                         onclick="toggleSerial(this)">
                      <div class="d-flex justify-content-between align-items-center">
                        <div>
                          <strong>${item.UniqueIdentifier || 'Sin serie'}</strong><br>
                          <small>ID: #${item.ID} • ${item.Location || 'Sin ubicación'}</small>
                        </div>
                        <div class="text-end">
                          <span class="badge ${(item.Stock || 0) > 0 ? 'bg-success' : 'bg-danger'}">
                            ${item.Stock || 0} disponibles
                          </span>
                        </div>
                      </div>
                    </div>
                  `).join('')}
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
              <button type="button" class="btn btn-primary" onclick="confirmSerialSelection()">
                <i class="fas fa-check me-2"></i>Agregar Selección
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
    
    const existingModal = document.getElementById('serialSelectionModal');
    if (existingModal) {
      existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    const modal = new bootstrap.Modal(document.getElementById('serialSelectionModal'));
    modal.show();
    
    window.currentGroupItems = groupItems;
    window.selectedSerials = [];
    
    console.log('Modal creado con', groupItems.length, 'items');
  }

  window.changeModalQuantity = function(delta) {
    const quantityInput = document.getElementById('modalQuantity');
    if (!quantityInput) return;
    
    const currentQuantity = parseInt(quantityInput.value) || 1;
    const maxQuantity = parseInt(quantityInput.max) || 1;
    const newQuantity = Math.max(1, Math.min(maxQuantity, currentQuantity + delta));
    quantityInput.value = newQuantity;
  };

  window.toggleSerial = function(element) {
    if (element.classList.contains('disabled')) return;
    
    const itemId = parseInt(element.dataset.itemId);
    const stock = parseInt(element.dataset.stock);
    
    if (stock <= 0) return;
    
    if (element.classList.contains('selected')) {
      element.classList.remove('selected');
      window.selectedSerials = window.selectedSerials.filter(s => s.itemId !== itemId);
    } else {
      element.classList.add('selected');
      const item = window.currentGroupItems.find(i => i.ID === itemId);
      if (item) {
        window.selectedSerials.push({
          itemId: itemId,
          serial: item.UniqueIdentifier,
          stock: stock,
          item: item
        });
      }
    }
    
    console.log('Series seleccionadas:', window.selectedSerials);
  };

  window.confirmSerialSelection = function() {
    const quantityInput = document.getElementById('modalQuantity');
    if (!quantityInput) return;
    
    const quantity = parseInt(quantityInput.value) || 1;
    
    if (!window.selectedSerials || window.selectedSerials.length === 0) {
      alert('Debe seleccionar al menos un número de serie');
      return;
    }
    
    if (quantity > window.selectedSerials.length) {
      alert(`Solo puede retirar máximo ${window.selectedSerials.length} unidades basado en los números de serie seleccionados`);
      return;
    }
    
    const totalAvailableStock = window.selectedSerials.reduce((sum, s) => sum + s.stock, 0);
    if (quantity > totalAvailableStock) {
      alert(`Stock insuficiente. Total disponible: ${totalAvailableStock}`);
      return;
    }
    
    const groupItem = {
      groupName: window.currentGroupItems[0].Name,
      description: window.currentGroupItems[0].Description || '',
      selectedSerials: window.selectedSerials.slice(0, quantity),
      totalQuantity: quantity,
      categoryId: window.currentGroupItems[0].CategoryID,
      supplierId: window.currentGroupItems[0].SupplierID,
      statusId: window.currentGroupItems[0].StatusID,
      isGroup: true,
      originalItems: window.currentGroupItems
    };
    
    let targetIndex = -1;
    
    if (typeof window.editingGroupIndex !== 'undefined') {
      targetIndex = window.editingGroupIndex;
      window.editingGroupIndex = undefined;
    } else {
      targetIndex = selectedItems.findIndex(item => 
        item.isGroup && item.groupName === groupItem.groupName && item.description === groupItem.description
      );
    }
    
    if (targetIndex >= 0) {
      selectedItems[targetIndex] = groupItem;
    } else {
      selectedItems.push(groupItem);
    }
    
    updateSelectedItemsView();
    updateSummary();
    
    const modal = bootstrap.Modal.getInstance(document.getElementById('serialSelectionModal'));
    if (modal) {
      modal.hide();
    }
    
    window.currentGroupItems = null;
    window.selectedSerials = [];
  };

  // MANTENER TODAS TUS FUNCIONES DE ACTUALIZACIÓN ORIGINALES
  function updateSelectedItemsView() {
    if (!selectedItemsContainer) {
      console.error('selectedItemsContainer no encontrado');
      return;
    }
    
    if (selectedItems.length === 0) {
      selectedItemsContainer.style.display = 'none';
      return;
    }

    selectedItemsContainer.style.display = 'block';
    if (itemCount) {
      itemCount.textContent = selectedItems.length;
    }

    if (itemsList) {
      itemsList.innerHTML = selectedItems.map((item, index) => {
        if (item.isGroup) {
          return `
            <div class="product-item">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                  <h6 class="mb-1"><i class="fas fa-layer-group me-2"></i>${item.groupName}</h6>
                  <small class="text-muted">${item.description}</small><br>
                  <small class="text-muted"><strong>${item.totalQuantity} unidades seleccionadas</strong></small>
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeItem(${index})">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              
              <div class="serial-numbers mb-3">
                <h6 class="small">Números de serie seleccionados:</h6>
                ${item.selectedSerials.map(serial => `
                  <div class="serial-item selected">
                    <strong>${serial.serial}</strong><br>
                    <small>ID: #${serial.itemId} • Stock: ${serial.stock}</small>
                  </div>
                `).join('')}
              </div>
              
              <div class="row align-items-center">
                <div class="col-md-6">
                  <small class="text-muted">Total a retirar: <strong>${item.totalQuantity} unidades</strong></small>
                </div>
                <div class="col-md-6">
                  <button type="button" class="btn btn-outline-primary btn-sm" onclick="editGroupSelection(${index})">
                    <i class="fas fa-edit me-1"></i>Editar Selección
                  </button>
                </div>
              </div>
            </div>
          `;
        } else {
          return `
            <div class="product-item">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <div>
                  <h6 class="mb-1">${item.Name}</h6>
                  <small class="text-muted">ID: #${item.ID} ${item.UniqueIdentifier ? '• Serie: ' + item.UniqueIdentifier : ''}</small><br>
                  <small class="text-muted">Ubicación: ${item.Location || 'No especificada'}</small><br>
                  <small class="text-muted">Stock disponible: <strong>${item.Stock} unidades</strong></small>
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeItem(${index})">
                  <i class="fas fa-times"></i>
                </button>
              </div>
              
              <div class="row align-items-center">
                <div class="col-md-6">
                  <label class="form-label">Cantidad a retirar</label>
                </div>
                <div class="col-md-6">
                  <div class="input-group">
                    <button type="button" class="btn btn-outline-secondary" onclick="changeQuantity(${index}, -1)">
                      <i class="fas fa-minus"></i>
                    </button>
                    <input type="number" class="form-control text-center" 
                           value="${item.quantity}" 
                           min="1" max="${item.Stock}"
                           onchange="updateQuantity(${index}, this.value)">
                    <button type="button" class="btn btn-outline-secondary" onclick="changeQuantity(${index}, 1)">
                      <i class="fas fa-plus"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          `;
        }
      }).join('');
    }
  }

  window.editGroupSelection = function(index) {
    const groupItem = selectedItems[index];
    if (!groupItem.isGroup) return;
    
    let groupItems = [];
    
    if (groupItem.originalItems && groupItem.originalItems.length > 0) {
      groupItems = groupItem.originalItems;
    } else {
      groupItems = lastSearchResults.filter(item => 
        item.Name.toLowerCase().trim() === groupItem.groupName.toLowerCase().trim()
      );
    }
    
    if (groupItems.length === 0) {
      alert('Error: No se pudieron cargar los datos del grupo para editar');
      return;
    }
    
    showSerialSelectionModal(groupItems);
    
    setTimeout(() => {
      if (groupItem.selectedSerials) {
        groupItem.selectedSerials.forEach(selectedSerial => {
          const element = document.querySelector(`[data-item-id="${selectedSerial.itemId}"]`);
          if (element) {
            element.classList.add('selected');
          }
        });
        
        const quantityInput = document.getElementById('modalQuantity');
        if (quantityInput) {
          quantityInput.value = groupItem.totalQuantity;
        }
        window.selectedSerials = [...groupItem.selectedSerials];
      }
    }, 100);
    
    window.editingGroupIndex = index;
  };

  window.removeItem = function(index) {
    selectedItems.splice(index, 1);
    updateSelectedItemsView();
    updateSummary();
  };

  window.changeQuantity = function(index, delta) {
    const item = selectedItems[index];
    if (item.isGroup) return;
    
    const newQuantity = item.quantity + delta;
    
    if (newQuantity >= 1 && newQuantity <= item.Stock) {
      item.quantity = newQuantity;
      updateSelectedItemsView();
      updateSummary();
    }
  };

  window.updateQuantity = function(index, newQuantity) {
    const item = selectedItems[index];
    if (item.isGroup) return;
    
    const quantity = parseInt(newQuantity);
    
    if (quantity > item.Stock) {
      alert(`No hay suficiente stock. Stock disponible: ${item.Stock}`);
      updateSelectedItemsView();
      return;
    } else if (quantity < 1) {
      alert("La cantidad debe ser mayor a 0");
      updateSelectedItemsView();
      return;
    }
    
    item.quantity = quantity;
    updateSummary();
  };

  function updateSummary() {
    if (!summaryContent) {
      console.error('summaryContent no encontrado');
      return;
    }
    
    if (selectedItems.length === 0) {
      summaryContent.innerHTML = `
        <div class="text-center py-4">
          <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
          <p class="text-muted">No hay items seleccionados</p>
          <small class="text-muted">Busca y selecciona items para ver el resumen</small>
        </div>
      `;
      if (submitButton) submitButton.disabled = true;
      return;
    }

    const totalItems = selectedItems.reduce((sum, item) => {
      if (item.isGroup) {
        return sum + item.totalQuantity;
      } else {
        return sum + item.quantity;
      }
    }, 0);
    
    summaryContent.innerHTML = `
      <div class="summary-item">
        <span>Productos diferentes:</span>
        <span>${selectedItems.length}</span>
      </div>
      <div class="summary-item">
        <span>Unidades totales:</span>
        <span>${totalItems}</span>
      </div>
      <div class="summary-item">
        <span>Total a retirar:</span>
        <span>${totalItems} unidades</span>
      </div>
      
      <hr class="my-3">
      <h6 class="mb-2">Items seleccionados:</h6>
      ${selectedItems.map(item => {
        if (item.isGroup) {
          return `
            <div class="d-flex justify-content-between align-items-center mb-1">
              <small><i class="fas fa-layer-group me-1"></i>${item.groupName}</small>
              <small><strong>${item.totalQuantity}u</strong></small>
            </div>
            <div class="ms-3">
              ${item.selectedSerials.map(serial => `
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <small class="text-muted">• ${serial.serial}</small>
                  <small class="text-muted">1u</small>
                </div>
              `).join('')}
            </div>
          `;
        } else {
          return `
            <div class="d-flex justify-content-between align-items-center mb-1">
              <small>${item.Name}</small>
              <small><strong>${item.quantity}u</strong></small>
            </div>
          `;
        }
      }).join('')}
    `;

    if (submitButton) submitButton.disabled = false;
  }

  // MANTENER TODOS TUS EVENT LISTENERS ORIGINALES
  if (searchInput) {
    searchInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
          searchItems(query);
        }
      }
    });

    searchInput.addEventListener('input', function(e) {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        const query = e.target.value.trim();
        if (query.length >= 2) {
          searchItems(query);
        } else {
          hideSearchResults();
        }
      }, 300);
    });
  }

  if (searchButton) {
    searchButton.addEventListener("click", async function () {
      const query = searchInput.value.trim();
      if (query) {
        await searchItems(query);
      }
    });
  }

  document.addEventListener('click', function(e) {
    if (!e.target.closest('.search-container')) {
      hideSearchResults();
    }
  });

  function handleFiles(files) {
    Array.from(files).forEach((file) => {
      if (selectedFiles.has(file.name)) return;

      selectedFiles.add(file.name);
      const fileItem = document.createElement("div");
      fileItem.className = "file-item";
      fileItem.innerHTML = `
        <span>${file.name}</span>
        <i class="fas fa-times remove-file" onclick="removeFile('${file.name}')"></i>
      `;
      if (fileList) {
        fileList.appendChild(fileItem);
      }
    });
  }

  window.removeFile = function (fileName) {
    selectedFiles.delete(fileName);
    if (fileList) {
      const items = fileList.getElementsByClassName("file-item");
      for (let item of items) {
        if (item.firstElementChild.textContent === fileName) {
          item.remove();
          break;
        }
      }
    }
  };

  if (document.getElementById("dropArea")) {
    const dropArea = document.getElementById("dropArea");
    
    ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
      dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
    }

    ["dragenter", "dragover"].forEach((eventName) => {
      dropArea.addEventListener(eventName, highlight, false);
    });

    ["dragleave", "drop"].forEach((eventName) => {
      dropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
      dropArea.classList.add("dragover");
    }

    function unhighlight(e) {
      dropArea.classList.remove("dragover");
    }

    dropArea.addEventListener("drop", function (e) {
      const dt = e.dataTransfer;
      const files = dt.files;
      handleFiles(files);
    });

    if (fileInput) {
      fileInput.addEventListener("change", function () {
        handleFiles(this.files);
      });
    }
  }

  if (saveDraftButton) {
    saveDraftButton.addEventListener("click", function () {
      const draftData = {
        selectedItems: selectedItems,
        formData: {
          movement_type: document.getElementById('movement_type')?.value || '',
          responsible_name: document.getElementById('responsible_name')?.value || '',
          department: document.getElementById('department')?.value || '',
          responsible_email: document.getElementById('responsible_email')?.value || '',
          responsible_phone: document.getElementById('responsible_phone')?.value || '',
          notes: document.getElementById('notes')?.value || '',
          // NUEVOS CAMPOS PARA TIENDAS
          destination_type: document.querySelector('input[name="destination_type"]:checked')?.value || 'department',
          tienda_id: document.getElementById('tiendaSelect')?.value || ''
        }
      };
      
      localStorage.setItem("salidaDraft", JSON.stringify(draftData));
      alert("Borrador guardado exitosamente");
    });
  }

  function loadDraft() {
    const savedDraft = localStorage.getItem("salidaDraft");
    if (savedDraft) {
      try {
        const draftData = JSON.parse(savedDraft);
        
        if (draftData.selectedItems && Array.isArray(draftData.selectedItems)) {
          selectedItems = draftData.selectedItems;
          updateSelectedItemsView();
          updateSummary();
        }
        
        if (draftData.formData) {
          Object.keys(draftData.formData).forEach(key => {
            if (key === 'destination_type') {
              const radio = document.querySelector(`input[name="destination_type"][value="${draftData.formData[key]}"]`);
              if (radio) {
                radio.checked = true;
                // Trigger change event to update UI
                radio.dispatchEvent(new Event('change'));
              }
            } else {
              const element = document.getElementById(key);
              if (element) {
                element.value = draftData.formData[key];
              }
            }
          });
        }
      } catch (error) {
        console.error('Error cargando borrador:', error);
      }
    }
  }

  // ENVÍO DEL FORMULARIO - MODIFICADO PARA MANEJAR DESTINOS
  if (form) {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      if (selectedItems.length === 0) {
        alert("Debe seleccionar al menos un item");
        return;
      }

      // Validar campos requeridos básicos
      const basicRequiredFields = ['movement_type', 'movement_date', 'responsible_name'];
      for (let field of basicRequiredFields) {
        const element = document.getElementById(field);
        if (!element || !element.value.trim()) {
          alert(`El campo ${field.replace('_', ' ')} es requerido`);
          return;
        }
      }

      // NUEVA VALIDACIÓN: Validar destino según tipo seleccionado
      const destinationType = document.querySelector('input[name="destination_type"]:checked')?.value || 'department';
      
      if (destinationType === 'department') {
        const departmentElement = document.getElementById('department');
        if (!departmentElement || !departmentElement.value.trim()) {
          alert('Debe seleccionar un departamento');
          return;
        }
      } else if (destinationType === 'tienda') {
        const tiendaElement = document.getElementById('tiendaSelect');
        if (!tiendaElement || !tiendaElement.value.trim()) {
          alert('Debe seleccionar una tienda');
          return;
        }
      }

      // Validar stock para todos los items individuales
      for (let item of selectedItems) {
        if (!item.isGroup && item.quantity > item.Stock) {
          alert(`No hay suficiente stock para ${item.Name}. Stock disponible: ${item.Stock}`);
          return;
        }
      }

      const formData = new FormData();
      
      // Datos básicos del formulario
      formData.append('movement_type', document.getElementById('movement_type').value);
      formData.append('movement_date', document.getElementById('movement_date').value);
      formData.append('responsible_name', document.getElementById('responsible_name').value);
      formData.append('responsible_email', document.getElementById('responsible_email')?.value || '');
      formData.append('responsible_phone', document.getElementById('responsible_phone')?.value || '');
      formData.append('notes', document.getElementById('notes')?.value || '');
      
      // NUEVOS CAMPOS: Tipo de destino y destino específico
      formData.append('destination_type', destinationType);
      
      if (destinationType === 'department') {
        formData.append('department', document.getElementById('department').value);
      } else if (destinationType === 'tienda') {
        formData.append('tienda_id', document.getElementById('tiendaSelect').value);
      }
      
      // Items seleccionados
      formData.append('selected_items', JSON.stringify(selectedItems));

      // Archivos
      selectedFiles.forEach((fileName) => {
        formData.append("files", fileName);
      });

      try {
        const response = await fetch("/registrarSalida", {
          method: "POST",
          headers: {
            Accept: "application/json",
          },
          body: formData,
        });

        const result = await response.json();

        if (response.ok) {
          // Limpiar borrador
          localStorage.removeItem("salidaDraft");
          alert("Salida registrada exitosamente");
          window.location.href = "/inventario";
        } else {
          alert("Error: " + (result.error || "Error desconocido"));
        }
      } catch (error) {
        console.error("Error:", error);
        alert("Error al procesar la solicitud");
      }
    });
  }

  // Inicialización
  loadAllItems();
  loadDraft();
  updateSummary();
});