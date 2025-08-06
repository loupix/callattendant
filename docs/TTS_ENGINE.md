# Moteur TTS (Text-to-Speech) pour CallAttendant

## Vue d'ensemble

Le moteur TTS de CallAttendant permet de générer automatiquement des fichiers audio à partir de texte, remplaçant ou complétant les fichiers audio pré-enregistrés. Il supporte plusieurs moteurs de synthèse vocale et inclut un système de cache pour optimiser les performances.

## Fonctionnalités

- **Multiples moteurs TTS** : eSpeak (local), pyttsx3 (local), Google TTS (en ligne), Azure Speech, AWS Polly
- **Système de cache** : Les fichiers audio générés sont mis en cache pour éviter les régénérations
- **Configuration flexible** : Vitesse, volume, langue, voix personnalisables
- **Interface web** : Configuration et test via l'interface web
- **Gestion d'erreurs** : Gestion gracieuse des erreurs et fallback

## Installation

### Dépendances système

#### eSpeak (recommandé pour débuter)
```bash
# Ubuntu/Debian
sudo apt-get install espeak

# CentOS/RHEL
sudo yum install espeak

# macOS
brew install espeak
```

#### pyttsx3 (alternative locale)
```bash
pip install pyttsx3
```

### Dépendances Python

```bash
pip install -r requirements.txt
```

Les dépendances TTS incluent :
- `pyttsx3>=2.90` - Moteur TTS local
- `gTTS>=2.3.1` - Google Text-to-Speech
- `azure-cognitiveservices-speech>=1.31.0` - Azure Speech Services
- `boto3>=1.26.0` - AWS Polly

## Configuration

### Paramètres TTS

| Paramètre | Description | Valeur par défaut |
|-----------|-------------|-------------------|
| `TTS_ENABLED` | Active/désactive le TTS | `False` |
| `TTS_ENGINE` | Moteur TTS à utiliser | `espeak` |
| `TTS_VOICE` | Nom de la voix | `french` |
| `TTS_SPEED` | Vitesse de lecture (0.5-2.0) | `1.0` |
| `TTS_VOLUME` | Volume de sortie (0-100) | `80` |
| `TTS_LANGUAGE` | Langue pour la synthèse | `fr-FR` |
| `TTS_CACHE_DIR` | Répertoire de cache | `data/tts_cache` |
| `TTS_API_KEY` | Clé API (services cloud) | `""` |
| `TTS_API_REGION` | Région (services cloud) | `""` |

### Configuration via interface web

1. Allez dans **Settings** → **Edit Configuration**
2. Configurez la section **Moteur TTS**
3. Utilisez le bouton **Tester TTS** pour vérifier la configuration

### Configuration manuelle

Éditez le fichier `app.cfg` :

```python
# Configuration TTS
TTS_ENABLED = True
TTS_ENGINE = "espeak"
TTS_VOICE = "french"
TTS_SPEED = 1.0
TTS_VOLUME = 80
TTS_LANGUAGE = "fr-FR"
TTS_CACHE_DIR = "data/tts_cache"
TTS_API_KEY = ""
TTS_API_REGION = ""
```

## Moteurs TTS supportés

### 1. eSpeak (local)

**Avantages** : Gratuit, local, rapide, nombreuses langues
**Inconvénients** : Qualité vocale limitée

```python
TTS_ENGINE = "espeak"
TTS_VOICE = "french"  # ou "english", "spanish", etc.
```

### 2. pyttsx3 (local)

**Avantages** : Local, bonne qualité, voix système
**Inconvénients** : Dépend des voix installées

```python
TTS_ENGINE = "pyttsx3"
TTS_VOICE = "french"
```

### 3. Google TTS (en ligne)

**Avantages** : Excellente qualité, nombreuses langues
**Inconvénients** : Nécessite une connexion internet

```python
TTS_ENGINE = "gtts"
TTS_LANGUAGE = "fr-FR"
```

### 4. Azure Speech Services

**Avantages** : Qualité professionnelle, voix naturelles
**Inconvénients** : Payant, nécessite une clé API

```python
TTS_ENGINE = "azure"
TTS_API_KEY = "votre_clé_azure"
TTS_API_REGION = "westeurope"
TTS_VOICE = "fr-FR-Julie-Apollo"
```

### 5. AWS Polly

**Avantages** : Qualité professionnelle, nombreuses voix
**Inconvénients** : Payant, nécessite des clés AWS

```python
TTS_ENGINE = "aws"
TTS_API_KEY = "votre_access_key"
TTS_API_REGION = "votre_secret_key"
TTS_VOICE = "Lea"
```

## Utilisation

### Via l'interface web

1. **Configuration** : Allez dans Settings → Edit Configuration
2. **Test** : Utilisez le bouton "Tester TTS" pour vérifier la configuration
3. **Sauvegarde** : Cliquez sur "Sauvegarder" pour appliquer les changements

### Via l'API Python

```python
from messaging.tts_engine import TTSEngine

# Initialiser le moteur TTS
config = {
    'TTS_ENABLED': True,
    'TTS_ENGINE': 'espeak',
    'TTS_VOICE': 'french',
    'TTS_SPEED': 1.0,
    'TTS_VOLUME': 80,
    'TTS_LANGUAGE': 'fr-FR',
    'TTS_CACHE_DIR': 'data/tts_cache'
}

tts = TTSEngine(config)

# Synthétiser du texte
audio_file = tts.synthesize("Bonjour, ceci est un test.")

if audio_file:
    print(f"Fichier audio généré : {audio_file}")
else:
    print("Erreur de synthèse")
```

### Intégration avec CallAttendant

Le moteur TTS peut être utilisé pour :

1. **Générer des messages d'accueil dynamiques**
2. **Créer des annonces personnalisées**
3. **Remplacer les fichiers audio statiques**
4. **Supporter plusieurs langues**

## Gestion du cache

Le système de cache évite de régénérer les mêmes fichiers audio :

- **Emplacement** : `data/tts_cache/` (configurable)
- **Format** : Fichiers `.wav` avec hash MD5 du texte
- **Nettoyage** : Suppression manuelle recommandée périodiquement

## Dépannage

### Problèmes courants

1. **eSpeak non trouvé**
   ```bash
   sudo apt-get install espeak
   ```

2. **Erreur de permissions**
   ```bash
   chmod 755 data/tts_cache
   ```

3. **Erreur de clé API**
   - Vérifiez que la clé API est correcte
   - Vérifiez les permissions de la clé

4. **Erreur de réseau (services cloud)**
   - Vérifiez la connexion internet
   - Vérifiez les paramètres de proxy

### Logs

Les erreurs TTS sont loggées dans les logs de CallAttendant :

```bash
tail -f /var/log/callattendant.log | grep TTS
```

### Test de diagnostic

```python
from messaging.tts_engine import TTSEngine

config = {
    'TTS_ENABLED': True,
    'TTS_ENGINE': 'espeak',
    'TTS_VOICE': 'french'
}

tts = TTSEngine(config)
success = tts.test_synthesis("Test de diagnostic")
print(f"Test réussi : {success}")
```

## Performance

### Optimisations recommandées

1. **Utilisez le cache** : Évitez de régénérer les mêmes textes
2. **Choisissez un moteur local** : eSpeak ou pyttsx3 pour la rapidité
3. **Limitez la longueur** : Les textes longs prennent plus de temps
4. **Prégénérez** : Créez les fichiers audio importants à l'avance

### Temps de génération approximatifs

| Moteur | Temps moyen (10 mots) |
|--------|----------------------|
| eSpeak | 0.5-1 seconde |
| pyttsx3 | 1-2 secondes |
| Google TTS | 2-5 secondes |
| Azure | 1-3 secondes |
| AWS Polly | 1-3 secondes |

## Sécurité

### Clés API

- **Ne commitez jamais** les clés API dans le code
- **Utilisez des variables d'environnement** pour les clés sensibles
- **Limitez les permissions** des clés API au minimum nécessaire

### Fichiers de cache

- **Vérifiez périodiquement** le contenu du cache
- **Limitez l'espace disque** utilisé par le cache
- **Nettoyez régulièrement** les anciens fichiers

## Support

Pour obtenir de l'aide :

1. **Vérifiez les logs** de CallAttendant
2. **Testez avec l'interface web**
3. **Consultez la documentation** de chaque moteur TTS
4. **Ouvrez une issue** sur GitHub si nécessaire

## Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. **Fork** le projet
2. **Créez une branche** pour votre fonctionnalité
3. **Ajoutez des tests** pour les nouvelles fonctionnalités
4. **Soumettez une pull request**

## Licence

Ce module TTS est distribué sous la même licence que CallAttendant. 