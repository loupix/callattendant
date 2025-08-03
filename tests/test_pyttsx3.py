#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Test pyttsx3 - Moteur TTS local
# Teste toutes les voix disponibles

import pyttsx3
import time

def test_pyttsx3():
    """Test complet de pyttsx3"""
    print("🎤 Test pyttsx3 - Moteur TTS local")
    print("=" * 50)
    
    try:
        # Initialiser le moteur
        engine = pyttsx3.init()
        print("✅ Moteur pyttsx3 initialisé")
        
        # Récupérer toutes les voix
        voices = engine.getProperty('voices')
        print(f"🎵 {len(voices)} voix trouvées:")
        
        for i, voice in enumerate(voices):
            print(f"   {i+1}. {voice.name} ({voice.id})")
            if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                print(f"      ⭐ Voix française détectée!")
        
        # Test avec voix par défaut
        print(f"\n🎤 Test avec voix par défaut:")
        engine.say("Bonjour, ceci est un test de pyttsx3")
        engine.runAndWait()
        
        # Test avec paramètres
        print(f"\n⚙️ Test avec paramètres personnalisés:")
        engine.setProperty('rate', 150)    # Vitesse
        engine.setProperty('volume', 0.8)  # Volume
        engine.say("Test avec vitesse et volume modifiés")
        engine.runAndWait()
        
        # Test avec différentes voix
        print(f"\n🎵 Test avec différentes voix:")
        test_text = "Bonjour, je suis votre assistant vocal"
        
        for i, voice in enumerate(voices[:3]):  # Test les 3 premières
            print(f"   Test voix {i+1}: {voice.name}")
            engine.setProperty('voice', voice.id)
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.7)
            engine.say(test_text)
            engine.runAndWait()
            time.sleep(1)
        
        # Test français spécifique
        print(f"\n🇫🇷 Test voix françaises:")
        french_voices = []
        for voice in voices:
            if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                french_voices.append(voice)
        
        if french_voices:
            for voice in french_voices:
                print(f"   Test: {voice.name}")
                engine.setProperty('voice', voice.id)
                engine.setProperty('rate', 140)
                engine.setProperty('volume', 0.8)
                engine.say("Bonjour, je parle français avec pyttsx3")
                engine.runAndWait()
                time.sleep(1)
        else:
            print("   ⚠️ Aucune voix française trouvée")
            print("   💡 Test avec voix par défaut:")
            engine.setProperty('rate', 140)
            engine.setProperty('volume', 0.8)
            engine.say("Bonjour, test en français")
            engine.runAndWait()
        
        print(f"\n🎉 Tests terminés!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_voice_parameters():
    """Test des paramètres de voix"""
    print(f"\n🔧 Test des paramètres de voix:")
    
    try:
        engine = pyttsx3.init()
        
        # Test différentes vitesses
        speeds = [100, 150, 200, 250]
        for speed in speeds:
            print(f"   Vitesse {speed}:")
            engine.setProperty('rate', speed)
            engine.say("Test de vitesse")
            engine.runAndWait()
            time.sleep(0.5)
        
        # Test différents volumes
        volumes = [0.3, 0.6, 0.9]
        for volume in volumes:
            print(f"   Volume {volume}:")
            engine.setProperty('volume', volume)
            engine.say("Test de volume")
            engine.runAndWait()
            time.sleep(0.5)
        
        print(f"✅ Tests de paramètres terminés")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def save_to_file():
    """Test sauvegarde en fichier"""
    print(f"\n💾 Test sauvegarde en fichier:")
    
    try:
        engine = pyttsx3.init()
        
        # Sauvegarder en fichier WAV
        output_file = "test_pyttsx3.wav"
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.8)
        
        engine.save_to_file("Bonjour, ceci est un test sauvegardé en fichier", output_file)
        engine.runAndWait()
        
        print(f"✅ Fichier sauvegardé: {output_file}")
        
        # Test avec voix française si disponible
        voices = engine.getProperty('voices')
        french_voice = None
        for voice in voices:
            if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                french_voice = voice
                break
        
        if french_voice:
            output_fr = "test_pyttsx3_fr.wav"
            engine.setProperty('voice', french_voice.id)
            engine.save_to_file("Bonjour, test en français sauvegardé", output_fr)
            engine.runAndWait()
            print(f"✅ Fichier français sauvegardé: {output_fr}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Fonction principale"""
    test_pyttsx3()
    test_voice_parameters()
    save_to_file()
    
    print(f"\n🎯 Résumé:")
    print(f"   - pyttsx3 fonctionne hors ligne")
    print(f"   - Qualité variable selon le système")
    print(f"   - Parfait pour tests rapides")
    print(f"   - Fichiers générés dans le répertoire courant")

if __name__ == "__main__":
    main() 