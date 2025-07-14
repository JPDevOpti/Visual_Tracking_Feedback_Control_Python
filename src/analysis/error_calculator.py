"""
Calculador de Errores y Métricas de Rendimiento
Analiza el error entre posición deseada y actual del sistema
"""

import numpy as np
import time
from collections import deque
from typing import List, Tuple, Dict, Optional
import math


class ErrorCalculator:
    """
    Calcula errores y métricas de rendimiento del sistema de control.
    """
    
    def __init__(self, buffer_size: int = 1000):
        """
        Inicializa el calculador de errores.
        
        Args:
            buffer_size: Tamaño del buffer para mantener historial
        """
        print("📊 Inicializando Error Calculator...")
        
        self.buffer_size = buffer_size
        
        # Buffers circulares para datos
        self.timestamps = deque(maxlen=buffer_size)
        self.desired_positions = deque(maxlen=buffer_size)
        self.actual_positions = deque(maxlen=buffer_size)
        self.errors = deque(maxlen=buffer_size)
        self.error_magnitudes = deque(maxlen=buffer_size)
        self.correction_velocities = deque(maxlen=buffer_size)
        
        # Estado actual
        self.current_error = np.array([0.0, 0.0, 0.0])
        self.current_error_magnitude = 0.0
        self.current_correction_velocity = 0.0
        
        # Métricas acumuladas
        self.metrics = {
            'rms_error': 0.0,
            'max_error': 0.0,
            'mean_error': 0.0,
            'std_error': 0.0,
            'settling_time': None,
            'overshoot_percentage': 0.0,
            'steady_state_error': 0.0
        }
        
        # Configuración para detección de establecimiento
        self.settling_threshold = 0.05  # 5% del valor final
        self.settling_time_window = 50   # Puntos para confirmar establecimiento
        
        print("✅ Error Calculator inicializado")
    
    def update(self, desired_position: np.ndarray, actual_position: np.ndarray, 
               timestamp: Optional[float] = None) -> Dict[str, float]:
        """
        Actualiza el cálculo de errores con nuevos datos.
        
        Args:
            desired_position: Posición deseada [x, y, z]
            actual_position: Posición actual [x, y, z]
            timestamp: Tiempo actual (opcional)
            
        Returns:
            Diccionario con métricas actualizadas
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calcular error
        error = desired_position - actual_position
        error_magnitude = np.linalg.norm(error)
        
        # Calcular velocidad de corrección
        correction_velocity = self._calculate_correction_velocity(error_magnitude, timestamp)
        
        # Actualizar buffers
        self.timestamps.append(timestamp)
        self.desired_positions.append(desired_position.copy())
        self.actual_positions.append(actual_position.copy())
        self.errors.append(error.copy())
        self.error_magnitudes.append(error_magnitude)
        self.correction_velocities.append(correction_velocity)
        
        # Actualizar estado actual
        self.current_error = error
        self.current_error_magnitude = error_magnitude
        self.current_correction_velocity = correction_velocity
        
        # Calcular métricas
        self._update_metrics()
        
        return self.get_current_metrics()
    
    def _calculate_correction_velocity(self, error_magnitude: float, timestamp: float) -> float:
        """
        Calcula la velocidad de corrección del error.
        
        Args:
            error_magnitude: Magnitud del error actual
            timestamp: Tiempo actual
            
        Returns:
            Velocidad de corrección (cambio del error por tiempo)
        """
        if len(self.error_magnitudes) < 2 or len(self.timestamps) < 2:
            return 0.0
        
        # Calcular diferencia temporal
        dt = timestamp - self.timestamps[-1]
        if dt <= 0:
            return 0.0
        
        # Calcular cambio en magnitud del error
        de = error_magnitude - self.error_magnitudes[-1]
        
        # Velocidad de corrección (negativa indica mejora)
        correction_velocity = -de / dt  # Negativo porque queremos reducción del error
        
        return correction_velocity
    
    def _update_metrics(self):
        """Actualiza las métricas de rendimiento."""
        if len(self.error_magnitudes) < 2:
            return
        
        error_array = np.array(list(self.error_magnitudes))
        
        # Métricas básicas
        self.metrics['rms_error'] = np.sqrt(np.mean(error_array ** 2))
        self.metrics['max_error'] = np.max(error_array)
        self.metrics['mean_error'] = np.mean(error_array)
        self.metrics['std_error'] = np.std(error_array)
        
        # Error de estado estacionario (promedio de últimos 20% de puntos)
        if len(error_array) >= 10:
            steady_state_window = max(5, len(error_array) // 5)
            self.metrics['steady_state_error'] = np.mean(error_array[-steady_state_window:])
        
        # Tiempo de establecimiento
        self._calculate_settling_time()
        
        # Sobreimpulso
        self._calculate_overshoot()
    
    def _calculate_settling_time(self):
        """Calcula el tiempo de establecimiento."""
        if len(self.error_magnitudes) < self.settling_time_window:
            return
        
        error_array = np.array(list(self.error_magnitudes))
        
        # Buscar el punto donde el error se mantiene dentro del threshold
        target_error = self.settling_threshold
        
        for i in range(len(error_array) - self.settling_time_window):
            window = error_array[i:i + self.settling_time_window]
            if np.all(window <= target_error):
                # Tiempo de establecimiento encontrado
                settling_index = i
                if len(self.timestamps) > settling_index:
                    start_time = list(self.timestamps)[0]
                    settling_time_point = list(self.timestamps)[settling_index]
                    self.metrics['settling_time'] = settling_time_point - start_time
                    break
    
    def _calculate_overshoot(self):
        """Calcula el porcentaje de sobreimpulso."""
        if len(self.error_magnitudes) < 10:
            return
        
        error_array = np.array(list(self.error_magnitudes))
        
        # Buscar el valor final (promedio de últimos 20%)
        final_window = max(5, len(error_array) // 5)
        final_value = np.mean(error_array[-final_window:])
        
        # Buscar el máximo overshoot
        max_value = np.max(error_array)
        
        if final_value > 0:
            self.metrics['overshoot_percentage'] = ((max_value - final_value) / final_value) * 100
        else:
            self.metrics['overshoot_percentage'] = 0.0
    
    def get_current_metrics(self) -> Dict[str, float]:
        """
        Obtiene las métricas actuales.
        
        Returns:
            Diccionario con métricas actualizadas
        """
        return {
            'current_error_magnitude': self.current_error_magnitude,
            'current_correction_velocity': self.current_correction_velocity,
            'rms_error': self.metrics['rms_error'],
            'max_error': self.metrics['max_error'],
            'mean_error': self.metrics['mean_error'],
            'std_error': self.metrics['std_error'],
            'settling_time': self.metrics['settling_time'],
            'overshoot_percentage': self.metrics['overshoot_percentage'],
            'steady_state_error': self.metrics['steady_state_error']
        }
    
    def get_error_statistics(self, window_size: Optional[int] = None) -> Dict[str, float]:
        """
        Obtiene estadísticas del error en una ventana específica.
        
        Args:
            window_size: Tamaño de ventana (None para todos los datos)
            
        Returns:
            Estadísticas del error
        """
        if len(self.error_magnitudes) == 0:
            return {'count': 0}
        
        if window_size is None:
            error_data = list(self.error_magnitudes)
        else:
            error_data = list(self.error_magnitudes)[-window_size:]
        
        if not error_data:
            return {'count': 0}
        
        error_array = np.array(error_data)
        
        return {
            'count': len(error_data),
            'min': np.min(error_array),
            'max': np.max(error_array),
            'mean': np.mean(error_array),
            'median': np.median(error_array),
            'std': np.std(error_array),
            'var': np.var(error_array),
            'percentile_95': np.percentile(error_array, 95),
            'percentile_99': np.percentile(error_array, 99)
        }
    
    def get_time_series_data(self, max_points: Optional[int] = None) -> Dict[str, List]:
        """
        Obtiene datos de series de tiempo para graficación.
        
        Args:
            max_points: Número máximo de puntos a retornar
            
        Returns:
            Diccionario con arrays de datos
        """
        if max_points is None:
            max_points = len(self.timestamps)
        
        # Tomar últimos max_points
        start_idx = max(0, len(self.timestamps) - max_points)
        
        return {
            'timestamps': list(self.timestamps)[start_idx:],
            'desired_positions': [pos.tolist() for pos in list(self.desired_positions)[start_idx:]],
            'actual_positions': [pos.tolist() for pos in list(self.actual_positions)[start_idx:]],
            'errors': [err.tolist() for err in list(self.errors)[start_idx:]],
            'error_magnitudes': list(self.error_magnitudes)[start_idx:],
            'correction_velocities': list(self.correction_velocities)[start_idx:]
        }
    
    def reset(self):
        """Resetea todos los datos y métricas."""
        print("🔄 Reseteando Error Calculator...")
        
        self.timestamps.clear()
        self.desired_positions.clear()
        self.actual_positions.clear()
        self.errors.clear()
        self.error_magnitudes.clear()
        self.correction_velocities.clear()
        
        self.current_error = np.array([0.0, 0.0, 0.0])
        self.current_error_magnitude = 0.0
        self.current_correction_velocity = 0.0
        
        self.metrics = {
            'rms_error': 0.0,
            'max_error': 0.0,
            'mean_error': 0.0,
            'std_error': 0.0,
            'settling_time': None,
            'overshoot_percentage': 0.0,
            'steady_state_error': 0.0
        }
        
        print("✅ Error Calculator reseteado")
    
    def analyze_step_response(self, step_start_time: float, step_target: float) -> Dict[str, float]:
        """
        Analiza la respuesta a escalón del sistema.
        
        Args:
            step_start_time: Tiempo de inicio del escalón
            step_target: Valor objetivo del escalón
            
        Returns:
            Análisis de la respuesta a escalón
        """
        if len(self.timestamps) < 10:
            return {}
        
        # Encontrar índice de inicio del escalón
        timestamps_list = list(self.timestamps)
        start_idx = 0
        for i, t in enumerate(timestamps_list):
            if t >= step_start_time:
                start_idx = i
                break
        
        if start_idx >= len(timestamps_list) - 5:
            return {}
        
        # Datos posteriores al escalón
        step_errors = list(self.error_magnitudes)[start_idx:]
        step_times = timestamps_list[start_idx:]
        
        if not step_errors:
            return {}
        
        # Análisis de respuesta a escalón
        analysis = {}
        
        # Tiempo de subida (10% a 90% del valor final)
        final_value = np.mean(step_errors[-10:]) if len(step_errors) >= 10 else step_errors[-1]
        rise_start = final_value * 0.9  # Para error, buscamos reducción
        rise_end = final_value * 0.1
        
        rise_start_idx = None
        rise_end_idx = None
        
        for i, error in enumerate(step_errors):
            if rise_start_idx is None and error <= rise_start:
                rise_start_idx = i
            if rise_end_idx is None and error <= rise_end:
                rise_end_idx = i
                break
        
        if rise_start_idx is not None and rise_end_idx is not None:
            analysis['rise_time'] = step_times[rise_end_idx] - step_times[rise_start_idx]
        
        # Pico máximo
        max_error = np.max(step_errors)
        max_error_idx = np.argmax(step_errors)
        analysis['peak_error'] = max_error
        analysis['peak_time'] = step_times[max_error_idx] - step_times[0]
        
        # Sobreimpulso
        if final_value > 0:
            analysis['overshoot'] = ((max_error - final_value) / final_value) * 100
        else:
            analysis['overshoot'] = 0.0
        
        return analysis


class PerformanceMetrics:
    """
    Calcula y mantiene métricas de rendimiento del sistema.
    """
    
    def __init__(self):
        """Inicializa el calculador de métricas de rendimiento."""
        print("📈 Inicializando Performance Metrics...")
        
        self.session_start_time = time.time()
        self.total_commands_sent = 0
        self.successful_tracking_time = 0.0
        self.total_distance_traveled = 0.0
        self.energy_efficiency_score = 0.0
        
        # Contadores por modo
        self.mode_statistics = {
            'open_loop': {
                'time_active': 0.0,
                'commands_sent': 0,
                'avg_error': 0.0,
                'max_error': 0.0
            },
            'closed_loop': {
                'time_active': 0.0,
                'commands_sent': 0,
                'avg_error': 0.0,
                'max_error': 0.0
            }
        }
        
        print("✅ Performance Metrics inicializado")
    
    def update_mode_statistics(self, mode: str, error: float, command_sent: bool = True):
        """
        Actualiza estadísticas específicas del modo.
        
        Args:
            mode: Modo actual ('open_loop' o 'closed_loop')
            error: Error actual
            command_sent: Si se envió un comando
        """
        if mode not in self.mode_statistics:
            return
        
        stats = self.mode_statistics[mode]
        
        if command_sent:
            stats['commands_sent'] += 1
            self.total_commands_sent += 1
        
        # Actualizar error promedio
        current_count = stats['commands_sent']
        if current_count > 1:
            stats['avg_error'] = ((stats['avg_error'] * (current_count - 1)) + error) / current_count
        else:
            stats['avg_error'] = error
        
        # Actualizar error máximo
        stats['max_error'] = max(stats['max_error'], error)
    
    def get_session_summary(self) -> Dict[str, any]:
        """
        Obtiene resumen de la sesión actual.
        
        Returns:
            Resumen de métricas de la sesión
        """
        session_duration = time.time() - self.session_start_time
        
        return {
            'session_duration': session_duration,
            'total_commands': self.total_commands_sent,
            'commands_per_second': self.total_commands_sent / session_duration if session_duration > 0 else 0,
            'mode_statistics': self.mode_statistics,
            'total_distance_traveled': self.total_distance_traveled,
            'energy_efficiency': self.energy_efficiency_score
        }
    
    def reset_session(self):
        """Resetea las métricas de la sesión."""
        print("🔄 Reseteando Performance Metrics...")
        
        self.session_start_time = time.time()
        self.total_commands_sent = 0
        self.successful_tracking_time = 0.0
        self.total_distance_traveled = 0.0
        self.energy_efficiency_score = 0.0
        
        for mode in self.mode_statistics:
            self.mode_statistics[mode] = {
                'time_active': 0.0,
                'commands_sent': 0,
                'avg_error': 0.0,
                'max_error': 0.0
            }
        
        print("✅ Performance Metrics reseteado")
