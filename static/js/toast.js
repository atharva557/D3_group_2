/**
 * toast.js - Toast notification system
 * Features:
 *   - Success, error, warning, info notifications
 *   - Auto-dismiss with configurable duration
 *   - Manual close button
 *   - Stacked notifications
 * 
 * Usage:
 *   Toast.success('Operation completed!');
 *   Toast.error('Something went wrong!');
 *   Toast.warning('Please review');
 *   Toast.info('FYI: ...');
 */

const Toast = (() => {
  const TOAST_DURATION = 5000; // 5 seconds
  let toastContainer = null;
  
  /**
   * Initialize toast container if not exists
   */
  function ensureContainer() {
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.className = 'toast-container';
      toastContainer.setAttribute('role', 'region');
      toastContainer.setAttribute('aria-live', 'polite');
      toastContainer.setAttribute('aria-atomic', 'true');
      document.body.appendChild(toastContainer);
    }
    return toastContainer;
  }
  
  /**
   * Create and show a toast
   * @param {String} message - Toast message
   * @param {String} type - Type: 'success', 'error', 'warning', 'info'
   * @param {Number} duration - Auto-dismiss duration (ms), 0 = no auto-dismiss
   */
  function show(message, type = 'info', duration = TOAST_DURATION) {
    const container = ensureContainer();
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Create content
    const content = document.createElement('div');
    content.className = 'toast-message';
    content.textContent = message;
    
    // Create close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'toast-close';
    closeBtn.textContent = '✕';
    closeBtn.setAttribute('aria-label', 'Close notification');
    closeBtn.addEventListener('click', () => removeToast(toast));
    
    // Assemble toast
    toast.appendChild(content);
    toast.appendChild(closeBtn);
    
    // Add to container
    container.appendChild(toast);
    
    // Auto-dismiss if duration specified
    if (duration > 0) {
      setTimeout(() => removeToast(toast), duration);
    }
    
    return toast;
  }
  
  /**
   * Remove toast with animation
   * @param {HTMLElement} toast - Toast element
   */
  function removeToast(toast) {
    if (!toast || !toast.parentElement) return;
    
    toast.style.animation = 'slideOutRight 0.3s ease forwards';
    setTimeout(() => {
      if (toast.parentElement) {
        toast.remove();
      }
    }, 300);
  }
  
  /**
   * Clear all toasts
   */
  function clearAll() {
    if (toastContainer) {
      toastContainer.innerHTML = '';
    }
  }
  
  /**
   * Public API
   */
  return {
    success: (message, duration = TOAST_DURATION) => show(message, 'success', duration),
    error: (message, duration = TOAST_DURATION) => show(message, 'error', duration),
    warning: (message, duration = TOAST_DURATION) => show(message, 'warning', duration),
    info: (message, duration = TOAST_DURATION) => show(message, 'info', duration),
    show: show,
    remove: removeToast,
    clear: clearAll
  };
})();

/**
 * Add slideOutRight animation (if not in CSS)
 */
if (!document.querySelector('style[data-toast-animations]')) {
  const style = document.createElement('style');
  style.setAttribute('data-toast-animations', 'true');
  style.textContent = `
    @keyframes slideOutRight {
      from {
        opacity: 1;
        transform: translateX(0);
      }
      to {
        opacity: 0;
        transform: translateX(20px);
      }
    }
  `;
  document.head.appendChild(style);
}
