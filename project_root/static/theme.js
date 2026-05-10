(function () {
    var KEY = 'oz-theme';

    function get() {
        return localStorage.getItem(KEY) || 'light';
    }

    function set(theme) {
        localStorage.setItem(KEY, theme);
        document.documentElement.setAttribute('data-theme', theme);
    }

    function toggle() {
        var next = get() === 'dark' ? 'light' : 'dark';
        document.documentElement.classList.add('theme-transitioning');
        set(next);
        setTimeout(function () {
            document.documentElement.classList.remove('theme-transitioning');
        }, 300);
        syncButton(next);
    }

    function syncButton(theme) {
        var btn = document.getElementById('themeSwitch');
        if (btn) {
            btn.classList.toggle('is-dark', theme === 'dark');
        }
    }

    function initButton() {
        syncButton(get());
        var btn = document.getElementById('themeSwitch');
        if (btn) {
            btn.addEventListener('click', toggle);
        }
    }

    window.__theme = { get: get, toggle: toggle };

    if (document.readyState !== 'loading') {
        initButton();
    } else {
        document.addEventListener('DOMContentLoaded', initButton);
    }
})();
