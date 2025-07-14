#!/usr/bin/env python3
"""
Script de verificación para el sistema avanzado de control
Prueba todos los componentes sin conectar hardware
"""

import sys
import os
import traceback

# Agregar src al path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_imports():
    """Prueba todas las importaciones."""
    print("🧪 Probando importaciones...")
    
    tests = [
        ("numpy", "import numpy as np"),
        ("opencv", "import cv2"),
        ("matplotlib", "import matplotlib.pyplot as plt"),
        ("tkinter", "import tkinter as tk"),
        ("mediapipe", "import mediapipe as mp"),
        ("scipy", "import scipy"),
        ("pandas", "import pandas as pd"),
    ]
    
    results = []
    for name, import_cmd in tests:
        try:
            exec(import_cmd)
            print(f"  ✅ {name}")
            results.append(True)
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            results.append(False)
    
    return all(results)

def test_modules():
    """Prueba los módulos del proyecto."""
    print("\n🔧 Probando módulos del proyecto...")
    
    modules = [
        ("ControllerManager", "from control.controller_manager import ControllerManager"),
        ("ErrorCalculator", "from analysis.error_calculator import ErrorCalculator"),
        ("RealTimePlotter", "from visualization.real_time_plotter import RealTimePlotter"),
        ("GUIManager", "from visualization.gui_manager import GUIManager"),
        ("CameraManager", "from utils.camera_manager import CameraManager"),
        ("MediaPipeDetector", "from tracking.mediapipe_detector import MediaPipeHandDetector"),
    ]
    
    results = []
    for name, import_cmd in modules:
        try:
            exec(import_cmd)
            print(f"  ✅ {name}")
            results.append(True)
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            results.append(False)
        except Exception as e:
            print(f"  ⚠️ {name}: {e}")
            results.append(False)
    
    return all(results)

def test_basic_functionality():
    """Prueba funcionalidad básica sin hardware."""
    print("\n⚙️ Probando funcionalidad básica...")
    
    try:
        # Test ControllerManager
        from control.controller_manager import ControllerManager, ControlMode
        controller = ControllerManager()
        controller.set_control_mode(ControlMode.CLOSED_LOOP)
        print("  ✅ ControllerManager")
        
        # Test ErrorCalculator
        from analysis.error_calculator import ErrorCalculator
        import numpy as np
        error_calc = ErrorCalculator()
        error_calc.update(np.array([0.1, 0.1, 0.5]), np.array([0.0, 0.0, 0.5]))
        print("  ✅ ErrorCalculator")
        
        # Test RealTimePlotter (sin mostrar)
        from visualization.real_time_plotter import RealTimePlotter
        import matplotlib
        matplotlib.use('Agg')  # Backend sin GUI para prueba
        plotter = RealTimePlotter()
        plotter.update_data(0.1, 0.05, np.array([0.1, 0.1, 0.5]), np.array([0.0, 0.0, 0.5]))
        print("  ✅ RealTimePlotter")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error en funcionalidad: {e}")
        traceback.print_exc()
        return False

def test_gui_creation():
    """Prueba creación de GUI sin mostrarla."""
    print("\n🖥️ Probando creación de GUI...")
    
    try:
        import tkinter as tk
        from visualization.gui_manager import GUIManager
        
        # Crear root sin mostrar
        root = tk.Tk()
        root.withdraw()  # Ocultar ventana
        
        # Probar creación de componentes
        gui_manager = GUIManager()
        control_panel = gui_manager.get_control_panel()
        
        # Limpiar
        root.destroy()
        
        print("  ✅ GUI creada exitosamente")
        return True
        
    except Exception as e:
        print(f"  ❌ Error en GUI: {e}")
        traceback.print_exc()
        return False

def main():
    """Función principal de verificación."""
    print("🚀 VERIFICACIÓN DEL SISTEMA AVANZADO DE CONTROL")
    print("=" * 50)
    
    tests = [
        ("Importaciones básicas", test_imports),
        ("Módulos del proyecto", test_modules),
        ("Funcionalidad básica", test_basic_functionality),
        ("Creación de GUI", test_gui_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append(result)
            status = "✅ EXITOSO" if result else "❌ FALLIDO"
            print(f"   {status}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results)
    
    print(f"Total de pruebas: {total_tests}")
    print(f"Exitosas: {passed_tests}")
    print(f"Fallidas: {total_tests - passed_tests}")
    
    if all(results):
        print("\n🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("El sistema está listo para ejecutarse.")
        print("\nEjecuta:")
        print("  make run-advanced")
        print("  o")
        print("  python3 advanced_hand_robot_control.py")
    else:
        print("\n⚠️ ALGUNAS PRUEBAS FALLARON")
        print("Revisa las dependencias e instalación.")
        print("\nIntenta:")
        print("  pip install -r requirements.txt")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
