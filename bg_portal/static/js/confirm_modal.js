document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('confirmModal');
    const cancel = document.getElementById('confirmModalCancel');
    const confirm = document.getElementById('confirmModalConfirm');
    if (!modal || !cancel || !confirm) return;
    cancel.addEventListener('click', () => modal.style.display = 'none');
    confirm.addEventListener('click', () => {
        const form = document.getElementById('confirmModalForm');
        if (form) form.submit();
    });
});
