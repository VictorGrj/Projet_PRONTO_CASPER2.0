#Casper 2.0 – Robot interactif
#Installation

##Prérequis
- Raspberry Pi 4 avec Raspberry Pi OS 64-bit
- Connexion Internet
- Accès SSH ou écran + clavier
- Caméra, ReSpeaker Pi HAT, servomoteurs

##Procédure d'installation

1. Connexion SSH :
   ```bash
   ssh grp10@rpi.local

2. Cloner le projet7
git clone https://github.com/VictorGrj/Projet_PRONTO_CASPER2.0.git
cd Projet_PRONTO_CASPER2.0

3. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

4. Installer les dépendances Python
pip install --upgrade pip
pip install -r requirements.txt

5. Installer les dépendances système
sudo apt install portaudio19-dev libasound2-dev python3-opencv

6. Activer I2C
sudo raspi-config
Naviguez vers : Interface Options → I2C → Enable

7. Lancer le projet
python Main.py
