// ==================== КОНФИГУРАЦИЯ ====================

// Парные буквы (заглавная + строчная)
const LETTER_PAIRS = [
    { upper: 'A', lower: 'a' }, { upper: 'B', lower: 'b' },
    { upper: 'C', lower: 'c' }, { upper: 'D', lower: 'd' },
    { upper: 'E', lower: 'e' }, { upper: 'F', lower: 'f' },
    { upper: 'G', lower: 'g' }, { upper: 'H', lower: 'h' },
    { upper: 'I', lower: 'i' }, { upper: 'J', lower: 'j' },
    { upper: 'K', lower: 'k' }, { upper: 'L', lower: 'l' },
    { upper: 'M', lower: 'm' }, { upper: 'N', lower: 'n' },
    { upper: 'O', lower: 'o' }, { upper: 'P', lower: 'p' },
    { upper: 'Q', lower: 'q' }, { upper: 'R', lower: 'r' },
    { upper: 'S', lower: 's' }, { upper: 'T', lower: 't' },
    { upper: 'U', lower: 'u' }, { upper: 'V', lower: 'v' },
    { upper: 'W', lower: 'w' }, { upper: 'X', lower: 'x' },
    { upper: 'Y', lower: 'y' }, { upper: 'Z', lower: 'z' }
];

// Цифры
const DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

// Размеры canvas
const CANVAS_SIZE = 280;

// Координаты линий (для удаления перед отправкой)
const TOP_LINE_Y = 50;
const MID_LINE_Y = 110;
const BASE_LINE_Y = 180;