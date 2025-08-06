#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  install_tts.py
#
#  Script d'installation du module TTS pour CallAttendant
#

import os
import sys
import subprocess
import importlib.util


def check_python_version():
    """Vérifie la version de Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou supérieur est requis")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} détecté")
    return True


def check_dependencies():
    """Vérifie les dépendances requises"""
    required_packages = [
        'torch',
        'torchaudio', 
        'TTS',
        'pydub',
        'simpleaudio'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing_packages.append(package)
        else:
            print(f"✅ {package} installé")
    
    return missing_packages


def install_package(package):
    """Installe un package via pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False


def install_tts_dependencies():
    """Installe les dépendances TTS"""
    print("\n📦 Installation des dépendances TTS...")
    
    packages = [
        "torch>=1.13.0",
        "torchaudio>=0.13.0", 
        "TTS>=0.22.0",
        "pydub>=0.25.1",
        "simpleaudio>=1.0.4"
    ]
    
    for package in packages:
        print(f"Installation de {package}...")
        if install_package(package):
            print(f"✅ {package} installé avec succès")
        else:
            print(f"❌ Échec de l'installation de {package}")
            return False
    
    return True


def create_directories():
    """Crée les dossiers nécessaires"""
    print("\n📁 Création des dossiers...")
    
    directories = [
        "resources/tts_audios",
        "examples",
        "docs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Dossier créé: {directory}")


def test_tts_installation():
    """Teste l'installation du TTS"""
    print("\n🧪 Test de l'installation TTS...")
    
    try:
        # Test d'import
        from TTS.api import TTS
        print("✅ Import TTS réussi")
        
        # Test d'initialisation (sans télécharger le modèle)
        print("⚠️  Test d'initialisation (peut prendre du temps au premier lancement)...")
        
        # Configuration de test
        config = {"DEBUG": True}
        
        # Import du module local
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        from messaging.tts_engine import TTSEngine
        
        # Test simple
        engine = TTSEngine(config)
        print("✅ Moteur TTS initialisé avec succès")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False


def show_next_steps():
    """Affiche les prochaines étapes"""
    print("\n🎉 Installation terminée !")
    print("\n📋 Prochaines étapes:")
    print("1. Testez le TTS avec: python messaging/tts_engine.py")
    print("2. Consultez les exemples: python examples/tts_example.py")
    print("3. Lisez la documentation: docs/TTS_INTEGRATION.md")
    print("\n💡 Conseils:")
    print("- Le premier lancement téléchargera le modèle XTTS v2 (1.5 GB)")
    print("- Utilisez le mode DEBUG pour voir les logs détaillés")
    print("- Les fichiers audio sont mis en cache automatiquement")


def main():
    """Fonction principale"""
    print("🚀 Installation du module TTS pour CallAttendant")
    print("=" * 50)
    
    # Vérifications préliminaires
    if not check_python_version():
        sys.exit(1)
    
    # Vérifier les dépendances existantes
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"\n❌ Packages manquants: {', '.join(missing_packages)}")
        install = input("Voulez-vous les installer maintenant ? (o/n): ").strip().lower()
        
        if install in ['o', 'oui', 'y', 'yes']:
            if not install_tts_dependencies():
                print("❌ Échec de l'installation des dépendances")
                sys.exit(1)
        else:
            print("❌ Installation annulée")
            sys.exit(1)
    else:
        print("✅ Toutes les dépendances sont installées")
    
    # Créer les dossiers
    create_directories()
    
    # Tester l'installation
    if test_tts_installation():
        show_next_steps()
    else:
        print("❌ Échec du test d'installation")
        sys.exit(1)


if __name__ == "__main__":
    main() 