"""
Visualizador en Tiempo Real para Gráficos de Control
Muestra error, velocidad de corrección y posiciones en tiempo real
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
from collections import deque
from typing import Dict, List, Optional, Tuple
import time


class RealTimePlotter:
    """
    Graficador en tiempo real para métricas del sistema de control.
    """
    
    def __init__(self, max_points: int = 300, update_interval: int = 50):
        """
        Inicializa el graficador en tiempo real.
        
        Args:
            max_points: Número máximo de puntos a mostrar
            update_interval: Intervalo de actualización en ms
        """
        print("📊 Inicializando Real Time Plotter...")
        
        self.max_points = max_points
        self.update_interval = update_interval
        
        # Configurar estilo
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # Crear figura y subplots
        self.fig = plt.figure(figsize=(12, 8))
        self.fig.suptitle('Sistema de Control - Análisis en Tiempo Real', fontsize=14, fontweight='bold')
        
        # Crear grid de subplots
        gs = self.fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # Subplot 1: Error vs Tiempo
        self.ax_error = self.fig.add_subplot(gs[0, 0])
        self.ax_error.set_title('Error vs Tiempo', fontweight='bold')
        self.ax_error.set_xlabel('Tiempo (s)')
        self.ax_error.set_ylabel('Error (m)')
        self.ax_error.grid(True, alpha=0.3)
        
        # Subplot 2: Velocidad de Corrección
        self.ax_velocity = self.fig.add_subplot(gs[0, 1])
        self.ax_velocity.set_title('Velocidad de Corrección', fontweight='bold')
        self.ax_velocity.set_xlabel('Tiempo (s)')
        self.ax_velocity.set_ylabel('Velocidad (m/s)')
        self.ax_velocity.grid(True, alpha=0.3)
        
        # Subplot 3: Posiciones X-Y
        self.ax_position = self.fig.add_subplot(gs[1, 0])
        self.ax_position.set_title('Trayectoria X-Y', fontweight='bold')
        self.ax_position.set_xlabel('X (m)')
        self.ax_position.set_ylabel('Y (m)')
        self.ax_position.grid(True, alpha=0.3)
        self.ax_position.set_aspect('equal')
        
        # Subplot 4: Histograma de Error
        self.ax_hist = self.fig.add_subplot(gs[1, 1])
        self.ax_hist.set_title('Distribución de Error', fontweight='bold')
        self.ax_hist.set_xlabel('Error (m)')
        self.ax_hist.set_ylabel('Frecuencia')
        self.ax_hist.grid(True, alpha=0.3)
        
        # Subplot 5: Panel de información (ocupa toda la fila inferior)
        self.ax_info = self.fig.add_subplot(gs[2, :])
        self.ax_info.set_title('Métricas de Rendimiento', fontweight='bold')
        self.ax_info.axis('off')
        
        # Buffers de datos
        self.reset_data()
        
        # Configurar líneas de los gráficos
        self.setup_plot_lines()
        
        # Variables de control
        self.is_running = False
        self.animation = None
        self.start_time = time.time()
        
        print("✅ Real Time Plotter inicializado")
    
    def reset_data(self):
        """Resetea todos los buffers de datos."""
        self.timestamps = deque(maxlen=self.max_points)
        self.errors = deque(maxlen=self.max_points)
        self.velocities = deque(maxlen=self.max_points)
        self.desired_x = deque(maxlen=self.max_points)
        self.desired_y = deque(maxlen=self.max_points)
        self.actual_x = deque(maxlen=self.max_points)
        self.actual_y = deque(maxlen=self.max_points)
        
        # Datos para histograma
        self.error_history = deque(maxlen=1000)  # Mayor buffer para histograma
        
        # Estado actual
        self.current_mode = "unknown"
        self.current_metrics = {}
    
    def setup_plot_lines(self):
        """Configura las líneas de los gráficos."""
        # Línea de error
        self.line_error, = self.ax_error.plot([], [], 'r-', linewidth=2, label='Error')
        self.ax_error.legend()
        
        # Línea de velocidad de corrección
        self.line_velocity, = self.ax_velocity.plot([], [], 'b-', linewidth=2, label='Velocidad')
        self.ax_velocity.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        self.ax_velocity.legend()
        
        # Líneas de posición
        self.line_desired, = self.ax_position.plot([], [], 'g-', linewidth=2, label='Deseada', alpha=0.7)
        self.line_actual, = self.ax_position.plot([], [], 'orange', linewidth=2, label='Real')
        self.scatter_current = self.ax_position.scatter([], [], c='red', s=100, label='Actual', zorder=5)
        
        # Configurar límites del workspace
        self.ax_position.set_xlim(-0.35, 0.35)
        self.ax_position.set_ylim(-0.35, 0.35)
        
        # Agregar rectángulo del workspace
        workspace_rect = patches.Rectangle((-0.3, -0.3), 0.6, 0.6, 
                                         linewidth=2, edgecolor='gray', 
                                         facecolor='none', linestyle='--', alpha=0.5)
        self.ax_position.add_patch(workspace_rect)
        self.ax_position.legend()
        
        # Texto de información
        self.info_text = self.ax_info.text(0.02, 0.5, '', transform=self.ax_info.transAxes,
                                          fontsize=10, verticalalignment='center',
                                          bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    def update_data(self, error_magnitude: float, correction_velocity: float,
                   desired_pos: np.ndarray, actual_pos: np.ndarray,
                   current_time: Optional[float] = None, mode: str = "unknown",
                   metrics: Optional[Dict] = None):
        """
        Actualiza los datos para graficación.
        
        Args:
            error_magnitude: Magnitud del error actual
            correction_velocity: Velocidad de corrección
            desired_pos: Posición deseada [x, y, z]
            actual_pos: Posición actual [x, y, z]
            current_time: Tiempo actual
            mode: Modo de control actual
            metrics: Métricas adicionales
        """
        if current_time is None:
            current_time = time.time()
        
        # Tiempo relativo desde el inicio
        relative_time = current_time - self.start_time
        
        # Actualizar buffers
        self.timestamps.append(relative_time)
        self.errors.append(error_magnitude)
        self.velocities.append(correction_velocity)
        self.desired_x.append(desired_pos[0])
        self.desired_y.append(desired_pos[1])
        self.actual_x.append(actual_pos[0])
        self.actual_y.append(actual_pos[1])
        
        # Actualizar historial de errores
        self.error_history.append(error_magnitude)
        
        # Actualizar estado
        self.current_mode = mode
        self.current_metrics = metrics or {}
    
    def update_plots(self, frame):
        """
        Actualiza todos los gráficos (llamado por animación).
        
        Args:
            frame: Frame de animación (no usado)
        """
        if len(self.timestamps) < 2:
            return
        
        # Convertir a arrays
        times = np.array(list(self.timestamps))
        errors = np.array(list(self.errors))
        velocities = np.array(list(self.velocities))
        
        # Actualizar gráfico de error
        self.line_error.set_data(times, errors)
        self.ax_error.relim()
        self.ax_error.autoscale_view()
        
        # Actualizar gráfico de velocidad
        self.line_velocity.set_data(times, velocities)
        self.ax_velocity.relim()
        self.ax_velocity.autoscale_view()
        
        # Actualizar trayectoria
        desired_x_array = np.array(list(self.desired_x))
        desired_y_array = np.array(list(self.desired_y))
        actual_x_array = np.array(list(self.actual_x))
        actual_y_array = np.array(list(self.actual_y))
        
        self.line_desired.set_data(desired_x_array, desired_y_array)
        self.line_actual.set_data(actual_x_array, actual_y_array)
        
        # Actualizar punto actual
        if len(actual_x_array) > 0 and len(actual_y_array) > 0:
            self.scatter_current.set_offsets([[actual_x_array[-1], actual_y_array[-1]]])
        
        # Actualizar histograma
        self.update_histogram()
        
        # Actualizar panel de información
        self.update_info_panel()
        
        return [self.line_error, self.line_velocity, self.line_desired, 
                self.line_actual, self.scatter_current]
    
    def update_histogram(self):
        """Actualiza el histograma de distribución de errores."""
        if len(self.error_history) < 10:
            return
        
        self.ax_hist.clear()
        self.ax_hist.set_title('Distribución de Error', fontweight='bold')
        self.ax_hist.set_xlabel('Error (m)')
        self.ax_hist.set_ylabel('Frecuencia')
        self.ax_hist.grid(True, alpha=0.3)
        
        errors_array = np.array(list(self.error_history))
        
        # Crear histograma
        n_bins = min(30, len(errors_array) // 10)
        counts, bins, patches = self.ax_hist.hist(errors_array, bins=n_bins, 
                                                 alpha=0.7, color='skyblue', 
                                                 edgecolor='black', linewidth=0.5)
        
        # Agregar líneas de estadísticas
        mean_error = np.mean(errors_array)
        std_error = np.std(errors_array)
        
        self.ax_hist.axvline(mean_error, color='red', linestyle='--', 
                           linewidth=2, label=f'Media: {mean_error:.4f}')
        self.ax_hist.axvline(mean_error + std_error, color='orange', 
                           linestyle=':', linewidth=2, label=f'+1σ: {mean_error + std_error:.4f}')
        self.ax_hist.axvline(mean_error - std_error, color='orange', 
                           linestyle=':', linewidth=2, label=f'-1σ: {mean_error - std_error:.4f}')
        
        self.ax_hist.legend(fontsize=8)
    
    def update_info_panel(self):
        """Actualiza el panel de información."""
        if not self.current_metrics:
            return
        
        # Crear texto de información
        info_lines = []
        
        # Información del modo
        mode_color = "🟢" if self.current_mode == "closed_loop" else "🔵"
        info_lines.append(f"{mode_color} Modo: {self.current_mode.replace('_', ' ').title()}")
        
        # Métricas actuales
        if 'current_error_magnitude' in self.current_metrics:
            error = self.current_metrics['current_error_magnitude']
            info_lines.append(f"Error Actual: {error:.4f} m")
        
        if 'current_correction_velocity' in self.current_metrics:
            velocity = self.current_metrics['current_correction_velocity']
            velocity_icon = "⬇️" if velocity > 0 else "⬆️" if velocity < 0 else "➡️"
            info_lines.append(f"Velocidad Corrección: {velocity_icon} {velocity:.4f} m/s")
        
        # Métricas estadísticas
        if 'rms_error' in self.current_metrics:
            rms = self.current_metrics['rms_error']
            info_lines.append(f"Error RMS: {rms:.4f} m")
        
        if 'max_error' in self.current_metrics:
            max_err = self.current_metrics['max_error']
            info_lines.append(f"Error Máximo: {max_err:.4f} m")
        
        # Tiempo de establecimiento
        if 'settling_time' in self.current_metrics and self.current_metrics['settling_time']:
            settling = self.current_metrics['settling_time']
            info_lines.append(f"Tiempo Establecimiento: {settling:.2f} s")
        
        # Sobreimpulso
        if 'overshoot_percentage' in self.current_metrics:
            overshoot = self.current_metrics['overshoot_percentage']
            info_lines.append(f"Sobreimpulso: {overshoot:.1f}%")
        
        # Crear texto formateado
        info_text = "\n".join(info_lines)
        
        # Agregar tiempo de ejecución
        runtime = time.time() - self.start_time
        info_text += f"\n\n⏱️ Tiempo: {runtime:.1f} s"
        info_text += f"\n📊 Puntos: {len(self.timestamps)}"
        
        self.info_text.set_text(info_text)
    
    def start_animation(self):
        """Inicia la animación en tiempo real."""
        if self.is_running:
            return
        
        print("🎬 Iniciando animación en tiempo real...")
        self.is_running = True
        self.start_time = time.time()
        
        self.animation = FuncAnimation(self.fig, self.update_plots, 
                                     interval=self.update_interval,
                                     blit=False, cache_frame_data=False)
        
        plt.show(block=False)
        print("✅ Animación iniciada")
    
    def stop_animation(self):
        """Detiene la animación."""
        if not self.is_running:
            return
        
        print("⏹️ Deteniendo animación...")
        self.is_running = False
        
        if self.animation:
            self.animation.event_source.stop()
            self.animation = None
        
        print("✅ Animación detenida")
    
    def reset_plots(self):
        """Resetea todos los gráficos."""
        print("🔄 Reseteando gráficos...")
        
        self.reset_data()
        self.start_time = time.time()
        
        # Limpiar gráficos
        for ax in [self.ax_error, self.ax_velocity, self.ax_position, self.ax_hist]:
            for line in ax.lines:
                line.set_data([], [])
        
        # Resetear scatter
        self.scatter_current.set_offsets(np.empty((0, 2)))
        
        # Limpiar histograma
        self.ax_hist.clear()
        self.setup_plot_lines()
        
        print("✅ Gráficos reseteados")
    
    def save_plots(self, filename: str):
        """
        Guarda los gráficos actuales.
        
        Args:
            filename: Nombre del archivo
        """
        try:
            self.fig.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"✅ Gráficos guardados en: {filename}")
        except Exception as e:
            print(f"❌ Error guardando gráficos: {e}")
    
    def get_figure(self):
        """Retorna la figura de matplotlib para integración externa."""
        return self.fig


class ComparisonPlotter:
    """
    Graficador para comparar diferentes modos de control.
    """
    
    def __init__(self):
        """Inicializa el graficador de comparación."""
        print("📈 Inicializando Comparison Plotter...")
        
        self.data_storage = {
            'open_loop': {'timestamps': [], 'errors': [], 'metrics': {}},
            'closed_loop': {'timestamps': [], 'errors': [], 'metrics': {}}
        }
        
        print("✅ Comparison Plotter inicializado")
    
    def store_session_data(self, mode: str, timestamps: List[float], 
                          errors: List[float], metrics: Dict):
        """
        Almacena datos de una sesión para comparación.
        
        Args:
            mode: Modo de control
            timestamps: Lista de timestamps
            errors: Lista de errores
            metrics: Métricas calculadas
        """
        if mode in self.data_storage:
            self.data_storage[mode] = {
                'timestamps': timestamps.copy(),
                'errors': errors.copy(),
                'metrics': metrics.copy()
            }
            print(f"📊 Datos almacenados para modo: {mode}")
    
    def create_comparison_plot(self) -> plt.Figure:
        """
        Crea gráfico comparativo entre modos.
        
        Returns:
            Figura de matplotlib con comparación
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Comparación: Lazo Abierto vs Lazo Cerrado', fontsize=14, fontweight='bold')
        
        # Gráfico 1: Errores vs Tiempo
        ax1 = axes[0, 0]
        ax1.set_title('Error vs Tiempo')
        ax1.set_xlabel('Tiempo (s)')
        ax1.set_ylabel('Error (m)')
        ax1.grid(True, alpha=0.3)
        
        for mode, data in self.data_storage.items():
            if data['timestamps'] and data['errors']:
                label = mode.replace('_', ' ').title()
                color = 'blue' if mode == 'open_loop' else 'red'
                ax1.plot(data['timestamps'], data['errors'], 
                        label=label, color=color, alpha=0.7)
        ax1.legend()
        
        # Gráfico 2: Distribución de Errores
        ax2 = axes[0, 1]
        ax2.set_title('Distribución de Errores')
        ax2.set_xlabel('Error (m)')
        ax2.set_ylabel('Densidad')
        ax2.grid(True, alpha=0.3)
        
        for mode, data in self.data_storage.items():
            if data['errors']:
                label = mode.replace('_', ' ').title()
                color = 'blue' if mode == 'open_loop' else 'red'
                ax2.hist(data['errors'], bins=30, alpha=0.5, 
                        label=label, color=color, density=True)
        ax2.legend()
        
        # Gráfico 3: Métricas Comparativas
        ax3 = axes[1, 0]
        ax3.set_title('Métricas Comparativas')
        ax3.axis('off')
        
        # Crear tabla de métricas
        metrics_text = "Métrica\t\tLazo Abierto\tLazo Cerrado\n"
        metrics_text += "-" * 50 + "\n"
        
        metric_names = ['rms_error', 'max_error', 'mean_error', 'settling_time']
        for metric in metric_names:
            open_val = self.data_storage['open_loop']['metrics'].get(metric, 'N/A')
            closed_val = self.data_storage['closed_loop']['metrics'].get(metric, 'N/A')
            
            if isinstance(open_val, float):
                open_val = f"{open_val:.4f}"
            if isinstance(closed_val, float):
                closed_val = f"{closed_val:.4f}"
                
            metrics_text += f"{metric}\t{open_val}\t{closed_val}\n"
        
        ax3.text(0.1, 0.5, metrics_text, fontfamily='monospace', 
                fontsize=10, verticalalignment='center')
        
        # Gráfico 4: Análisis Estadístico
        ax4 = axes[1, 1]
        ax4.set_title('Análisis Estadístico')
        
        modes = []
        rms_errors = []
        max_errors = []
        
        for mode, data in self.data_storage.items():
            if data['metrics']:
                modes.append(mode.replace('_', ' ').title())
                rms_errors.append(data['metrics'].get('rms_error', 0))
                max_errors.append(data['metrics'].get('max_error', 0))
        
        x = np.arange(len(modes))
        width = 0.35
        
        ax4.bar(x - width/2, rms_errors, width, label='RMS Error', alpha=0.7)
        ax4.bar(x + width/2, max_errors, width, label='Max Error', alpha=0.7)
        
        ax4.set_xlabel('Modo de Control')
        ax4.set_ylabel('Error (m)')
        ax4.set_xticks(x)
        ax4.set_xticklabels(modes)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
