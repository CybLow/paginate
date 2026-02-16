/**
 * pypaginate Documentation - Version switcher fallback.
 *
 * The RTD theme handles toggle via jQuery, but this vanilla JS
 * fallback ensures it works on GitHub Pages if jQuery fails.
 * Also adds "close on outside click" behavior.
 */

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {
        var versions = document.querySelector('.rst-versions');
        if (!versions) return;

        // Only bind toggle if jQuery/RTD theme JS is not available
        if (typeof jQuery === 'undefined' || typeof SphinxRtdTheme === 'undefined') {
            var toggle = versions.querySelector('.rst-current-version');
            if (toggle) {
                toggle.addEventListener('click', function() {
                    versions.classList.toggle('shift-up');
                });
            }
        }

        // Close on click outside (always active — not provided by RTD theme)
        document.addEventListener('click', function(event) {
            if (!versions.contains(event.target)) {
                versions.classList.remove('shift-up');
            }
        });
    });
})();
