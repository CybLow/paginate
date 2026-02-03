/**
 * pypaginate Documentation Custom JavaScript
 * - Version switcher toggle functionality
 */

(function() {
    'use strict';
    
    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        // Version switcher toggle
        var versions = document.querySelector('.rst-versions');
        if (versions) {
            var currentVersion = versions.querySelector('.rst-current-version');
            if (currentVersion) {
                currentVersion.addEventListener('click', function() {
                    versions.classList.toggle('shift-up');
                });
            }
            
            // Close on click outside
            document.addEventListener('click', function(event) {
                if (!versions.contains(event.target)) {
                    versions.classList.remove('shift-up');
                }
            });
        }
    });
})();
