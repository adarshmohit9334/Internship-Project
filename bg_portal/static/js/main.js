document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.flash').forEach((item) => {
        setTimeout(() => item.remove(), 4000);
    });
    document.querySelectorAll('[data-confirm="true"]').forEach((btn) => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const message = btn.getAttribute('data-message') || 'Are you sure?';
            const modal = document.getElementById('confirmModal');
            if (modal) {
                document.getElementById('confirmModalMessage').textContent = message;
                const form = document.getElementById('confirmModalForm');
                form.action = btn.dataset.formAction || '';
                modal.style.display = 'flex';
            }
        });
    });
});
