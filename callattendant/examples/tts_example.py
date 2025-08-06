#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tts_example.py
#
#  Exemple d'utilisation du moteur TTS dans CallAttendant
#

import os
import sys

# Ajouter le chemin du projet pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from messaging.tts_engine import TTSEngine


def example_basic_usage():
    """Exemple d'utilisation basique du TTS"""
    print("=== Exemple d'utilisation basique du TTS ===")
    
    # Configuration de test
    config = {"DEBUG": True}
    
    # Initialiser le moteur TTS
    engine = TTSEngine(config)
    
    # Générer un fichier audio
    text = "Bonjour, bienvenue chez CallAttendant. Comment puis-je vous aider ?"
    audio_file = engine.generate_wav(text, "Zacharie Aimilios")
    
    if audio_file:
        print(f"Fichier audio généré: {audio_file}")
        
        # Jouer l'audio
        print("Lecture de l'audio...")
        engine.play_audio(audio_file)
    else:
        print("Erreur lors de la génération audio")


def example_generate_from_intents():
    """Exemple de génération d'audios depuis les intents"""
    print("\n=== Génération d'audios depuis les intents ===")
    
    config = {"DEBUG": True}
    engine = TTSEngine(config)
    
    # Générer tous les audios depuis le fichier intents.json
    engine.generate_audios_from_intents()
    print("Génération terminée !")


def example_speaker_selection():
    """Exemple de sélection de différents speakers"""
    print("\n=== Test avec différents speakers ===")
    
    config = {"DEBUG": True}
    engine = TTSEngine(config)
    
    # Liste des speakers recommandés
    speakers = ["Zacharie Aimilios", "Dionisio Schuyler", "Abrahan Mack", "Luis Moray"]
    
    text = "Bonjour, ceci est un test de synthèse vocale."
    
    for speaker in speakers:
        print(f"\nTest avec le speaker: {speaker}")
        audio_file = engine.generate_wav(text, speaker)
        if audio_file:
            print(f"Audio généré: {audio_file}")
            # Décommenter la ligne suivante pour jouer l'audio
            # engine.play_audio(audio_file)


def example_interactive():
    """Mode interactif pour tester le TTS"""
    print("\n=== Mode interactif ===")
    print("Tapez du texte pour le synthétiser, ou 'quit' pour quitter")
    print("Speakers disponibles: Zacharie Aimilios, Dionisio Schuyler, Abrahan Mack, Luis Moray")
    
    config = {"DEBUG": True}
    engine = TTSEngine(config)
    
    while True:
        try:
            text = input("\nTexte à synthétiser: ")
            if text.lower() == 'quit':
                break
                
            speaker = input("Speaker (défaut: Zacharie Aimilios): ").strip()
            if not speaker:
                speaker = "Zacharie Aimilios"
                
            audio_file = engine.generate_wav(text, speaker)
            if audio_file:
                print(f"Audio généré: {audio_file}")
                play = input("Jouer l'audio ? (o/n): ").strip().lower()
                if play in ['o', 'oui', 'y', 'yes']:
                    engine.play_audio(audio_file)
            else:
                print("Erreur lors de la génération")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Erreur: {e}")


def main():
    """Fonction principale avec menu d'exemples"""
    print("=== Exemples d'utilisation du TTS CallAttendant ===\n")
    
    while True:
        print("Choisissez un exemple:")
        print("1. Utilisation basique")
        print("2. Génération depuis les intents")
        print("3. Test avec différents speakers")
        print("4. Mode interactif")
        print("5. Quitter")
        
        choice = input("\nVotre choix (1-5): ").strip()
        
        if choice == '1':
            example_basic_usage()
        elif choice == '2':
            example_generate_from_intents()
        elif choice == '3':
            example_speaker_selection()
        elif choice == '4':
            example_interactive()
        elif choice == '5':
            print("Au revoir !")
            break
        else:
            print("Choix invalide. Veuillez choisir 1-5.")
        
        input("\nAppuyez sur Entrée pour continuer...")


if __name__ == "__main__":
    main() 