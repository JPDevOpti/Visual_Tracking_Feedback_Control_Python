#!/usr/bin/env python3
"""
Sistema Completo de Control con Lazo Abierto y Cerrado
Versión avanzada con interfaz gráfica y análisis en tiempo real
"""

import cv2
import time
import sys
import os
import numpy as np
import threading
from typing import Optional, Dict, Any

# Agregar el directorio src al path para los imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

try:
    from utils.camera_manager import CameraManager
    from tracking.mediapipe_detector import MediaPipeHandDetector
    from control.coppeliasim_robot_arm import CoppeliaSimRobotArm
    from control.controller_manager import ControllerManager, ControlMode
    from analysis.error_calculator import ErrorCalculator, PerformanceMetrics
    from visualization.real_time_plotter import RealTimePlotter
    from visualization.gui_manager import GUIManager
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print(f"💡 Directorio actual: {current_dir}")
    print(f"💡 Directorio src: {src_dir}")
    print("💡 Verifica que los archivos existan en src/")
    sys.exit(1)


class AdvancedHandRobotControl:
    """
    Sistema avanzado de control mano-robot con análisis completo.
    """
    
    def __init__(self):
        """Inicializa el sistema de control avanzado."""
        print("🚀 Inicializando Sistema Avanzado de Control Mano-Robot")
        print("=" * 60)
        
        # Componentes básicos del sistema
        self.camera = CameraManager(camera_index=0, width=640, height=480)
        self.hand_detector = MediaPipeHandDetector(max_hands=1, min_detection_confidence=0.7)
        self.robot = CoppeliaSimRobotArm()
        
        # Componentes de control y análisis
        self.controller_manager = ControllerManager()
        self.error_calculator = ErrorCalculator(buffer_size=1000)
        self.performance_metrics = PerformanceMetrics()
        
        # Componentes de visualización
        self.plotter = RealTimePlotter(max_points=300, update_interval=50)
        self.gui_manager = GUIManager()
        self.control_panel = self.gui_manager.get_control_panel()
        
        # Estado del sistema
        self.is_running = False
        self.is_system_initialized = False
        self.main_thread = None
        self.last_hand_position = None
        
        # Configuración del mapeo
        self.camera_width = 640
        self.camera_height = 480
        self.robot_x_range = (-0.3, 0.3)
        self.robot_y_range = (-0.3, 0.3)
        self.robot_z_fixed = 0.5
        
        # Configurar callbacks de la GUI
        self.setup_gui_callbacks()
        
        # Integrar matplotlib en GUI
        self.control_panel.set_matplotlib_figure(self.plotter.get_figure())
        
        print("✅ Sistema inicializado correctamente")
        print("📋 Listo para configurar y ejecutar")
    
    def setup_gui_callbacks(self):
        """Configura los callbacks de la interfaz gráfica."""
        self.control_panel.set_callbacks(
            on_mode_change=self.on_mode_change,
            on_parameter_change=self.on_parameter_change,
            on_reset_system=self.on_reset_system,
            on_start_stop=self.on_start_stop,
            on_export_data=self.on_export_data
        )
    
    def on_mode_change(self, mode: str):
        """
        Callback cuando cambia el modo de control.
        
        Args:
            mode: Nuevo modo ('open_loop' o 'closed_loop')
        """
        print(f"🔄 Cambiando modo a: {mode}")
        
        control_mode = ControlMode.OPEN_LOOP if mode == "open_loop" else ControlMode.CLOSED_LOOP
        self.controller_manager.set_control_mode(control_mode)
        
        # Resetear análisis
        self.error_calculator.reset()
        self.plotter.reset_plots()
        
        print(f"✅ Modo cambiado a: {mode}")
    
    def on_parameter_change(self, params: Dict[str, float]):
        """
        Callback cuando cambian los parámetros de control.
        
        Args:
            params: Nuevos parámetros
        """
        # Actualizar parámetros del controlador
        self.controller_manager.update_control_parameters(params)
        print(f"🔧 Parámetros actualizados: {params}")
    
    def on_reset_system(self):
        """Callback para resetear el sistema."""
        print("🔄 Reseteando sistema...")
        
        # Resetear controlador
        self.controller_manager.reset_controller_state()
        
        # Resetear análisis
        self.error_calculator.reset()
        self.performance_metrics.reset_session()
        
        # Resetear gráficos
        self.plotter.reset_plots()
        
        # Resetear robot a posición central
        if self.robot and self.robot.is_connected:
            center_pos = [0.0, 0.0, self.robot_z_fixed]
            self.robot.set_target_position(center_pos[0], center_pos[1], center_pos[2])
        
        print("✅ Sistema reseteado")
    
    def on_start_stop(self, start: bool):
        """
        Callback para iniciar/detener el sistema.
        
        Args:
            start: True para iniciar, False para detener
        """
        if start and not self.is_running:
            self.start_system()
        elif not start and self.is_running:
            self.stop_system()
    
    def on_export_data(self, filename: str):
        """
        Callback para exportar datos.
        
        Args:
            filename: Nombre del archivo
        """
        try:
            # Exportar datos del controlador
            self.controller_manager.export_data(filename)
            
            # Exportar gráficos
            plot_filename = filename.replace('.json', '_plots.png')
            self.plotter.save_plots(plot_filename)
            
            self.control_panel.show_info_message("Exportar Datos", 
                                               f"Datos exportados exitosamente:\\n{filename}\\n{plot_filename}")
        
        except Exception as e:
            self.control_panel.show_error_message("Error de Exportación", f"Error exportando datos: {e}")
    
    def hand_to_robot_coordinates(self, hand_x: int, hand_y: int) -> np.ndarray:
        """
        Convierte coordenadas de la mano a coordenadas del robot.
        
        Args:
            hand_x, hand_y: Coordenadas en píxeles
            
        Returns:
            Coordenadas del robot [x, y, z]
        """
        # Normalizar coordenadas de cámara (0-1)
        norm_x = hand_x / self.camera_width
        norm_y = hand_y / self.camera_height
        
        # Mapear a workspace del robot
        robot_x = self.robot_x_range[0] + norm_x * (self.robot_x_range[1] - self.robot_x_range[0])
        robot_y = self.robot_y_range[0] + norm_y * (self.robot_y_range[1] - self.robot_y_range[0])
        robot_z = self.robot_z_fixed
        
        return np.array([robot_x, robot_y, robot_z])
    
    def initialize_system(self) -> bool:
        """
        Inicializa todos los componentes del sistema.
        
        Returns:
            True si la inicialización fue exitosa
        """
        if self.is_system_initialized:
            return True
        
        print("\\n🔧 Inicializando componentes del sistema...")
        
        # Inicializar cámara
        self.control_panel.update_system_status("Inicializando cámara...", False)
        if not self.camera.initialize():
            self.control_panel.show_error_message("Error de Cámara", 
                                                "No se pudo inicializar la cámara.\\nVerifica permisos y conexión.")
            return False
        print("✅ Cámara inicializada")
        
        # Conectar al robot
        self.control_panel.update_system_status("Conectando robot...", False)
        if not self.robot.connect():
            self.control_panel.show_error_message("Error de Robot", 
                                                "No se pudo conectar al robot.\\nVerifica que CoppeliaSim esté ejecutándose.")
            return False
        print("✅ Robot conectado")
        
        # Iniciar simulación
        self.control_panel.update_system_status("Iniciando simulación...", False)
        if not self.robot.start_simulation():
            self.control_panel.show_error_message("Error de Simulación", 
                                                "No se pudo iniciar la simulación en CoppeliaSim.")
            return False
        print("✅ Simulación iniciada")
        
        # Obtener posición inicial del robot
        initial_pos = self.robot.get_current_position()
        print(f"📍 Posición inicial del robot: {initial_pos}")
        
        # Inicializar gráficos
        self.plotter.start_animation()
        print("✅ Gráficos iniciados")
        
        self.is_system_initialized = True
        print("✅ Sistema completamente inicializado")
        return True
    
    def start_system(self):
        """Inicia el sistema de control."""
        if self.is_running:
            return
        
        if not self.initialize_system():
            return
        
        print("\\n🚀 Iniciando sistema de control...")
        self.is_running = True
        
        # Iniciar thread principal
        self.main_thread = threading.Thread(target=self.main_control_loop, daemon=True)
        self.main_thread.start()
        
        self.control_panel.update_system_status("Ejecutándose", True)
        print("✅ Sistema iniciado")
    
    def stop_system(self):
        """Detiene el sistema de control."""
        if not self.is_running:
            return
        
        print("\\n⏹️ Deteniendo sistema...")
        self.is_running = False
        
        # Esperar a que termine el thread principal
        if self.main_thread and self.main_thread.is_alive():
            self.main_thread.join(timeout=2.0)
        
        self.control_panel.update_system_status("Detenido", False)
        print("✅ Sistema detenido")
    
    def main_control_loop(self):
        """Loop principal del sistema de control."""
        print("🔄 Iniciando loop principal de control...")
        
        try:
            while self.is_running:
                start_time = time.time()
                
                # Capturar frame de cámara
                ret, frame = self.camera.capture_frame()
                if not ret:
                    print("⚠️ Error capturando frame")
                    continue
                
                # Procesar frame
                processed_frame = self.process_frame(frame)
                
                # Actualizar video en GUI
                self.gui_manager.update_gui_safe(
                    lambda: self.control_panel.update_video_frame(processed_frame)
                )
                
                # Control de frecuencia (30 FPS)
                elapsed = time.time() - start_time
                sleep_time = max(0, 1/30 - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except Exception as e:
            print(f"❌ Error en loop principal: {e}")
            self.gui_manager.update_gui_safe(
                lambda: self.control_panel.show_error_message("Error del Sistema", f"Error en loop principal: {e}")
            )
        
        finally:
            print("🔄 Loop principal terminado")
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Procesa un frame: detecta mano, controla robot y actualiza análisis.
        
        Args:
            frame: Frame de la cámara
            
        Returns:
            Frame procesado con visualizaciones
        """
        current_time = time.time()
        
        # Detectar mano
        detection = self.hand_detector.detect(frame)
        
        if detection:
            # Obtener posición de la mano
            hand_x, hand_y = detection['position']
            confidence = detection['confidence']
            
            # Convertir a coordenadas del robot
            desired_position = self.hand_to_robot_coordinates(hand_x, hand_y)
            
            # Obtener posición actual del robot
            actual_position = np.array(self.robot.get_current_position())
            
            # Calcular señal de control
            control_signal = self.controller_manager.calculate_control_signal(
                desired_position, actual_position
            )
            
            # Enviar comando al robot
            self.robot.set_target_position(control_signal[0], control_signal[1], control_signal[2])
            
            # Actualizar análisis de error
            error_metrics = self.error_calculator.update(
                desired_position, actual_position, current_time
            )
            
            # Actualizar métricas de rendimiento
            error_magnitude = error_metrics['current_error_magnitude']
            mode = self.controller_manager.current_mode.value
            self.performance_metrics.update_mode_statistics(mode, error_magnitude)
            
            # Actualizar visualización en tiempo real
            self.plotter.update_data(
                error_magnitude=error_magnitude,
                correction_velocity=error_metrics['current_correction_velocity'],
                desired_pos=desired_position,
                actual_pos=actual_position,
                current_time=current_time,
                mode=mode,
                metrics=error_metrics
            )
            
            # Actualizar GUI con métricas
            controller_status = self.controller_manager.get_current_status()
            combined_metrics = {**error_metrics, **controller_status}
            
            self.gui_manager.update_gui_safe(
                lambda: self.control_panel.update_metrics_display(combined_metrics)
            )
            
            # Dibujar visualizaciones en el frame
            frame = self.draw_frame_overlays(frame, hand_x, hand_y, confidence, 
                                           desired_position, actual_position, error_metrics)
            
            self.last_hand_position = (hand_x, hand_y)
        
        else:
            # No se detectó mano
            if self.control_panel.show_debug.get():
                cv2.putText(frame, "Buscando mano...", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        return frame
    
    def draw_frame_overlays(self, frame: np.ndarray, hand_x: int, hand_y: int, 
                          confidence: float, desired_pos: np.ndarray, actual_pos: np.ndarray,
                          metrics: Dict[str, float]) -> np.ndarray:
        """
        Dibuja overlays informativos en el frame.
        
        Args:
            frame: Frame de video
            hand_x, hand_y: Posición de la mano
            confidence: Confianza de detección
            desired_pos: Posición deseada
            actual_pos: Posición actual
            metrics: Métricas actuales
            
        Returns:
            Frame con overlays
        """
        # Dibujar punto de la mano
        cv2.circle(frame, (hand_x, hand_y), 10, (0, 255, 0), -1)
        cv2.circle(frame, (hand_x, hand_y), 12, (255, 255, 255), 2)
        
        # Dibujar cruz
        cv2.line(frame, (hand_x-15, hand_y), (hand_x+15, hand_y), (0, 255, 255), 2)
        cv2.line(frame, (hand_x, hand_y-15), (hand_x, hand_y+15), (0, 255, 255), 2)
        
        # Mostrar información si debug está activo
        if self.control_panel.show_debug.get():
            # Información de la mano
            cv2.putText(frame, f"Mano: ({hand_x}, {hand_y})", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Confianza: {confidence:.2f}", (10, 55), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Información del robot
            cv2.putText(frame, f"Deseada: ({desired_pos[0]:.2f}, {desired_pos[1]:.2f})", 
                       (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Real: ({actual_pos[0]:.2f}, {actual_pos[1]:.2f})", 
                       (10, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
            
            # Error
            error = metrics.get('current_error_magnitude', 0)
            cv2.putText(frame, f"Error: {error:.4f} m", (10, 130), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Modo de control
            mode = self.controller_manager.current_mode.value.replace('_', ' ').title()
            mode_color = (0, 255, 0) if 'Cerrado' in mode else (255, 0, 0)
            cv2.putText(frame, f"Modo: {mode}", (10, 155), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, mode_color, 2)
        
        # Mostrar controles básicos
        cv2.putText(frame, "Usar GUI para controles completos", 
                   (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def cleanup(self):
        """Limpia los recursos del sistema."""
        print("\\n🧹 Limpiando recursos del sistema...")
        
        # Detener sistema si está corriendo
        self.stop_system()
        
        # Detener gráficos
        if self.plotter:
            self.plotter.stop_animation()
        
        # Limpiar componentes
        if self.camera:
            self.camera.release()
        
        if self.hand_detector:
            self.hand_detector.cleanup()
        
        if self.robot:
            self.robot.disconnect()
        
        print("✅ Recursos limpiados")
    
    def run(self):
        """Ejecuta el sistema con interfaz gráfica."""
        print("\\n🖥️ Iniciando interfaz gráfica...")
        print("📋 Usa la interfaz para:")
        print("   • Seleccionar modo de control")
        print("   • Ajustar parámetros PID")
        print("   • Ver análisis en tiempo real")
        print("   • Exportar datos")
        print("\\n🎯 Muestra tu mano frente a la cámara para comenzar")
        
        try:
            # Iniciar GUI (bloquea hasta cerrar)
            self.gui_manager.start()
        
        finally:
            self.cleanup()


def main():
    """Función principal."""
    print("=" * 70)
    print("🤖 SISTEMA AVANZADO DE CONTROL MANO-ROBOT")
    print("📊 ANÁLISIS DE LAZO ABIERTO vs LAZO CERRADO")
    print("=" * 70)
    print()
    print("Este sistema permite:")
    print("• 🔵 Control en Lazo Abierto")
    print("• 🟢 Control en Lazo Cerrado (PID)")
    print("• 📈 Análisis en tiempo real")
    print("• 📊 Métricas de rendimiento")
    print("• 💾 Exportación de datos")
    print()
    
    # Verificar dependencias básicas
    print("📋 Verificando dependencias...")
    
    dependencies_ok = True
    
    try:
        import zmq
        print("✅ pyzmq")
    except ImportError:
        print("❌ pyzmq no instalado - ejecuta: pip install pyzmq")
        dependencies_ok = False
    
    try:
        from coppeliasim_zmqremoteapi_client import RemoteAPIClient
        print("✅ coppeliasim-zmqremoteapi-client")
    except ImportError:
        print("❌ coppeliasim-zmqremoteapi-client no instalado")
        print("   Ejecuta: pip install coppeliasim-zmqremoteapi-client")
        dependencies_ok = False
    
    try:
        import matplotlib
        print("✅ matplotlib")
    except ImportError:
        print("❌ matplotlib no instalado - ejecuta: pip install matplotlib")
        dependencies_ok = False
    
    try:
        import tkinter
        print("✅ tkinter")
    except ImportError:
        print("❌ tkinter no disponible - instala python3-tk")
        dependencies_ok = False
    
    if not dependencies_ok:
        print("\\n❌ Faltan dependencias. Ejecuta:")
        print("   pip install -r requirements.txt")
        return
    
    print("✅ Todas las dependencias verificadas")
    print()
    
    # Crear y ejecutar sistema
    try:
        control_system = AdvancedHandRobotControl()
        control_system.run()
    
    except KeyboardInterrupt:
        print("\\n🛑 Interrumpido por el usuario")
    
    except Exception as e:
        print(f"\\n❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
