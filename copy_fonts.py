import os
import shutil

# Путь к исходной папке со шрифтами
SOURCE_DIR = r"C:\MyHobby\260521_Diploma_Python_EnglishLetters"

# Целевая папка
TARGET_DIR = r"C:\Users\User\Desktop\english-handwriting-app\static\fonts"

# Создаём целевую папку, если её нет
os.makedirs(TARGET_DIR, exist_ok=True)

# Счётчики
copied = 0
skipped = 0
errors = 0

# Рекурсивно обходим все папки
for root, dirs, files in os.walk(SOURCE_DIR):
    for file in files:
        if file.endswith('.ttf'):
            source_path = os.path.join(root, file)
            target_path = os.path.join(TARGET_DIR, file)
            
            # Если файл уже существует — пропускаем
            if os.path.exists(target_path):
                print(f"[ПРОПУЩЕН] {file} (уже есть)")
                skipped += 1
            else:
                try:
                    shutil.copy2(source_path, target_path)
                    print(f"[КОПИРОВАН] {file}")
                    copied += 1
                except Exception as e:
                    print(f"[ОШИБКА] {file}: {e}")
                    errors += 1

print("\n" + "=" * 60)
print("СТАТИСТИКА КОПИРОВАНИЯ")
print("=" * 60)
print(f"Скопировано: {copied}")
print(f"Пропущено (уже есть): {skipped}")
print(f"Ошибок: {errors}")
print("=" * 60)
print(f"Все шрифты скопированы в: {TARGET_DIR}")