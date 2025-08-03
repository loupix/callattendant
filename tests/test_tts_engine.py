#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  test_tts_engine.py
#
#  Copyright 2024 Loupix  <loupix@github.com>
#
#  Tests unitaires pour le moteur TTS

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock

# Import du module à tester
import sys
sys.path.append('..')
from messaging.tts_engine import TTSEngine


class TestTTSEngine(unittest.TestCase):
    """Tests pour le moteur TTS"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.config = {
            'TTS_ENABLED': True,
            'TTS_ENGINE': 'espeak',
            'TTS_VOICE': 'french',
            'TTS_SPEED': 1.0,
            'TTS_VOLUME': 80,
            'TTS_LANGUAGE': 'fr-FR',
            'TTS_CACHE_DIR': tempfile.mkdtemp(),
            'TTS_API_KEY': '',
            'TTS_API_REGION': ''
        }
    
    def tearDown(self):
        """Nettoyage après les tests"""
        # Supprimer le répertoire de cache temporaire
        if os.path.exists(self.config['TTS_CACHE_DIR']):
            import shutil
            shutil.rmtree(self.config['TTS_CACHE_DIR'])
    
    def test_init_disabled(self):
        """Test initialisation avec TTS désactivé"""
        config = self.config.copy()
        config['TTS_ENABLED'] = False
        
        tts = TTSEngine(config)
        self.assertFalse(tts.enabled)
    
    def test_init_enabled(self):
        """Test initialisation avec TTS activé"""
        tts = TTSEngine(self.config)
        self.assertTrue(tts.enabled)
        self.assertEqual(tts.engine, 'espeak')
        self.assertEqual(tts.voice, 'french')
    
    @patch('subprocess.run')
    def test_espeak_initialization(self, mock_run):
        """Test initialisation eSpeak"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "eSpeak text-to-speech"
        
        tts = TTSEngine(self.config)
        self.assertEqual(tts.engine, 'espeak')
    
    def test_synthesize_disabled(self):
        """Test synthèse avec TTS désactivé"""
        config = self.config.copy()
        config['TTS_ENABLED'] = False
        
        tts = TTSEngine(config)
        result = tts.synthesize("Test")
        self.assertIsNone(result)
    
    def test_synthesize_empty_text(self):
        """Test synthèse avec texte vide"""
        tts = TTSEngine(self.config)
        result = tts.synthesize("")
        self.assertIsNone(result)
    
    def test_cache_filename_generation(self):
        """Test génération nom de fichier cache"""
        tts = TTSEngine(self.config)
        filename = tts._get_cache_filename("Test de synthèse")
        self.assertTrue(filename.endswith('.wav'))
        self.assertEqual(len(filename), 32 + 4)  # hash MD5 + .wav
    
    def test_get_cached_file_none(self):
        """Test récupération fichier cache inexistant"""
        tts = TTSEngine(self.config)
        result = tts._get_cached_file("Texte inexistant")
        self.assertIsNone(result)
    
    def test_get_available_voices(self):
        """Test récupération voix disponibles"""
        tts = TTSEngine(self.config)
        voices = tts.get_available_voices()
        # Peut être vide si eSpeak n'est pas installé
        self.assertIsInstance(voices, list)
    
    def test_test_synthesis(self):
        """Test fonction de test de synthèse"""
        tts = TTSEngine(self.config)
        # Le test peut échouer si eSpeak n'est pas installé
        # mais on vérifie que la fonction ne plante pas
        try:
            result = tts.test_synthesis()
            self.assertIsInstance(result, bool)
        except Exception as e:
            # Acceptable si eSpeak n'est pas installé
            self.assertIn("eSpeak", str(e) or "FileNotFoundError", str(e))
    
    def test_invalid_engine(self):
        """Test moteur TTS invalide"""
        config = self.config.copy()
        config['TTS_ENGINE'] = 'invalid_engine'
        
        tts = TTSEngine(config)
        result = tts.synthesize("Test")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main() 