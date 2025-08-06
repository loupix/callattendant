#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tts_engine.py
#
<<<<<<< HEAD
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
=======
#  Copyright 2024 Loupix  <loupix@github.com>
#
#  Text-to-Speech Engine pour CallAttendant
#  Supporte plusieurs moteurs TTS : eSpeak, pyttsx3, Google TTS, Azure, AWS Polly

import os
import hashlib
import subprocess
import tempfile
from pathlib import Path
import logging

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    from gtts import gTTS
except ImportError:
    gTTS = None

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    speechsdk = None

try:
    import boto3
except ImportError:
    boto3 = None
>>>>>>> 53bb185dde9731510228007572ca35b8a285f4d9


class TTSEngine:
    """
<<<<<<< HEAD
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
=======
    Moteur de synthèse vocale unifié pour CallAttendant
    Supporte plusieurs backends : eSpeak, pyttsx3, Google TTS, Azure, AWS Polly
    """
    
    def __init__(self, config):
        """
        Initialise le moteur TTS avec la configuration
        
        Args:
            config: Configuration du système CallAttendant
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Paramètres TTS depuis la config
        self.enabled = config.get('TTS_ENABLED', False)
        self.engine = config.get('TTS_ENGINE', 'espeak')
        self.voice = config.get('TTS_VOICE', 'french')
        self.speed = config.get('TTS_SPEED', 1.0)
        self.volume = config.get('TTS_VOLUME', 80)
        self.language = config.get('TTS_LANGUAGE', 'fr-FR')
        self.cache_dir = config.get('TTS_CACHE_DIR', 'data/tts_cache')
        self.api_key = config.get('TTS_API_KEY', '')
        self.api_region = config.get('TTS_API_REGION', '')
        
        # Modèles de personnes disponibles
        self.person_models = {
            'espeak': {
                'Marie': {'voice': 'fr-fr+f2', 'speed': 1.0, 'pitch': 50},
                'Pierre': {'voice': 'fr-fr+m2', 'speed': 1.0, 'pitch': 30},
                'Sophie': {'voice': 'fr-fr+f3', 'speed': 1.1, 'pitch': 60},
                'Jean': {'voice': 'fr-fr+m3', 'speed': 0.9, 'pitch': 25},
                'Emma': {'voice': 'fr-fr+f4', 'speed': 1.2, 'pitch': 70},
                'Louis': {'voice': 'fr-fr+m4', 'speed': 0.8, 'pitch': 20}
            },
            'pyttsx3': {
                'Marie': {'voice': 'french', 'speed': 1.0, 'volume': 0.8},
                'Pierre': {'voice': 'french', 'speed': 0.9, 'volume': 0.9},
                'Sophie': {'voice': 'french', 'speed': 1.1, 'volume': 0.7},
                'Jean': {'voice': 'french', 'speed': 0.8, 'volume': 1.0},
                'Emma': {'voice': 'french', 'speed': 1.2, 'volume': 0.6},
                'Louis': {'voice': 'french', 'speed': 0.7, 'volume': 1.0}
            },
            'gtts': {
                'Marie': {'language': 'fr', 'slow': False},
                'Pierre': {'language': 'fr', 'slow': True},
                'Sophie': {'language': 'fr', 'slow': False},
                'Jean': {'language': 'fr', 'slow': True},
                'Emma': {'language': 'fr', 'slow': False},
                'Louis': {'language': 'fr', 'slow': True}
            },
            'azure': {
                'Marie': {'voice': 'fr-FR-Julie-Apollo', 'style': 'cheerful'},
                'Pierre': {'voice': 'fr-FR-Paul-Apollo', 'style': 'friendly'},
                'Sophie': {'voice': 'fr-FR-Julie-Apollo', 'style': 'excited'},
                'Jean': {'voice': 'fr-FR-Paul-Apollo', 'style': 'calm'},
                'Emma': {'voice': 'fr-FR-Julie-Apollo', 'style': 'hopeful'},
                'Louis': {'voice': 'fr-FR-Paul-Apollo', 'style': 'serious'}
            },
            'aws': {
                'Marie': {'voice': 'Lea', 'engine': 'neural'},
                'Pierre': {'voice': 'Mathieu', 'engine': 'neural'},
                'Sophie': {'voice': 'Lea', 'engine': 'standard'},
                'Jean': {'voice': 'Mathieu', 'engine': 'standard'},
                'Emma': {'voice': 'Lea', 'engine': 'neural'},
                'Louis': {'voice': 'Mathieu', 'engine': 'neural'}
            }
        }
        
        # Créer le répertoire de cache si nécessaire
        if self.cache_dir:
            Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialiser le moteur approprié
        self._init_engine()
    
    def _init_engine(self):
        """Initialise le moteur TTS approprié"""
        if not self.enabled:
            self.logger.info("TTS désactivé")
            return
            
        if self.engine == 'espeak':
            self._init_espeak()
        elif self.engine == 'pyttsx3':
            self._init_pyttsx3()
        elif self.engine == 'gtts':
            self._init_gtts()
        elif self.engine == 'azure':
            self._init_azure()
        elif self.engine == 'aws':
            self._init_aws()
        else:
            self.logger.error(f"Moteur TTS non supporté : {self.engine}")
    
    def _init_espeak(self):
        """Initialise eSpeak-ng"""
        try:
            # Essayer d'abord eSpeak-ng
            result = subprocess.run(['espeak-ng', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info("eSpeak-ng initialisé")
                self.espeak_cmd = 'espeak-ng'
            else:
                # Fallback vers eSpeak classique
                result = subprocess.run(['espeak', '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.logger.info("eSpeak classique initialisé")
                    self.espeak_cmd = 'espeak'
                else:
                    self.logger.error("Aucune version d'eSpeak trouvée")
        except FileNotFoundError:
            self.logger.error("eSpeak-ng non installé")
    
    def _init_pyttsx3(self):
        """Initialise pyttsx3"""
        if pyttsx3 is None:
            self.logger.error("pyttsx3 non installé")
            return
            
        try:
            self.pyttsx3_engine = pyttsx3.init()
            self.pyttsx3_engine.setProperty('rate', int(200 * self.speed))
            self.pyttsx3_engine.setProperty('volume', self.volume / 100.0)
            
            # Définir la voix si disponible
            voices = self.pyttsx3_engine.getProperty('voices')
            for voice in voices:
                if self.voice.lower() in voice.name.lower():
                    self.pyttsx3_engine.setProperty('voice', voice.id)
                    break
                    
            self.logger.info("pyttsx3 initialisé")
        except Exception as e:
            self.logger.error(f"Erreur initialisation pyttsx3 : {e}")
    
    def _init_gtts(self):
        """Initialise Google TTS"""
        if gTTS is None:
            self.logger.error("gTTS non installé")
            return
        self.logger.info("Google TTS initialisé")
    
    def _init_azure(self):
        """Initialise Azure Speech"""
        if speechsdk is None:
            self.logger.error("Azure Speech SDK non installé")
            return
            
        if not self.api_key:
            self.logger.error("Clé API Azure manquante")
            return
            
        self.azure_config = speechsdk.SpeechConfig(
            subscription=self.api_key, 
            region=self.api_region
        )
        self.azure_config.speech_synthesis_voice_name = self.voice
        self.logger.info("Azure Speech initialisé")
    
    def _init_aws(self):
        """Initialise AWS Polly"""
        if boto3 is None:
            self.logger.error("boto3 non installé")
            return
            
        if not self.api_key:
            self.logger.error("Clé API AWS manquante")
            return
            
        self.aws_client = boto3.client(
            'polly',
            aws_access_key_id=self.api_key,
            aws_secret_access_key=self.api_region,  # Utilise la région comme secret
            region_name='us-east-1'  # Région par défaut
        )
        self.logger.info("AWS Polly initialisé")
    
    def _get_cache_filename(self, text):
        """Génère un nom de fichier de cache basé sur le texte"""
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"{text_hash}.wav"
    
    def _get_cached_file(self, text):
        """Récupère le fichier depuis le cache s'il existe"""
        if not self.cache_dir:
            return None
            
        cache_file = os.path.join(self.cache_dir, self._get_cache_filename(text))
        if os.path.exists(cache_file):
            self.logger.debug(f"Fichier trouvé en cache : {cache_file}")
            return cache_file
        return None
    
    def _save_to_cache(self, text, audio_file):
        """Sauvegarde le fichier audio en cache"""
        if not self.cache_dir:
            return
            
        cache_file = os.path.join(self.cache_dir, self._get_cache_filename(text))
        try:
            with open(audio_file, 'rb') as src, open(cache_file, 'wb') as dst:
                dst.write(src.read())
            self.logger.debug(f"Fichier sauvegardé en cache : {cache_file}")
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde cache : {e}")
    
    def _synthesize_espeak(self, text, person_model=None):
        """Synthèse avec eSpeak"""
        try:
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            # Appliquer les paramètres du modèle de personne si spécifié
            voice = self.voice
            speed = self.speed
            pitch = 50  # Pitch par défaut
            
            if person_model and person_model in self.person_models.get('espeak', {}):
                model_config = self.person_models['espeak'][person_model]
                voice = model_config.get('voice', voice)
                speed = model_config.get('speed', speed)
                pitch = model_config.get('pitch', pitch)
            
            # Commande eSpeak-ng (ou eSpeak)
            cmd = [
                getattr(self, 'espeak_cmd', 'espeak-ng'),
                '-v', voice,
                '-s', str(int(150 * speed)),  # Vitesse
                '-a', str(self.volume),  # Volume
                '-p', str(pitch),  # Pitch
                '-q', '1',  # Qualité normale
                '-w', output_file,
                text
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Convertir vers 8kHz pour téléphone
                try:
                    import subprocess
                    final_output = output_file.replace('.wav', '_8khz.wav')
                    convert_cmd = ['sox', output_file, '-r', '8000', final_output]
                    convert_result = subprocess.run(convert_cmd, capture_output=True, text=True)
                    
                    if convert_result.returncode == 0:
                        # Nettoyer le fichier temporaire
                        os.unlink(output_file)
                        return final_output
                    else:
                        self.logger.warning(f"Conversion 8kHz échouée, utilisation du fichier original : {convert_result.stderr}")
                        return output_file
                except FileNotFoundError:
                    self.logger.warning("sox non installé, utilisation du fichier original")
                    return output_file
            else:
                self.logger.error(f"Erreur eSpeak : {result.stderr}")
                return None
        except Exception as e:
            self.logger.error(f"Erreur synthèse eSpeak : {e}")
            return None
    
    def _synthesize_pyttsx3(self, text, person_model=None):
        """Synthèse avec pyttsx3"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            # Appliquer les paramètres du modèle de personne si spécifié
            if person_model and person_model in self.person_models.get('pyttsx3', {}):
                model_config = self.person_models['pyttsx3'][person_model]
                self.pyttsx3_engine.setProperty('rate', int(200 * model_config.get('speed', self.speed)))
                self.pyttsx3_engine.setProperty('volume', model_config.get('volume', self.volume / 100.0))
            
            self.pyttsx3_engine.save_to_file(text, output_file)
            self.pyttsx3_engine.runAndWait()
            
            return output_file
        except Exception as e:
            self.logger.error(f"Erreur synthèse pyttsx3 : {e}")
            return None
    
    def _synthesize_gtts(self, text, person_model=None):
        """Synthèse avec Google TTS"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
                # Appliquer les paramètres du modèle de personne si spécifié
                lang = self.language.split('-')[0]
                slow = False
                
                if person_model and person_model in self.person_models.get('gtts', {}):
                    model_config = self.person_models['gtts'][person_model]
                    lang = model_config.get('language', lang)
                    slow = model_config.get('slow', slow)
                
                tts = gTTS(text=text, lang=lang, slow=slow)
                tts.save(output_file.name)
                return output_file.name
        except Exception as e:
            self.logger.error(f"Erreur synthèse Google TTS : {e}")
            return None
    
    def _synthesize_azure(self, text, person_model=None):
        """Synthèse avec Azure Speech"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
                # Appliquer les paramètres du modèle de personne si spécifié
                voice_name = self.voice
                style = None
                
                if person_model and person_model in self.person_models.get('azure', {}):
                    model_config = self.person_models['azure'][person_model]
                    voice_name = model_config.get('voice', voice_name)
                    style = model_config.get('style', style)
                
                # Configurer la voix
                self.azure_config.speech_synthesis_voice_name = voice_name
                
                audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file.name)
                synthesizer = speechsdk.SpeechSynthesizer(
                    speech_config=self.azure_config, 
                    audio_config=audio_config
                )
                
                # Ajouter le style si spécifié
                if style:
                    ssml_text = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="fr-FR"><voice name="{voice_name}"><mstts:express-as style="{style}">{text}</mstts:express-as></voice></speak>'
                    result = synthesizer.speak_ssml_async(ssml_text).get()
                else:
                    result = synthesizer.speak_text_async(text).get()
                
                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    return output_file.name
                else:
                    self.logger.error(f"Erreur Azure : {result.reason}")
                    return None
        except Exception as e:
            self.logger.error(f"Erreur synthèse Azure : {e}")
            return None
    
    def _synthesize_aws(self, text, person_model=None):
        """Synthèse avec AWS Polly"""
        try:
            # Appliquer les paramètres du modèle de personne si spécifié
            voice_id = self.voice
            engine = 'neural'
            
            if person_model and person_model in self.person_models.get('aws', {}):
                model_config = self.person_models['aws'][person_model]
                voice_id = model_config.get('voice', voice_id)
                engine = model_config.get('engine', engine)
            
            response = self.aws_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine=engine
            )
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as output_file:
                output_file.write(response['AudioStream'].read())
                return output_file.name
        except Exception as e:
            self.logger.error(f"Erreur synthèse AWS : {e}")
            return None
    
    def synthesize(self, text, person_model=None):
        """
        Synthétise le texte en audio
        
        Args:
            text: Texte à synthétiser
            person_model: Modèle de personne à utiliser (ex: 'Marie', 'Pierre')
            
        Returns:
            str: Chemin vers le fichier audio généré, ou None en cas d'erreur
        """
        if not self.enabled:
            self.logger.warning("TTS désactivé")
            return None
        
        if not text:
            self.logger.warning("Texte vide")
            return None
        
        # Appliquer le modèle de personne si spécifié
        original_voice = self.voice
        original_speed = self.speed
        original_volume = self.volume
        
        if person_model and person_model in self.person_models.get(self.engine, {}):
            model_config = self.person_models[self.engine][person_model]
            self.voice = model_config.get('voice', self.voice)
            self.speed = model_config.get('speed', self.speed)
            self.volume = model_config.get('volume', self.volume)
            self.logger.info(f"Application du modèle {person_model} pour {self.engine}")
        
        # Vérifier le cache d'abord
        cache_key = f"{text}_{person_model}" if person_model else text
        cached_file = self._get_cached_file(cache_key)
        if cached_file:
            return cached_file
        
        # Synthétiser selon le moteur
        audio_file = None
        if self.engine == 'espeak':
            audio_file = self._synthesize_espeak(text, person_model)
        elif self.engine == 'pyttsx3':
            audio_file = self._synthesize_pyttsx3(text, person_model)
        elif self.engine == 'gtts':
            audio_file = self._synthesize_gtts(text, person_model)
        elif self.engine == 'azure':
            audio_file = self._synthesize_azure(text, person_model)
        elif self.engine == 'aws':
            audio_file = self._synthesize_aws(text, person_model)
        else:
            self.logger.error(f"Moteur TTS non supporté : {self.engine}")
            return None
        
        # Restaurer les paramètres originaux
        self.voice = original_voice
        self.speed = original_speed
        self.volume = original_volume
        
        # Sauvegarder en cache si réussi
        if audio_file and os.path.exists(audio_file):
            self._save_to_cache(cache_key, audio_file)
            return audio_file
        
        return None
    
    def get_available_voices(self):
        """Retourne la liste des voix disponibles selon le moteur"""
        voices = []
        
        if self.engine == 'espeak':
            try:
                result = subprocess.run(['espeak', '--voices'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n')[1:]:
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 4:
                                voices.append(parts[3])
            except Exception as e:
                self.logger.error(f"Erreur récupération voix eSpeak : {e}")
        
        elif self.engine == 'pyttsx3' and pyttsx3:
            try:
                engine = pyttsx3.init()
                voices = [voice.name for voice in engine.getProperty('voices')]
            except Exception as e:
                self.logger.error(f"Erreur récupération voix pyttsx3 : {e}")
        
        return voices
    
    def get_available_person_models(self):
        """Retourne la liste des modèles de personnes disponibles"""
        return list(self.person_models.get(self.engine, {}).keys())
    
    def get_person_model_description(self, person_model):
        """Retourne la description d'un modèle de personne"""
        if person_model in self.person_models.get(self.engine, {}):
            model_config = self.person_models[self.engine][person_model]
            if self.engine == 'espeak':
                return f"Voix: {model_config['voice']}, Vitesse: {model_config['speed']}, Pitch: {model_config['pitch']}"
            elif self.engine == 'pyttsx3':
                return f"Vitesse: {model_config['speed']}, Volume: {model_config['volume']}"
            elif self.engine == 'gtts':
                return f"Langue: {model_config['language']}, Ralenti: {model_config['slow']}"
            elif self.engine == 'azure':
                return f"Voix: {model_config['voice']}, Style: {model_config['style']}"
            elif self.engine == 'aws':
                return f"Voix: {model_config['voice']}, Moteur: {model_config['engine']}"
        return "Modèle non disponible"
    
    def test_synthesis(self, text="Test de synthèse vocale"):
        """Teste la synthèse vocale"""
        self.logger.info(f"Test de synthèse avec le moteur {self.engine}")
        result = self.synthesize(text)
        if result:
            self.logger.info(f"Test réussi : {result}")
            return True
        else:
            self.logger.error("Test échoué")
            return False 
>>>>>>> 53bb185dde9731510228007572ca35b8a285f4d9
