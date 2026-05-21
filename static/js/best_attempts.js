function setupTableSorting(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const headers = table.querySelectorAll('th');
    let currentSortColumn = null;
    let currentSortDirection = 'asc';
    
    headers.forEach((header, idx) => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            if (currentSortColumn === idx) {
                currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                currentSortColumn = idx;
                currentSortDirection = 'asc';
            }
            
            rows.sort((a, b) => {
                let aVal, bVal;
                
                if (idx === 0) {
                    aVal = a.cells[0].innerText;
                    bVal = b.cells[0].innerText;
                    return currentSortDirection === 'asc' 
                        ? aVal.localeCompare(bVal) 
                        : bVal.localeCompare(aVal);
                } 
                else if (idx === 2) {
                    aVal = parseInt(a.cells[4].getAttribute('data-max-errors')) || 0;
                    bVal = parseInt(b.cells[4].getAttribute('data-max-errors')) || 0;
                    return currentSortDirection === 'asc' ? aVal - bVal : bVal - aVal;
                }
                else {
                    const aScores = [];
                    const bScores = [];
                    for (let i = 1; i <= 3; i++) {
                        const aScore = a.cells[i].getAttribute('data-score');
                        const bScore = b.cells[i].getAttribute('data-score');
                        if (aScore) aScores.push(parseInt(aScore));
                        if (bScore) bScores.push(parseInt(bScore));
                    }
                    aVal = Math.max(...aScores);
                    bVal = Math.max(...bScores);
                    return currentSortDirection === 'asc' ? aVal - bVal : bVal - aVal;
                }
            });
            
            const fragment = document.createDocumentFragment();
            rows.forEach(row => fragment.appendChild(row));
            tbody.innerHTML = '';
            tbody.appendChild(fragment);
        });
    });
}

setupTableSorting('allTable');