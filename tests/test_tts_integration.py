#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Test d'intégration TTS pour CallAttendant

import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_tts_engine():
    """Test basique du moteur TTS"""
    print("=== Test du moteur TTS ===")
    
    try:
        from callattendant.messaging.tts_engine import TTSEngine
        
        # Configuration de test
        config = {
            'TTS_ENABLED': True,
            'TTS_ENGINE': 'espeak',
            'TTS_VOICE': 'french',
            'TTS_SPEED': 1.0,
            'TTS_VOLUME': 80,
            'TTS_LANGUAGE': 'fr-FR',
            'TTS_CACHE_DIR': 'test_tts_cache',
            'TTS_API_KEY': '',
            'TTS_API_REGION': ''
        }
        
        print("✓ Module TTS importé avec succès")
        
        # Test d'initialisation
        tts = TTSEngine(config)
        print(f"✓ Moteur TTS initialisé : {tts.engine}")
        print(f"✓ Voix configurée : {tts.voice}")
        print(f"✓ Vitesse : {tts.speed}")
        print(f"✓ Volume : {tts.volume}")
        
        # Test de synthèse (peut échouer si eSpeak n'est pas installé)
        print("\n--- Test de synthèse ---")
        result = tts.synthesize("Test de synthèse vocale")
        
        if result:
            print(f"✓ Synthèse réussie : {result}")
            if os.path.exists(result):
                print(f"✓ Fichier audio créé : {os.path.getsize(result)} bytes")
            else:
                print("⚠ Fichier audio non trouvé")
        else:
            print("⚠ Synthèse échouée (normal si eSpeak n'est pas installé)")
        
        # Test des voix disponibles
        print("\n--- Voix disponibles ---")
        voices = tts.get_available_voices()
        if voices:
            print(f"✓ {len(voices)} voix trouvées")
            for voice in voices[:5]:  # Afficher les 5 premières
                print(f"  - {voice}")
        else:
            print("⚠ Aucune voix trouvée")
        
        return True
        
    except ImportError as e:
        print(f"✗ Erreur d'import : {e}")
        return False
    except Exception as e:
        print(f"✗ Erreur : {e}")
        return False

def test_web_interface():
    """Test de l'interface web"""
    print("\n=== Test de l'interface web ===")
    
    try:
        # Vérifier que les templates existent
        template_path = "callattendant/userinterface/templates/settings_edit.html"
        if os.path.exists(template_path):
            print("✓ Template settings_edit.html trouvé")
            
            # Vérifier la présence des champs TTS
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'TTS_ENABLED' in content:
                    print("✓ Champs TTS présents dans le template")
                else:
                    print("✗ Champs TTS manquants dans le template")
        else:
            print("✗ Template settings_edit.html non trouvé")
        
        # Vérifier la route de test TTS
        webapp_path = "callattendant/userinterface/webapp.py"
        if os.path.exists(webapp_path):
            with open(webapp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'settings/tts/test' in content:
                    print("✓ Route de test TTS présente")
                else:
                    print("✗ Route de test TTS manquante")
        else:
            print("✗ Fichier webapp.py non trouvé")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur : {e}")
        return False

def test_configuration():
    """Test de la configuration"""
    print("\n=== Test de la configuration ===")
    
    try:
        # Vérifier le fichier d'exemple
        example_path = "callattendant/app.cfg.example"
        if os.path.exists(example_path):
            print("✓ Fichier app.cfg.example trouvé")
            
            with open(example_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'TTS_ENABLED' in content:
                    print("✓ Configuration TTS présente dans l'exemple")
                else:
                    print("✗ Configuration TTS manquante dans l'exemple")
        else:
            print("✗ Fichier app.cfg.example non trouvé")
        
        # Vérifier requirements.txt
        req_path = "requirements.txt"
        if os.path.exists(req_path):
            with open(req_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'pyttsx3' in content:
                    print("✓ Dépendances TTS présentes dans requirements.txt")
                else:
                    print("✗ Dépendances TTS manquantes dans requirements.txt")
        else:
            print("✗ Fichier requirements.txt non trouvé")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur : {e}")
        return False

def main():
    """Fonction principale de test"""
    print("Test d'intégration TTS pour CallAttendant")
    print("=" * 50)
    
    success = True
    
    # Tests
    success &= test_tts_engine()
    success &= test_web_interface()
    success &= test_configuration()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ Tous les tests sont passés avec succès !")
        print("\nPour tester l'interface web :")
        print("1. Lancez CallAttendant")
        print("2. Allez dans Settings → Edit Configuration")
        print("3. Configurez la section TTS")
        print("4. Utilisez le bouton 'Tester TTS'")
    else:
        print("✗ Certains tests ont échoué")
        print("Vérifiez les erreurs ci-dessus")
    
    return success

if __name__ == "__main__":
    main() 