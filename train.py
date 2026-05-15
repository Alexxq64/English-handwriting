# import numpy as np
# import pandas as pd
# import tensorflow as tf
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import Conv2D, MaxPool2D, Dropout, Flatten, Dense
# from tensorflow.keras.utils import to_categorical
# from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
# from sklearn.model_selection import train_test_split
# import os
# import matplotlib.pyplot as plt

# from utils.preprocessing import fix_emnist_batch

# IMG_SIZE = 28
# NUM_CLASSES = 62
# BATCH_SIZE = 64
# EPOCHS = 5

# TRAIN_CSV = 'data/emnist/emnist-byclass-train.csv'
# TEST_CSV = 'data/emnist/emnist-byclass-test.csv'
# MODEL_SAVE_PATH = 'models/cnn_model.keras'


# def load_data(csv_path, max_rows=None):
#     print(f"Загрузка {csv_path}...")
#     df = pd.read_csv(csv_path, nrows=max_rows)
#     labels = df.iloc[:, 0].values
#     pixels = df.iloc[:, 1:].values
#     images = pixels.reshape(-1, IMG_SIZE, IMG_SIZE).astype('float32')
#     return images, labels


# def create_model():
#     model = Sequential([
#         Conv2D(32, (3, 3), activation='relu', padding='same',
#                input_shape=(IMG_SIZE, IMG_SIZE, 1)),
#         MaxPool2D((2, 2)),
#         Dropout(0.25),

#         Conv2D(64, (3, 3), activation='relu', padding='same'),
#         MaxPool2D((2, 2)),
#         Dropout(0.25),

#         Flatten(),
#         Dense(128, activation='relu'),
#         Dropout(0.5),
#         Dense(NUM_CLASSES, activation='softmax')
#     ])

#     model.compile(
#         optimizer='adam',
#         loss='categorical_crossentropy',
#         metrics=['accuracy']
#     )
#     return model


# def main():
#     print("=" * 50)
#     print("EMNIST CNN training")
#     print("=" * 50)

#     X_train, y_train = load_data(TRAIN_CSV)
#     X_test, y_test = load_data(TEST_CSV)

#     print(f"Train: {X_train.shape}, Test: {X_test.shape}")

#     # ✔ ИСПРАВЛЕНО: УБРАНА ИНВЕРСИЯ
#     X_train = fix_emnist_batch(X_train)
#     X_test = fix_emnist_batch(X_test)

#     print("\nSANITY CHECK")
#     print("Label:", y_train[0])
#     plt.imshow(X_train[0], cmap='gray')
#     plt.show()

#     y_train = to_categorical(y_train, NUM_CLASSES)
#     y_test = to_categorical(y_test, NUM_CLASSES)

#     y_train_argmax = np.argmax(y_train, axis=1)

#     X_train, X_val, y_train, y_val = train_test_split(
#         X_train, y_train,
#         test_size=0.2,
#         random_state=42,
#         stratify=y_train_argmax
#     )

#     X_train = X_train.reshape(-1, IMG_SIZE, IMG_SIZE, 1)
#     X_val = X_val.reshape(-1, IMG_SIZE, IMG_SIZE, 1)
#     X_test = X_test.reshape(-1, IMG_SIZE, IMG_SIZE, 1)

#     model = create_model()
#     model.summary()

#     callbacks = [
#         EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
#         ModelCheckpoint(MODEL_SAVE_PATH, monitor='val_loss', save_best_only=True)
#     ]

#     model.fit(
#         X_train, y_train,
#         validation_data=(X_val, y_val),
#         epochs=EPOCHS,
#         batch_size=BATCH_SIZE,
#         callbacks=callbacks
#     )

#     loss, acc = model.evaluate(X_test, y_test, verbose=0)
#     print("Test acc:", acc)

#     model.save(MODEL_SAVE_PATH)


# if __name__ == "__main__":
#     main()


import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPool2D, Dropout, Flatten, Dense
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split
import os
import matplotlib.pyplot as plt

from utils.preprocessing import fix_emnist_batch

IMG_SIZE = 28
NUM_CLASSES = 52  # 26 заглавных + 26 строчных (без цифр)
BATCH_SIZE = 64
EPOCHS = 5

TRAIN_CSV = 'data/emnist/emnist-byclass-train.csv'
TEST_CSV = 'data/emnist/emnist-byclass-test.csv'
MODEL_SAVE_PATH = 'models/cnn_model.keras'


def load_data_only_letters(csv_path, max_rows=None):
    """
    Загружает данные из CSV, оставляет только буквы (классы 10-61).
    Классы 0-9 (цифры) отбрасываются.
    """
    print(f"Загрузка {csv_path}...")
    df = pd.read_csv(csv_path, nrows=max_rows)
    
    # Оставляем только буквы: классы 10-61
    mask = (df.iloc[:, 0] >= 10) & (df.iloc[:, 0] <= 61)
    df = df[mask].reset_index(drop=True)
    
    labels = df.iloc[:, 0].values
    pixels = df.iloc[:, 1:].values
    images = pixels.reshape(-1, IMG_SIZE, IMG_SIZE).astype('float32')
    
    # Перенумеровываем классы в 0-51 (было 10-61)
    labels = labels - 10
    
    print(f"  Осталось {len(images)} изображений (только буквы)")
    return images, labels


def create_model():
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', padding='same',
               input_shape=(IMG_SIZE, IMG_SIZE, 1)),
        MaxPool2D((2, 2)),
        Dropout(0.25),

        Conv2D(64, (3, 3), activation='relu', padding='same'),
        MaxPool2D((2, 2)),
        Dropout(0.25),

        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(NUM_CLASSES, activation='softmax')
    ])

    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    return model


def main():
    print("=" * 50)
    print("EMNIST CNN training (только буквы, без цифр)")
    print("=" * 50)

    X_train, y_train = load_data_only_letters(TRAIN_CSV)
    X_test, y_test = load_data_only_letters(TEST_CSV)

    print(f"Train: {X_train.shape}, Test: {X_test.shape}")

    # Приводим EMNIST к нормальной ориентации
    X_train = fix_emnist_batch(X_train)
    X_test = fix_emnist_batch(X_test)

    print("\nSANITY CHECK")
    print("Label (0-51):", y_train[0])
    print("Соответствие: 0=A, 25=Z, 26=a, 51=z")
    plt.imshow(X_train[0], cmap='gray')
    plt.title(f"Label: {y_train[0]}")
    plt.show()

    # One-hot кодирование
    y_train = to_categorical(y_train, NUM_CLASSES)
    y_test = to_categorical(y_test, NUM_CLASSES)

    y_train_argmax = np.argmax(y_train, axis=1)

    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train,
        test_size=0.2,
        random_state=42,
        stratify=y_train_argmax
    )

    X_train = X_train.reshape(-1, IMG_SIZE, IMG_SIZE, 1)
    X_val = X_val.reshape(-1, IMG_SIZE, IMG_SIZE, 1)
    X_test = X_test.reshape(-1, IMG_SIZE, IMG_SIZE, 1)

    model = create_model()
    model.summary()

    callbacks = [
        EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
        ModelCheckpoint(MODEL_SAVE_PATH, monitor='val_loss', save_best_only=True)
    ]

    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks
    )

    loss, acc = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test accuracy: {acc:.4f} ({acc*100:.2f}%)")

    model.save(MODEL_SAVE_PATH)
    print(f"Модель сохранена: {MODEL_SAVE_PATH}")


if __name__ == "__main__":
    main()