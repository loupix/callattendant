#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Test LLM TTS Engine - Modèles modernes
# Teste XTTS-v2, ChatTTS, Dia, Kokoro

import os
import sys
import time
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_llm_tts_installation():
    """Teste l'installation des dépendances LLM TTS"""
    print("🔍 Test installation LLM TTS...")
    
    required_packages = [
        'transformers',
        'torch', 
        'torchaudio',
        'soundfile',
        'huggingface_hub'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} installé")
        except ImportError:
            print(f"❌ {package} manquant")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 Installez les packages manquants:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def test_llm_tts_engine():
    """Teste le moteur LLM TTS"""
    print(f"\n🎤 Test LLM TTS Engine...")
    
    try:
        from callattendant.messaging.llm_tts_engine import LLMTTSEngine
        
        # Configuration de test
        config = {
            'TTS_ENABLED': True,
            'TTS_ENGINE': 'xtts-v2',
            'TTS_LANGUAGE': 'fr',
            'TTS_CACHE_DIR': 'data/tts_cache',
            'TTS_MODEL_DIR': 'data/tts_models'
        }
        
        # Initialiser le moteur
        engine = LLMTTSEngine(config)
        print("✅ Moteur LLM TTS initialisé")
        
        # Afficher les modèles disponibles
        models = engine.get_available_models()
        print(f"\n🎯 Modèles disponibles:")
        for model_id, model_info in models.items():
            print(f"   {model_id}: {model_info['name']}")
            print(f"      Description: {model_info['description']}")
            print(f"      Langues: {', '.join(model_info['languages'])}")
            print(f"      Taille: {model_info['size']}")
            print(f"      Licence: {model_info['license']}")
            print()
        
        # Afficher les modèles de personnes
        person_models = engine.get_available_person_models()
        print(f"👥 Modèles de personnes pour {config['TTS_ENGINE']}:")
        for person, config_person in person_models.items():
            print(f"   {person}: {config_person}")
        
        return engine
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

def test_model_download(engine):
    """Teste le téléchargement des modèles"""
    print(f"\n📥 Test téléchargement modèles...")
    
    if not engine:
        print("❌ Moteur non initialisé")
        return
    
    try:
        # Test avec différents moteurs
        engines_to_test = ['xtts-v2', 'chattts', 'dia', 'kokoro']
        
        for engine_name in engines_to_test:
            print(f"\n🔧 Test {engine_name}:")
            
            # Changer le moteur
            engine.engine = engine_name
            
            # Initialiser le nouveau moteur
            if engine_name == 'xtts-v2':
                engine._init_xtts_v2()
            elif engine_name == 'chattts':
                engine._init_chattts()
            elif engine_name == 'dia':
                engine._init_dia()
            elif engine_name == 'kokoro':
                engine._init_kokoro()
            
            # Vérifier si le modèle existe
            model_path = os.path.join(engine.model_dir, engine_name)
            if os.path.exists(model_path):
                print(f"   ✅ Modèle {engine_name} trouvé")
            else:
                print(f"   ⚠️ Modèle {engine_name} non trouvé (téléchargement nécessaire)")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_synthesis(engine):
    """Teste la synthèse vocale"""
    print(f"\n🎵 Test synthèse vocale...")
    
    if not engine:
        print("❌ Moteur non initialisé")
        return
    
    test_texts = [
        "Bonjour, je suis votre assistant vocal.",
        "Votre appel est important pour nous.",
        "Laissez un message après le bip sonore."
    ]
    
    try:
        for i, text in enumerate(test_texts):
            print(f"\n🎤 Test {i+1}: '{text}'")
            
            # Test avec moteur actuel
            result = engine.synthesize(text)
            if result:
                print(f"   ✅ Synthèse réussie: {result}")
            else:
                print(f"   ❌ Échec de synthèse")
            
            time.sleep(1)
        
        # Test avec modèles de personnes
        person_models = engine.get_available_person_models()
        if person_models:
            print(f"\n👥 Test avec modèles de personnes:")
            for person in list(person_models.keys())[:2]:  # Test les 2 premiers
                print(f"   Test {person}:")
                result = engine.synthesize("Test avec modèle de personne", person)
                if result:
                    print(f"      ✅ Réussi: {result}")
                else:
                    print(f"      ❌ Échec")
                time.sleep(1)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_performance(engine):
    """Teste les performances"""
    print(f"\n⚡ Test performances...")
    
    if not engine:
        print("❌ Moteur non initialisé")
        return
    
    test_text = "Test de performance pour évaluer la vitesse de synthèse."
    
    try:
        # Test de vitesse
        start_time = time.time()
        result = engine.synthesize(test_text)
        end_time = time.time()
        
        if result:
            duration = end_time - start_time
            print(f"   ⏱️ Temps de synthèse: {duration:.2f} secondes")
            
            # Vérifier la taille du fichier
            if os.path.exists(result):
                size = os.path.getsize(result)
                print(f"   📁 Taille fichier: {size} bytes")
            
            # Test cache
            print(f"   🔄 Test cache...")
            start_time = time.time()
            result_cached = engine.synthesize(test_text)
            end_time = time.time()
            
            if result_cached:
                duration_cached = end_time - start_time
                print(f"   ⚡ Temps avec cache: {duration_cached:.2f} secondes")
                speedup = duration / duration_cached if duration_cached > 0 else 0
                print(f"   🚀 Accélération: {speedup:.1f}x")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Fonction principale"""
    print("🎯 Test LLM TTS Engine - Modèles modernes")
    print("=" * 60)
    
    # Test installation
    if not test_llm_tts_installation():
        print("\n❌ Installation incomplète!")
        sys.exit(1)
    
    # Test moteur
    engine = test_llm_tts_engine()
    if not engine:
        print("\n❌ Impossible d'initialiser le moteur!")
        sys.exit(1)
    
    # Test téléchargement modèles
    test_model_download(engine)
    
    # Test synthèse
    test_synthesis(engine)
    
    # Test performances
    test_performance(engine)
    
    print(f"\n🎉 Tests terminés!")
    print(f"💡 Modèles disponibles dans: {engine.model_dir}")
    print(f"💾 Cache dans: {engine.cache_dir}")
    print(f"📚 Consultez la documentation pour l'implémentation complète")

if __name__ == "__main__":
    main() 