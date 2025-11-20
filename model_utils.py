import os
import numpy as np
from keras.models import load_model
from keras.utils import load_img, img_to_array
from config import Config

MODEL_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "models")

def load_models():
    brain_path = os.path.join(MODEL_DIR, "brain_tumor_model.h5")
    pneumo_path = os.path.join(MODEL_DIR, "pneumonia_model.h5")

    brain = None
    pneumo = None
    if os.path.exists(brain_path):
        brain = load_model(brain_path)
    else:
        print(f"[model_utils] brain model not found at {brain_path}")

    if os.path.exists(pneumo_path):
        pneumo = load_model(pneumo_path)
    else:
        print(f"[model_utils] pneumonia model not found at {pneumo_path}")

    return brain, pneumo

def preprocess_image(path, target_size=(224,224), grayscale=False):
    # load_img supports color_mode
    if grayscale:
        img = load_img(path, color_mode="grayscale", target_size=target_size)
        arr = img_to_array(img)  # shape (h,w,1)
    else:
        img = load_img(path, color_mode="rgb", target_size=target_size)
        arr = img_to_array(img)  # shape (h,w,3)
    arr = arr.astype("float32") / 255.0
    # expand dims
    arr = np.expand_dims(arr, axis=0)
    return arr

def predict_brain_tumor(image_path, model):
    """
    model should output either a single sigmoid [p] or softmax [p_no,p_yes].
    Returns dict: {"label": "Tumor Detected"|"No Tumor", "score": 0.92}
    """
    if model is None:
        return {"label": "Model not available", "score": 0.0}

    x = preprocess_image(image_path, target_size=(224,224), grayscale=False)
    preds = model.predict(x)
    # handle output formats
    if preds.shape[-1] == 1:
        p = float(preds[0][0])
        label = "Tumor Detected" if p > 0.5 else "No Tumor"
        score = p if p > 0.5 else 1 - p
    else:
        p_no = float(preds[0][0])
        p_yes = float(preds[0][1])
        if p_yes >= p_no:
            label = "Tumor Detected"
            score = p_yes
        else:
            label = "No Tumor"
            score = p_no
    return {"label": label, "score": float(round(score, 4))}

def predict_pneumonia(image_path, model):
    """
    Handles grayscale X-rays. Returns {"label":"Pneumonia Detected"|"Normal","score":...}
    """
    if model is None:
        return {"label": "Model not available", "score": 0.0}

    # Many X-ray models expect grayscale; try grayscale first
    try:
        x = preprocess_image(image_path, target_size=(224,224), grayscale=True)
        preds = model.predict(x)
    except Exception:
        # fallback to RGB
        x = preprocess_image(image_path, target_size=(224,224), grayscale=False)
        preds = model.predict(x)

    if preds.shape[-1] == 1:
        p = float(preds[0][0])
        label = "Pneumonia Detected" if p > 0.5 else "Normal"
        score = p if p > 0.5 else 1 - p
    else:
        # assume [normal, pneumonia] or [pneumo, normal] try choose by max
        probs = preds[0]
        idx = int(np.argmax(probs))
        # attempt to guess mapping: check which label corresponds to higher prob historically commonly [Normal,Pneumonia]
        # Safer: return index and score but map to labels conservatively:
        if len(probs) == 2:
            # common: [Normal, Pneumonia]
            label = "Pneumonia Detected" if idx == 1 else "Normal"
            score = float(probs[idx])
        else:
            # multi-class unknown -> return max index
            label = f"Class_{idx}"
            score = float(probs[idx])
    return {"label": label, "score": float(round(score, 4))}
