#!/bin/bash

echo "=== Instalando dependencias para Hand Tracking System ==="

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado"
    exit 1
fi

echo "Versión de Python:"
python3 --version

# Verificar si pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 no está instalado"
    exit 1
fi

echo "Instalando dependencias..."

# Instalar dependencias
pip3 install -r requirements.txt

echo ""
echo "=== Instalación completada ==="
echo ""
echo "Para ejecutar el sistema de tracking:"
echo "  cd src"
echo "  python3 main_tracking.py"
echo ""
echo "Para ejecutar las pruebas:"
echo "  cd tests"
echo "  python3 test_tracking.py"
