/**
 * navbar.js - Shared navbar functionality for all pages
 * Handles: Mobile menu toggle, dropdown menu, navigation
 * Include in every HTML page: <script src="{{ url_for('static', filename='js/navbar.js') }}"></script>
 */

document.addEventListener('DOMContentLoaded', function() {
  initNavbar();
  initDropdown();
});

/**
 * Initialize mobile menu toggle
 */
function initNavbar() {
  const mobileMenu = document.getElementById('mobile-menu');
  const navList = document.getElementById('nav-list');
  
  if (!mobileMenu || !navList) return; // Exit if elements don't exist
  
  // Toggle mobile menu on button click
  mobileMenu.addEventListener('click', (e) => {
    e.stopPropagation();
    navList.classList.toggle('active');
  });
  
  // Close menu when clicking on a link
  const navLinks = navList.querySelectorAll('a');
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      navList.classList.remove('active');
    });
  });
  
  // Close menu when clicking outside
  document.addEventListener('click', (e) => {
    if (navList.classList.contains('active') && !navList.contains(e.target) && !mobileMenu.contains(e.target)) {
      navList.classList.remove('active');
    }
  });
}

/**
 * Initialize dropdown menu
 */
function initDropdown() {
  const dropdownBtn = document.querySelector('.dropbtn');
  const dropdownContent = document.getElementById('analyzeDropdown');
  
  if (!dropdownBtn || !dropdownContent) return; // Exit if elements don't exist
  
  // Toggle dropdown on button click
  dropdownBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdownContent.classList.toggle('show');
  });
  
  // Close dropdown when clicking on a link
  const dropdownLinks = dropdownContent.querySelectorAll('a');
  dropdownLinks.forEach(link => {
    link.addEventListener('click', () => {
      dropdownContent.classList.remove('show');
    });
  });
  
  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (dropdownContent.classList.contains('show') && 
        !dropdownContent.contains(e.target) && 
        !dropdownBtn.contains(e.target)) {
      dropdownContent.classList.remove('show');
    }
  });
}
