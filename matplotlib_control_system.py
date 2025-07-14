#!/usr/bin/env python3
"""
Sistema de Control Simplificado - Solo Matplotlib
Versión sin tkinter para evitar problemas de compatibilidad en macOS
"""

import cv2
import time
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider, Button
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
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print(f"💡 Directorio actual: {current_dir}")
    print(f"💡 Directorio src: {src_dir}")
    print("💡 Verifica que los archivos existan en src/")
    sys.exit(1)


class MatplotlibControlSystem:
    """
    Sistema de control usando solo matplotlib para la interfaz.
    """
    
    def __init__(self):
        """Inicializa el sistema."""
        print("🚀 Inicializando Sistema de Control con Matplotlib")
        print("=" * 60)
        
        # Componentes básicos
        self.camera = CameraManager(camera_index=0, width=640, height=480)
        self.hand_detector = MediaPipeHandDetector(max_hands=1, min_detection_confidence=0.7)
        self.robot = CoppeliaSimRobotArm()
        
        # Componentes de control y análisis
        self.controller_manager = ControllerManager()
        self.error_calculator = ErrorCalculator(buffer_size=1000)
        self.performance_metrics = PerformanceMetrics()
        
        # Estado del sistema
        self.is_running = False
        self.is_system_initialized = False
        self.show_debug = True
        
        # Configuración del mapeo
        self.camera_width = 640
        self.camera_height = 480
        self.robot_x_range = (-0.3, 0.3)
        self.robot_y_range = (-0.3, 0.3)
        self.robot_z_fixed = 0.5
        
        # Variables de control
        self.current_mode = "open_loop"
        self.kp = 2.0
        self.ki = 0.1
        self.kd = 0.05
        self.smoothing = 0.7
        
        # Setup matplotlib
        self.setup_matplotlib_interface()
        
        print("✅ Sistema inicializado")
    
    def setup_matplotlib_interface(self):
        """Configura la interfaz de matplotlib."""
        # Configurar matplotlib para mejor layout
        plt.style.use('default')
        
        # Crear figura principal con más espacio
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('Sistema de Control - Lazo Abierto vs Cerrado', fontsize=16, fontweight='bold', y=0.95)
        
        # Usar GridSpec para mejor control del layout
        from matplotlib.gridspec import GridSpec
        
        # Layout: 3 filas, 3 columnas
        # Fila 1: Gráfico Error | Cámara
        # Fila 2: Gráfico Velocidad | Controles
        # Fila 3: Métricas | (vacío)
        gs = GridSpec(3, 2, figure=self.fig, 
                     height_ratios=[2, 2, 1],  # Gráficos grandes, métricas pequeñas
                     width_ratios=[2, 1.5],    # Gráficos más anchos que cámara
                     hspace=0.3, wspace=0.3,
                     left=0.08, right=0.95, top=0.90, bottom=0.15)
        
        # Gráfico de error (superior izquierdo)
        self.ax_error = self.fig.add_subplot(gs[0, 0])
        self.ax_error.set_title('Error vs Tiempo', fontweight='bold', fontsize=12)
        self.ax_error.set_xlabel('Tiempo (s)', fontsize=10)
        self.ax_error.set_ylabel('Error (m)', fontsize=10)
        self.ax_error.grid(True, alpha=0.3)
        self.ax_error.tick_params(labelsize=9)
        
        # Gráfico de velocidad (medio izquierdo)
        self.ax_velocity = self.fig.add_subplot(gs[1, 0])
        self.ax_velocity.set_title('Velocidad de Corrección', fontweight='bold', fontsize=12)
        self.ax_velocity.set_xlabel('Tiempo (s)', fontsize=10)
        self.ax_velocity.set_ylabel('Velocidad (m/s)', fontsize=10)
        self.ax_velocity.grid(True, alpha=0.3)
        self.ax_velocity.tick_params(labelsize=9)
        
        # Panel de video (superior derecho)
        self.ax_video = self.fig.add_subplot(gs[0, 1])
        self.ax_video.set_title('Vista de Cámara', fontweight='bold', fontsize=12)
        self.ax_video.axis('off')
        
        # Panel de información (inferior izquierdo)
        self.ax_info = self.fig.add_subplot(gs[2, 0])
        self.ax_info.set_title('Métricas del Sistema', fontweight='bold', fontsize=11)
        self.ax_info.axis('off')
        
        # Panel de controles (medio derecho, debajo de la cámara)
        # Los controles se configuran con coordenadas absolutas en setup_controls()
        
        # Inicializar líneas de gráficos
        self.init_plot_lines()
        
        # Datos para gráficos
        self.reset_plot_data()
        
        # Configurar controles después del layout
        self.setup_controls()
    
    def setup_controls(self):
        """Configura los controles debajo de la cámara."""
        # Área de controles debajo de la cámara (lado derecho)
        # Calcular posiciones basadas en la posición de la cámara
        
        # Radio buttons para modo de control
        ax_mode = plt.axes([0.65, 0.45, 0.25, 0.15])  # x, y, width, height
        ax_mode.set_title('Modo de Control', fontsize=10, fontweight='bold')
        self.radio_mode = RadioButtons(ax_mode, ('Lazo Abierto', 'Lazo Cerrado'))
        self.radio_mode.on_clicked(self.on_mode_change)
        
        # Botones de control principales
        button_width = 0.1
        button_height = 0.04
        button_x_start = 0.65
        button_y_start = 0.35
        
        # Botón Iniciar/Detener
        ax_start = plt.axes([button_x_start, button_y_start, button_width, button_height])
        self.btn_start = Button(ax_start, 'Iniciar', color='lightgreen')
        self.btn_start.on_clicked(self.on_start_stop)
        
        # Botón Reset
        ax_reset = plt.axes([button_x_start + 0.12, button_y_start, button_width, button_height])
        self.btn_reset = Button(ax_reset, 'Reset', color='orange')
        self.btn_reset.on_clicked(self.on_reset)
        
        # Botón Exportar
        ax_export = plt.axes([button_x_start, button_y_start - 0.06, button_width, button_height])
        self.btn_export = Button(ax_export, 'Exportar', color='lightblue')
        self.btn_export.on_clicked(self.on_export)
        
        # Sliders PID (más compactos, debajo de los botones)
        slider_width = 0.2
        slider_height = 0.025
        slider_x = 0.65
        slider_y_start = 0.22
        
        # Kp
        ax_kp = plt.axes([slider_x, slider_y_start, slider_width, slider_height])
        self.slider_kp = Slider(ax_kp, 'Kp', 0.1, 5.0, valinit=self.kp, 
                               valfmt='%.1f', color='lightblue')
        self.slider_kp.on_changed(self.on_kp_change)
        
        # Ki
        ax_ki = plt.axes([slider_x, slider_y_start - 0.04, slider_width, slider_height])
        self.slider_ki = Slider(ax_ki, 'Ki', 0.0, 1.0, valinit=self.ki,
                               valfmt='%.2f', color='lightgreen')
        self.slider_ki.on_changed(self.on_ki_change)
        
        # Kd
        ax_kd = plt.axes([slider_x, slider_y_start - 0.08, slider_width, slider_height])
        self.slider_kd = Slider(ax_kd, 'Kd', 0.0, 0.2, valinit=self.kd,
                               valfmt='%.3f', color='lightcoral')
        self.slider_kd.on_changed(self.on_kd_change)
        
        # Suavizado
        ax_smooth = plt.axes([slider_x, slider_y_start - 0.12, slider_width, slider_height])
        self.slider_smooth = Slider(ax_smooth, 'Suavizado', 0.1, 0.95, valinit=self.smoothing,
                                   valfmt='%.2f', color='lightyellow')
        self.slider_smooth.on_changed(self.on_smooth_change)
    
    def init_plot_lines(self):
        """Inicializa las líneas de los gráficos."""
        # Líneas de error
        self.line_error, = self.ax_error.plot([], [], 'r-', linewidth=2, label='Error')
        self.ax_error.legend()
        
        # Líneas de velocidad
        self.line_velocity, = self.ax_velocity.plot([], [], 'b-', linewidth=2, label='Velocidad')
        self.ax_velocity.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        self.ax_velocity.legend()
        
        # Imagen de video
        self.video_image = None
    
    def reset_plot_data(self):
        """Resetea los datos de los gráficos."""
        self.timestamps = []
        self.errors = []
        self.velocities = []
        self.start_time = time.time()
    
    def hand_to_robot_coordinates(self, hand_x: int, hand_y: int) -> np.ndarray:
        """Convierte coordenadas de la mano a coordenadas del robot."""
        norm_x = hand_x / self.camera_width
        norm_y = hand_y / self.camera_height
        
        robot_x = self.robot_x_range[0] + norm_x * (self.robot_x_range[1] - self.robot_x_range[0])
        robot_y = self.robot_y_range[0] + norm_y * (self.robot_y_range[1] - self.robot_y_range[0])
        robot_z = self.robot_z_fixed
        
        return np.array([robot_x, robot_y, robot_z])
    
    def initialize_system(self) -> bool:
        """Inicializa todos los componentes del sistema."""
        if self.is_system_initialized:
            return True
        
        print("\n🔧 Inicializando componentes del sistema...")
        
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
        
        self.is_system_initialized = True
        print("✅ Sistema completamente inicializado")
        return True
    
    def update_display(self):
        """Actualiza la visualización."""
        if not self.is_running:
            return
        
        # Capturar frame
        ret, frame = self.camera.capture_frame()
        if not ret:
            return
        
        # Procesar frame
        processed_frame = self.process_frame(frame)
        
        # Actualizar video
        if self.video_image is None:
            self.video_image = self.ax_video.imshow(processed_frame)
        else:
            self.video_image.set_array(processed_frame)
        
        # Actualizar gráficos
        self.update_plots()
        
        # Redibujar
        self.fig.canvas.draw_idle()
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Procesa un frame del video."""
        current_time = time.time()
        
        # Detectar mano
        detection = self.hand_detector.detect(frame)
        
        if detection:
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
            
            # Actualizar análisis
            error_metrics = self.error_calculator.update(
                desired_position, actual_position, current_time
            )
            
            # Actualizar datos para gráficos
            relative_time = current_time - self.start_time
            self.timestamps.append(relative_time)
            self.errors.append(error_metrics['current_error_magnitude'])
            self.velocities.append(error_metrics['current_correction_velocity'])
            
            # Mantener solo los últimos 300 puntos
            if len(self.timestamps) > 300:
                self.timestamps = self.timestamps[-300:]
                self.errors = self.errors[-300:]
                self.velocities = self.velocities[-300:]
            
            # Dibujar overlays
            frame = self.draw_overlays(frame, hand_x, hand_y, confidence, 
                                     desired_position, actual_position, error_metrics)
        
        else:
            if self.show_debug:
                cv2.putText(frame, "Buscando mano...", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    def draw_overlays(self, frame, hand_x, hand_y, confidence, desired_pos, actual_pos, metrics):
        """Dibuja información en el frame."""
        # Punto de la mano
        cv2.circle(frame, (hand_x, hand_y), 10, (0, 255, 0), -1)
        cv2.circle(frame, (hand_x, hand_y), 12, (255, 255, 255), 2)
        
        # Cruz
        cv2.line(frame, (hand_x-15, hand_y), (hand_x+15, hand_y), (0, 255, 255), 2)
        cv2.line(frame, (hand_x, hand_y-15), (hand_x, hand_y+15), (0, 255, 255), 2)
        
        if self.show_debug:
            # Información
            cv2.putText(frame, f"Mano: ({hand_x}, {hand_y})", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Error: {metrics['current_error_magnitude']:.4f} m", (10, 55), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.putText(frame, f"Modo: {self.current_mode.replace('_', ' ').title()}", (10, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return frame
    
    def update_plots(self):
        """Actualiza todos los gráficos."""
        if len(self.timestamps) < 2:
            return
        
        # Gráfico de error
        self.line_error.set_data(self.timestamps, self.errors)
        self.ax_error.relim()
        self.ax_error.autoscale_view()
        
        # Gráfico de velocidad
        self.line_velocity.set_data(self.timestamps, self.velocities)
        self.ax_velocity.relim()
        self.ax_velocity.autoscale_view()
        
        # Panel de información
        self.update_info_panel()
    
    def update_info_panel(self):
        """Actualiza el panel de información."""
        self.ax_info.clear()
        self.ax_info.set_title('Métricas del Sistema', fontweight='bold')
        self.ax_info.axis('off')
        
        if len(self.errors) > 0:
            current_error = self.errors[-1]
            current_velocity = self.velocities[-1] if len(self.velocities) > 0 else 0
            rms_error = np.sqrt(np.mean(np.square(self.errors)))
            max_error = np.max(self.errors)
            
            info_text = f"""
Error Actual: {current_error:.4f} m
Velocidad Corrección: {current_velocity:.4f} m/s
Error RMS: {rms_error:.4f} m
Error Máximo: {max_error:.4f} m
Modo: {self.current_mode.replace('_', ' ').title()}
Puntos: {len(self.timestamps)}
            """
            
            self.ax_info.text(0.1, 0.5, info_text, fontsize=10, 
                             verticalalignment='center', fontfamily='monospace')
    
    def on_mode_change(self, label):
        """Callback para cambio de modo."""
        if label == 'Lazo Abierto':
            self.current_mode = 'open_loop'
            mode = ControlMode.OPEN_LOOP
        else:
            self.current_mode = 'closed_loop'
            mode = ControlMode.CLOSED_LOOP
        
        self.controller_manager.set_control_mode(mode)
        self.reset_analysis()
        print(f"Modo cambiado a: {self.current_mode}")
    
    def on_kp_change(self, val):
        """Callback para cambio de Kp."""
        self.kp = val
        self.update_controller_params()
    
    def on_ki_change(self, val):
        """Callback para cambio de Ki."""
        self.ki = val
        self.update_controller_params()
    
    def on_kd_change(self, val):
        """Callback para cambio de Kd."""
        self.kd = val
        self.update_controller_params()
    
    def on_smooth_change(self, val):
        """Callback para cambio de suavizado."""
        self.smoothing = val
        self.update_controller_params()
    
    def update_controller_params(self):
        """Actualiza los parámetros del controlador."""
        params = {
            'kp': self.kp,
            'ki': self.ki,
            'kd': self.kd,
            'smoothing': self.smoothing
        }
        self.controller_manager.update_control_parameters(params)
    
    def on_start_stop(self, event):
        """Callback para iniciar/detener."""
        if not self.is_running:
            if self.initialize_system():
                self.is_running = True
                self.btn_start.label.set_text('Detener')
                print("🚀 Sistema iniciado")
                # Iniciar timer para actualización
                self.timer = self.fig.canvas.new_timer(interval=33)  # ~30 FPS
                self.timer.add_callback(self.update_display)
                self.timer.start()
        else:
            self.is_running = False
            self.btn_start.label.set_text('Iniciar')
            if hasattr(self, 'timer'):
                self.timer.stop()
            print("⏹️ Sistema detenido")
    
    def on_reset(self, event):
        """Callback para reset."""
        print("🔄 Reseteando sistema...")
        self.reset_analysis()
        if self.robot and self.robot.is_connected:
            self.robot.set_target_position(0.0, 0.0, self.robot_z_fixed)
    
    def on_export(self, event):
        """Callback para exportar."""
        try:
            # Exportar datos
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"control_data_{timestamp}.json"
            self.controller_manager.export_data(filename)
            
            # Exportar gráfico
            plot_filename = f"control_plots_{timestamp}.png"
            self.fig.savefig(plot_filename, dpi=300, bbox_inches='tight')
            
            print(f"✅ Datos exportados: {filename}, {plot_filename}")
        except Exception as e:
            print(f"❌ Error exportando: {e}")
    
    def reset_analysis(self):
        """Resetea el análisis."""
        self.controller_manager.reset_controller_state()
        self.error_calculator.reset()
        self.performance_metrics.reset_session()
        self.reset_plot_data()
        
        # Limpiar gráficos
        self.line_error.set_data([], [])
        self.line_velocity.set_data([], [])
        self.ax_info.clear()
        
        self.fig.canvas.draw_idle()
    
    def run(self):
        """Ejecuta el sistema."""
        print("\n🖥️ Iniciando interfaz de matplotlib...")
        print("📋 Controles disponibles:")
        print("   • Radio buttons: Cambiar modo de control")
        print("   • Sliders: Ajustar parámetros PID")
        print("   • Botones: Iniciar, Reset, Exportar")
        print("\n🎯 Usa los controles en la interfaz para operar el sistema")
        
        plt.show()


def main():
    """Función principal."""
    print("=" * 70)
    print("🤖 SISTEMA DE CONTROL - VERSIÓN MATPLOTLIB")
    print("📊 ANÁLISIS DE LAZO ABIERTO vs LAZO CERRADO")
    print("=" * 70)
    
    try:
        system = MatplotlibControlSystem()
        system.run()
    
    except KeyboardInterrupt:
        print("\n🛑 Interrumpido por el usuario")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
