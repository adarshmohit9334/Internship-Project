function renderBarChart(elementId, labels, datasets) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    new Chart(ctx, { type: 'bar', data: { labels, datasets }, options: { responsive: true } });
}
function renderPieChart(elementId, labels, data, colors) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    new Chart(ctx, { type: 'doughnut', data: { labels, datasets: [{ data, backgroundColor: colors }] }, options: { responsive: true } });
}
