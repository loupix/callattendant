#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Test complet des modèles LLM TTS
# Teste tous les modèles : XTTS-v2, ChatTTS, Dia, Kokoro, Chatterbox, MeloTTS, OpenVoice v2

import os
import sys
import time
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_all_models():
    """Teste tous les modèles LLM TTS"""
    print("🎯 Test complet des modèles LLM TTS")
    print("=" * 70)
    
    try:
        from callattendant.messaging.llm_tts_engine import LLMTTSEngine
        
        # Configuration de test
        config = {
            'TTS_ENABLED': True,
            'TTS_LANGUAGE': 'fr',
            'TTS_CACHE_DIR': 'data/tts_cache',
            'TTS_MODEL_DIR': 'data/tts_models'
        }
        
        # Initialiser le moteur
        engine = LLMTTSEngine(config)
        print("✅ Moteur LLM TTS initialisé")
        
        # Afficher tous les modèles disponibles
        models = engine.get_available_models()
        print(f"\n🎯 {len(models)} modèles disponibles:")
        
        for model_id, model_info in models.items():
            print(f"\n📦 {model_id.upper()}:")
            print(f"   Nom: {model_info['name']}")
            print(f"   Description: {model_info['description']}")
            print(f"   Langues: {', '.join(model_info['languages'][:5])}{'...' if len(model_info['languages']) > 5 else ''}")
            print(f"   Fonctionnalités: {', '.join(model_info['features'])}")
            print(f"   Licence: {model_info['license']}")
            print(f"   Taille: {model_info['size']}")
        
        # Test rapide de chaque modèle
        test_text = "Bonjour, test de synthèse vocale."
        
        for model_id in models.keys():
            print(f"\n🔧 Test {model_id.upper()}:")
            
            # Changer le moteur
            engine.engine = model_id
            
            # Afficher les modèles de personnes disponibles
            person_models = engine.get_available_person_models()
            if person_models:
                print(f"   👥 Modèles de personnes: {list(person_models.keys())}")
            
            # Test de synthèse
            try:
                start_time = time.time()
                result = engine.synthesize(test_text)
                end_time = time.time()
                
                if result:
                    duration = end_time - start_time
                    print(f"   ✅ Synthèse réussie en {duration:.2f}s")
                    
                    if os.path.exists(result):
                        size = os.path.getsize(result)
                        print(f"   📁 Fichier: {size} bytes")
                else:
                    print(f"   ❌ Échec de synthèse")
                    
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
            
            time.sleep(1)
        
        print(f"\n🎉 Tests terminés!")
        print(f"💡 Modèles dans: {engine.model_dir}")
        print(f"💾 Cache dans: {engine.cache_dir}")
        
        # Recommandations
        print(f"\n🏆 Recommandations:")
        print(f"   🥇 MeloTTS: Parfait pour français multilingue")
        print(f"   🥈 Chatterbox: Excellent pour émotions et qualité")
        print(f"   🥉 OpenVoice v2: Idéal pour voice cloning")
        print(f"   ⚡ Kokoro: Rapide et léger pour Pi3")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_specific_model(model_name):
    """Teste un modèle spécifique"""
    print(f"🎯 Test spécifique: {model_name.upper()}")
    print("=" * 50)
    
    try:
        from callattendant.messaging.llm_tts_engine import LLMTTSEngine
        
        config = {
            'TTS_ENABLED': True,
            'TTS_ENGINE': model_name,
            'TTS_LANGUAGE': 'fr',
            'TTS_CACHE_DIR': 'data/tts_cache',
            'TTS_MODEL_DIR': 'data/tts_models'
        }
        
        engine = LLMTTSEngine(config)
        
        # Informations du modèle
        model_info = engine.get_model_info()
        if model_info:
            print(f"📦 Modèle: {model_info['name']}")
            print(f"📝 Description: {model_info['description']}")
            print(f"🌍 Langues: {', '.join(model_info['languages'])}")
            print(f"⚙️ Fonctionnalités: {', '.join(model_info['features'])}")
            print(f"📄 Licence: {model_info['license']}")
            print(f"💾 Taille: {model_info['size']}")
        
        # Modèles de personnes
        person_models = engine.get_available_person_models()
        print(f"\n👥 Modèles de personnes:")
        for person, config_person in person_models.items():
            print(f"   {person}: {config_person}")
        
        # Tests de synthèse
        test_texts = [
            "Bonjour, je suis votre assistant vocal.",
            "Votre appel est important pour nous.",
            "Laissez un message après le bip sonore."
        ]
        
        for i, text in enumerate(test_texts):
            print(f"\n🎤 Test {i+1}: '{text}'")
            
            start_time = time.time()
            result = engine.synthesize(text)
            end_time = time.time()
            
            if result:
                duration = end_time - start_time
                print(f"   ✅ Réussi en {duration:.2f}s: {result}")
                
                if os.path.exists(result):
                    size = os.path.getsize(result)
                    print(f"   📁 Taille: {size} bytes")
            else:
                print(f"   ❌ Échec")
            
            time.sleep(1)
        
        # Test avec modèles de personnes
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

def main():
    """Fonction principale"""
    if len(sys.argv) > 1:
        # Test d'un modèle spécifique
        model_name = sys.argv[1]
        test_specific_model(model_name)
    else:
        # Test de tous les modèles
        test_all_models()

if __name__ == "__main__":
    main() 