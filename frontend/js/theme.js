/**
 * StoryVerse AI — Theme Management (theme.js)
 * Handles light and dark mode toggling with localStorage persistence.
 */

(function () {
  'use strict';

  const THEME_STORAGE_KEY = 'storyverse_theme';
  const THEME_LIGHT = 'light';
  const THEME_DARK = 'dark';

  /**
   * Retrieves the initial theme from localStorage or system preference.
   */
  function getPreferredTheme() {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    if (savedTheme) {
      return savedTheme;
    }
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      ? THEME_DARK
      : THEME_LIGHT;
  }

  /**
   * Applies the theme attribute to the HTML root element.
   * @param {string} theme - 'light' or 'dark'
   */
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  }

  // Set theme immediately to avoid flash of unstyled content
  applyTheme(getPreferredTheme());

  // Setup toggle button listeners when DOM is loaded
  document.addEventListener('DOMContentLoaded', () => {
    const themeToggleButtons = document.querySelectorAll('.theme-toggle');

    themeToggleButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') || THEME_LIGHT;
        const newTheme = currentTheme === THEME_DARK ? THEME_LIGHT : THEME_DARK;
        applyTheme(newTheme);
      });
    });
  });

  // Export functions to global scope
  window.StoryVerseTheme = {
    getPreferredTheme,
    applyTheme
  };
})();
