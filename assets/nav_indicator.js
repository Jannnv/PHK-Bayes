/**
 * Smooth sliding nav indicator
 * Watches for URL changes and repositions the indicator element.
 */
(function() {
    'use strict';

    function updateIndicator() {
        var pathname = window.location.pathname;
        var targetId = 'nav-overview';

        if (pathname === '/trends') {
            targetId = 'nav-trends';
        } else if (pathname === '/analysis') {
            targetId = 'nav-analysis';
        }

        var target = document.getElementById(targetId);
        var indicator = document.getElementById('nav-indicator');

        if (!target || !indicator) return;

        var navContainer = target.closest('.sidebar-nav');
        if (!navContainer) return;

        var navRect = navContainer.getBoundingClientRect();
        var targetRect = target.getBoundingClientRect();
        var topPos = targetRect.top - navRect.top;

        indicator.style.top = topPos + 'px';
        indicator.style.height = targetRect.height + 'px';
    }

    // Run on initial load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(updateIndicator, 100);
        });
    } else {
        setTimeout(updateIndicator, 100);
    }

    // Watch for URL changes (Dash uses pushState)
    var _pushState = history.pushState;
    history.pushState = function() {
        _pushState.apply(history, arguments);
        setTimeout(updateIndicator, 50);
    };

    window.addEventListener('popstate', function() {
        setTimeout(updateIndicator, 50);
    });

    // Also observe DOM mutations for when Dash re-renders nav links
    var observer = new MutationObserver(function(mutations) {
        for (var i = 0; i < mutations.length; i++) {
            var m = mutations[i];
            if (m.type === 'attributes' && m.attributeName === 'class' &&
                m.target.classList && m.target.classList.contains('sidebar-link')) {
                setTimeout(updateIndicator, 20);
                break;
            }
        }
    });

    // Start observing once DOM is ready
    function startObserving() {
        var sidebar = document.querySelector('.sidebar-nav');
        if (sidebar) {
            observer.observe(sidebar, { attributes: true, subtree: true });
        } else {
            setTimeout(startObserving, 200);
        }
    }
    startObserving();
})();
