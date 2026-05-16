// static/js/test_mode_config.js
export const WORDS_BY_LEVEL = {
    1: ["Cat", "Dog", "Sun", "Car", "Bus", "Hat", "Leg", "Eye", "Cup", "Bag",
        "Ant", "Bed", "Box", "Fox", "Hen", "Pig", "Rat", "Pen", "Red"],
    2: ["House", "Mouse", "Apple", "Table", "Chair", "Door", "Bird", "Fish",
        "Horse", "Duck", "Frog", "Star", "Moon", "Sweet", "Happy", "Bread", "Water", "Light"],
    3: ["Pencil", "Teacher", "Garden", "Brother", "Sister", "Morning", "Evening",
        "Dinner", "Bicycle", "Blanket", "Picture", "Project", "Student", "Monster",
        "Kitchen", "Weather", "Library"]
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