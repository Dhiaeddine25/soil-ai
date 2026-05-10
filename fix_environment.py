# fix_environment.py
import subprocess
import sys

def fix_numpy_tf_conflict():
    """Résout le conflit entre NumPy 2.x et TensorFlow"""
    
    packages_to_uninstall = [
        'tensorflow', 'tensorflow-intel', 'keras', 
        'numpy', 'protobuf', 'pillow'
    ]
    
    print("📦 Désinstallation des packages problématiques...")
    for package in packages_to_uninstall:
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', package, '-y'])
    
    print("🧹 Nettoyage du cache pip...")
    subprocess.run([sys.executable, '-m', 'pip', 'cache', 'purge'])
    
    print("📥 Installation des versions compatibles...")
    
    # Installer dans le bon ordre
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'numpy==1.24.3'])
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'tensorflow==2.13.0'])
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'keras==2.13.1'])
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'protobuf==3.20.3'])
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pillow==10.0.0'])
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'typing-extensions==4.5.0'])
    
    print("📥 Installation des autres dépendances...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 
                   'pandas', 'scikit-learn', 'opencv-python', 
                   'scikit-image', 'matplotlib', 'albumentations'])
    
    print("✅ Vérification des versions...")
    subprocess.run([sys.executable, '-c', 
                   '"import numpy; print(f\'NumPy version: {numpy.__version__}\'); import tensorflow; print(f\'TensorFlow version: {tensorflow.__version__}\')"'])

if __name__ == "__main__":
    fix_numpy_tf_conflict()