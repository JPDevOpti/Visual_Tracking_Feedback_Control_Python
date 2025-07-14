#!/usr/bin/env python3
"""
Script de diagnóstico para verificar cámaras y permisos en macOS.
"""

import cv2
import sys
import subprocess
import platform

def check_system_info():
    """Verificar información del sistema."""
    print("=== INFORMACIÓN DEL SISTEMA ===")
    print(f"Sistema operativo: {platform.system()}")
    print(f"Versión: {platform.release()}")
    print(f"Arquitectura: {platform.machine()}")
    print(f"Python: {sys.version}")
    print(f"OpenCV: {cv2.__version__}")
    print()

def check_camera_permissions():
    """Verificar permisos de cámara en macOS."""
    if platform.system() != "Darwin":
        print("Este diagnóstico es específico para macOS")
        return
    
    print("=== VERIFICACIÓN DE PERMISOS DE CÁMARA ===")
    
    try:
        # Verificar cámaras del sistema
        result = subprocess.run(['system_profiler', 'SPCameraDataType'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Cámaras detectadas por el sistema:")
            print(result.stdout)
        else:
            print("No se pudo obtener información de cámaras del sistema")
    
    except Exception as e:
        print(f"Error al verificar cámaras del sistema: {e}")
    
    print()

def test_camera_access():
    """Probar acceso directo a las cámaras."""
    print("=== PRUEBA DE ACCESO A CÁMARAS ===")
    
    successful_cameras = []
    
    for camera_index in range(5):
        print(f"Probando cámara {camera_index}...")
        
        try:
            cap = cv2.VideoCapture(camera_index)
            
            if cap.isOpened():
                print(f"  ✓ Cámara {camera_index} se puede abrir")
                
                # Intentar capturar un frame
                ret, frame = cap.read()
                
                if ret and frame is not None:
                    height, width = frame.shape[:2]
                    print(f"  ✓ Frame capturado: {width}x{height}")
                    successful_cameras.append(camera_index)
                else:
                    print(f"  ✗ No se puede capturar frame de cámara {camera_index}")
                
                cap.release()
            else:
                print(f"  ✗ No se puede abrir cámara {camera_index}")
        
        except Exception as e:
            print(f"  ✗ Error con cámara {camera_index}: {e}")
    
    print()
    print(f"Cámaras funcionales encontradas: {successful_cameras}")
    return successful_cameras

def show_permission_instructions():
    """Mostrar instrucciones para otorgar permisos."""
    if platform.system() == "Darwin":
        print("=== INSTRUCCIONES PARA OTORGAR PERMISOS EN macOS ===")
        print()
        print("Si no se detectaron cámaras funcionales:")
        print()
        print("1. Abrir 'Configuración del Sistema' (System Settings)")
        print("2. Ir a 'Privacidad y Seguridad' (Privacy & Security)")
        print("3. Buscar 'Cámara' en la lista de la izquierda")
        print("4. Habilitar el acceso para:")
        print("   - Terminal (si ejecutas desde terminal)")
        print("   - Python")
        print("   - Visual Studio Code (si ejecutas desde VS Code)")
        print()
        print("5. Reiniciar el terminal o aplicación después de otorgar permisos")
        print("6. Ejecutar de nuevo este diagnóstico")
        print()
        print("Alternativamente, puedes ejecutar desde un terminal nuevo:")
        print("  sudo python3 src/main_tracking.py")
        print()

def main():
    """Función principal del diagnóstico."""
    print("🔍 DIAGNÓSTICO DE CÁMARA Y PERMISOS")
    print("=" * 50)
    print()
    
    check_system_info()
    check_camera_permissions()
    
    cameras = test_camera_access()
    
    if cameras:
        print("✅ DIAGNÓSTICO EXITOSO")
        print(f"Se encontraron {len(cameras)} cámara(s) funcional(es)")
        print("Puedes ejecutar el sistema de tracking con:")
        print("  make run")
    else:
        print("❌ PROBLEMA DETECTADO")
        print("No se encontraron cámaras funcionales")
        show_permission_instructions()

if __name__ == "__main__":
    main()
