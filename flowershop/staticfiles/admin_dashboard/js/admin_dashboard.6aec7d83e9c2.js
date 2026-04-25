document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('adminSidebar');
    const toggle = document.getElementById('sidebarToggle');
    const backdrop = document.getElementById('sidebarBackdrop');

    if (toggle && sidebar) {
        const setSidebarState = (isOpen) => {
            sidebar.classList.toggle('is-open', isOpen);
            toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
            document.body.classList.toggle('admin-sidebar-open', isOpen);
            if (backdrop) {
                backdrop.classList.toggle('is-open', isOpen);
            }
        };

        toggle.addEventListener('click', () => {
            setSidebarState(!sidebar.classList.contains('is-open'));
        });

        if (backdrop) {
            backdrop.addEventListener('click', () => {
                setSidebarState(false);
            });
        }

        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                setSidebarState(false);
            }
        });
    }

    document.querySelectorAll('[data-confirm]').forEach((button) => {
        button.addEventListener('click', (event) => {
            const message = button.getAttribute('data-confirm') || 'Are you sure?';
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

    document.querySelectorAll('form').forEach((form) => {
        form.addEventListener('submit', () => {
            const submit = form.querySelector('button[type="submit"]');
            if (submit) {
                submit.dataset.originalText = submit.textContent;
                submit.textContent = 'Saving...';
                submit.disabled = true;
            }
        });
    });
});
