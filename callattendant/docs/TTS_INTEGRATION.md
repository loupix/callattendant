# Intégration TTS (Text-to-Speech) dans CallAttendant

Ce document explique comment utiliser le moteur de synthèse vocale intégré dans CallAttendant.

## Vue d'ensemble

Le module TTS utilise le modèle XTTS v2 de Coqui TTS pour générer des fichiers audio de haute qualité à partir de texte en français. Il s'intègre parfaitement avec l'architecture existante de CallAttendant.

## Installation

### 1. Dépendances requises

Ajoutez les dépendances TTS à votre environnement :

```bash
pip install -r requirements.txt
```

Les nouvelles dépendances ajoutées sont :
- `TTS>=0.22.0` - Moteur de synthèse vocale
- `pydub>=0.25.1` - Manipulation audio
- `simpleaudio>=1.0.4` - Lecture audio
- `torch>=1.13.0` - Framework PyTorch
- `torchaudio>=0.13.0` - Audio pour PyTorch

### 2. Premier téléchargement

Lors de la première utilisation, le modèle XTTS v2 sera automatiquement téléchargé (environ 1.5 GB). Cela peut prendre quelques minutes selon votre connexion internet.

## Utilisation basique

### Initialisation

```python
from messaging.tts_engine import TTSEngine

# Configuration
config = {"DEBUG": True}

# Initialiser le moteur TTS
engine = TTSEngine(config)
```

### Génération d'audio

```python
# Générer un fichier WAV
text = "Bonjour, bienvenue chez CallAttendant."
audio_file = engine.generate_wav(text, "Zacharie Aimilios")

# Jouer l'audio
engine.play_audio(audio_file)
```

## Speakers disponibles

Le système propose 50+ voix différentes. Voici les speakers recommandés :

### Voix masculines
- `Zacharie Aimilios` - Voix claire et professionnelle
- `Dionisio Schuyler` - Voix chaleureuse
- `Abrahan Mack` - Voix posée
- `Luis Moray` - Voix dynamique

### Voix féminines
- `Claribel Dervla` - Voix douce
- `Daisy Studious` - Voix claire
- `Ana Florence` - Voix professionnelle

## Intégration avec les intents

### Fichier intents.json

Créez un fichier `resources/intents.json` avec vos réponses :

```json
{
  "intents": [
    {
      "tag": "greeting",
      "patterns": ["bonjour", "salut"],
      "responses": [
        "Bonjour, bienvenue chez CallAttendant. Comment puis-je vous aider ?",
        "Salut ! Je suis votre assistant vocal."
      ]
    }
  ]
}
```

### Génération automatique

```python
# Générer tous les audios depuis les intents
engine.generate_audios_from_intents()
```

## Exemples d'utilisation

### Exemple 1 : Utilisation simple

```python
from messaging.tts_engine import TTSEngine

config = {"DEBUG": True}
engine = TTSEngine(config)

# Générer et jouer un message
text = "Votre message a été enregistré avec succès."
audio_file = engine.generate_wav(text, "Zacharie Aimilios")
engine.play_audio(audio_file)
```

### Exemple 2 : Intégration dans VoiceMail

```python
# Dans votre classe VoiceMail
def play_tts_message(self, text, speaker="Zacharie Aimilios"):
    """Joue un message TTS généré dynamiquement"""
    tts_engine = TTSEngine(self.config)
    audio_file = tts_engine.generate_wav(text, speaker)
    
    if audio_file and os.path.exists(audio_file):
        # Utiliser le modem existant pour jouer l'audio
        self.modem.play_audio(audio_file)
        return True
    return False
```

### Exemple 3 : Messages personnalisés

```python
def generate_personalized_greeting(self, caller_name):
    """Génère un message de bienvenue personnalisé"""
    text = f"Bonjour {caller_name}, bienvenue chez CallAttendant."
    return self.play_tts_message(text, "Dionisio Schuyler")
```

## Configuration avancée

### Paramètres du moteur TTS

```python
# Initialisation avec paramètres personnalisés
engine = TTSEngine(
    config=config,
    language='fr',
    audios_dir="resources/custom_audios"
)
```

### Optimisation des performances

- Les fichiers audio sont mis en cache automatiquement
- La conversion en 8kHz/8-bit est optimisée pour les systèmes téléphoniques
- Le modèle est chargé une seule fois en mémoire

## Structure des fichiers

```
callattendant/
├── messaging/
│   └── tts_engine.py          # Module TTS principal
├── resources/
│   ├── intents.json           # Fichier d'intents
│   └── tts_audios/            # Dossier des audios générés
│       ├── Zacharie_Aimilios/ # Audios par speaker
│       └── Dionisio_Schuyler/
└── examples/
    └── tts_example.py         # Exemples d'utilisation
```

## Tests et exemples

### Lancer les exemples

```bash
cd callattendant
python examples/tts_example.py
```

### Test interactif

```bash
cd callattendant/messaging
python tts_engine.py
```

## Dépannage

### Erreurs courantes

1. **Modèle non trouvé** : Vérifiez votre connexion internet pour le téléchargement initial
2. **Erreur de mémoire** : Le modèle XTTS nécessite environ 2GB de RAM
3. **Erreur audio** : Vérifiez que `simpleaudio` est installé correctement

### Logs de débogage

Activez le mode DEBUG dans la configuration :

```python
config = {"DEBUG": True}
engine = TTSEngine(config)
```

## Intégration future

Le module TTS est conçu pour s'intégrer facilement avec :
- Le système de messagerie vocale existant
- Les menus interactifs
- Les notifications personnalisées
- Les réponses dynamiques basées sur l'IA

## Support

Pour toute question ou problème avec l'intégration TTS, consultez :
- La documentation de Coqui TTS : https://tts.readthedocs.io/
- Les exemples dans `callattendant/examples/`
- Les logs de débogage avec `DEBUG=True` 