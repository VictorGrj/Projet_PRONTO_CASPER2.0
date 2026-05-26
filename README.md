# Casper 2.0 – Robot interactif compagnon

Projet PRONTO – IMT Atlantique (S6 2025–2026 – Campus de Brest)

---

## Description

Casper 2.0 est un robot compagnon interactif développé dans le cadre du projet PRONTO.

L’objectif est d’améliorer une plateforme robotique existante afin de rendre les interactions **plus naturelles et multimodales**, en combinant :

- Interaction vocale en langage naturel
- Suivi visuel de l’utilisateur en temps réel
- Gestuelle synchronisée avec la parole
- Dialogue via intelligence artificielle (Google Gemini)

---

## Architecture du système

Le système repose sur une **Raspberry Pi** comme unité centrale, connectée à plusieurs modules :

- Caméra (vision)
- ReSpeaker Pi HAT (audio)
- API Gemini (IA)
- Synthèse vocale Piper
- Servomoteurs (PCA9685 via I2C)
- Interface graphique (Pygame)

---

## Architecture logicielle

Le projet est entièrement développé en **Python** avec une architecture multi-thread :

| Module | Rôle |
|------|------|
| `Main.py` | Orchestration globale (machine à états) |
| `AudioProcessing.py` | Capture audio + STT + IA + TTS |
| `CameraTracking.py` | Détection et suivi du visage |
| `Servo.py` | Contrôle des moteurs |
| `Screen.py` | Interface visuelle (expressions) |
| `Speak.py` | Lecture audio |

---

## Pipeline vocal

1. Capture audio via ReSpeaker
2. Transcription via **Vosk**
3. Traitement de la requête via **Google Gemini API**
4. Synthèse vocale via **Piper TTS**
5. Lecture audio synchronisée avec les mouvements

---

## Suivi visuel

- Détection de visage via **OpenCV (Haar Cascade)**
- Calcul du centre du visage
- Correction du servo moteur de la tête via PCA9685
- Arrêt automatique du tracking pendant la prise de parole

---

## Gestuelle

- Animation des bras synchronisée avec la parole
- Mouvements simplifiés pour réduire la charge CPU
- Optimisation pour Raspberry Pi (limitation des threads et PWM)

---

## Équipe projet

Projet réalisé par une équipe de 5 étudiants :

| Nom |
|-----|
| Greillier Matthieu |
| Lunven Nathan |
| Miannay Benjamin |
| Seillé Gautier |
| Garajeu Victor |

---

## Installation

```bash
git clone https://github.com/VictorGrj/Projet_PRONTO_CASPER2.0.git
cd Projet_PRONTO_CASPER2.0
pip install -r requirements.txt
