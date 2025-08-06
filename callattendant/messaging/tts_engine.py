#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tts_engine.py
#
#  Copyright 2024  <loupix>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import os
import json
from pydub import AudioSegment
from TTS.api import TTS
import simpleaudio as sa
import wave


class TTSEngine:
    """
    Moteur de synthèse vocale utilisant XTTS v2 pour générer des fichiers audio
    à partir de texte en français.
    """
    
    def __init__(self, config, language='fr', audios_dir="resources/tts_audios"):
        """
        Initialise le moteur TTS.
        
        Args:
            config: Configuration de l'application
            language: Langue pour la synthèse vocale (défaut: 'fr')
            audios_dir: Dossier de stockage des fichiers audio générés
        """
        self.config = config
        self.language = language
        
        # Déterminer le chemin racine du projet
        root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        
        # Créer le dossier audio s'il n'existe pas
        audio_path = os.path.join(root_path, audios_dir)
        if not os.path.isdir(audio_path):
            if self.config.get("DEBUG", False):
                print(f"Le dossier AUDIO_PATH n'existe pas. Création de {audio_path}")
            os.makedirs(audio_path)
        self.audios_dir = audio_path
        
        # Initialiser le modèle TTS
        try:
            self.tts = TTS(
                model_name="tts_models/multilingual/multi-dataset/xtts_v2", 
                progress_bar=False,  # Désactiver la barre de progression pour l'intégration
                gpu=False
            )
            if self.config.get("DEBUG", False):
                print("Moteur TTS initialisé avec succès")
        except Exception as e:
            print(f"Erreur lors de l'initialisation du TTS: {e}")
            self.tts = None

    def _generate_filename(self, text, speaker):
        """
        Génère un nom de fichier sécurisé basé sur le texte et le speaker.
        
        Args:
            text: Le texte à synthétiser
            speaker: Le nom du speaker
            
        Returns:
            str: Chemin complet du fichier sans extension
        """
        # Créer un nom de fichier basé sur les 30 premiers caractères du texte
        # et remplacer les caractères non alphanumériques par des underscores
        safe_text = "".join(c if c.isalnum() else "_" for c in text[:30])
        safe_dir = "".join(c if c.isalnum() else "_" for c in speaker[:30])
        
        speaker_dir = os.path.join(self.audios_dir, safe_dir)
        if not os.path.isdir(speaker_dir):
            os.makedirs(speaker_dir)
            
        return os.path.join(speaker_dir, safe_text)

    def generate_wav(self, text, speaker="Zacharie Aimilios"):
        """
        Génère un fichier WAV à partir du texte.
        
        Args:
            text: Le texte à synthétiser
            speaker: Le nom du speaker (défaut: Zacharie Aimilios)
            
        Returns:
            str: Chemin vers le fichier WAV généré
        """
        if not self.tts:
            print("Erreur: Moteur TTS non initialisé")
            return None
            
        base_filename = self._generate_filename(text, speaker)
        wav_file = f"{base_filename}.wav"

        # Vérifier si le fichier WAV existe déjà
        if not os.path.exists(wav_file):
            try:
                if self.config.get("DEBUG", False):
                    print(f"Génération audio pour: '{text[:50]}...'")
                    
                self.tts.tts_to_file(
                    text=text, 
                    language="fr", 
                    speaker=speaker, 
                    file_path=wav_file
                )
                
                # Convertir le fichier WAV en 8 kHz et en PCM non signé 8 bits
                # pour compatibilité avec le système téléphonique
                audio_segment = AudioSegment.from_wav(wav_file)
                audio_segment = audio_segment.set_frame_rate(8000).set_sample_width(1)
                audio_segment.export(wav_file, format="wav")
                
                if self.config.get("DEBUG", False):
                    print(f"Fichier audio généré: {wav_file}")
                    
            except Exception as e:
                print(f"Erreur lors de la génération audio: {e}")
                return None

        return wav_file

    def play_audio(self, wav_file):
        """
        Joue un fichier audio.
        
        Args:
            wav_file: Chemin vers le fichier WAV à jouer
        """
        if not wav_file or not os.path.exists(wav_file):
            print(f"Erreur: Impossible de lire le fichier {wav_file}")
            return False
            
        try:
            # Charger le fichier WAV
            wave_obj = sa.WaveObject.from_wave_file(wav_file)
            wave_obj.play()  # Jouer l'audio

            # Obtenir la durée du fichier WAV
            with wave.open(wav_file, 'rb') as wf:
                duration = wf.getnframes() / wf.getframerate()

            sa.sleep(duration)  # Attendre la fin de la lecture
            return True
            
        except Exception as e:
            print(f"Erreur lors de la lecture audio: {e}")
            return False

    def generate_audios_from_intents(self, intents_file="resources/intents.json"):
        """
        Génère des fichiers audio pour tous les intents d'un fichier JSON.
        
        Args:
            intents_file: Chemin vers le fichier JSON contenant les intents
        """
        root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        intents_path = os.path.join(root_path, intents_file)
        
        if not os.path.exists(intents_path):
            print(f"Fichier intents non trouvé: {intents_path}")
            return
            
        try:
            with open(intents_path, 'r', encoding='utf-8') as f:
                intents_json = json.load(f)

            for intent in intents_json.get("intents", []):
                for response in intent.get("responses", []):
                    self.generate_wav(response)
                    
        except Exception as e:
            print(f"Erreur lors de la génération des audios depuis les intents: {e}")

    def get_available_speakers(self):
        """
        Retourne la liste des speakers disponibles.
        
        Returns:
            list: Liste des noms de speakers
        """
        return [
            'Claribel Dervla', 'Daisy Studious', 'Gracie Wise', 'Tammie Ema', 
            'Alison Dietlinde', 'Ana Florence', 'Annmarie Nele', 'Asya Anara', 
            'Brenda Stern', 'Gitta Nikolina', 'Henriette Usha', 'Sofia Hellen', 
            'Tammy Grit', 'Tanja Adelina', 'Vjollca Johnnie', 'Andrew Chipper', 
            'Badr Odhiambo', 'Dionisio Schuyler', 'Royston Min', 'Viktor Eka', 
            'Abrahan Mack', 'Adde Michal', 'Baldur Sanjin', 'Craig Gutsy', 
            'Damien Black', 'Gilberto Mathias', 'Ilkin Urbano', 'Kazuhiko Atallah', 
            'Ludvig Milivoj', 'Suad Qasim', 'Torcull Diarmuid', 'Viktor Menelaos', 
            'Zacharie Aimilios', 'Nova Hogarth', 'Maja Ruoho', 'Uta Obando', 
            'Lidiya Szekeres', 'Chandra MacFarland', 'Szofi Granger', 
            'Camilla Holmström', 'Lilya Stainthorpe', 'Zofija Kendrick', 
            'Narelle Moon', 'Barbora MacLean', 'Alexandra Hisakawa', 'Alma María', 
            'Rosemary Okafor', 'Ige Behringer', 'Filip Traverse', 'Damjan Chapman', 
            'Wulf Carlevaro', 'Aaron Dreschner', 'Kumar Dahl', 'Ferran Simen', 
            'Xavier Hayasaka', 'Luis Moray', 'Marcos Rudaski'
        ]


# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration de test
    test_config = {"DEBUG": True}
    
    engine = TTSEngine(test_config)
    
    # Test interactif
    print("Moteur TTS CallAttendant")
    print("Speakers recommandés: Zacharie Aimilios, Dionisio Schuyler, Abrahan Mack, Luis Moray")
    print("Tapez 'quit' pour quitter")
    
    while True:
        try:
            message = input(" > ")
            if message.lower() == 'quit':
                break
                
            audio_file = engine.generate_wav(message, 'Zacharie Aimilios')
            if audio_file:
                engine.play_audio(audio_file)
                
        except KeyboardInterrupt:
            break 