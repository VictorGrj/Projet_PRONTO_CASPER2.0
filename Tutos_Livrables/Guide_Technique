#Guide technique – Casper 2.0

##Présentation

Ce document décrit l’architecture matérielle et logicielle du robot Casper 2.0 ainsi que son fonctionnement global.
Il a pour objectif de permettre à un utilisateur ou futur développeur de comprendre et reproduire le système.

---

#1. Organisation du système

Le robot repose sur une architecture embarquée autour d’une Raspberry Pi 4.

### Modules principaux :

- Interaction vocale (Vosk + Gemini + Piper)
- Suivi visuel (OpenCV)
- Contrôle moteurs (PCA9685 + servomoteurs)
- Interface visuelle (Pygame)

---

# 2. Composants électroniques

## Matériel utilisé

- Raspberry Pi 4 Model B
- Caméra Raspberry Pi
- ReSpeaker Pi HAT (micro + audio)
- Écran LCD (affichage visage)
- Servomoteurs (bras + tête)
- Module PCA9685 (contrôle PWM)
- Bouton poussoir
- Résistance 1 kΩ

---

## Interfaces matérielles

- GPIO 4 → Bouton poussoir
- GPIO 17 → Contrôle servomoteurs (OE)
- I2C → PCA9685 (servomoteurs + bus)

---

# 3. Architecture logicielle

Le code est écrit en Python et repose sur un système multi-thread.

## Modules principaux

| Module | Rôle |
|--------|------|
| `Main.py` | Orchestration globale + machine à états |
| `AudioProcessing.py` | Capture audio + reconnaissance + IA |
| `Speak.py` | Lecture des fichiers audio |
| `CameraTracking.py` | Suivi visuel |
| `Servo.py` | Contrôle des moteurs |
| `Screen.py` | Interface graphique |

---

# 4. Fonctionnement global

## Cycle d’interaction

1. L’utilisateur appuie sur le bouton
2. Le micro enregistre la voix
3. Vosk transforme la voix en texte
4. Gemini génère une réponse
5. Piper transforme le texte en audio
6. Le robot parle et bouge

---

## États du robot

- `waiting` → attente utilisateur
- `thinking` → traitement IA
- `speaking` → réponse audio
- `teaching` → explication
- `idle` → repos

---

# 5. Suivi visuel

Le module `CameraTracking.py` utilise :

- OpenCV
- Haar Cascade (détection de visage)
- Calcul du centre du visage
- Correction du servo moteur de la tête

Objectif : garder l’utilisateur centré dans le champ de vision.

---

# 6. Contrôle des servomoteurs

## Carte utilisée

- PCA9685 (I2C)
- Permet de gérer plusieurs servomoteurs en PWM

## Mouvements

- Bras gauche
- Bras droit
- Tête (tracking visage)

Les mouvements sont simplifiés pour éviter une surcharge CPU.

---

# 7. Système audio

## Entrée audio

- ReSpeaker Pi HAT
- Capture du signal audio
- Activation via bouton poussoir

## Traitement

- Vosk → transcription texte
- Gemini → génération réponse IA

## Sortie audio

- Piper TTS
- Lecture du fichier `.wav`

---

# 8. Interface graphique

- Bibliothèque : `pygame`
- Affichage des expressions du robot :

| Mode | Description |
|------|-------------|
| waiting | attente utilisateur |
| thinking | traitement IA |
| speaking | parole |
| teaching | explication |

---

# 9. Problèmes rencontrés

- Limitation CPU Raspberry Pi
- Latence du suivi visuel
- Bruit moteur perturbant le micro
- Limites API Gemini
- Reconnaissance vocale sensible au bruit

---

# 10. Améliorations possibles

- Passage à Raspberry Pi 5
- Remplacement Haar Cascade → MediaPipe
- Ajout mémoire conversationnelle
- Activation vocale (wake word)
- Amélioration fluidité des servomoteurs

---

# Conclusion

Casper 2.0 est un robot interactif complet combinant :

- Vision
- Audio
- Intelligence artificielle
- Mécanique embarquée

Il constitue une plateforme expérimentale de robot compagnon interactif.
