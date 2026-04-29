console.log("Borrador cargado exitosamente");

document.addEventListener("DOMContentLoaded", function () {});

async function handleFiles() {
  const dropArea = document.getElementById("dropArea");
  const fileInput = document.getElementById("fileInput");
  const previewContainer = document.getElementById("previewContainer");

  // Evitar el comportamiento por defecto de arrastrar y soltar
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, (e) => e.preventDefault(), false);
  });

  // Resaltar cuando se arrastran archivos
  ["dragenter", "dragover"].forEach((eventName) => {
    dropArea.addEventListener(
      eventName,
      () => dropArea.classList.add("highlight"),
      false
    );
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(
      eventName,
      () => dropArea.classList.remove("highlight"),
      false
    );
  });

  // Manejar archivos al soltarlos
  dropArea.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    handleFiles(files);
  });

  // Manejar archivos seleccionados manualmente
  fileInput.addEventListener("change", (e) => {
    const files = e.target.files;
    handleFiles(files);
  });

  function handleFiles(files) {
    previewContainer.innerHTML = ""; // Limpiar la vista previa
    Array.from(files).forEach((file) => {
      previewFile(file);
      uploadFile(file);
    });
  }

  function previewFile(file) {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = function () {
      const img = document.createElement("img");
      img.src = reader.result;
      img.classList.add("preview-image");
      previewContainer.appendChild(img);
    };
  }

  async function uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file, file.name);

    try {
      const response = await fetch("/upload-endpoint", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Error al subir el archivo");
      }

      const result = await response.json();
      console.log("Archivo subido con éxito:", result);
    } catch (error) {
      console.error("Error al subir el archivo:", error);
    }
  }
}
