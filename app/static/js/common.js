/**
 * MCT Dashboard - Common JavaScript functions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();

    // Set active sidebar item
    highlightActiveSidebarItem();

    // Set up data filters
    setupDataFilters();

    // Setup collapsible sections
    setupCollapsibleSections();

    // Initialize notifications
    setupNotifications();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Highlight the current page in the sidebar
 */
function highlightActiveSidebarItem() {
    // Get current URL path
    const currentPath = window.location.pathname;

    // Find all sidebar links
    const sidebarLinks = document.querySelectorAll('.sidebar-nav .nav-link');

    // Check each link to see if it matches the current path
    sidebarLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

/**
 * Setup generic data filter functionality
 */
function setupDataFilters() {
    // Find all filter forms
    const filterForms = document.querySelectorAll('[data-filter-target]');

    filterForms.forEach(form => {
        const targetSelector = form.dataset.filterTarget;
        const targetItems = document.querySelectorAll(targetSelector);
        const inputs = form.querySelectorAll('input, select');

        // Handle input changes
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                filterItems(form, targetItems);
            });

            if (input.tagName === 'INPUT' && input.type === 'text') {
                input.addEventListener('keyup', function() {
                    filterItems(form, targetItems);
                });
            }
        });

        // Handle reset button
        const resetBtn = form.querySelector('[data-filter-reset]');
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                inputs.forEach(input => {
                    if (input.tagName === 'SELECT') {
                        input.selectedIndex = 0;
                    } else if (input.type === 'text' || input.type === 'number') {
                        input.value = '';
                    } else if (input.type === 'checkbox' || input.type === 'radio') {
                        input.checked = false;
                    }
                });

                // Show all items
                targetItems.forEach(item => {
                    item.style.display = '';
                });
            });
        }
    });
}

/**
 * Filter items based on form values
 */
function filterItems(form, items) {
    // Build filter criteria
    const filters = {};

    form.querySelectorAll('input, select').forEach(input => {
        if (input.name && input.value) {
            filters[input.name] = input.value.toLowerCase();
        }
    });

    // Apply filters
    items.forEach(item => {
        let show = true;

        // Check each filter
        Object.keys(filters).forEach(key => {
            const filterValue = filters[key];
            const itemValue = item.dataset[key] ? item.dataset[key].toLowerCase() : '';

            if (filterValue && !itemValue.includes(filterValue)) {
                show = false;
            }
        });

        item.style.display = show ? '' : 'none';
    });
}

/**
 * Setup collapsible section functionality
 */
function setupCollapsibleSections() {
    const collapsibleHeaders = document.querySelectorAll('[data-bs-toggle="collapse"]');

    collapsibleHeaders.forEach(header => {
        const iconElement = header.querySelector('.fas');
        if (iconElement) {
            header.addEventListener('click', function() {
                const targetId = this.getAttribute('data-bs-target');
                const target = document.querySelector(targetId);

                // Check if it's expanded after Bootstrap handles the click
                setTimeout(() => {
                    const isExpanded = target.classList.contains('show');

                    if (isExpanded) {
                        iconElement.classList.remove('fa-chevron-down');
                        iconElement.classList.add('fa-chevron-up');
                    } else {
                        iconElement.classList.remove('fa-chevron-up');
                        iconElement.classList.add('fa-chevron-down');
                    }
                }, 50);
            });
        }
    });
}

/**
 * Setup in-app notifications
 */
function setupNotifications() {
    // Auto-dismiss existing alerts
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        setTimeout(() => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) {
                closeBtn.click();
            }
        }, 5000);
    });
}

/**
 * Show a notification to the user
 * @param {string} message - The message to display
 * @param {string} type - 'success', 'error', 'warning', or 'info'
 * @param {number} timeout - Time in ms before the notification is hidden
 */
function showNotification(message, type = 'info', timeout = 3000) {
    const typeClass = type === 'error' ? 'danger' : type;
    const iconClass = type === 'success' ? 'check-circle' :
                      type === 'error' ? 'exclamation-circle' :
                      type === 'warning' ? 'exclamation-triangle' : 'info-circle';

    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${typeClass} alert-dismissible fade show position-fixed bottom-0 end-0 m-3`;
    notification.style.zIndex = '1050';
    notification.innerHTML = `
        <i class="fas fa-${iconClass} me-2"></i>${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Add to DOM
    document.body.appendChild(notification);

    // Auto dismiss
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 150);
    }, timeout);
}

/**
 * Format a currency value
 * @param {number} value - The value to format as currency
 * @param {string} currency - Currency symbol
 * @returns {string} Formatted currency string
 */
function formatCurrency(value, currency = '$') {
    return `${currency}${parseFloat(value).toFixed(2)}`;
}

/**
 * Format a date in a human-readable format
 * @param {Date|string} date - Date object or date string
 * @param {string} format - 'short', 'long', or 'relative'
 * @returns {string} Formatted date string
 */
function formatDate(date, format = 'short') {
    if (!(date instanceof Date)) {
        date = new Date(date);
    }

    if (format === 'short') {
        return date.toLocaleDateString();
    } else if (format === 'long') {
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } else if (format === 'relative') {
        const now = new Date();
        const diffMs = now - date;
        const diffSec = Math.floor(diffMs / 1000);
        const diffMin = Math.floor(diffSec / 60);
        const diffHour = Math.floor(diffMin / 60);
        const diffDay = Math.floor(diffHour / 24);

        if (diffSec < 60) {
            return 'just now';
        } else if (diffMin < 60) {
            return `${diffMin} minute${diffMin !== 1 ? 's' : ''} ago`;
        } else if (diffHour < 24) {
            return `${diffHour} hour${diffHour !== 1 ? 's' : ''} ago`;
        } else if (diffDay < 30) {
            return `${diffDay} day${diffDay !== 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    return date.toLocaleString();
}

/**
 * Export data to CSV
 * @param {Array} data - Array of objects to export
 * @param {string} filename - Filename for the download
 */
function exportToCSV(data, filename = 'export.csv') {
    if (!data || !data.length) {
        showNotification('No data to export', 'warning');
        return;
    }

    // Extract headers
    const headers = Object.keys(data[0]);

    // Build CSV content
    let csvContent = headers.join(',') + '\n';

    data.forEach(item => {
        const row = headers.map(header => {
            let cell = item[header] || '';

            // Escape commas and quotes
            if (typeof cell === 'string' && (cell.includes(',') || cell.includes('"'))) {
                cell = `"${cell.replace(/"/g, '""')}"`;
            }

            return cell;
        });

        csvContent += row.join(',') + '\n';
    });

    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.display = 'none';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}