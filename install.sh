#!/bin/bash

echo "🤖 INSTALADOR UNIFICADO - CONTROL DE BRAZO ROBÓTICO CON MANO"
echo "============================================================="
echo ""

# Verificar si Python está instalado
echo "🔍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    echo "💡 Instala Python 3.8 o superior desde: https://python.org"
    exit 1
fi

python_version=$(python3 --version)
echo "✅ $python_version encontrado"

# Verificar si pip está instalado
echo "🔍 Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 no está instalado"
    echo "💡 Instala pip con: sudo apt install python3-pip (Linux) o brew install python (macOS)"
    exit 1
fi

echo "✅ pip3 encontrado"
echo ""

# Actualizar pip
echo "⬆️ Actualizando pip..."
pip3 install --upgrade pip

echo ""
echo "📦 Instalando dependencias principales..."
echo "----------------------------------------"

# Instalar dependencias básicas de Python
echo "🔧 Instalando librerías básicas de Python..."
pip3 install opencv-python==4.8.1.78
pip3 install mediapipe==0.10.7
pip3 install numpy==1.24.3

echo ""
echo "🤖 Instalando dependencias de CoppeliaSim..."
echo "--------------------------------------------"

# Instalar dependencias para CoppeliaSim
echo "🔌 Instalando ZMQ para comunicación..."
pip3 install pyzmq msgpack

echo "🤖 Instalando API de CoppeliaSim..."
pip3 install coppeliasim-zmqremoteapi-client

echo ""
echo "✅ INSTALACIÓN COMPLETADA!"
echo "========================"
echo ""
echo "📋 PRÓXIMOS PASOS:"
echo "1. 🎮 Abrir CoppeliaSim 4.1.0 o superior"
echo "2. 📁 Cargar una escena con robot UR5"
echo "3. ▶️  Iniciar simulación (botón Play)"
echo "4. 🚀 Ejecutar: python3 simple_hand_robot_control.py"
echo ""
echo "🎯 PARA EJECUTAR EL SISTEMA:"
echo "   python3 simple_hand_robot_control.py"
echo ""
echo "🎮 CONTROLES:"
echo "   'q' - Salir"
echo "   'd' - Toggle debug"
echo "   'r' - Reset robot"
echo ""
echo "💡 Si tienes problemas, asegúrate de que:"
echo "   - CoppeliaSim esté ejecutándose"
echo "   - El robot UR5 esté cargado en la escena"
echo "   - La cámara tenga permisos de acceso"
echo ""
