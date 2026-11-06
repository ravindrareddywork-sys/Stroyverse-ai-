/**
 * StoryVerse AI — Main Application Script (main.js)
 * Manages global navigation, mobile drawer, toasts, and backend connectivity indicator.
 */

(function () {
  'use strict';

  /**
   * Displays a toast notification.
   * @param {string} message - Notification text
   * @param {string} type - 'success' | 'error' | 'warning' | 'info'
   * @param {number} duration - Display time in milliseconds
   */
  function showToast(message, type = 'info', duration = 4000) {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <div class="toast-content">${escapeHTML(message)}</div>
      <button class="toast-close" aria-label="Close">&times;</button>
    `;

    container.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(() => {
      toast.classList.add('show');
    });

    const closeBtn = toast.querySelector('.toast-close');
    const removeToast = () => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    };

    closeBtn.addEventListener('click', removeToast);

    if (duration > 0) {
      setTimeout(removeToast, duration);
    }
  }

  function escapeHTML(str) {
    const p = document.createElement('p');
    p.textContent = str;
    return p.innerHTML;
  }

  /**
   * Initializes mobile navigation toggle.
   */
  function initMobileNav() {
    const toggle = document.querySelector('.mobile-toggle');
    const menu = document.querySelector('.nav-menu');

    if (toggle && menu) {
      toggle.addEventListener('click', () => {
        menu.classList.toggle('open');
      });

      // Close menu when clicking outside
      document.addEventListener('click', (e) => {
        if (!toggle.contains(e.target) && !menu.contains(e.target) && menu.classList.contains('open')) {
          menu.classList.remove('open');
        }
      });
    }
  }

  let backendStatusChecked = false;

  /**
   * Checks backend status and updates status badge if present.
   * Guarded to run only once per page lifecycle.
   */
  async function initBackendStatus() {
    if (backendStatusChecked) return;
    const dot = document.querySelector('.status-dot');
    const text = document.querySelector('.status-text');

    if (!dot) return;
    backendStatusChecked = true;

    if (window.StoryVerseAPI) {
      const isHealthy = await window.StoryVerseAPI.checkHealth();
      if (isHealthy) {
        dot.classList.add('online');
        dot.classList.remove('offline');
        if (text) text.textContent = 'Backend: Online';
      } else {
        dot.classList.add('offline');
        dot.classList.remove('online');
        if (text) text.textContent = 'Backend: Offline';
      }
    }
  }

  /**
   * Sets the active nav link based on current page URL.
   */
  function highlightActiveNavLink() {
    const currentPath = window.location.pathname.toLowerCase();
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (!href) return;

      const cleanHref = href.toLowerCase().split('/').pop();
      const cleanPath = currentPath.split('/').pop() || 'index.html';

      if (cleanHref === cleanPath || (cleanPath === '' && cleanHref === 'index.html')) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    initMobileNav();
    highlightActiveNavLink();
    initBackendStatus();
  });

  // Global helper exports
  window.StoryVerse = {
    showToast,
    escapeHTML
  };
})();
