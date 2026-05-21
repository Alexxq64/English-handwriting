// ==================== ПАРСИНГ URL ====================

function parseUrl() {
    const urlPath = window.location.pathname;
    const urlParams = new URLSearchParams(window.location.search);
    const mode = urlParams.get('mode');
    const from = urlParams.get('from');
    const exact = urlParams.get('exact');  // Точный символ для тренировки
    let rawSymbol = urlPath.split('/').pop();
    return { rawSymbol, mode, from, exact };
}

const { rawSymbol, mode, from, exact } = parseUrl();

// Сохраняем referrer для возврата
if (from === 'best') {
    sessionStorage.setItem('returnUrl', '/best_attempts');
} else {
    sessionStorage.setItem('returnUrl', '/');
}