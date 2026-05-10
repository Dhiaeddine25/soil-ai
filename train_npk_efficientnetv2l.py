# ====================================================
# train_npk_efficientnetv2l.py
# Entraînement EfficientNetV2L + graphique unique loss/accuracy
# avec vérification des historiques
# ====================================================

import os
import json
import gc
import time
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, optimizers, callbacks
from tensorflow.keras.applications.efficientnet_v2 import EfficientNetV2L, preprocess_input
from sklearn.metrics import accuracy_score, f1_score
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt

# ====================================================
# CONFIGURATION - À ADAPTER
# ====================================================
DATA_PATH = r"C:\Users\surface pro 7\Desktop\npk_90percent\data"
SAVE_DIR = r"C:\Users\surface pro 7\Desktop\npk_90percent\npk_models_efficientnetv2l"
os.makedirs(SAVE_DIR, exist_ok=True)

IMG_SIZE = 224
BATCH_SIZE = 8
EPOCHS_PHASE1 = 5
EPOCHS_PHASE2 = 5

labels = ['K0', 'K1', 'K2', 'N0', 'N1', 'N2', 'P0', 'P1']

# ====================================================
# CHARGEMENT DES DONNÉES
# ====================================================
print("=" * 60)
print("📥 CHARGEMENT DES DONNÉES")
print("=" * 60)

train_df = pd.read_csv(os.path.join(DATA_PATH, "_classesTR.csv"))
valid_df = pd.read_csv(os.path.join(DATA_PATH, "_classesv.csv"))
test_df = pd.read_csv(os.path.join(DATA_PATH, "_classes.csv"))

for df in [train_df, valid_df, test_df]:
    for col in labels:
        df[col] = df[col].astype(np.float32)

print(f"Train: {len(train_df)} images")
print(f"Valid: {len(valid_df)} images")
print(f"Test: {len(test_df)} images")

# ====================================================
# DATA AUGMENTATION (avec preprocessing EfficientNetV2)
# ====================================================
def get_augmentation():
    return tf.keras.preprocessing.image.ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=45,
        width_shift_range=0.15,
        height_shift_range=0.15,
        shear_range=0.15,
        zoom_range=0.25,
        horizontal_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode='reflect'
    )

val_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
    preprocessing_function=preprocess_input
)

def create_generator(df, label, folder, augment=False):
    if augment:
        gen = get_augmentation()
    else:
        gen = val_datagen
    return gen.flow_from_dataframe(
        df,
        directory=os.path.join(DATA_PATH, folder),
        x_col='filename',
        y_col=label,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='raw',
        shuffle=augment,
        seed=42
    )

# ====================================================
# CONSTRUCTION DU MODÈLE (EfficientNetV2L)
# ====================================================
def build_efficientnetv2l():
    base = EfficientNetV2L(
        weights='imagenet',
        include_top=False,
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )
    base.trainable = False
    x = layers.GlobalAveragePooling2D()(base.output)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(256, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.4)(x)
    output = layers.Dense(1, activation='sigmoid')(x)
    return tf.keras.Model(base.input, output), base

# ====================================================
# FONCTIONS UTILITAIRES
# ====================================================
def get_class_weights(y_train):
    weights = compute_class_weight('balanced', classes=np.array([0, 1]), y=y_train)
    return {0: weights[0], 1: weights[1]}

def find_best_threshold(y_true, y_prob):
    best_t, best_f1 = 0.5, 0
    for t in np.arange(0.1, 0.9, 0.02):
        y_pred = (y_prob > t).astype(int)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_t = t
    return best_t

def plot_training_history(history1, history2, label, save_dir):
    """Sauvegarde les courbes individuelles et les historiques JSON"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(f'EfficientNetV2L - {label}', fontsize=14)

    # Phase 1
    epochs1 = range(1, len(history1.history['loss']) + 1)
    axes[0,0].plot(epochs1, history1.history['loss'], 'b-', label='Train Loss')
    axes[0,0].plot(epochs1, history1.history['val_loss'], 'r-', label='Val Loss')
    axes[0,0].set_title('Phase 1 - Loss')
    axes[0,0].set_xlabel('Epochs')
    axes[0,0].legend()

    axes[1,0].plot(epochs1, history1.history['accuracy'], 'b-', label='Train Accuracy')
    axes[1,0].plot(epochs1, history1.history['val_accuracy'], 'r-', label='Val Accuracy')
    axes[1,0].set_title('Phase 1 - Accuracy')
    axes[1,0].set_xlabel('Epochs')
    axes[1,0].legend()

    # Phase 2
    epochs2 = range(1, len(history2.history['loss']) + 1)
    axes[0,1].plot(epochs2, history2.history['loss'], 'b-', label='Train Loss')
    axes[0,1].plot(epochs2, history2.history['val_loss'], 'r-', label='Val Loss')
    axes[0,1].set_title('Phase 2 - Loss')
    axes[0,1].set_xlabel('Epochs')
    axes[0,1].legend()

    axes[1,1].plot(epochs2, history2.history['accuracy'], 'b-', label='Train Accuracy')
    axes[1,1].plot(epochs2, history2.history['val_accuracy'], 'r-', label='Val Accuracy')
    axes[1,1].set_title('Phase 2 - Accuracy')
    axes[1,1].set_xlabel('Epochs')
    axes[1,1].legend()

    plt.tight_layout()
    plot_dir = os.path.join(save_dir, 'training_plots', label)
    os.makedirs(plot_dir, exist_ok=True)
    plt.savefig(os.path.join(plot_dir, 'efficientnetv2l_training.png'), dpi=150)
    plt.close()

    # Sauvegarde des historiques pour les graphiques combinés
    hist_dir = os.path.join(save_dir, 'histories', label)
    os.makedirs(hist_dir, exist_ok=True)
    with open(os.path.join(hist_dir, 'history_phase1.json'), 'w') as f:
        json.dump(history1.history, f, indent=2)
    with open(os.path.join(hist_dir, 'history_phase2.json'), 'w') as f:
        json.dump(history2.history, f, indent=2)

def plot_all_metrics_combined(save_dir):
    """
    Crée une figure avec deux sous‑graphiques (Loss et Accuracy) si des données existent.
    """
    # Vérifier qu'au moins un label a des historiques
    has_data = False
    for label in labels:
        hist_file1 = os.path.join(save_dir, 'histories', label, 'history_phase1.json')
        hist_file2 = os.path.join(save_dir, 'histories', label, 'history_phase2.json')
        if os.path.exists(hist_file1) and os.path.exists(hist_file2):
            has_data = True
            break

    if not has_data:
        print("\n⚠️  Aucune donnée d'historique trouvée. Les graphiques ne peuvent pas être générés.")
        print("   Pour générer les graphiques, vous devez entraîner les modèles.")
        print("   Si des modèles existent déjà, supprimez les fichiers 'seuil_*.json' dans le dossier de sauvegarde et relancez le script.\n")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    colors = plt.cm.tab10(np.linspace(0, 1, len(labels)))

    for idx, label in enumerate(labels):
        hist_file1 = os.path.join(save_dir, 'histories', label, 'history_phase1.json')
        hist_file2 = os.path.join(save_dir, 'histories', label, 'history_phase2.json')

        if not os.path.exists(hist_file1) or not os.path.exists(hist_file2):
            print(f"⚠️  Historiques manquants pour {label}, ignoré.")
            continue

        with open(hist_file1, 'r') as f:
            h1 = json.load(f)
        with open(hist_file2, 'r') as f:
            h2 = json.load(f)

        # Vérifier que les clés existent
        if 'loss' not in h1 or 'val_loss' not in h1 or 'accuracy' not in h1 or 'val_accuracy' not in h1:
            print(f"⚠️  Format d'historique incorrect pour {label} (phase1), ignoré.")
            continue
        if 'loss' not in h2 or 'val_loss' not in h2 or 'accuracy' not in h2 or 'val_accuracy' not in h2:
            print(f"⚠️  Format d'historique incorrect pour {label} (phase2), ignoré.")
            continue

        # Concaténation des epochs
        epochs1 = range(1, len(h1['loss']) + 1)
        epochs2_start = len(h1['loss']) + 1
        epochs2 = range(epochs2_start, epochs2_start + len(h2['loss']))

        # Loss
        ax1.plot(epochs1, h1['loss'], color=colors[idx], linestyle='-', label=f'{label} Train')
        ax1.plot(epochs1, h1['val_loss'], color=colors[idx], linestyle='--', label=f'{label} Val')
        ax1.plot(epochs2, h2['loss'], color=colors[idx], linestyle='-')
        ax1.plot(epochs2, h2['val_loss'], color=colors[idx], linestyle='--')

        # Accuracy
        ax2.plot(epochs1, h1['accuracy'], color=colors[idx], linestyle='-', label=f'{label} Train')
        ax2.plot(epochs1, h1['val_accuracy'], color=colors[idx], linestyle='--', label=f'{label} Val')
        ax2.plot(epochs2, h2['accuracy'], color=colors[idx], linestyle='-')
        ax2.plot(epochs2, h2['val_accuracy'], color=colors[idx], linestyle='--')

    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Évolution de la Loss (Train vs Validation)')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')

    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.set_title('Évolution de l\'Accuracy (Train vs Validation)')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')

    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'all_metrics_combined.png'), dpi=150)
    plt.close()
    print(f"📊 Graphique combiné (loss et accuracy) sauvegardé : {os.path.join(save_dir, 'all_metrics_combined.png')}")

def plot_final_summary(results, save_dir, dataset='test'):
    """Barplot de l'accuracy par label"""
    labels_list = list(results['per_label_accuracy'].keys())
    accuracies = list(results['per_label_accuracy'].values())

    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels_list, accuracies, color='skyblue', edgecolor='navy')
    plt.ylim(0, 1)
    plt.ylabel('Accuracy')
    plt.title(f'Accuracy par label sur l\'ensemble de {dataset} - EfficientNetV2L')
    plt.axhline(y=results['hamming_accuracy'], color='red', linestyle='--', label=f"Hamming Accuracy: {results['hamming_accuracy']:.3f}")
    plt.legend()

    for bar, acc in zip(bars, accuracies):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, f'{acc:.3f}', ha='center', va='bottom')

    plt.tight_layout()
    filename = f'final_accuracy_summary_{dataset}.png'
    plt.savefig(os.path.join(save_dir, filename), dpi=150)
    plt.close()
    print(f"📊 Graphique récapitulatif ({dataset}) sauvegardé : {os.path.join(save_dir, filename)}")

# ====================================================
# ENTRAÎNEMENT POUR UN LABEL
# ====================================================
def train_single_model(train_df, valid_df, label):
    print(f"\n🎯 Entraînement EfficientNetV2L pour {label}")
    model, base = build_efficientnetv2l()

    y_train = train_df[label].astype(int).values
    class_weight = get_class_weights(y_train)
    print(f"  📊 Poids: classe0={class_weight[0]:.2f}, classe1={class_weight[1]:.2f}")

    train_gen = create_generator(train_df, label, 'train', augment=True)
    valid_gen = create_generator(valid_df, label, 'valid', augment=False)

    # Phase 1
    print("  Phase 1: Transfer Learning...")
    model.compile(optimizer=optimizers.Adam(3e-4),
                  loss='binary_crossentropy',
                  metrics=['accuracy', tf.keras.metrics.AUC(name='auc')])
    history1 = model.fit(
        train_gen,
        validation_data=valid_gen,
        epochs=EPOCHS_PHASE1,
        class_weight=class_weight,
        callbacks=[callbacks.EarlyStopping(monitor='val_auc', patience=2, restore_best_weights=True, mode='max')],
        verbose=1
    )

    # Phase 2
    print("  Phase 2: Fine-tuning...")
    base.trainable = True
    for layer in base.layers[:-60]:
        layer.trainable = False
    model.compile(optimizer=optimizers.Adam(8e-6),
                  loss='binary_crossentropy',
                  metrics=['accuracy', tf.keras.metrics.AUC(name='auc')])
    history2 = model.fit(
        train_gen,
        validation_data=valid_gen,
        epochs=EPOCHS_PHASE2,
        class_weight=class_weight,
        callbacks=[callbacks.EarlyStopping(monitor='val_auc', patience=2, restore_best_weights=True, mode='max')],
        verbose=1
    )

    # Seuil optimal sur validation
    valid_gen_pred = val_datagen.flow_from_dataframe(
        valid_df,
        directory=os.path.join(DATA_PATH, 'valid'),
        x_col='filename',
        y_col=None,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        shuffle=False,
        class_mode=None,
        seed=42
    )
    val_probs = model.predict(valid_gen_pred, verbose=0).ravel()
    best_t = find_best_threshold(valid_df[label].values, val_probs)
    val_pred = (val_probs > best_t).astype(int)
    val_f1 = f1_score(valid_df[label].values, val_pred, zero_division=0)
    val_acc = accuracy_score(valid_df[label].values, val_pred)
    print(f"  ✅ Seuil: {best_t:.3f}, F1: {val_f1:.4f}, Acc: {val_acc:.4f}")

    # Sauvegarde des courbes et historiques
    plot_training_history(history1, history2, label, SAVE_DIR)

    return model, best_t, val_f1

# ====================================================
# ENTRAÎNEMENT POUR TOUS LES LABELS
# ====================================================
def train_all_labels(train_df, valid_df):
    print(f"\n{'='*60}\n🏆 ENTRAINEMENT POUR TOUS LES LABELS (EfficientNetV2L)\n{'='*60}")
    thresholds = {}

    for label in labels:
        print(f"\n--- Début de l'entraînement pour {label} ---")
        seuil_fichier = os.path.join(SAVE_DIR, f"seuil_{label}.json")
        if os.path.exists(seuil_fichier):
            with open(seuil_fichier, 'r') as f:
                thresholds[label] = json.load(f)['seuil']                                                                                                           
            print(f"✅ {label} déjà entraîné, seuil = {thresholds[label]:.3f}")
    :!         continue

        model, seuil, _ = train_single_model(train_df, valid_df, label)
        thresholds[label] = seuil

        label_dir = os.path.join(SAVE_DIR, label)
        os.makedirs(label_dir, exist_ok=True)
        model.save(os.path.join(label_dir, 'model.keras'))
        with open(seuil_fichier, 'w') as f:
            json.dump({'seuil': seuil}, f, indent=2)

        tf.keras.backend.clear_session()
        gc.collect()
        print(f"--- Fin de l'entraînement pour {label} ---")

    return thresholds

# ====================================================
# ÉVALUATION SUR UN ENSEMBLE DONNÉ
# ====================================================
def evaluate_on_dataset(df, thresholds, dataset_name='test'):
    print(f"\n🔮 Prédiction sur l'ensemble {dataset_name}...")
    gen = val_datagen.flow_from_dataframe(
        df,
        directory=os.path.join(DATA_PATH, dataset_name),
        x_col='filename',
        y_col=None,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        shuffle=False,
        class_mode=None,
        seed=42
    )

    final_predictions = np.zeros((len(df), len(labels)))
    for i, label in enumerate(labels):
        print(f"  {label}...")
        model = tf.keras.models.load_model(os.path.join(SAVE_DIR, label, 'model.keras'))
        preds = model.predict(gen, verbose=0).ravel()
        final_predictions[:, i] = preds

    thresholds_list = [thresholds[label] for label in labels]
    y_pred_binary = (final_predictions > np.array(thresholds_list)).astype(int)

    # Post-traitement (un seul niveau par nutriment)
    for i in range(len(df)):
        # K
        k = [0,1,2]
        if y_pred_binary[i,k].sum() > 1:
            probs = final_predictions[i,k]
            y_pred_binary[i,k] = 0
            y_pred_binary[i, k[np.argmax(probs)]] = 1
        elif y_pred_binary[i,k].sum() == 0:
            probs = final_predictions[i,k]
            y_pred_binary[i, k[np.argmax(probs)]] = 1

        # N
        n = [3,4,5]
        if y_pred_binary[i,n].sum() > 1:
            probs = final_predictions[i,n]
            y_pred_binary[i,n] = 0
            y_pred_binary[i, n[np.argmax(probs)]] = 1
        elif y_pred_binary[i,n].sum() == 0:
            probs = final_predictions[i,n]
            y_pred_binary[i, n[np.argmax(probs)]] = 1

        # P
        p = [6,7]
        if y_pred_binary[i,p].sum() > 1:
            probs = final_predictions[i,p]
            y_pred_binary[i,p] = 0
            y_pred_binary[i, p[np.argmax(probs)]] = 1
        elif y_pred_binary[i,p].sum() == 0:
            probs = final_predictions[i,p]
            y_pred_binary[i, p[np.argmax(probs)]] = 1

    y_true = df[labels].values
    hamming_acc = np.mean(y_true == y_pred_binary)

    print("\n" + "="*60)
    print(f"🏆 HAMMING ACCURACY SUR {dataset_name.upper()} : {hamming_acc:.4f} ({hamming_acc*100:.2f}%)")
    print("="*60)

    results = {
        'hamming_accuracy': float(hamming_acc),
        'thresholds': {label: float(thresholds[label]) for label in labels},
        'per_label_accuracy': {label: float(np.mean(y_true[:,i] == y_pred_binary[:,i])) for i, label in enumerate(labels)}
    }

    with open(os.path.join(SAVE_DIR, f'results_{dataset_name}.json'), 'w') as f:
        json.dump(results, f, indent=2)

    plot_final_summary(results, SAVE_DIR, dataset=dataset_name)

    # Sauvegarde des prédictions
    pred_df = df[['filename']].copy()
    for i, lbl in enumerate(labels):
        pred_df[f'{lbl}_pred'] = y_pred_binary[:, i]
        pred_df[f'{lbl}_prob'] = final_predictions[:, i]
    pred_df.to_csv(os.path.join(SAVE_DIR, f'{dataset_name}_predictions.csv'), index=False)

    return results

# ====================================================
# EXÉCUTION PRINCIPALE
# ====================================================
if __name__ == "__main__":
    print("\n🚀 DÉBUT DE L'ENTRAÎNEMENT AVEC EfficientNetV2L")
    start_time = time.time()

    thresholds = train_all_labels(train_df, valid_df)

    # Évaluations
    valid_results = evaluate_on_dataset(valid_df, thresholds, dataset_name='valid')
    test_results = evaluate_on_dataset(test_df, thresholds, dataset_name='test')

    # Graphique combiné loss + accuracy
    plot_all_metrics_combined(SAVE_DIR)

    print("\n" + "="*60)
    print("📊 RÉCAPITULATIF FINAL")
    print(f"   Validation Hamming Accuracy : {valid_results['hamming_accuracy']:.4f}")
    print(f"   Test Hamming Accuracy       : {test_results['hamming_accuracy']:.4f}")
    print("="*60)

    print(f"⏱️  Temps total : {(time.time()-start_time)/3600:.2f} heures")