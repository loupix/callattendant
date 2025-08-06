#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  llm_tts_engine.py
#
#  Copyright 2024 Loupix  <loupix@github.com>
#
#  LLM Text-to-Speech Engine pour CallAttendant
#  Supporte les modèles modernes : XTTS-v2, ChatTTS, Dia, Kokoro

import os
import hashlib
import tempfile
import subprocess
from pathlib import Path
import logging
import requests
import json

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    import torchaudio
except ImportError:
    torch = None
    torchaudio = None

try:
    import soundfile as sf
except ImportError:
    sf = None


class LLMTTSEngine:
    """
    Moteur de synthèse vocale LLM moderne pour CallAttendant
    Supporte XTTS-v2, ChatTTS, Dia, Kokoro
    """
    
    def __init__(self, config):
        """
        Initialise le moteur TTS LLM avec la configuration
        
        Args:
            config: Configuration du système CallAttendant
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Paramètres TTS depuis la config
        self.enabled = config.get('TTS_ENABLED', False)
        self.engine = config.get('TTS_ENGINE', 'xtts-v2')
        self.language = config.get('TTS_LANGUAGE', 'fr')
        self.cache_dir = config.get('TTS_CACHE_DIR', 'data/tts_cache')
        self.model_dir = config.get('TTS_MODEL_DIR', 'data/tts_models')
        
        # Modèles disponibles
        self.available_models = {
            'xtts-v2': {
                'name': 'XTTS-v2',
                'description': 'Voice cloning avec 6 secondes audio',
                'languages': ['fr', 'en', 'es', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 'nl', 'cs', 'ar', 'zh', 'ja', 'ko', 'hi'],
                'features': ['voice_cloning', 'multilingual', 'emotion_control'],
                'license': 'non-commercial',
                'size': '~1GB'
            },
            'chattts': {
                'name': 'ChatTTS',
                'description': 'Optimisé pour conversations et dialogues',
                'languages': ['en', 'zh'],
                'features': ['dialogue_optimized', 'high_quality', 'token_control'],
                'license': 'open',
                'size': '~500MB'
            },
            'dia': {
                'name': 'Dia',
                'description': 'Génération de dialogues multi-locuteurs',
                'languages': ['en'],
                'features': ['multi_speaker', 'emotion_control', 'nonverbal_tags'],
                'license': 'apache2',
                'size': '~1.6GB'
            },
            'kokoro': {
                'name': 'Kokoro',
                'description': 'Léger et rapide (82M paramètres)',
                'languages': ['en', 'ja'],
                'features': ['lightweight', 'fast', 'efficient'],
                'license': 'apache2',
                'size': '~100MB'
            },
            'chatterbox': {
                'name': 'Chatterbox',
                'description': 'Haute performance avec contrôle émotionnel',
                'languages': ['en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh'],
                'features': ['emotion_exaggeration', 'voice_cloning', 'low_latency', 'watermarked'],
                'license': 'mit',
                'size': '~500MB'
            },
            'melotts': {
                'name': 'MeloTTS',
                'description': 'Multilingue optimisé temps réel',
                'languages': ['en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi', 'th', 'vi'],
                'features': ['multilingual', 'real_time', 'mixed_language', 'cpu_optimized'],
                'license': 'mit',
                'size': '~300MB'
            },
            'openvoice-v2': {
                'name': 'OpenVoice v2',
                'description': 'Voice cloning instantané avec contrôle granulaire',
                'languages': ['en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi'],
                'features': ['instant_cloning', 'cross_lingual', 'style_control', 'emotion_control'],
                'license': 'mit',
                'size': '~400MB'
            }
        }
        
        # Modèles de personnes pour chaque moteur
        self.person_models = {
            'xtts-v2': {
                'Marie': {'voice_file': 'marie_reference.wav', 'style': 'friendly'},
                'Pierre': {'voice_file': 'pierre_reference.wav', 'style': 'professional'},
                'Sophie': {'voice_file': 'sophie_reference.wav', 'style': 'energetic'},
                'Jean': {'voice_file': 'jean_reference.wav', 'style': 'calm'}
            },
            'chattts': {
                'Assistant': {'style': 'conversational', 'tone': 'friendly'},
                'Receptionist': {'style': 'professional', 'tone': 'helpful'},
                'Guide': {'style': 'informative', 'tone': 'clear'}
            },
            'dia': {
                'Speaker1': {'style': 'friendly', 'emotion': 'neutral'},
                'Speaker2': {'style': 'professional', 'emotion': 'calm'}
            },
            'kokoro': {
                'Default': {'style': 'natural', 'speed': 1.0}
            },
            'chatterbox': {
                'Emma': {'style': 'cheerful', 'emotion_exaggeration': 0.7, 'voice_file': 'emma_ref.wav'},
                'Alex': {'style': 'professional', 'emotion_exaggeration': 0.3, 'voice_file': 'alex_ref.wav'},
                'Sarah': {'style': 'friendly', 'emotion_exaggeration': 0.5, 'voice_file': 'sarah_ref.wav'},
                'David': {'style': 'calm', 'emotion_exaggeration': 0.2, 'voice_file': 'david_ref.wav'}
            },
            'melotts': {
                'French': {'language': 'fr', 'accent': 'france', 'style': 'natural'},
                'English': {'language': 'en', 'accent': 'us', 'style': 'natural'},
                'Spanish': {'language': 'es', 'accent': 'spain', 'style': 'natural'},
                'German': {'language': 'de', 'accent': 'germany', 'style': 'natural'},
                'Mixed': {'language': 'mixed', 'style': 'conversational'}
            },
            'openvoice-v2': {
                'Cloned_Voice_1': {'voice_file': 'voice1_ref.wav', 'style': 'natural', 'emotion': 'neutral'},
                'Cloned_Voice_2': {'voice_file': 'voice2_ref.wav', 'style': 'professional', 'emotion': 'calm'},
                'Cloned_Voice_3': {'voice_file': 'voice3_ref.wav', 'style': 'friendly', 'emotion': 'happy'},
                'Default': {'style': 'natural', 'accent': 'neutral'}
            }
        }
        
        # Créer les répertoires nécessaires
        if self.cache_dir:
            Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
        if self.model_dir:
            Path(self.model_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialiser le moteur approprié
        self._init_engine()
    
    def _init_engine(self):
        """Initialise le moteur TTS approprié"""
        if not self.enabled:
            self.logger.info("TTS LLM désactivé")
            return
            
        if self.engine == 'xtts-v2':
            self._init_xtts_v2()
        elif self.engine == 'chattts':
            self._init_chattts()
        elif self.engine == 'dia':
            self._init_dia()
        elif self.engine == 'kokoro':
            self._init_kokoro()
        elif self.engine == 'chatterbox':
            self._init_chatterbox()
        elif self.engine == 'melotts':
            self._init_melotts()
        elif self.engine == 'openvoice-v2':
            self._init_openvoice_v2()
        else:
            self.logger.error(f"Moteur TTS LLM non supporté : {self.engine}")
    
    def _init_xtts_v2(self):
        """Initialise XTTS-v2"""
        try:
            # Vérifier si le modèle est disponible
            model_path = os.path.join(self.model_dir, 'xtts-v2')
            if not os.path.exists(model_path):
                self.logger.info("Téléchargement du modèle XTTS-v2...")
                self._download_xtts_v2()
            
            self.logger.info("XTTS-v2 initialisé")
        except Exception as e:
            self.logger.error(f"Erreur initialisation XTTS-v2 : {e}")
    
    def _init_chattts(self):
        """Initialise ChatTTS"""
        try:
            # Vérifier si le modèle est disponible
            model_path = os.path.join(self.model_dir, 'chattts')
            if not os.path.exists(model_path):
                self.logger.info("Téléchargement du modèle ChatTTS...")
                self._download_chattts()
            
            self.logger.info("ChatTTS initialisé")
        except Exception as e:
            self.logger.error(f"Erreur initialisation ChatTTS : {e}")
    
    def _init_dia(self):
        """Initialise Dia"""
        try:
            # Vérifier si le modèle est disponible
            model_path = os.path.join(self.model_dir, 'dia')
            if not os.path.exists(model_path):
                self.logger.info("Téléchargement du modèle Dia...")
                self._download_dia()
            
            self.logger.info("Dia initialisé")
        except Exception as e:
            self.logger.error(f"Erreur initialisation Dia : {e}")
    
    def _init_kokoro(self):
        """Initialise Kokoro"""
        try:
            # Vérifier si le modèle est disponible
            model_path = os.path.join(self.model_dir, 'kokoro')
            if not os.path.exists(model_path):
                self.logger.info("Téléchargement du modèle Kokoro...")
                self._download_kokoro()
            
            self.logger.info("Kokoro initialisé")
        except Exception as e:
            self.logger.error(f"Erreur initialisation Kokoro : {e}")
    
    def _init_chatterbox(self):
        """Initialise Chatterbox"""
        try:
            # Vérifier si le modèle est disponible
            model_path = os.path.join(self.model_dir, 'chatterbox')
            if not os.path.exists(model_path):
                self.logger.info("Téléchargement du modèle Chatterbox...")
                self._download_chatterbox()
            
            self.logger.info("Chatterbox initialisé")
        except Exception as e:
            self.logger.error(f"Erreur initialisation Chatterbox : {e}")
    
    def _init_melotts(self):
        """Initialise MeloTTS"""
        try:
            # Vérifier si le modèle est disponible
            model_path = os.path.join(self.model_dir, 'melotts')
            if not os.path.exists(model_path):
                self.logger.info("Téléchargement du modèle MeloTTS...")
                self._download_melotts()
            
            self.logger.info("MeloTTS initialisé")
        except Exception as e:
            self.logger.error(f"Erreur initialisation MeloTTS : {e}")
    
    def _init_openvoice_v2(self):
        """Initialise OpenVoice v2"""
        try:
            # Vérifier si le modèle est disponible
            model_path = os.path.join(self.model_dir, 'openvoice-v2')
            if not os.path.exists(model_path):
                self.logger.info("Téléchargement du modèle OpenVoice v2...")
                self._download_openvoice_v2()
            
            self.logger.info("OpenVoice v2 initialisé")
        except Exception as e:
            self.logger.error(f"Erreur initialisation OpenVoice v2 : {e}")
    
    def _download_xtts_v2(self):
        """Télécharge le modèle XTTS-v2"""
        try:
            # Utiliser Hugging Face pour télécharger
            from huggingface_hub import snapshot_download
            
            model_path = os.path.join(self.model_dir, 'xtts-v2')
            snapshot_download(
                repo_id="coqui/XTTS-v2",
                local_dir=model_path,
                local_dir_use_symlinks=False
            )
            self.logger.info("XTTS-v2 téléchargé avec succès")
        except Exception as e:
            self.logger.error(f"Erreur téléchargement XTTS-v2 : {e}")
    
    def _download_chattts(self):
        """Télécharge le modèle ChatTTS"""
        try:
            from huggingface_hub import snapshot_download
            
            model_path = os.path.join(self.model_dir, 'chattts')
            snapshot_download(
                repo_id="2noise/ChatTTS",
                local_dir=model_path,
                local_dir_use_symlinks=False
            )
            self.logger.info("ChatTTS téléchargé avec succès")
        except Exception as e:
            self.logger.error(f"Erreur téléchargement ChatTTS : {e}")
    
    def _download_dia(self):
        """Télécharge le modèle Dia"""
        try:
            from huggingface_hub import snapshot_download
            
            model_path = os.path.join(self.model_dir, 'dia')
            snapshot_download(
                repo_id="nari-labs/Dia",
                local_dir=model_path,
                local_dir_use_symlinks=False
            )
            self.logger.info("Dia téléchargé avec succès")
        except Exception as e:
            self.logger.error(f"Erreur téléchargement Dia : {e}")
    
    def _download_kokoro(self):
        """Télécharge le modèle Kokoro"""
        try:
            from huggingface_hub import snapshot_download
            
            model_path = os.path.join(self.model_dir, 'kokoro')
            snapshot_download(
                repo_id="plachtaa/Kokoro",
                local_dir=model_path,
                local_dir_use_symlinks=False
            )
            self.logger.info("Kokoro téléchargé avec succès")
        except Exception as e:
            self.logger.error(f"Erreur téléchargement Kokoro : {e}")
    
    def _download_chatterbox(self):
        """Télécharge le modèle Chatterbox"""
        try:
            from huggingface_hub import snapshot_download
            
            model_path = os.path.join(self.model_dir, 'chatterbox')
            snapshot_download(
                repo_id="resemble-ai/Chatterbox",
                local_dir=model_path,
                local_dir_use_symlinks=False
            )
            self.logger.info("Chatterbox téléchargé avec succès")
        except Exception as e:
            self.logger.error(f"Erreur téléchargement Chatterbox : {e}")
    
    def _download_melotts(self):
        """Télécharge le modèle MeloTTS"""
        try:
            from huggingface_hub import snapshot_download
            
            model_path = os.path.join(self.model_dir, 'melotts')
            snapshot_download(
                repo_id="myshell-ai/MeloTTS",
                local_dir=model_path,
                local_dir_use_symlinks=False
            )
            self.logger.info("MeloTTS téléchargé avec succès")
        except Exception as e:
            self.logger.error(f"Erreur téléchargement MeloTTS : {e}")
    
    def _download_openvoice_v2(self):
        """Télécharge le modèle OpenVoice v2"""
        try:
            from huggingface_hub import snapshot_download
            
            model_path = os.path.join(self.model_dir, 'openvoice-v2')
            snapshot_download(
                repo_id="myshell-ai/OpenVoice",
                local_dir=model_path,
                local_dir_use_symlinks=False
            )
            self.logger.info("OpenVoice v2 téléchargé avec succès")
        except Exception as e:
            self.logger.error(f"Erreur téléchargement OpenVoice v2 : {e}")
    
    def _get_cache_filename(self, text, person_model=None):
        """Génère un nom de fichier de cache basé sur le texte et le modèle"""
        cache_key = f"{text}_{person_model}_{self.engine}" if person_model else f"{text}_{self.engine}"
        text_hash = hashlib.md5(cache_key.encode('utf-8')).hexdigest()
        return f"{text_hash}.wav"
    
    def _get_cached_file(self, text, person_model=None):
        """Récupère le fichier depuis le cache s'il existe"""
        if not self.cache_dir:
            return None
            
        cache_file = os.path.join(self.cache_dir, self._get_cache_filename(text, person_model))
        if os.path.exists(cache_file):
            self.logger.debug(f"Fichier trouvé en cache : {cache_file}")
            return cache_file
        return None
    
    def _save_to_cache(self, text, audio_file, person_model=None):
        """Sauvegarde le fichier audio en cache"""
        if not self.cache_dir:
            return
            
        cache_file = os.path.join(self.cache_dir, self._get_cache_filename(text, person_model))
        try:
            with open(audio_file, 'rb') as src, open(cache_file, 'wb') as dst:
                dst.write(src.read())
            self.logger.debug(f"Fichier sauvegardé en cache : {cache_file}")
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde cache : {e}")
    
    def _synthesize_xtts_v2(self, text, person_model=None):
        """Synthèse avec XTTS-v2"""
        try:
            # Utiliser l'API XTTS-v2 ou l'implémentation locale
            if person_model and person_model in self.person_models.get('xtts-v2', {}):
                voice_file = self.person_models['xtts-v2'][person_model]['voice_file']
                style = self.person_models['xtts-v2'][person_model]['style']
                
                # Générer avec voice cloning
                return self._generate_with_voice_cloning(text, voice_file, style)
            else:
                # Générer avec voix par défaut
                return self._generate_default_voice(text)
                
        except Exception as e:
            self.logger.error(f"Erreur synthèse XTTS-v2 : {e}")
            return None
    
    def _synthesize_chattts(self, text, person_model=None):
        """Synthèse avec ChatTTS"""
        try:
            # Optimiser pour les dialogues
            if person_model and person_model in self.person_models.get('chattts', {}):
                style = self.person_models['chattts'][person_model]['style']
                tone = self.person_models['chattts'][person_model]['tone']
                
                # Formater pour dialogue
                formatted_text = f"[{style.upper()}] {text}"
                return self._generate_chattts_dialogue(formatted_text, tone)
            else:
                return self._generate_chattts_default(text)
                
        except Exception as e:
            self.logger.error(f"Erreur synthèse ChatTTS : {e}")
            return None
    
    def _synthesize_dia(self, text, person_model=None):
        """Synthèse avec Dia"""
        try:
            # Formater pour dialogue multi-locuteur
            if person_model and person_model in self.person_models.get('dia', {}):
                style = self.person_models['dia'][person_model]['style']
                emotion = self.person_models['dia'][person_model]['emotion']
                
                # Format Dia avec tags
                formatted_text = f"[S1] {text}"
                if emotion != 'neutral':
                    formatted_text += f" ({emotion})"
                
                return self._generate_dia_dialogue(formatted_text)
            else:
                return self._generate_dia_default(text)
                
        except Exception as e:
            self.logger.error(f"Erreur synthèse Dia : {e}")
            return None
    
    def _synthesize_kokoro(self, text, person_model=None):
        """Synthèse avec Kokoro"""
        try:
            # Kokoro léger et rapide
            if person_model and person_model in self.person_models.get('kokoro', {}):
                style = self.person_models['kokoro'][person_model]['style']
                speed = self.person_models['kokoro'][person_model]['speed']
                
                return self._generate_kokoro_optimized(text, style, speed)
            else:
                return self._generate_kokoro_default(text)
                
        except Exception as e:
            self.logger.error(f"Erreur synthèse Kokoro : {e}")
            return None
    
    def _generate_with_voice_cloning(self, text, voice_file, style):
        """Génère avec voice cloning (XTTS-v2)"""
        # Implémentation simplifiée - utiliser l'API ou le modèle local
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            # Ici on utiliserait l'API XTTS-v2 ou l'implémentation locale
            # Pour l'instant, on simule
            self.logger.info(f"Génération voice cloning: {text} avec {voice_file}")
            
            # Placeholder - remplacer par vraie implémentation
            return output_file
            
        except Exception as e:
            self.logger.error(f"Erreur voice cloning : {e}")
            return None
    
    def _generate_chattts_dialogue(self, text, tone):
        """Génère dialogue avec ChatTTS"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            # Implémentation ChatTTS pour dialogues
            self.logger.info(f"Génération ChatTTS dialogue: {text} avec ton {tone}")
            
            # Placeholder - remplacer par vraie implémentation
            return output_file
            
        except Exception as e:
            self.logger.error(f"Erreur ChatTTS dialogue : {e}")
            return None
    
    def _generate_dia_dialogue(self, text):
        """Génère dialogue avec Dia"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            # Implémentation Dia pour dialogues multi-locuteur
            self.logger.info(f"Génération Dia dialogue: {text}")
            
            # Placeholder - remplacer par vraie implémentation
            return output_file
            
        except Exception as e:
            self.logger.error(f"Erreur Dia dialogue : {e}")
            return None
    
    def _generate_kokoro_optimized(self, text, style, speed):
        """Génère avec Kokoro optimisé"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            # Implémentation Kokoro légère et rapide
            self.logger.info(f"Génération Kokoro: {text} avec style {style}, vitesse {speed}")
            
            # Placeholder - remplacer par vraie implémentation
            return output_file
            
        except Exception as e:
            self.logger.error(f"Erreur Kokoro : {e}")
            return None
    
    def _generate_default_voice(self, text):
        """Génère avec voix par défaut"""
        # Méthodes par défaut pour chaque moteur
        pass
    
    def _generate_chattts_default(self, text):
        """Génère avec ChatTTS par défaut"""
        pass
    
    def _generate_dia_default(self, text):
        """Génère avec Dia par défaut"""
        pass
    
    def _generate_kokoro_default(self, text):
        """Génère avec Kokoro par défaut"""
        pass
    
    def _synthesize_chatterbox(self, text, person_model=None):
        """Synthèse avec Chatterbox"""
        try:
            # Chatterbox avec contrôle émotionnel
            if person_model and person_model in self.person_models.get('chatterbox', {}):
                style = self.person_models['chatterbox'][person_model]['style']
                emotion_exaggeration = self.person_models['chatterbox'][person_model]['emotion_exaggeration']
                voice_file = self.person_models['chatterbox'][person_model]['voice_file']
                
                return self._generate_chatterbox_emotional(text, style, emotion_exaggeration, voice_file)
            else:
                return self._generate_chatterbox_default(text)
                
        except Exception as e:
            self.logger.error(f"Erreur synthèse Chatterbox : {e}")
            return None
    
    def _synthesize_melotts(self, text, person_model=None):
        """Synthèse avec MeloTTS"""
        try:
            # MeloTTS multilingue optimisé
            if person_model and person_model in self.person_models.get('melotts', {}):
                language = self.person_models['melotts'][person_model]['language']
                accent = self.person_models['melotts'][person_model]['accent']
                style = self.person_models['melotts'][person_model]['style']
                
                return self._generate_melotts_multilingual(text, language, accent, style)
            else:
                return self._generate_melotts_default(text)
                
        except Exception as e:
            self.logger.error(f"Erreur synthèse MeloTTS : {e}")
            return None
    
    def _synthesize_openvoice_v2(self, text, person_model=None):
        """Synthèse avec OpenVoice v2"""
        try:
            # OpenVoice v2 avec voice cloning instantané
            if person_model and person_model in self.person_models.get('openvoice-v2', {}):
                voice_file = self.person_models['openvoice-v2'][person_model]['voice_file']
                style = self.person_models['openvoice-v2'][person_model]['style']
                emotion = self.person_models['openvoice-v2'][person_model]['emotion']
                
                return self._generate_openvoice_cloning(text, voice_file, style, emotion)
            else:
                return self._generate_openvoice_default(text)
                
        except Exception as e:
            self.logger.error(f"Erreur synthèse OpenVoice v2 : {e}")
            return None
    
    def _generate_chatterbox_emotional(self, text, style, emotion_exaggeration, voice_file):
        """Génère avec Chatterbox et contrôle émotionnel"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            # Implémentation Chatterbox avec exagération émotionnelle
            self.logger.info(f"Génération Chatterbox: {text} avec style {style}, émotion {emotion_exaggeration}")
            
            # Placeholder - remplacer par vraie implémentation
            return output_file
            
        except Exception as e:
            self.logger.error(f"Erreur Chatterbox émotionnel : {e}")
            return None
    
    def _generate_melotts_multilingual(self, text, language, accent, style):
        """Génère avec MeloTTS multilingue"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            # Implémentation MeloTTS multilingue optimisée temps réel
            self.logger.info(f"Génération MeloTTS: {text} en {language} avec accent {accent}")
            
            # Placeholder - remplacer par vraie implémentation
            return output_file
            
        except Exception as e:
            self.logger.error(f"Erreur MeloTTS multilingue : {e}")
            return None
    
    def _generate_openvoice_cloning(self, text, voice_file, style, emotion):
        """Génère avec OpenVoice v2 voice cloning"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            # Implémentation OpenVoice v2 avec voice cloning instantané
            self.logger.info(f"Génération OpenVoice v2: {text} avec voice {voice_file}, style {style}, émotion {emotion}")
            
            # Placeholder - remplacer par vraie implémentation
            return output_file
            
        except Exception as e:
            self.logger.error(f"Erreur OpenVoice v2 cloning : {e}")
            return None
    
    def _generate_chatterbox_default(self, text):
        """Génère avec Chatterbox par défaut"""
        pass
    
    def _generate_melotts_default(self, text):
        """Génère avec MeloTTS par défaut"""
        pass
    
    def _generate_openvoice_default(self, text):
        """Génère avec OpenVoice v2 par défaut"""
        pass
    
    def synthesize(self, text, person_model=None):
        """
        Synthétise le texte en audio avec le moteur LLM
        
        Args:
            text: Texte à synthétiser
            person_model: Modèle de personne à utiliser
            
        Returns:
            str: Chemin vers le fichier audio généré, ou None en cas d'erreur
        """
        if not self.enabled:
            self.logger.warning("TTS LLM désactivé")
            return None
        
        if not text:
            self.logger.warning("Texte vide")
            return None
        
        # Vérifier le cache d'abord
        cached_file = self._get_cached_file(text, person_model)
        if cached_file:
            return cached_file
        
        # Synthétiser selon le moteur
        audio_file = None
        if self.engine == 'xtts-v2':
            audio_file = self._synthesize_xtts_v2(text, person_model)
        elif self.engine == 'chattts':
            audio_file = self._synthesize_chattts(text, person_model)
        elif self.engine == 'dia':
            audio_file = self._synthesize_dia(text, person_model)
        elif self.engine == 'kokoro':
            audio_file = self._synthesize_kokoro(text, person_model)
        elif self.engine == 'chatterbox':
            audio_file = self._synthesize_chatterbox(text, person_model)
        elif self.engine == 'melotts':
            audio_file = self._synthesize_melotts(text, person_model)
        elif self.engine == 'openvoice-v2':
            audio_file = self._synthesize_openvoice_v2(text, person_model)
        else:
            self.logger.error(f"Moteur TTS LLM non supporté : {self.engine}")
            return None
        
        # Sauvegarder en cache si réussi
        if audio_file and os.path.exists(audio_file):
            self._save_to_cache(text, audio_file, person_model)
            return audio_file
        
        return None
    
    def get_available_models(self):
        """Retourne la liste des modèles disponibles"""
        return self.available_models
    
    def get_available_person_models(self):
        """Retourne la liste des modèles de personnes disponibles"""
        return self.person_models.get(self.engine, {})
    
    def get_model_info(self):
        """Retourne les informations sur le modèle actuel"""
        if self.engine in self.available_models:
            return self.available_models[self.engine]
        return None
    
    def test_synthesis(self, text="Test de synthèse vocale LLM"):
        """Teste la synthèse vocale LLM"""
        self.logger.info(f"Test de synthèse avec le moteur LLM {self.engine}")
        result = self.synthesize(text)
        if result:
            self.logger.info(f"Test réussi : {result}")
            return True
        else:
            self.logger.error("Test échoué")
            return False 