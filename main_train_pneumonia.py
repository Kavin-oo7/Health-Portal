import os
import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from keras import layers, models
from keras.callbacks import EarlyStopping, ModelCheckpoint

# === Paths ===
base_dir = os.path.join("datasets", "pneumonia")
train_dir = os.path.join(base_dir, "train")
test_dir = os.path.join(base_dir, "test")
model_save_path = os.path.join("models", "pneumonia_model.h5")

# === Data Preparation ===
img_size = (224, 224)
batch_size = 32

train_datagen = ImageDataGenerator(
    rescale=1.0/255,
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode="nearest"
)

test_datagen = ImageDataGenerator(rescale=1.0/255)

train_gen = train_datagen.flow_from_directory(
    train_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='binary'
)

test_gen = test_datagen.flow_from_directory(
    test_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='binary'
)

# === Model Architecture ===
model = models.Sequential([
    layers.Conv2D(32, (3,3), activation='relu', input_shape=(*img_size, 3)),
    layers.MaxPooling2D(2,2),
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),
    layers.Conv2D(128, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.3),
    layers.Dense(1, activation='sigmoid')
])

# === Compile Model ===
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

# === Callbacks ===
callbacks = [
    EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
    ModelCheckpoint(model_save_path, save_best_only=True)
]

# === Train Model ===
history = model.fit(
    train_gen,
    epochs=20,
    validation_data=test_gen,
    callbacks=callbacks
)

# === Save Final Model ===
model.save(model_save_path)
print(f"✅ Pneumonia model saved to: {model_save_path}")
