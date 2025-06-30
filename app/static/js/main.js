document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })

    // Flash message auto-dismiss
    var alertList = document.querySelectorAll('.alert')
    alertList.forEach(function (alert) {
        setTimeout(function() {
            bootstrap.Alert.getInstance(alert).close()
        }, 5000)
    })
})