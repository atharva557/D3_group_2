/**
 * theme-manager.js - Theme persistence and initialization
 * Features: 
 *   - Respects localStorage preference
 *   - Falls back to system preference
 *   - No flash of wrong theme on load
 *   - Syncs with backend
 * Include in <head> BEFORE other scripts to prevent flash
 */

class ThemeManager {
  constructor() {
    this.STORAGE_KEY = 'reddit-pulse-theme';
    this.LIGHT_CLASS = 'light';
    this.init();
  }
  
  /**
   * Initialize theme on page load
   */
  init() {
    this.applyStoredTheme();
    this.setupToggleButton();
    this.observeSystemPreference();
  }
  
  /**
   * Apply theme from localStorage or system preference
   */
  applyStoredTheme() {
    const saved = localStorage.getItem(this.STORAGE_KEY);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Determine if theme should be dark
    const shouldBeDark = saved ? saved === 'dark' : prefersDark;
    
    // Apply theme class
    const root = document.documentElement;
    if (shouldBeDark) {
      root.classList.remove(this.LIGHT_CLASS);
    } else {
      root.classList.add(this.LIGHT_CLASS);
    }
    
    // Update button icon
    this.updateThemeButton();
  }
  
  /**
   * Setup theme toggle button click handler
   */
  setupToggleButton() {
    const btn = document.getElementById('themeToggle');
    if (!btn) return;
    
    btn.addEventListener('click', () => this.toggle());
  }
  
  /**
   * Toggle between light and dark theme
   */
  toggle() {
    const root = document.documentElement;
    const isLight = root.classList.toggle(this.LIGHT_CLASS);
    const theme = isLight ? 'light' : 'dark';
    
    // Save to localStorage
    localStorage.setItem(this.STORAGE_KEY, theme);
    
    // Update button icon
    this.updateThemeButton();
    
    // Sync with backend (non-blocking)
    this.syncWithBackend(theme);
  }
  
  /**
   * Update theme button icon
   */
  updateThemeButton() {
    const btn = document.getElementById('themeToggle');
    if (!btn) return;
    
    const isLight = document.documentElement.classList.contains(this.LIGHT_CLASS);
    btn.textContent = isLight ? '🌙' : '☀️';
    btn.title = isLight ? 'Switch to dark mode' : 'Switch to light mode';
  }
  
  /**
   * Listen for system preference changes
   */
  observeSystemPreference() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    mediaQuery.addEventListener('change', (e) => {
      // Only apply if user hasn't manually set a preference
      if (!localStorage.getItem(this.STORAGE_KEY)) {
        if (e.matches) {
          document.documentElement.classList.remove(this.LIGHT_CLASS);
        } else {
          document.documentElement.classList.add(this.LIGHT_CLASS);
        }
        this.updateThemeButton();
      }
    });
  }
  
  /**
   * Sync theme preference with backend
   * This saves user preference to database for cross-device sync
   */
  syncWithBackend(theme) {
    // Only sync if user is logged in
    if (!this.isUserLoggedIn()) return;
    
    fetch('/api/user/theme', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify({ theme: theme })
    })
    .catch(err => {
      // Silent fail - theme still works locally
      console.debug('Theme sync failed:', err);
    });
  }
  
  /**
   * Check if user is logged in (simple check)
   */
  isUserLoggedIn() {
    // Check if there's a CSRF token in the DOM (Flask-WTF marker of logged-in state)
    return document.querySelector('input[name="csrf_token"]') !== null;
  }
}

/**
 * Initialize theme BEFORE page renders to prevent flash
 * Run this script in <head> tag before any other scripts
 */
(function() {
  const saved = localStorage.getItem('reddit-pulse-theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const isDark = saved ? saved === 'dark' : prefersDark;
  
  // Apply immediately to prevent flash
  if (!isDark) {
    document.documentElement.classList.add('light');
  }
})();

/**
 * Initialize theme manager when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
  window.themeManager = new ThemeManager();
});

/**
 * Global function for backward compatibility
 */
function toggleTheme() {
  if (window.themeManager) {
    window.themeManager.toggle();
  }
}
