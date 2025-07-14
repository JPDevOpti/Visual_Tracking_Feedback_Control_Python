.PHONY: install run test clean help

# Variables
PYTHON = python3
SRC_DIR = src
TEST_DIR = tests

# Ayuda
help:
	@echo "=== Hand Tracking System - Comandos disponibles ==="
	@echo ""
	@echo "  make install       - Instalar dependencias básicas"
	@echo "  make install-robot - Instalar dependencias para control robótico"
	@echo "  make run           - Ejecutar el sistema de tracking"
	@echo "  make run-robot     - Ejecutar control simple de brazo robótico"
	@echo "  make test          - Ejecutar pruebas"
	@echo "  make test-robot    - Probar configuración de CoppeliaSim"
	@echo "  make diagnose      - Diagnosticar cámara y permisos"
	@echo "  make clean         - Limpiar archivos temporales"
	@echo "  make check         - Verificar estructura del proyecto"
	@echo "  make help          - Mostrar esta ayuda"
	@echo ""

# Instalar dependencias
install:
	@echo "Instalando dependencias..."
	pip3 install -r requirements.txt
	@echo "Instalación completada"

# Ejecutar el sistema principal
run:
	@echo "Iniciando sistema de tracking de mano..."
	cd $(SRC_DIR) && $(PYTHON) main_tracking.py

# Ejecutar control simple de brazo robótico
run-robot:
	@echo "Iniciando control simple de brazo robótico..."
	PYTHONPATH=src $(PYTHON) simple_hand_robot_control.py

# Instalar dependencias para control robótico
install-robot:
	@echo "Instalando dependencias para control robótico..."
	pip3 install pyzmq msgpack coppeliasim-zmqremoteapi-client
	@echo "Dependencias de robot instaladas"

# Probar configuración de CoppeliaSim
test-robot:
	@echo "Probando configuración de CoppeliaSim..."
	$(PYTHON) test_coppeliasim_setup.py

# Ejecutar pruebas
test:
	@echo "Ejecutando pruebas..."
	cd $(TEST_DIR) && $(PYTHON) test_tracking.py

# Limpiar archivos temporales
clean:
	@echo "Limpiando archivos temporales..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "Limpieza completada"

# Verificar estructura del proyecto
check:
	@echo "Verificando estructura del proyecto..."
	@echo "Archivos principales:"
	@ls -la $(SRC_DIR)/main_tracking.py 2>/dev/null && echo "✓ main_tracking.py" || echo "✗ main_tracking.py faltante"
	@ls -la $(SRC_DIR)/tracking/mediapipe_detector.py 2>/dev/null && echo "✓ mediapipe_detector.py" || echo "✗ mediapipe_detector.py faltante"
	@ls -la $(SRC_DIR)/utils/camera_manager.py 2>/dev/null && echo "✓ camera_manager.py" || echo "✗ camera_manager.py faltante"
	@ls -la requirements.txt 2>/dev/null && echo "✓ requirements.txt" || echo "✗ requirements.txt faltante"

# Diagnóstico de cámara y permisos
diagnose:
	@echo "Ejecutando diagnóstico de cámara..."
	$(PYTHON) $(SRC_DIR)/diagnose_camera.py
