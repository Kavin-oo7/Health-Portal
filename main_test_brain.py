import os
import tensorflow as tf
from keras.preprocessing import image
import numpy as np

# === Load Model ===
model_path = os.path.join("models", "brain_tumor_model.h5")
model = tf.keras.models.load_model(model_path)

# === Test Single Image ===
test_image_path = "datasets/brain_tumor/test/tumor/sample1.jpg"  # change path as needed

img = image.load_img(test_image_path, target_size=(224, 224))
img_array = image.img_to_array(img) / 255.0
img_array = np.expand_dims(img_array, axis=0)

prediction = model.predict(img_array)
label = "Tumor Detected 🧠" if prediction[0][0] > 0.5 else "No Tumor Detected ✅"

print(f"Prediction: {label}")
