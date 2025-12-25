/**
 * Manager Panel JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
  initSearch();
  initToasts();
  initMobileMenu();
});

/**
 * Search functionality
 */
function initSearch() {
  const searchInput = document.getElementById('search-input');
  if (!searchInput) return;

  let timeout = null;
  searchInput.addEventListener('input', function(e) {
    clearTimeout(timeout);
    timeout = setTimeout(function() {
      const form = searchInput.closest('form');
      if (form) {
        form.submit();
      }
    }, 500);
  });
}

/**
 * Toast notifications
 */
function showToast(message, type = 'info') {
  const existing = document.querySelector('.toast-notification');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = `toast-notification ${type}`;

  let icon = 'info-circle';
  if (type === 'success') icon = 'check';
  else if (type === 'error') icon = 'x';
  else if (type === 'warning') icon = 'alert-triangle';

  toast.innerHTML = `
    <i class="ti ti-${icon}"></i>
    ${message}
  `;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function initToasts() {
  // Auto-show toast for Django messages
  const messages = document.querySelectorAll('[data-toast]');
  messages.forEach(msg => {
    const text = msg.textContent.trim();
    const type = msg.dataset.toast;
    if (text) {
      showToast(text, type);
    }
    msg.remove();
  });
}

/**
 * Mobile menu toggle
 */
function initMobileMenu() {
  const menuToggle = document.getElementById('menu-toggle');
  const sidebar = document.querySelector('.manager-sidebar');

  if (!menuToggle || !sidebar) return;

  menuToggle.addEventListener('click', function() {
    sidebar.classList.toggle('open');
  });

  // Close on outside click
  document.addEventListener('click', function(e) {
    if (sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) &&
        !menuToggle.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });
}

/**
 * Confirm action
 */
function confirmAction(message) {
  return confirm(message);
}

/**
 * Format relative time
 */
function formatTimeAgo(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now - date) / 1000);

  if (seconds < 60) return 'Ahora';
  if (seconds < 3600) return `Hace ${Math.floor(seconds / 60)} min`;
  if (seconds < 86400) return `Hace ${Math.floor(seconds / 3600)} h`;
  if (seconds < 604800) return `Hace ${Math.floor(seconds / 86400)} d`;

  return date.toLocaleDateString('es-CO', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
  @keyframes slideOut {
    from {
      transform: translateY(0);
      opacity: 1;
    }
    to {
      transform: translateY(1rem);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);
