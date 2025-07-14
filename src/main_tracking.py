#!/usr/bin/env python3
"""
Sistema de Tracking de Mano usando MediaPipe
Parte 1: Implementación básica de detección y seguimiento de mano

Controles:
- 'q': Salir del programa
- 'c': Mostrar/ocultar información de debug
- 'l': Mostrar/ocultar landmarks de la mano
- 'Espacio': Pausar/reanudar
"""

import cv2
import time
import sys
import os

# Agregar el directorio src al path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.camera_manager import CameraManager
from utils.visualization import draw_tracking_point, draw_tracking_info, draw_crosshair
from tracking.mediapipe_detector import MediaPipeHandDetector


class HandTrackingSystem:
    """
    Sistema principal de tracking de mano.
    """
    
    def __init__(self):
        """
        Inicializa el sistema de tracking.
        """
        # Configuración inicial
        self.camera_width = 640
        self.camera_height = 480
        self.show_debug_info = True
        self.show_landmarks = True
        self.is_paused = False
        
        # Inicializar componentes
        self.camera = CameraManager(
            camera_index=0, 
            width=self.camera_width, 
            height=self.camera_height
        )
        
        self.hand_detector = MediaPipeHandDetector(
            max_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Variables para FPS
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0.0
        
        # Estado del tracking
        self.last_hand_position = None
        self.tracking_active = False
        
        print("Sistema de Tracking de Mano inicializado")
        print("Controles:")
        print("  'q' - Salir")
        print("  'c' - Mostrar/ocultar info debug")
        print("  'l' - Mostrar/ocultar landmarks")
        print("  'Espacio' - Pausar/reanudar")
    
    def initialize(self) -> bool:
        """
        Inicializa todos los componentes del sistema.
        
        Returns:
            bool: True si la inicialización fue exitosa
        """
        if not self.camera.initialize():
            print("Error: No se pudo inicializar la cámara")
            return False
        
        print(f"Cámara inicializada: {self.camera.get_resolution()}")
        print(f"FPS de cámara: {self.camera.get_fps()}")
        return True
    
    def calculate_fps(self):
        """
        Calcula los FPS actuales del sistema.
        """
        self.fps_counter += 1
        current_time = time.time()
        
        # Actualizar FPS cada segundo
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter / (current_time - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def process_frame(self, frame):
        """
        Procesa un frame para detectar y trackear la mano.
        
        Args:
            frame: Frame de la cámara
            
        Returns:
            Frame procesado con visualizaciones
        """
        if self.is_paused:
            return frame
        
        # Detectar mano
        detection = self.hand_detector.detect(frame)
        
        if detection:
            position = detection['position']
            confidence = detection['confidence']
            
            # Actualizar estado del tracking
            self.last_hand_position = position
            self.tracking_active = True
            
            # Dibujar punto de tracking principal
            frame = draw_tracking_point(frame, position, color=(0, 0, 255), radius=8)
            
            # Dibujar cruz centrada en la mano
            frame = draw_crosshair(frame, position, size=15, color=(0, 255, 255))
            
            # Dibujar landmarks si está habilitado
            if self.show_landmarks:
                frame = self.hand_detector.draw_landmarks(frame, draw_connections=True)
            
            # Dibujar información de debug
            if self.show_debug_info:
                frame = draw_tracking_info(frame, position, confidence, self.current_fps)
        
        else:
            # No se detectó mano
            self.tracking_active = False
            
            # Mostrar mensaje de "buscando mano"
            if self.show_debug_info:
                cv2.putText(frame, "Buscando mano...", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(frame, f"FPS: {self.current_fps:.1f}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def handle_keyboard_input(self, key: int) -> bool:
        """
        Maneja la entrada del teclado.
        
        Args:
            key: Código de la tecla presionada
            
        Returns:
            bool: False si se debe salir del programa
        """
        if key == ord('q') or key == ord('Q'):
            return False
        
        elif key == ord('c') or key == ord('C'):
            self.show_debug_info = not self.show_debug_info
            print(f"Debug info: {'ON' if self.show_debug_info else 'OFF'}")
        
        elif key == ord('l') or key == ord('L'):
            self.show_landmarks = not self.show_landmarks
            print(f"Landmarks: {'ON' if self.show_landmarks else 'OFF'}")
        
        elif key == ord(' '):  # Espacio
            self.is_paused = not self.is_paused
            print(f"Sistema: {'PAUSADO' if self.is_paused else 'ACTIVO'}")
        
        return True
    
    def run(self):
        """
        Ejecuta el bucle principal del sistema de tracking.
        """
        if not self.initialize():
            return
        
        print("\nIniciando tracking de mano...")
        print("Muestra tu mano frente a la cámara")
        
        try:
            while True:
                # Capturar frame
                ret, frame = self.camera.capture_frame()
                
                if not ret:
                    print("Error: No se pudo capturar frame de la cámara")
                    break
                
                # Procesar frame
                processed_frame = self.process_frame(frame)
                
                # Calcular FPS
                self.calculate_fps()
                
                # Mostrar frame
                cv2.imshow('Hand Tracking - MediaPipe', processed_frame)
                
                # Manejar entrada del teclado
                key = cv2.waitKey(1) & 0xFF
                if not self.handle_keyboard_input(key):
                    break
        
        except KeyboardInterrupt:
            print("\nInterrumpido por el usuario")
        
        except Exception as e:
            print(f"Error durante la ejecución: {e}")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """
        Limpia los recursos del sistema.
        """
        print("\nCerrando sistema...")
        
        if self.camera:
            self.camera.release()
        
        if self.hand_detector:
            self.hand_detector.cleanup()
        
        cv2.destroyAllWindows()
        print("Sistema cerrado correctamente")


def main():
    """
    Función principal del programa.
    """
    print("=== Sistema de Tracking de Mano con MediaPipe ===")
    print("Versión 1.0 - Implementación básica")
    print()
    
    # Crear y ejecutar el sistema
    tracking_system = HandTrackingSystem()
    tracking_system.run()


if __name__ == "__main__":
    main()
