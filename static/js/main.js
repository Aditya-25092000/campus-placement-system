/**
 * Campus Placement System - Main JavaScript
 */
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar Toggle (Mobile)
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
            if (overlay) overlay.classList.toggle('show');
        });
    }
    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });
    }

    // Flash messages auto-dismiss
    document.querySelectorAll('.flash-message').forEach(function(msg) {
        setTimeout(function() {
            msg.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(function() { msg.remove(); }, 300);
        }, 5000);
        var btn = msg.querySelector('.flash-close');
        if (btn) btn.addEventListener('click', function() { msg.remove(); });
    });

    // Confirm delete
    document.querySelectorAll('.delete-form').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this record? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // CGPA validation
    var cgpa = document.getElementById('cgpa');
    if (cgpa) {
        cgpa.addEventListener('input', function() {
            var v = parseFloat(this.value);
            this.classList.toggle('is-invalid', v < 0 || v > 10);
        });
    }

    // Backlog validation
    var bl = document.getElementById('active_backlogs');
    if (bl) {
        bl.addEventListener('input', function() {
            if (parseInt(this.value) < 0) this.value = 0;
        });
    }

    // Active sidebar link
    var path = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(function(link) {
        var href = link.getAttribute('href');
        if (href === path || (href !== '/' && path.startsWith(href))) {
            link.classList.add('active');
        }
    });

    // Bootstrap tooltips
    [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]')).map(function(el) {
        return new bootstrap.Tooltip(el);
    });
});

function initChart(canvasId, type, labels, datasets, options) {
    var canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    var defaults = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position: 'bottom', labels: { padding: 16, usePointStyle: true, font: { size: 12 } } }
        }
    };
    return new Chart(canvas, {
        type: type,
        data: { labels: labels, datasets: datasets },
        options: Object.assign({}, defaults, options || {})
    });
}
