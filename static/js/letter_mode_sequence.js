// ==================== ГЕНЕРАЦИЯ ПОСЛЕДОВАТЕЛЬНОСТИ ====================

function shuffleArray(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

function generateLetterAttempts(letterPair) {
    let attempts = [];
    for (let i = 0; i < 5; i++) attempts.push(letterPair.upper);
    for (let i = 0; i < 5; i++) attempts.push(letterPair.lower);
    return shuffleArray(attempts);
}

function generateDigitAttempts() {
    return shuffleArray([...DIGITS]);
}

function findLetterPair(symbol) {
    return LETTER_PAIRS.find(pair => 
        pair.upper === symbol.toUpperCase() || 
        pair.lower === symbol
    );
}

function generateSequence() {
    let attemptsList = [];
    let targetDisplayText = '';
    let currentLetter = rawSymbol;

    // ТОЧНЫЙ РЕЖИМ (при переходе из лучших попыток)
    if (exact) {
        attemptsList = Array(10).fill(exact);
        if (DIGITS.includes(exact)) {
            targetDisplayText = `Цифра ${exact}`;
        } else {
            targetDisplayText = `Буква ${exact}`;
        }
        currentLetter = exact;
    }
    // СТАНДАРТНЫЙ РЕЖИМ
    else if (rawSymbol === 'digits') {
        attemptsList = generateDigitAttempts();
        targetDisplayText = 'Цифры 0-9';
        currentLetter = attemptsList[0];
    } else if (mode === 'letters') {
        const foundPair = findLetterPair(rawSymbol);
        if (foundPair) {
            attemptsList = generateLetterAttempts(foundPair);
            targetDisplayText = `Буквы ${foundPair.upper}/${foundPair.lower}`;
            currentLetter = attemptsList[0];
        } else {
            attemptsList = Array(10).fill(rawSymbol);
            targetDisplayText = `Символ ${rawSymbol}`;
        }
    } else {
        if (DIGITS.includes(rawSymbol)) {
            attemptsList = generateDigitAttempts();
            targetDisplayText = 'Цифры 0-9';
            currentLetter = attemptsList[0];
        } else {
            const foundPair = findLetterPair(rawSymbol);
            if (foundPair) {
                attemptsList = generateLetterAttempts(foundPair);
                targetDisplayText = `Буквы ${foundPair.upper}/${foundPair.lower}`;
                currentLetter = attemptsList[0];
            } else {
                attemptsList = Array(10).fill(rawSymbol);
                targetDisplayText = `Символ ${rawSymbol}`;
            }
        }
    }

    return { attemptsList, targetDisplayText, currentLetter };
}

let attemptsList = [];
let currentAttemptIndex = 0;
let scores = [];
let canvasLocked = false;
let targetDisplayText = '';
let currentLetter = '';

const sequenceData = generateSequence();
attemptsList = sequenceData.attemptsList;
targetDisplayText = sequenceData.targetDisplayText;
currentLetter = sequenceData.currentLetter;