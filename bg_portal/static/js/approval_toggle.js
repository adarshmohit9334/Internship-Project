document.addEventListener('DOMContentLoaded', () => {
    const bgAmount = document.getElementById('bg_amount');
    const mdBanner = document.getElementById('approval-banner-md');
    const boardBanner = document.getElementById('approval-banner-board');
    const mdFile = document.getElementById('md_approval_file');
    const boardFile = document.getElementById('board_approval_file');
    if (!bgAmount) return;
    function updateBanner() {
        const value = parseFloat(bgAmount.value || 0);
        if (value > 0 && value <= 1500000) {
            mdBanner.style.display = 'block';
            boardBanner.style.display = 'none';
            if (mdFile) mdFile.required = true;
            if (boardFile) boardFile.required = false;
        } else if (value > 1500000) {
            mdBanner.style.display = 'none';
            boardBanner.style.display = 'block';
            if (mdFile) mdFile.required = false;
            if (boardFile) boardFile.required = true;
        } else {
            mdBanner.style.display = 'none';
            boardBanner.style.display = 'none';
            if (mdFile) mdFile.required = false;
            if (boardFile) boardFile.required = false;
        }
    }
    bgAmount.addEventListener('input', updateBanner);
    updateBanner();
});
