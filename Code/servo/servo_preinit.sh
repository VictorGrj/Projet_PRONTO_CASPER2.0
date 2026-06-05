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
