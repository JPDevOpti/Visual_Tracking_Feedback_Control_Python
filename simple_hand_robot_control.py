#!/usr/bin/env python3
"""
Sistema Simple de Control de Brazo Robótico con Mano
Control directo del UR5 en CoppeliaSim usando tracking de manos
"""

import cv2
import time
import sys
import os
import numpy as np

# Agregar el directorio src al path para los imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

try:
    from utils.camera_manager import CameraManager
    from tracking.mediapipe_detector import MediaPipeHandDetector
    from control.coppeliasim_robot_arm import CoppeliaSimRobotArm
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print(f"💡 Directorio actual: {current_dir}")
    print(f"💡 Directorio src: {src_dir}")
    print("💡 Verifica que los archivos existan en src/")
    sys.exit(1)


class SimpleHandRobotControl:
    """
    Sistema simple para controlar robot con movimientos de mano.
    """
    
    def __init__(self):
        """Inicializa el sistema de control simple."""
        print("🤖 Inicializando Sistema Simple de Control Mano-Robot")
        
        # Componentes del sistema
        self.camera = CameraManager(camera_index=0, width=640, height=480)
        self.hand_detector = MediaPipeHandDetector(max_hands=1, min_detection_confidence=0.7)
        self.robot = CoppeliaSimRobotArm()
        
        # Estado del sistema
        self.is_running = False
        self.show_debug = True
        
        # Mapeo simple de coordenadas (cámara -> robot)
        self.camera_width = 640
        self.camera_height = 480
        
        # Workspace del robot (en metros)
        self.robot_x_range = (-0.3, 0.3)  # -30cm a +30cm
        self.robot_y_range = (-0.3, 0.3)  # -30cm a +30cm  
        self.robot_z_fixed = 0.5          # Altura fija de 50cm
        
        # Variables para suavizado
        self.last_robot_pos = np.array([0.0, 0.0, self.robot_z_fixed])
        self.smoothing = 0.7  # Factor de suavizado (0.0 = sin suavizado, 0.9 = muy suave)
        
        print("✅ Sistema inicializado")
    
    def hand_to_robot_coordinates(self, hand_x, hand_y):
        """
        Convierte coordenadas de la mano (píxeles) a coordenadas del robot (metros).
        
        Args:
            hand_x, hand_y: Coordenadas en píxeles (0-640, 0-480)
            
        Returns:
            Tupla (x, y, z) en metros para el robot
        """
        # Normalizar coordenadas de cámara (0-1)
        norm_x = hand_x / self.camera_width
        norm_y = hand_y / self.camera_height
        
        # Mapear a workspace del robot
        robot_x = self.robot_x_range[0] + norm_x * (self.robot_x_range[1] - self.robot_x_range[0])
        robot_y = self.robot_y_range[0] + norm_y * (self.robot_y_range[1] - self.robot_y_range[0])
        robot_z = self.robot_z_fixed
        
        return robot_x, robot_y, robot_z
    
    def smooth_movement(self, new_pos):
        """
        Aplica suavizado al movimiento del robot.
        
        Args:
            new_pos: Nueva posición objetivo
            
        Returns:
            Posición suavizada
        """
        smoothed_pos = (
            self.smoothing * self.last_robot_pos + 
            (1 - self.smoothing) * np.array(new_pos)
        )
        self.last_robot_pos = smoothed_pos
        return smoothed_pos
    
    def initialize(self):
        """Inicializa todos los componentes."""
        print("\n🔧 Inicializando componentes...")
        
        # Inicializar cámara
        if not self.camera.initialize():
            print("❌ Error: No se pudo inicializar la cámara")
            return False
        print("✅ Cámara inicializada")
        
        # Conectar al robot
        if not self.robot.connect():
            print("❌ Error: No se pudo conectar al robot")
            print("💡 Asegúrate de que CoppeliaSim esté ejecutándose con el UR5 cargado")
            return False
        print("✅ Robot conectado")
        
        # Iniciar simulación
        if not self.robot.start_simulation():
            print("❌ Error: No se pudo iniciar la simulación")
            return False
        print("✅ Simulación iniciada")
        
        # Obtener posición inicial del robot
        initial_pos = self.robot.get_current_position()
        self.last_robot_pos = np.array(initial_pos)
        print(f"📍 Posición inicial del robot: {initial_pos}")
        
        return True
    
    def process_frame(self, frame):
        """
        Procesa un frame: detecta mano y controla robot.
        
        Args:
            frame: Frame de la cámara
            
        Returns:
            Frame procesado con visualizaciones
        """
        # Detectar mano
        detection = self.hand_detector.detect(frame)
        
        if detection:
            # Obtener posición de la mano
            hand_x, hand_y = detection['position']
            confidence = detection['confidence']
            
            # Convertir a coordenadas del robot
            robot_x, robot_y, robot_z = self.hand_to_robot_coordinates(hand_x, hand_y)
            
            # Aplicar suavizado
            smooth_pos = self.smooth_movement([robot_x, robot_y, robot_z])
            
            # Enviar comando al robot
            self.robot.set_target_position(smooth_pos[0], smooth_pos[1], smooth_pos[2])
            
            # Visualizar en la cámara
            # Dibujar punto de la mano
            cv2.circle(frame, (hand_x, hand_y), 10, (0, 255, 0), -1)
            cv2.circle(frame, (hand_x, hand_y), 12, (255, 255, 255), 2)
            
            # Dibujar cruz
            cv2.line(frame, (hand_x-15, hand_y), (hand_x+15, hand_y), (0, 255, 255), 2)
            cv2.line(frame, (hand_x, hand_y-15), (hand_x, hand_y+15), (0, 255, 255), 2)
            
            # Mostrar información si debug está activo
            if self.show_debug:
                # Información de la mano
                cv2.putText(frame, f"Mano: ({hand_x}, {hand_y})", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, f"Confianza: {confidence:.2f}", (10, 55), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Información del robot
                cv2.putText(frame, f"Robot: ({smooth_pos[0]:.2f}, {smooth_pos[1]:.2f}, {smooth_pos[2]:.2f})", 
                           (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        else:
            # No se detectó mano
            if self.show_debug:
                cv2.putText(frame, "Buscando mano...", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Mostrar controles
        cv2.putText(frame, "Controles: 'q'=salir, 'd'=debug, 'r'=reset", 
                   (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def reset_robot(self):
        """Resetea el robot a posición central."""
        print("🔄 Reseteando robot a posición central...")
        center_pos = [0.0, 0.0, self.robot_z_fixed]
        self.robot.set_target_position(center_pos[0], center_pos[1], center_pos[2])
        self.last_robot_pos = np.array(center_pos)
        print("✅ Robot reseteado")
    
    def run(self):
        """Ejecuta el loop principal del sistema."""
        if not self.initialize():
            print("❌ Error en la inicialización")
            return
        
        print("\n🚀 Iniciando control mano-robot")
        print("📹 Muestra tu mano frente a la cámara")
        print("🤖 El robot seguirá los movimientos de tu mano")
        print("\nControles:")
        print("  'q' - Salir")
        print("  'd' - Activar/desactivar debug")
        print("  'r' - Resetear robot al centro")
        
        self.is_running = True
        
        try:
            while self.is_running:
                # Capturar frame
                ret, frame = self.camera.capture_frame()
                if not ret:
                    print("❌ Error capturando frame")
                    break
                
                # Procesar frame
                processed_frame = self.process_frame(frame)
                
                # Mostrar frame
                cv2.imshow('Control Simple Mano-Robot', processed_frame)
                
                # Manejar entrada del teclado
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("\n🛑 Saliendo...")
                    break
                elif key == ord('d') or key == ord('D'):
                    self.show_debug = not self.show_debug
                    print(f"Debug: {'ON' if self.show_debug else 'OFF'}")
                elif key == ord('r') or key == ord('R'):
                    self.reset_robot()
        
        except KeyboardInterrupt:
            print("\n🛑 Interrumpido por el usuario")
        
        except Exception as e:
            print(f"\n❌ Error durante la ejecución: {e}")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Limpia los recursos del sistema."""
        print("\n🧹 Limpiando recursos...")
        
        self.is_running = False
        
        if self.camera:
            self.camera.release()
        
        if self.hand_detector:
            self.hand_detector.cleanup()
        
        if self.robot:
            self.robot.disconnect()
        
        cv2.destroyAllWindows()
        print("✅ Recursos liberados")


def main():
    """Función principal."""
    print("=" * 60)
    print("🤖 SISTEMA SIMPLE DE CONTROL MANO-ROBOT")
    print("=" * 60)
    print()
    print("Este sistema permite controlar un brazo robótico UR5")
    print("en CoppeliaSim usando movimientos de tu mano.")
    print()
    
    # Verificar dependencias básicas
    print("📋 Verificando dependencias...")
    
    try:
        import zmq
        print("✅ pyzmq")
    except ImportError:
        print("❌ pyzmq no instalado - ejecuta: pip install pyzmq")
        return
    
    try:
        from coppeliasim_zmqremoteapi_client import RemoteAPIClient
        print("✅ coppeliasim-zmqremoteapi-client")
    except ImportError:
        print("❌ coppeliasim-zmqremoteapi-client no instalado")
        print("   Ejecuta: pip install coppeliasim-zmqremoteapi-client")
        return
    
    print("✅ Dependencias verificadas")
    print()
    
    # Crear y ejecutar sistema
    control_system = SimpleHandRobotControl()
    control_system.run()


if __name__ == "__main__":
    main()
