# ============================================================
# train_npk_multitask_efficientnetv2l_v2.py
# Version multitask corrigée et améliorée
# ============================================================

import os
import json
import random
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from tensorflow.keras import layers, Model, callbacks, optimizers
from tensorflow.keras.applications.efficientnet_v2 import (
    EfficientNetV2L,
    preprocess_input
)

# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

DATA_PATH = r"C:\Users\surface pro 7\Desktop\npk_90percent\data"
SAVE_DIR = r"C:\Users\surface pro 7\Desktop\npk_90percent\npk_multitask_efficientnetv2l_v2"
os.makedirs(SAVE_DIR, exist_ok=True)

TRAIN_CSV = os.path.join(DATA_PATH, "_classesTR.csv")
VALID_CSV = os.path.join(DATA_PATH, "_classesv.csv")
TEST_CSV  = os.path.join(DATA_PATH, "_classes.csv")

TRAIN_FOLDER = os.path.join(DATA_PATH, "train")
VALID_FOLDER = os.path.join(DATA_PATH, "valid")
TEST_FOLDER  = os.path.join(DATA_PATH, "test")

IMG_SIZE = 320
BATCH_SIZE = 6
EPOCHS_PHASE1 = 10
EPOCHS_PHASE2 = 12

LABEL_COLS = ['K0', 'K1', 'K2', 'N0', 'N1', 'N2', 'P0', 'P1']

# ============================================================
# OUTILS
# ============================================================

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def save_json(obj, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def set_float_columns(df: pd.DataFrame):
    for col in LABEL_COLS:
        df[col] = df[col].astype(np.float32)
    return df

def convert_onehot_to_multiclass(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convertit :
      K0,K1,K2 -> k_label in {0,1,2}
      N0,N1,N2 -> n_label in {0,1,2}
      P0,P1    -> p_label in {0,1}
    """
    df = df.copy()
    df["k_label"] = df[["K0", "K1", "K2"]].values.argmax(axis=1).astype(np.int32)
    df["n_label"] = df[["N0", "N1", "N2"]].values.argmax(axis=1).astype(np.int32)
    df["p_label"] = df[["P0", "P1"]].values.argmax(axis=1).astype(np.int32)
    return df

# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

print("=" * 70)
print("CHARGEMENT DES DONNÉES")
print("=" * 70)

train_df = pd.read_csv(TRAIN_CSV)
valid_df = pd.read_csv(VALID_CSV)
test_df  = pd.read_csv(TEST_CSV)

train_df = set_float_columns(train_df)
valid_df = set_float_columns(valid_df)
test_df  = set_float_columns(test_df)

train_df = convert_onehot_to_multiclass(train_df)
valid_df = convert_onehot_to_multiclass(valid_df)
test_df  = convert_onehot_to_multiclass(test_df)

print(f"Train: {len(train_df)} images")
print(f"Valid: {len(valid_df)} images")
print(f"Test : {len(test_df)} images")

# ============================================================
# DATA AUGMENTATION
# ============================================================

data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.08),
    layers.RandomZoom(0.10),
    layers.RandomTranslation(0.08, 0.08),
    layers.RandomContrast(0.08),
], name="data_augmentation")

def decode_and_resize(path, img_size=IMG_SIZE):
    img = tf.io.read_file(path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    img = tf.image.resize(img, [img_size, img_size])
    img = tf.cast(img, tf.float32)
    img = preprocess_input(img)
    return img

def make_dataset(df: pd.DataFrame, folder: str, training: bool) -> tf.data.Dataset:
    paths = [os.path.join(folder, fname) for fname in df["filename"].tolist()]
    y_k = df["k_label"].values.astype(np.int32)
    y_n = df["n_label"].values.astype(np.int32)
    y_p = df["p_label"].values.astype(np.int32)

    ds = tf.data.Dataset.from_tensor_slices((
        paths,
        y_k,
        y_n,
        y_p
    ))

    if training:
        ds = ds.shuffle(buffer_size=len(df), seed=SEED)

    def _load(path, yk, yn, yp):
        img = decode_and_resize(path)
        y = {
            "k_output": yk,
            "n_output": yn,
            "p_output": yp
        }
        return img, y

    ds = ds.map(_load, num_parallel_calls=tf.data.AUTOTUNE)

    if training:
        ds = ds.map(
            lambda x, y: (data_augmentation(x, training=True), y),
            num_parallel_calls=tf.data.AUTOTUNE
        )

    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds

train_ds = make_dataset(train_df, TRAIN_FOLDER, training=True)
valid_ds = make_dataset(valid_df, VALID_FOLDER, training=False)
test_ds  = make_dataset(test_df, TEST_FOLDER, training=False)

# ============================================================
# MODÈLE MULTITASK
# ============================================================

def build_multitask_model(img_size=IMG_SIZE):
    base = EfficientNetV2L(
        weights="imagenet",
        include_top=False,
        input_shape=(img_size, img_size, 3)
    )
    base.trainable = False

    x = layers.GlobalAveragePooling2D()(base.output)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.30)(x)
    x = layers.Dense(256, activation="relu")(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.20)(x)

    k_output = layers.Dense(3, activation="softmax", name="k_output")(x)
    n_output = layers.Dense(3, activation="softmax", name="n_output")(x)
    p_output = layers.Dense(2, activation="softmax", name="p_output")(x)

    model = Model(
        inputs=base.input,
        outputs={
            "k_output": k_output,
            "n_output": n_output,
            "p_output": p_output
        },
        name="NPK_Multitask_EfficientNetV2L_V2"
    )
    return model, base

model, base = build_multitask_model()

# ============================================================
# COMPILATION
# ============================================================

def compile_model(model, lr):
    model.compile(
        optimizer=optimizers.Adam(learning_rate=lr),
        loss={
            "k_output": "sparse_categorical_crossentropy",
            "n_output": "sparse_categorical_crossentropy",
            "p_output": "sparse_categorical_crossentropy",
        },
        loss_weights={
            "k_output": 1.0,
            "n_output": 1.0,
            "p_output": 1.15
        },
        metrics={
            "k_output": ["accuracy"],
            "n_output": ["accuracy"],
            "p_output": ["accuracy"],
        }
    )

# ============================================================
# CALLBACKS
# ============================================================

checkpoint_path = os.path.join(SAVE_DIR, "best_multitask_model.keras")

cb_list = [
    callbacks.EarlyStopping(
        monitor="val_loss",
        patience=4,
        restore_best_weights=True,
        verbose=1
    ),
    callbacks.ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=2,
        min_lr=1e-7,
        verbose=1
    ),
    callbacks.ModelCheckpoint(
        filepath=checkpoint_path,
        monitor="val_loss",
        save_best_only=True,
        verbose=1
    )
]

# ============================================================
# PHASE 1 : TRANSFER LEARNING
# ============================================================

print("\n" + "=" * 70)
print("PHASE 1 : TRANSFER LEARNING")
print("=" * 70)

compile_model(model, lr=2e-4)

history1 = model.fit(
    train_ds,
    validation_data=valid_ds,
    epochs=EPOCHS_PHASE1,
    callbacks=cb_list,
    verbose=1
)

# ============================================================
# PHASE 2 : FINE-TUNING
# ============================================================

print("\n" + "=" * 70)
print("PHASE 2 : FINE-TUNING")
print("=" * 70)

base.trainable = True

# Débloquer davantage de couches
for layer in base.layers[:-100]:
    layer.trainable = False

compile_model(model, lr=5e-6)

history2 = model.fit(
    train_ds,
    validation_data=valid_ds,
    epochs=EPOCHS_PHASE2,
    callbacks=cb_list,
    verbose=1
)

# ============================================================
# SAUVEGARDE DES HISTORIQUES
# ============================================================

ensure_dir(os.path.join(SAVE_DIR, "histories"))
save_json(history1.history, os.path.join(SAVE_DIR, "histories", "history_phase1.json"))
save_json(history2.history, os.path.join(SAVE_DIR, "histories", "history_phase2.json"))

# ============================================================
# COURBES
# ============================================================

def plot_history_two_phases(history1, history2, save_dir):
    h1 = history1.history
    h2 = history2.history

    def concat_metric(metric):
        return list(h1.get(metric, [])) + list(h2.get(metric, []))

    total_epochs = list(range(1, len(concat_metric("loss")) + 1))

    plt.figure(figsize=(14, 10))

    plt.subplot(2, 2, 1)
    plt.plot(total_epochs, concat_metric("loss"), label="Train Loss")
    plt.plot(total_epochs, concat_metric("val_loss"), label="Val Loss")
    plt.title("Loss globale")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()

    plt.subplot(2, 2, 2)
    plt.plot(total_epochs, concat_metric("k_output_accuracy"), label="Train K Acc")
    plt.plot(total_epochs, concat_metric("val_k_output_accuracy"), label="Val K Acc")
    plt.title("Accuracy sortie K")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()

    plt.subplot(2, 2, 3)
    plt.plot(total_epochs, concat_metric("n_output_accuracy"), label="Train N Acc")
    plt.plot(total_epochs, concat_metric("val_n_output_accuracy"), label="Val N Acc")
    plt.title("Accuracy sortie N")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()

    plt.subplot(2, 2, 4)
    plt.plot(total_epochs, concat_metric("p_output_accuracy"), label="Train P Acc")
    plt.plot(total_epochs, concat_metric("val_p_output_accuracy"), label="Val P Acc")
    plt.title("Accuracy sortie P")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "training_curves_multitask.png"), dpi=150)
    plt.close()

plot_history_two_phases(history1, history2, SAVE_DIR)

# ============================================================
# ÉVALUATION
# ============================================================

best_model = tf.keras.models.load_model(checkpoint_path)

def prepare_true_labels(df: pd.DataFrame):
    yk = df["k_label"].values.astype(np.int32)
    yn = df["n_label"].values.astype(np.int32)
    yp = df["p_label"].values.astype(np.int32)
    return yk, yn, yp

def make_inference_dataset(df: pd.DataFrame, folder: str) -> tf.data.Dataset:
    paths = [os.path.join(folder, fname) for fname in df["filename"].tolist()]
    ds = tf.data.Dataset.from_tensor_slices(paths)

    def _load(path):
        img = decode_and_resize(path)
        return img

    ds = ds.map(_load, num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return ds

def evaluate_multitask_model(model, df, folder, dataset_name: str):
    print(f"\nÉvaluation sur {dataset_name}...")

    infer_ds = make_inference_dataset(df, folder)
    preds = model.predict(infer_ds, verbose=1)

    if isinstance(preds, dict):
        pred_k = preds["k_output"]
        pred_n = preds["n_output"]
        pred_p = preds["p_output"]
    elif isinstance(preds, (list, tuple)) and len(preds) == 3:
        pred_k, pred_n, pred_p = preds
    else:
        raise ValueError(f"Format inattendu pour predict(): {type(preds)}")

    pred_k = np.asarray(pred_k)
    pred_n = np.asarray(pred_n)
    pred_p = np.asarray(pred_p)

    print("Shapes des prédictions :")
    print("K :", pred_k.shape)
    print("N :", pred_n.shape)
    print("P :", pred_p.shape)

    if pred_k.ndim != 2 or pred_k.shape[1] != 3:
        raise ValueError(f"Sortie K invalide : {pred_k.shape}")
    if pred_n.ndim != 2 or pred_n.shape[1] != 3:
        raise ValueError(f"Sortie N invalide : {pred_n.shape}")
    if pred_p.ndim != 2 or pred_p.shape[1] != 2:
        raise ValueError(f"Sortie P invalide : {pred_p.shape}")

    yk_true, yn_true, yp_true = prepare_true_labels(df)

    yk_pred = np.argmax(pred_k, axis=1)
    yn_pred = np.argmax(pred_n, axis=1)
    yp_pred = np.argmax(pred_p, axis=1)

    # Reconstruction binaire des 8 labels
    y_true_bin = df[LABEL_COLS].values.astype(np.int32)
    y_pred_bin = np.zeros_like(y_true_bin)

    for i in range(len(df)):
        y_pred_bin[i, yk_pred[i]] = 1
        y_pred_bin[i, 3 + yn_pred[i]] = 1
        y_pred_bin[i, 6 + yp_pred[i]] = 1

    hamming_acc = np.mean(y_true_bin == y_pred_bin)

    k_acc = accuracy_score(yk_true, yk_pred)
    n_acc = accuracy_score(yn_true, yn_pred)
    p_acc = accuracy_score(yp_true, yp_pred)

    k_f1 = f1_score(yk_true, yk_pred, average="macro")
    n_f1 = f1_score(yn_true, yn_pred, average="macro")
    p_f1 = f1_score(yp_true, yp_pred, average="macro")

    per_label_accuracy = {
        label: float(np.mean(y_true_bin[:, i] == y_pred_bin[:, i]))
        for i, label in enumerate(LABEL_COLS)
    }

    results = {
        "dataset": dataset_name,
        "hamming_accuracy": float(hamming_acc),
        "per_nutrient_accuracy": {
            "K_accuracy": float(k_acc),
            "N_accuracy": float(n_acc),
            "P_accuracy": float(p_acc),
        },
        "per_nutrient_macro_f1": {
            "K_macro_f1": float(k_f1),
            "N_macro_f1": float(n_f1),
            "P_macro_f1": float(p_f1),
        },
        "per_label_accuracy": per_label_accuracy,
        "classification_report": {
            "K": classification_report(yk_true, yk_pred, output_dict=True, zero_division=0),
            "N": classification_report(yn_true, yn_pred, output_dict=True, zero_division=0),
            "P": classification_report(yp_true, yp_pred, output_dict=True, zero_division=0),
        },
        "confusion_matrices": {
            "K": confusion_matrix(yk_true, yk_pred).tolist(),
            "N": confusion_matrix(yn_true, yn_pred).tolist(),
            "P": confusion_matrix(yp_true, yp_pred).tolist(),
        }
    }

    save_json(results, os.path.join(SAVE_DIR, f"results_{dataset_name}_multitask.json"))

    pred_df = df[["filename"]].copy()

    pred_df["K_true"] = yk_true
    pred_df["K_pred"] = yk_pred
    pred_df["K_conf"] = np.max(pred_k, axis=1)

    pred_df["N_true"] = yn_true
    pred_df["N_pred"] = yn_pred
    pred_df["N_conf"] = np.max(pred_n, axis=1)

    pred_df["P_true"] = yp_true
    pred_df["P_pred"] = yp_pred
    pred_df["P_conf"] = np.max(pred_p, axis=1)

    for i in range(3):
        pred_df[f"K_prob_{i}"] = pred_k[:, i]
        pred_df[f"N_prob_{i}"] = pred_n[:, i]

    for i in range(2):
        pred_df[f"P_prob_{i}"] = pred_p[:, i]

    pred_df.to_csv(
        os.path.join(SAVE_DIR, f"{dataset_name}_predictions_multitask.csv"),
        index=False
    )

    print(f"Hamming Accuracy ({dataset_name}) : {hamming_acc:.4f}")
    print(f"K Accuracy : {k_acc:.4f} | K Macro-F1 : {k_f1:.4f}")
    print(f"N Accuracy : {n_acc:.4f} | N Macro-F1 : {n_f1:.4f}")
    print(f"P Accuracy : {p_acc:.4f} | P Macro-F1 : {p_f1:.4f}")

    return results

valid_results = evaluate_multitask_model(best_model, valid_df, VALID_FOLDER, "valid")
test_results = evaluate_multitask_model(best_model, test_df, TEST_FOLDER, "test")

# ============================================================
# BARPLOTS FINAUX
# ============================================================

def plot_final_summary(results, save_dir, dataset_name):
    labels_list = list(results["per_label_accuracy"].keys())
    accuracies = list(results["per_label_accuracy"].values())

    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels_list, accuracies, color="skyblue", edgecolor="navy")
    plt.ylim(0, 1.0)
    plt.ylabel("Accuracy")
    plt.title(f"Accuracy par label - {dataset_name} - multitask v2")
    plt.axhline(
        y=results["hamming_accuracy"],
        color="red",
        linestyle="--",
        label=f"Hamming Accuracy: {results['hamming_accuracy']:.3f}"
    )
    plt.legend()

    for bar, acc in zip(bars, accuracies):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"{acc:.3f}",
            ha="center",
            va="bottom"
        )

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f"final_accuracy_summary_{dataset_name}_multitask.png"), dpi=150)
    plt.close()

plot_final_summary(valid_results, SAVE_DIR, "valid")
plot_final_summary(test_results, SAVE_DIR, "test")

# ============================================================
# FIN
# ============================================================

print("\n" + "=" * 70)
print("ENTRAÎNEMENT ET ÉVALUATION TERMINÉS")
print("=" * 70)
print(f"Validation Hamming Accuracy : {valid_results['hamming_accuracy']:.4f}")
print(f"Test Hamming Accuracy       : {test_results['hamming_accuracy']:.4f}")
print(f"Modèle sauvegardé dans      : {checkpoint_path}")
print(f"Dossier de sortie           : {SAVE_DIR}")