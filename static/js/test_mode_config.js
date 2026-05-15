// static/js/test_mode_config.js
export const WORDS_BY_LEVEL = {
    1: ["cat", "dog", "sun", "car", "bus", "hat", "leg", "eye", "cup", "bag",
        "ant", "bed", "box", "fox", "hen", "pig", "rat", "pen", "red"],
    2: ["house", "mouse", "apple", "table", "chair", "door", "bird", "fish",
        "horse", "duck", "frog", "star", "moon", "sweet", "happy", "bread", "water", "light"],
    3: ["pencil", "teacher", "garden", "brother", "sister", "morning", "evening",
        "dinner", "bicycle", "blanket", "picture", "project", "student", "monster",
        "kitchen", "weather", "library"]
    // 1: ["CAT", "DOG", "SUN", "CAR", "BUS", "HAT", "LEG", "EYE", "CUP", "BAG",
    //     "ANT", "BED", "BOX", "FOX", "HEN", "PIG", "RAT", "PEN", "RED"],
    // 2: ["HOUSE", "MOUSE", "APPLE", "TABLE", "CHAIR", "DOOR", "BIRD", "FISH",
    //     "HORSE", "DUCK", "FROG", "STAR", "MOON", "SWEET", "HAPPY", "BREAD", "WATER", "LIGHT"],
    // 3: ["PENCIL", "TEACHER", "GARDEN", "BROTHER", "SISTER", "MORNING", "EVENING",
    //     "DINNER", "BICYCLE", "BLANKET", "PICTURE", "PROJECT", "STUDENT", "MONSTER",
    //     "KITCHEN", "WEATHER", "LIBRARY"]    
};

export const LINES = {
    TOP: 50,
    MID: 110,
    BASE: 180
};

export function getCanvasWidthForWord(word) {
    const len = word.length;
    if (len <= 3) return 420;
    if (len <= 5) return 560;
    return 700;
}