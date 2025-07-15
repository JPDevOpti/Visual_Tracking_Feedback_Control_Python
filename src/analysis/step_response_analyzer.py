"""
Analizador de Respuesta al Escalón para Métricas Académicas
Calcula tiempo de subida, tiempo de establecimiento, sobreimpulso y error en estado estacionario
"""

import numpy as np
import time
from collections import deque
from typing import Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
from datetime import datetime


class StepResponseAnalyzer:
    """
    Analizador específico para respuesta al escalón según criterios académicos.
    Calcula las métricas clásicas de sistemas de control.
    """
    
    def __init__(self, buffer_size: int = 500):
        """
        Inicializa el analizador de respuesta al escalón.
        
        Args:
            buffer_size: Tamaño del buffer para datos de análisis
        """
        print("📊 Inicializando Step Response Analyzer...")
        
        self.buffer_size = buffer_size
        
        # Buffers para datos del escalón
        self.step_timestamps = deque(maxlen=buffer_size)
        self.step_desired_positions = deque(maxlen=buffer_size)
        self.step_actual_positions = deque(maxlen=buffer_size)
        self.step_errors = deque(maxlen=buffer_size)
        
        # Estado del análisis
        self.is_analyzing = False
        self.step_detected = False
        self.step_start_time = None
        self.step_initial_value = None
        self.step_target_value = None
        self.step_direction = None  # 'up' or 'down'
        
        # Configuración de umbrales académicos estándar
        self.config = {
            'step_detection_threshold': 0.08,  # 8cm para detectar escalón
            'rise_time_start': 0.10,          # 10% del valor final
            'rise_time_end': 0.90,            # 90% del valor final
            'settling_tolerance': 0.02,        # ±2% para settling time
            'settling_confirmation_time': 1.0, # 1 segundo dentro de la banda
            'steady_state_window': 1.5,       # 1.5 segundos para estado estacionario
            'min_analysis_duration': 3.0,     # Mínimo 3 segundos de análisis
            'max_analysis_duration': 10.0     # Máximo 10 segundos de análisis
        }
        
        # Métricas calculadas
        self.academic_metrics = {
            'rise_time': None,
            'settling_time': None,
            'overshoot_percentage': None,
            'steady_state_error': None,
            'peak_value': None,
            'peak_time': None,
            'final_value': None,
            'analysis_valid': False,
            'analysis_timestamp': None
        }
        
        print("✅ Step Response Analyzer inicializado")
    
    def start_step_analysis(self, initial_position: np.ndarray):
        """
        Inicia un nuevo análisis de escalón.
        
        Args:
            initial_position: Posición inicial del sistema
        """
        print("🎯 Iniciando análisis de escalón...")
        
        # Limpiar buffers
        self.step_timestamps.clear()
        self.step_desired_positions.clear()
        self.step_actual_positions.clear()
        self.step_errors.clear()
        
        # Resetear estado
        self.is_analyzing = True
        self.step_detected = False
        self.step_start_time = time.time()
        self.step_initial_value = np.linalg.norm(initial_position[:2])  # Solo X,Y
        self.step_target_value = None
        self.step_direction = None
        
        # Resetear métricas
        for key in self.academic_metrics:
            if key not in ['analysis_timestamp']:
                self.academic_metrics[key] = None
        
        self.academic_metrics['analysis_valid'] = False
        
        print(f"📍 Valor inicial: {self.step_initial_value:.4f}")
    
    def update_analysis(self, desired_position: np.ndarray, actual_position: np.ndarray, 
                       timestamp: float) -> Dict[str, any]:
        """
        Actualiza el análisis con nuevos datos.
        
        Args:
            desired_position: Posición deseada [x, y, z]
            actual_position: Posición actual [x, y, z]
            timestamp: Tiempo actual
            
        Returns:
            Diccionario con métricas actualizadas
        """
        if not self.is_analyzing:
            return self.academic_metrics
        
        # Convertir a magnitudes (solo X, Y)
        desired_magnitude = np.linalg.norm(desired_position[:2])
        actual_magnitude = np.linalg.norm(actual_position[:2])
        error_magnitude = abs(desired_magnitude - actual_magnitude)
        
        # Detectar escalón si no se ha detectado aún
        if not self.step_detected:
            self._detect_step(desired_magnitude)
        
        # Almacenar datos
        self.step_timestamps.append(timestamp - self.step_start_time)
        self.step_desired_positions.append(desired_magnitude)
        self.step_actual_positions.append(actual_magnitude)
        self.step_errors.append(error_magnitude)
        
        # Verificar si terminar análisis
        analysis_duration = timestamp - self.step_start_time
        if (analysis_duration > self.config['max_analysis_duration'] or 
            (analysis_duration > self.config['min_analysis_duration'] and self._is_settled())):
            self._finalize_analysis()
        
        return self.academic_metrics
    
    def _detect_step(self, current_desired: float):
        """Detecta cuándo ocurre un escalón en la señal de referencia."""
        if len(self.step_desired_positions) < 5:  # Necesitamos algunos puntos
            return
        
        # Calcular cambio promedio en los últimos puntos
        recent_values = list(self.step_desired_positions)[-5:]
        value_change = abs(current_desired - self.step_initial_value)
        
        if value_change > self.config['step_detection_threshold']:
            self.step_detected = True
            self.step_target_value = current_desired
            self.step_direction = 'up' if current_desired > self.step_initial_value else 'down'
            
            print(f"📈 Escalón detectado: {self.step_initial_value:.4f} → {self.step_target_value:.4f}")
            print(f"📏 Amplitud: {value_change:.4f} ({self.step_direction})")
    
    def _is_settled(self) -> bool:
        """Verifica si el sistema se ha establecido."""
        if not self.step_detected or len(self.step_actual_positions) < 30:
            return False
        
        # Verificar si está dentro de la banda de tolerancia
        tolerance = abs(self.step_target_value * self.config['settling_tolerance'])
        recent_values = list(self.step_actual_positions)[-30:]  # Últimos 30 puntos
        
        upper_bound = self.step_target_value + tolerance
        lower_bound = self.step_target_value - tolerance
        
        # Todos los valores recientes deben estar dentro de la banda
        return all(lower_bound <= val <= upper_bound for val in recent_values)
    
    def _finalize_analysis(self):
        """Finaliza el análisis y calcula todas las métricas."""
        if not self.step_detected or len(self.step_actual_positions) < 50:
            print("⚠️ Análisis incompleto - datos insuficientes")
            self.is_analyzing = False
            return
        
        print("🧮 Calculando métricas académicas...")
        
        # Convertir a arrays numpy
        timestamps = np.array(self.step_timestamps)
        actual_positions = np.array(self.step_actual_positions)
        
        # Calcular cada métrica
        self._calculate_rise_time(timestamps, actual_positions)
        self._calculate_settling_time(timestamps, actual_positions)
        self._calculate_overshoot(actual_positions)
        self._calculate_steady_state_error(actual_positions)
        
        # Marcar análisis como válido
        self.academic_metrics['analysis_valid'] = True
        self.academic_metrics['analysis_timestamp'] = datetime.now().isoformat()
        self.academic_metrics['final_value'] = float(np.mean(actual_positions[-20:]))
        
        self.is_analyzing = False
        
        print("✅ Análisis completado:")
        for key, value in self.academic_metrics.items():
            if value is not None and key not in ['analysis_timestamp', 'analysis_valid']:
                if 'time' in key:
                    print(f"   {key}: {value:.3f} s")
                elif 'percentage' in key:
                    print(f"   {key}: {value:.2f} %")
                else:
                    print(f"   {key}: {value:.4f}")
    
    def _calculate_rise_time(self, timestamps: np.ndarray, positions: np.ndarray):
        """Calcula el tiempo de subida (10% a 90%)."""
        try:
            step_amplitude = self.step_target_value - self.step_initial_value
            
            # Valores de referencia
            ten_percent_value = self.step_initial_value + 0.1 * step_amplitude
            ninety_percent_value = self.step_initial_value + 0.9 * step_amplitude
            
            # Encontrar índices donde se cruzan estos valores
            if self.step_direction == 'up':
                idx_10 = np.where(positions >= ten_percent_value)[0]
                idx_90 = np.where(positions >= ninety_percent_value)[0]
            else:  # down
                idx_10 = np.where(positions <= ten_percent_value)[0]
                idx_90 = np.where(positions <= ninety_percent_value)[0]
            
            if len(idx_10) > 0 and len(idx_90) > 0:
                t_10 = timestamps[idx_10[0]]
                t_90 = timestamps[idx_90[0]]
                
                if t_90 > t_10:
                    self.academic_metrics['rise_time'] = float(t_90 - t_10)
                else:
                    # Interpolación para mayor precisión
                    t_10_interp = np.interp(ten_percent_value, positions, timestamps)
                    t_90_interp = np.interp(ninety_percent_value, positions, timestamps)
                    self.academic_metrics['rise_time'] = float(abs(t_90_interp - t_10_interp))
        
        except Exception as e:
            print(f"⚠️ Error calculando rise time: {e}")
            self.academic_metrics['rise_time'] = None
    
    def _calculate_settling_time(self, timestamps: np.ndarray, positions: np.ndarray):
        """Calcula el tiempo de establecimiento (±2%)."""
        try:
            tolerance = abs(self.step_target_value * self.config['settling_tolerance'])
            upper_bound = self.step_target_value + tolerance
            lower_bound = self.step_target_value - tolerance
            
            # Encontrar el último punto fuera de la banda
            outside_band = (positions > upper_bound) | (positions < lower_bound)
            
            if np.any(outside_band):
                last_outside_idx = np.where(outside_band)[0][-1]
                
                # Verificar que se mantiene dentro después de este punto
                remaining_points = positions[last_outside_idx+1:]
                if len(remaining_points) > 10:  # Al menos 10 puntos de confirmación
                    within_band = (remaining_points >= lower_bound) & (remaining_points <= upper_bound)
                    if np.all(within_band):
                        self.academic_metrics['settling_time'] = float(timestamps[last_outside_idx])
                    else:
                        self.academic_metrics['settling_time'] = float(timestamps[-1])
            else:
                self.academic_metrics['settling_time'] = 0.0  # Ya estaba establecido
        
        except Exception as e:
            print(f"⚠️ Error calculando settling time: {e}")
            self.academic_metrics['settling_time'] = None
    
    def _calculate_overshoot(self, positions: np.ndarray):
        """Calcula el sobreimpulso como porcentaje."""
        try:
            if self.step_direction == 'up':
                peak_value = np.max(positions)
                overshoot_condition = peak_value > self.step_target_value
            else:  # down
                peak_value = np.min(positions)
                overshoot_condition = peak_value < self.step_target_value
            
            self.academic_metrics['peak_value'] = float(peak_value)
            
            # Encontrar tiempo del pico
            peak_idx = np.argmax(positions) if self.step_direction == 'up' else np.argmin(positions)
            self.academic_metrics['peak_time'] = float(np.array(self.step_timestamps)[peak_idx])
            
            if overshoot_condition:
                step_amplitude = abs(self.step_target_value - self.step_initial_value)
                overshoot_magnitude = abs(peak_value - self.step_target_value)
                overshoot_percentage = (overshoot_magnitude / step_amplitude) * 100
                self.academic_metrics['overshoot_percentage'] = float(overshoot_percentage)
            else:
                self.academic_metrics['overshoot_percentage'] = 0.0
        
        except Exception as e:
            print(f"⚠️ Error calculando overshoot: {e}")
            self.academic_metrics['overshoot_percentage'] = None
    
    def _calculate_steady_state_error(self, positions: np.ndarray):
        """Calcula el error en estado estacionario."""
        try:
            # Usar los últimos puntos para el estado estacionario
            steady_state_points = int(len(positions) * 0.3)  # Último 30%
            steady_state_points = max(20, min(steady_state_points, 50))  # Entre 20 y 50 puntos
            
            steady_state_values = positions[-steady_state_points:]
            steady_state_mean = np.mean(steady_state_values)
            
            self.academic_metrics['steady_state_error'] = float(abs(self.step_target_value - steady_state_mean))
        
        except Exception as e:
            print(f"⚠️ Error calculando steady state error: {e}")
            self.academic_metrics['steady_state_error'] = None
    
    def stop_analysis(self):
        """Detiene el análisis actual."""
        if self.is_analyzing:
            print("⏹️ Deteniendo análisis de escalón...")
            self._finalize_analysis()
    
    def get_metrics(self) -> Dict[str, any]:
        """Retorna las métricas calculadas."""
        return self.academic_metrics.copy()
    
    def is_analysis_active(self) -> bool:
        """Verifica si hay un análisis en curso."""
        return self.is_analyzing
    
    def has_valid_analysis(self) -> bool:
        """Verifica si hay un análisis válido disponible."""
        return self.academic_metrics.get('analysis_valid', False)
    
    def reset(self):
        """Resetea el analizador para un nuevo análisis."""
        self.is_analyzing = False
        self.step_detected = False
        self.step_start_time = None
        self.step_initial_value = None
        self.step_target_value = None
        self.step_direction = None
        
        # Limpiar buffers
        self.step_timestamps.clear()
        self.step_desired_positions.clear()
        self.step_actual_positions.clear()
        self.step_errors.clear()
        
        # Resetear métricas
        for key in self.academic_metrics:
            self.academic_metrics[key] = None
        
        self.academic_metrics['analysis_valid'] = False
        
        print("🔄 Step Response Analyzer reseteado")
    
    def export_step_analysis(self, filename: str) -> bool:
        """
        Exporta el análisis de escalón a un archivo.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            True si la exportación fue exitosa
        """
        try:
            if not self.has_valid_analysis():
                print("⚠️ No hay análisis válido para exportar")
                return False
            
            # Preparar datos para exportación
            analysis_data = {
                'step_analysis': {
                    'configuration': self.config,
                    'step_parameters': {
                        'initial_value': self.step_initial_value,
                        'target_value': self.step_target_value,
                        'step_direction': self.step_direction,
                        'step_amplitude': abs(self.step_target_value - self.step_initial_value) if self.step_target_value else None
                    },
                    'academic_metrics': self.academic_metrics,
                    'raw_data': {
                        'timestamps': list(self.step_timestamps),
                        'desired_positions': list(self.step_desired_positions),
                        'actual_positions': list(self.step_actual_positions),
                        'errors': list(self.step_errors)
                    }
                }
            }
            
            import json
            with open(filename, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            print(f"📄 Análisis exportado a: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando análisis: {e}")
            return False
    
    def analyze_step_response(self, timestamps: List[float], error_data: List[float], 
                             target_value: float = 0.0) -> Dict[str, float]:
        """
        Analiza respuesta a escalón basado en datos históricos (compatibilidad).
        
        Args:
            timestamps: Lista de timestamps
            error_data: Lista de magnitudes de error
            target_value: Valor objetivo (generalmente 0 para errores)
            
        Returns:
            Diccionario con métricas de análisis
        """
        if len(timestamps) < 10 or len(error_data) < 10:
            return {
                'rise_time': None,
                'settling_time': None,
                'overshoot': None,
                'steady_state_error': None,
                'analysis_valid': False
            }
        
        try:
            # Convertir a arrays numpy
            time_array = np.array(timestamps)
            error_array = np.array(error_data)
            
            # Normalizar tiempo a partir de cero
            time_array = time_array - time_array[0]
            
            # Para análisis de error, el valor objetivo es mínimo error
            final_value = np.mean(error_array[-10:])  # Promedio de últimos 10 puntos
            
            # Tiempo de subida (90% a 10% del valor inicial para error)
            initial_value = error_array[0]
            rise_10_percent = initial_value * 0.9
            rise_90_percent = initial_value * 0.1
            
            rise_start_idx = None
            rise_end_idx = None
            
            for i, error in enumerate(error_array):
                if rise_start_idx is None and error <= rise_10_percent:
                    rise_start_idx = i
                if rise_end_idx is None and error <= rise_90_percent:
                    rise_end_idx = i
                    break
            
            rise_time = None
            if rise_start_idx is not None and rise_end_idx is not None:
                rise_time = time_array[rise_end_idx] - time_array[rise_start_idx]
            
            # Tiempo de establecimiento (±5% del valor final)
            tolerance = final_value * 0.05
            settling_time = None
            
            for i in range(len(error_array) - 10):  # Buscar desde el final hacia atrás
                window = error_array[i:i+10]
                if all(abs(val - final_value) <= tolerance for val in window):
                    settling_time = time_array[i]
                    break
            
            # Sobreimpulso
            min_error = np.min(error_array)
            overshoot = 0.0
            if final_value > 0:
                overshoot = max(0, (final_value - min_error) / final_value * 100)
            
            return {
                'rise_time': rise_time,
                'settling_time': settling_time,
                'overshoot': overshoot,
                'steady_state_error': final_value,
                'peak_error': min_error,
                'final_value': final_value,
                'analysis_valid': True
            }
            
        except Exception as e:
            print(f"⚠️ Error en análisis de escalón: {e}")
            return {
                'rise_time': None,
                'settling_time': None,
                'overshoot': None,
                'steady_state_error': None,
                'analysis_valid': False
            }
