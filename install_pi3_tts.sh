#!/bin/bash
# Installation TTS pour Raspberry Pi 3 + Python 3.9
# Script d'installation des dépendances LLM TTS

echo "🍓 Installation TTS pour Raspberry Pi 3 + Python 3.9"
echo "=================================================="

# Vérifier la version Python
echo "🐍 Vérification Python..."
python3 --version

# Mettre à jour le système
# echo "📦 Mise à jour du système..."
# sudo apt-get update
# sudo apt-get install -y python3-pip python3-dev python3-venv

# Installer les dépendances système pour audio
echo "🔊 Installation dépendances audio..."
sudo apt-get install -y espeak-ng sox ffmpeg portaudio19-dev
sudo apt-get install -y libasound2-dev libportaudio2 libportaudiocpp0
sudo apt-get install -y libsndfile1-dev libfftw3-dev libvorbis-dev

# Créer un environnement virtuel (optionnel mais recommandé)
# echo "🐍 Création environnement virtuel..."
# python3 -m venv tts_env
# source tts_env/bin/activate

# Installer PyTorch pour ARM + Python 3.9
echo "🔥 Installation PyTorch pour ARM + Python 3.9..."
pip3 install torch==1.13.1 torchaudio==0.13.1 --index-url https://download.pytorch.org/whl/cpu

# Installer les autres dépendances compatibles Python 3.9
echo "📚 Installation autres dépendances..."
pip3 install transformers>=4.20.0,<4.30.0
pip3 install soundfile>=0.10.0,<0.13.0
pip3 install huggingface-hub>=0.10.0,<0.17.0
pip3 install numpy>=1.21.0,<1.24.0
pip3 install scipy>=1.7.0,<1.10.0
pip3 install librosa>=0.9.0,<0.10.0

# Installer les dépendances TTS classiques
echo "🎤 Installation moteurs TTS classiques..."
pip3 install pyttsx3>=2.90
pip3 install gTTS>=2.3.1

# Installer packages audio supplémentaires
echo "🎵 Installation packages audio..."
pip3 install pyaudio>=0.2.11  # Capture audio
pip3 install webrtcvad>=2.0.10  # Détection voix
pip3 install resampy>=0.3.1  # Resampling audio
pip3 install audioread>=2.1.9  # Lecture audio
pip3 install pydub>=0.25.1  # Manipulation audio

# Installer packages pour traitement avancé
echo "🧠 Installation packages IA..."
pip3 install sentencepiece>=0.1.97  # Tokenization
pip3 install protobuf>=3.20.0,<4.0.0  # Sérialisation
pip3 install tokenizers>=0.12.0,<0.14.0  # Tokenization rapide

# Créer les répertoires nécessaires
echo "📁 Création répertoires..."
mkdir -p data/tts_cache
mkdir -p data/tts_models
mkdir -p data/static/audio
mkdir -p data/voice_samples

# Test d'installation
echo "🧪 Test d'installation..."
python3 -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python3 -c "import transformers; print('Transformers installé')"
python3 -c "import soundfile; print('Soundfile installé')"
python3 -c "import librosa; print('Librosa installé')"
python3 -c "import pyaudio; print('PyAudio installé')"

echo "✅ Installation terminée!"
echo "💡 Pour activer l'environnement: source tts_env/bin/activate"
echo "🎯 Pour tester: python3 tests/test_llm_tts.py"
echo "🔊 Pour tester audio: python3 -c \"import pyaudio; print('Audio OK')\"" 