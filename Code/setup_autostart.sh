#!/bin/bash

# /!\ Déplacer ce fichier vers le chemin "/home/grp10/setup_autostart.sh" /!\

# Script de configuration pour le démarrage automatique du robot P10 (version améliorée)
# À exécuter avec les privilèges sudo

echo "=== Configuration du démarrage automatique du robot P10 (avec pré-init servo) ==="

# Vérifier que le script est exécuté avec sudo
if [ "$EUID" -ne 0 ]; then
    echo "Erreur: Ce script doit être exécuté avec sudo"
    echo "Usage: sudo bash setup_autostart.sh"
    exit 1
fi

# Vérifier l'existence des fichiers nécessaires
PYTHON_VENV="/home/grp10/p10/bin/python"
MAIN_SCRIPT="/home/grp10/p10/projet-pronto/Main.py"
SCRIPTS_DIR="/home/grp10/p10/projet-pronto/servo"

if [ ! -f "$PYTHON_VENV" ]; then
    echo "Erreur: L'environnement virtuel Python n'existe pas à $PYTHON_VENV"
    exit 1
fi

if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "Erreur: Le script Main.py n'existe pas à $MAIN_SCRIPT"
    exit 1
fi

# Créer le script de pré-initialisation des servos
SERVO_PREINIT_SCRIPT="$SCRIPTS_DIR/servo_preinit.sh"
cat > "$SERVO_PREINIT_SCRIPT" << 'EOF'
#!/bin/bash

echo "=== Pré-initialisation des servomoteurs ==="

# Configurer le GPIO 17 (pin OE) pour désactiver les servos
echo "17" > /sys/class/gpio/export 2>/dev/null || true
echo "out" > /sys/class/gpio/gpio17/direction
echo "1" > /sys/class/gpio/gpio17/value

echo "✓ Servomoteurs désactivés (OE = HIGH)"

# Attendre que le réseau soit disponible
echo "Attente de la connexion réseau..."
timeout=60
counter=0
while ! ping -c 1 8.8.8.8 &> /dev/null && [ $counter -lt $timeout ]; do
    sleep 1
    counter=$((counter + 1))
done

if [ $counter -lt $timeout ]; then
    echo "✓ Connexion réseau établie"
else
    echo "⚠ Timeout réseau - continuation sans réseau"
fi

echo "Pré-initialisation terminée. Lancement du programme principal..."
EOF

# Rendre le script exécutable
chmod +x "$SERVO_PREINIT_SCRIPT"
chown grp10:grp10 "$SERVO_PREINIT_SCRIPT"

echo "✓ Script de pré-initialisation créé à $SERVO_PREINIT_SCRIPT"

# Créer le service de pré-initialisation
PREINIT_SERVICE_FILE="/etc/systemd/system/robot-p10-preinit.service"
cat > "$PREINIT_SERVICE_FILE" << EOF
[Unit]
Description=Robot P10 Servo Pre-initialization
DefaultDependencies=false
After=local-fs.target
Before=robot-p10.service

[Service]
Type=oneshot
ExecStart=$SERVO_PREINIT_SCRIPT
RemainAfterExit=yes
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service de pré-initialisation créé à $PREINIT_SERVICE_FILE"

# Créer le fichier de service principal modifié
MAIN_SERVICE_FILE="/etc/systemd/system/robot-p10.service"
cat > "$MAIN_SERVICE_FILE" << 'EOF'
[Unit]
Description=Robot P10 Service
After=network.target
After=sound.target
After=graphical-session.target
After=robot-p10-preinit.service
Wants=graphical-session.target
Requires=robot-p10-preinit.service

[Service]
Type=simple
User=grp10
Group=grp10
WorkingDirectory=/home/grp10/p10/projet-pronto
Environment=DISPLAY=:0
Environment=PULSE_RUNTIME_PATH=/run/user/1000/pulse
ExecStart=/home/grp10/p10/bin/python /home/grp10/p10/projet-pronto/Main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Fichier de service principal créé à $MAIN_SERVICE_FILE"

# Recharger systemd pour prendre en compte les nouveaux services
systemctl daemon-reload
echo "✓ Configuration systemd rechargée"

# Activer les services pour qu'ils démarrent automatiquement
systemctl enable robot-p10-preinit.service
systemctl enable robot-p10.service
echo "✓ Services robot-p10-preinit et robot-p10 activés pour le démarrage automatique"

# Démarrer les services immédiatement (optionnel)
read -p "Voulez-vous démarrer les services maintenant ? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl start robot-p10-preinit.service
    systemctl start robot-p10.service
    echo "✓ Services démarrés"
    
    # Attendre un peu et afficher le statut
    sleep 2
    echo ""
    echo "=== Statut des services ==="
    systemctl status robot-p10-preinit.service --no-pager
    echo ""
    systemctl status robot-p10.service --no-pager
fi

echo ""
echo "=== Configuration terminée ==="
echo "Les servomoteurs seront désactivés dès le démarrage système."
echo "Le robot P10 se lancera automatiquement après stabilisation du réseau."
echo ""
echo "Commandes utiles :"
echo "  - Voir le statut :          sudo systemctl status robot-p10"
echo "  - Voir les logs :           sudo journalctl -u robot-p10 -f"
echo "  - Voir les logs pré-init :  sudo journalctl -u robot-p10-preinit -f"
echo "  - Arrêter le service :      sudo systemctl stop robot-p10"
echo "  - Démarrer le service:      sudo systemctl start robot-p10"
echo "  - Désactiver l'auto-démarrage: sudo systemctl disable robot-p10"
