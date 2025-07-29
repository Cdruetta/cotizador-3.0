// JavaScript principal para el sistema de cotizaciones

// Import Bootstrap
const bootstrap = window.bootstrap

document.addEventListener("DOMContentLoaded", () => {
  // Inicializar tooltips de Bootstrap
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  var tooltipList = tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))

  // Inicializar popovers de Bootstrap
  var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
  var popoverList = popoverTriggerList.map((popoverTriggerEl) => new bootstrap.Popover(popoverTriggerEl))

  // Auto-hide alerts después de 5 segundos
  setTimeout(() => {
    var alerts = document.querySelectorAll(".alert:not(.alert-permanent)")
    alerts.forEach((alert) => {
      var bsAlert = new bootstrap.Alert(alert)
      bsAlert.close()
    })
  }, 5000)

  // Confirmación para eliminaciones
  var deleteLinks = document.querySelectorAll('a[href*="eliminar"], a[href*="delete"]')
  deleteLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      if (!confirm("¿Está seguro de que desea eliminar este elemento?")) {
        e.preventDefault()
      }
    })
  })

  // Búsqueda en tiempo real (opcional)
  var searchInputs = document.querySelectorAll('input[name="search"]')
  searchInputs.forEach((input) => {
    var timeoutId
    input.addEventListener("input", () => {
      clearTimeout(timeoutId)
      timeoutId = setTimeout(() => {
        // Aquí podrías implementar búsqueda AJAX si lo deseas
        console.log("Buscando:", input.value)
      }, 500)
    })
  })

  // Formatear números como moneda
  function formatCurrency(amount) {
    return new Intl.NumberFormat("es-AR", {
      style: "currency",
      currency: "ARS",
    }).format(amount)
  }

  // Calcular totales en formularios de cotización
  function calculateTotal() {
    var total = 0
    var rows = document.querySelectorAll(".item-row")

    rows.forEach((row) => {
      var cantidad = Number.parseFloat(row.querySelector(".cantidad").value) || 0
      var precio = Number.parseFloat(row.querySelector(".precio").value) || 0
      var subtotal = cantidad * precio

      row.querySelector(".subtotal").textContent = formatCurrency(subtotal)
      total += subtotal
    })

    var totalElement = document.querySelector(".total-general")
    if (totalElement) {
      totalElement.textContent = formatCurrency(total)
    }
  }

  // Event listeners para cálculos
  document.addEventListener("input", (e) => {
    if (e.target.classList.contains("cantidad") || e.target.classList.contains("precio")) {
      calculateTotal()
    }
  })

  // Smooth scrolling para enlaces internos
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault()
      var target = document.querySelector(this.getAttribute("href"))
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        })
      }
    })
  })

  // Validación de formularios
  var forms = document.querySelectorAll(".needs-validation")
  forms.forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
      }
      form.classList.add("was-validated")
    })
  })

  // Loading states para botones
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", () => {
      var submitBtn = form.querySelector('button[type="submit"]')
      if (submitBtn) {
        submitBtn.disabled = true
        submitBtn.innerHTML =
          '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Procesando...'
      }
    })
  })

  // Copiar al portapapeles
  function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
      // Mostrar mensaje de éxito
      var toast = document.createElement("div")
      toast.className = "toast align-items-center text-white bg-success border-0"
      toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">
                        Copiado al portapapeles
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            `
      document.body.appendChild(toast)
      var bsToast = new bootstrap.Toast(toast)
      bsToast.show()

      setTimeout(() => {
        document.body.removeChild(toast)
      }, 3000)
    })
  }

  // Event listeners para copiar
  document.querySelectorAll(".copy-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      var text = this.getAttribute("data-copy")
      copyToClipboard(text)
    })
  })
})

// Función para imprimir
function printPage() {
  window.print()
}

// Función para exportar tabla a CSV
function exportTableToCSV(tableId, filename) {
  var csv = []
  var rows = document.querySelectorAll("#" + tableId + " tr")

  for (var i = 0; i < rows.length; i++) {
    var row = [],
      cols = rows[i].querySelectorAll("td, th")

    for (var j = 0; j < cols.length; j++) {
      row.push(cols[j].innerText)
    }

    csv.push(row.join(","))
  }

  downloadCSV(csv.join("\n"), filename)
}

function downloadCSV(csv, filename) {
  var csvFile
  var downloadLink

  csvFile = new Blob([csv], { type: "text/csv" })
  downloadLink = document.createElement("a")
  downloadLink.download = filename
  downloadLink.href = window.URL.createObjectURL(csvFile)
  downloadLink.style.display = "none"
  document.body.appendChild(downloadLink)
  downloadLink.click()
  document.body.removeChild(downloadLink)
}

// Utilidades para fechas
function formatDate(date) {
  return new Intl.DateTimeFormat("es-AR").format(new Date(date))
}

// Validaciones personalizadas
function validateEmail(email) {
  var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

function validatePhone(phone) {
  var re = /^[\d\s\-+$$$$]+$/
  return re.test(phone)
}

// Función para mostrar notificaciones
function showNotification(message, type = "info") {
  var alertClass = "alert-" + type
  var alert = document.createElement("div")
  alert.className = "alert " + alertClass + " alert-dismissible fade show"
  alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `

  var container = document.querySelector(".container-fluid")
  if (container) {
    container.insertBefore(alert, container.firstChild)
  }

  setTimeout(() => {
    if (alert.parentNode) {
      alert.parentNode.removeChild(alert)
    }
  }, 5000)
}
