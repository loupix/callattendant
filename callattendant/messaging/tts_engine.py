#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  tts_engine.py
#
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


class TTSEngine:
    """
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
        """Initialise eSpeak"""
        try:
            # Vérifier si eSpeak est installé
            result = subprocess.run(['espeak', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info("eSpeak initialisé")
            else:
                self.logger.error("eSpeak non trouvé")
        except FileNotFoundError:
            self.logger.error("eSpeak non installé")
    
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
    
    def _synthesize_espeak(self, text):
        """Synthèse avec eSpeak"""
        try:
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            # Commande eSpeak
            cmd = [
                'espeak',
                '-v', self.voice,
                '-s', str(int(150 * self.speed)),  # Vitesse
                '-a', str(self.volume),  # Volume
                '-w', output_file,
                text
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return output_file
            else:
                self.logger.error(f"Erreur eSpeak : {result.stderr}")
                return None
        except Exception as e:
            self.logger.error(f"Erreur synthèse eSpeak : {e}")
            return None
    
    def _synthesize_pyttsx3(self, text):
        """Synthèse avec pyttsx3"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            self.pyttsx3_engine.save_to_file(text, output_file)
            self.pyttsx3_engine.runAndWait()
            
            return output_file
        except Exception as e:
            self.logger.error(f"Erreur synthèse pyttsx3 : {e}")
            return None
    
    def _synthesize_gtts(self, text):
        """Synthèse avec Google TTS"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
                tts = gTTS(text=text, lang=self.language.split('-')[0])
                tts.save(output_file.name)
                return output_file.name
        except Exception as e:
            self.logger.error(f"Erreur synthèse Google TTS : {e}")
            return None
    
    def _synthesize_azure(self, text):
        """Synthèse avec Azure Speech"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
                audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file.name)
                synthesizer = speechsdk.SpeechSynthesizer(
                    speech_config=self.azure_config, 
                    audio_config=audio_config
                )
                
                result = synthesizer.speak_text_async(text).get()
                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    return output_file.name
                else:
                    self.logger.error(f"Erreur Azure : {result.reason}")
                    return None
        except Exception as e:
            self.logger.error(f"Erreur synthèse Azure : {e}")
            return None
    
    def _synthesize_aws(self, text):
        """Synthèse avec AWS Polly"""
        try:
            response = self.aws_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=self.voice
            )
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as output_file:
                output_file.write(response['AudioStream'].read())
                return output_file.name
        except Exception as e:
            self.logger.error(f"Erreur synthèse AWS : {e}")
            return None
    
    def synthesize(self, text):
        """
        Synthétise le texte en audio
        
        Args:
            text: Texte à synthétiser
            
        Returns:
            str: Chemin vers le fichier audio généré, ou None en cas d'erreur
        """
        if not self.enabled:
            self.logger.warning("TTS désactivé")
            return None
        
        if not text:
            self.logger.warning("Texte vide")
            return None
        
        # Vérifier le cache d'abord
        cached_file = self._get_cached_file(text)
        if cached_file:
            return cached_file
        
        # Synthétiser selon le moteur
        audio_file = None
        if self.engine == 'espeak':
            audio_file = self._synthesize_espeak(text)
        elif self.engine == 'pyttsx3':
            audio_file = self._synthesize_pyttsx3(text)
        elif self.engine == 'gtts':
            audio_file = self._synthesize_gtts(text)
        elif self.engine == 'azure':
            audio_file = self._synthesize_azure(text)
        elif self.engine == 'aws':
            audio_file = self._synthesize_aws(text)
        else:
            self.logger.error(f"Moteur TTS non supporté : {self.engine}")
            return None
        
        # Sauvegarder en cache si réussi
        if audio_file and os.path.exists(audio_file):
            self._save_to_cache(text, audio_file)
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