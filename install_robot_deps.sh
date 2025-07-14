#!/bin/bash

echo "🚀 Instalando dependencias para control de brazo robótico"
echo "================================================"

# Instalar dependencias básicas
echo "📦 Instalando dependencias básicas..."
pip3 install pyzmq msgpack

# Instalar API de CoppeliaSim
echo "🤖 Instalando API de CoppeliaSim..."
pip3 install coppeliasim-zmqremoteapi-client

echo ""
echo "✅ Instalación completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Abrir CoppeliaSim"
echo "2. Cargar una escena con el robot UR5"
echo "3. Ejecutar: python3 simple_hand_robot_control.py"
