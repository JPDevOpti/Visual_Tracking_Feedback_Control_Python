"""
Gestor Principal de Control para Sistema de Lazo Abierto y Cerrado
Maneja la transición entre modos y coordina los controladores
"""

import numpy as np
import time
from enum import Enum
from typing import Tuple, Optional, Dict, Any, List

class ControlMode(Enum):
    """Modos de control disponibles."""
    OPEN_LOOP = "open_loop"
    CLOSED_LOOP = "closed_loop"


class ControllerManager:
    """
    Gestor principal que coordina el control en lazo abierto y cerrado.
    """
    
    def __init__(self):
        """Inicializa el gestor de control."""
        print("🎮 Inicializando Controller Manager...")
        
        # Estado del sistema
        self.current_mode = ControlMode.OPEN_LOOP
        self.is_active = False
        
        # Parámetros del workspace
        self.workspace_limits = {
            'x_range': (-0.3, 0.3),
            'y_range': (-0.3, 0.3),
            'z_fixed': 0.5
        }
        
        # Parámetros de control
        self.control_params = {
            'open_loop': {
                'smoothing': 0.7  # Factor de suavizado
            },
            'closed_loop': {
                'kp': 2.0,  # Ganancia proporcional
                'ki': 0.1,  # Ganancia integral  
                'kd': 0.05, # Ganancia derivativa
                'integral_limit': 0.5,  # Límite para windup
                'derivative_filter': 0.1  # Filtro para derivada
            }
        }
        
        # Estado interno del control
        self.state = {
            'last_position': np.array([0.0, 0.0, self.workspace_limits['z_fixed']]),
            'last_error': np.array([0.0, 0.0, 0.0]),
            'integral_error': np.array([0.0, 0.0, 0.0]),
            'last_time': time.time()
        }
        
        # Historial para análisis
        self.history = {
            'desired_positions': [],
            'actual_positions': [],
            'control_signals': [],
            'errors': [],
            'timestamps': [],
            'mode_changes': []
        }
        
        print("✅ Controller Manager inicializado")
    
    def set_control_mode(self, mode: ControlMode) -> bool:
        """
        Cambia el modo de control.
        
        Args:
            mode: Nuevo modo de control
            
        Returns:
            True si el cambio fue exitoso
        """
        if mode == self.current_mode:
            return True
        
        print(f"🔄 Cambiando modo: {self.current_mode.value} → {mode.value}")
        
        # Registrar cambio de modo
        self.history['mode_changes'].append({
            'timestamp': time.time(),
            'from_mode': self.current_mode.value,
            'to_mode': mode.value
        })
        
        # Resetear estado interno al cambiar modo
        self.reset_controller_state()
        
        self.current_mode = mode
        print(f"✅ Modo cambiado a: {mode.value}")
        return True
    
    def reset_controller_state(self):
        """Resetea el estado interno del controlador."""
        print("🔄 Reseteando estado del controlador...")
        
        self.state['last_error'] = np.array([0.0, 0.0, 0.0])
        self.state['integral_error'] = np.array([0.0, 0.0, 0.0])
        self.state['last_time'] = time.time()
        
        # Limpiar historial reciente pero mantener para análisis
        if len(self.history['timestamps']) > 1000:  # Mantener últimos 1000 puntos
            for key in ['desired_positions', 'actual_positions', 'control_signals', 'errors', 'timestamps']:
                self.history[key] = self.history[key][-1000:]
    
    def calculate_control_signal(self, desired_position: np.ndarray, 
                                actual_position: np.ndarray) -> np.ndarray:
        """
        Calcula la señal de control según el modo activo.
        
        Args:
            desired_position: Posición deseada [x, y, z]
            actual_position: Posición actual del robot [x, y, z]
            
        Returns:
            Señal de control [x, y, z]
        """
        current_time = time.time()
        
        # Registrar en historial
        self.history['desired_positions'].append(desired_position.copy())
        self.history['actual_positions'].append(actual_position.copy())
        self.history['timestamps'].append(current_time)
        
        if self.current_mode == ControlMode.OPEN_LOOP:
            control_signal = self._open_loop_control(desired_position)
        else:  # CLOSED_LOOP
            control_signal = self._closed_loop_control(desired_position, actual_position, current_time)
        
        # Registrar señal de control
        self.history['control_signals'].append(control_signal.copy())
        
        # Actualizar estado
        self.state['last_position'] = control_signal.copy()
        self.state['last_time'] = current_time
        
        return control_signal
    
    def _open_loop_control(self, desired_position: np.ndarray) -> np.ndarray:
        """
        Control en lazo abierto con suavizado.
        
        Args:
            desired_position: Posición deseada
            
        Returns:
            Posición suavizada
        """
        smoothing = self.control_params['open_loop']['smoothing']
        
        # Aplicar suavizado
        smoothed_position = (
            smoothing * self.state['last_position'] + 
            (1 - smoothing) * desired_position
        )
        
        # El error en lazo abierto es siempre la diferencia con la entrada
        error = desired_position - smoothed_position
        self.history['errors'].append(error.copy())
        
        return smoothed_position
    
    def _closed_loop_control(self, desired_position: np.ndarray, 
                           actual_position: np.ndarray, current_time: float) -> np.ndarray:
        """
        Control en lazo cerrado con PID.
        
        Args:
            desired_position: Posición de referencia
            actual_position: Posición actual del sistema
            current_time: Tiempo actual
            
        Returns:
            Señal de control PID
        """
        # Calcular error
        error = desired_position - actual_position
        self.history['errors'].append(error.copy())
        
        # Calcular dt
        dt = current_time - self.state['last_time']
        if dt <= 0:
            dt = 0.01  # Prevenir división por cero
        
        # Parámetros PID
        kp = self.control_params['closed_loop']['kp']
        ki = self.control_params['closed_loop']['ki']
        kd = self.control_params['closed_loop']['kd']
        integral_limit = self.control_params['closed_loop']['integral_limit']
        derivative_filter = self.control_params['closed_loop']['derivative_filter']
        
        # Término Proporcional
        proportional = kp * error
        
        # Término Integral (con anti-windup)
        self.state['integral_error'] += error * dt
        # Limitar integral para prevenir windup
        self.state['integral_error'] = np.clip(
            self.state['integral_error'], 
            -integral_limit, 
            integral_limit
        )
        integral = ki * self.state['integral_error']
        
        # Término Derivativo (con filtro)
        derivative_error = (error - self.state['last_error']) / dt
        derivative = kd * derivative_error
        
        # Aplicar filtro pasa-bajas a la derivada para reducir ruido
        if hasattr(self.state, 'filtered_derivative'):
            self.state['filtered_derivative'] = (
                derivative_filter * derivative + 
                (1 - derivative_filter) * self.state['filtered_derivative']
            )
        else:
            self.state['filtered_derivative'] = derivative
        
        # Señal de control total
        control_signal = actual_position + proportional + integral + self.state['filtered_derivative']
        
        # Aplicar límites del workspace
        control_signal = self._apply_workspace_limits(control_signal)
        
        # Actualizar error anterior
        self.state['last_error'] = error.copy()
        
        return control_signal
    
    def _apply_workspace_limits(self, position: np.ndarray) -> np.ndarray:
        """
        Aplica límites del workspace a la posición.
        
        Args:
            position: Posición a limitar
            
        Returns:
            Posición limitada
        """
        limited_position = position.copy()
        
        # Limitar X
        limited_position[0] = np.clip(
            limited_position[0],
            self.workspace_limits['x_range'][0],
            self.workspace_limits['x_range'][1]
        )
        
        # Limitar Y
        limited_position[1] = np.clip(
            limited_position[1],
            self.workspace_limits['y_range'][0],
            self.workspace_limits['y_range'][1]
        )
        
        # Mantener Z fijo
        limited_position[2] = self.workspace_limits['z_fixed']
        
        return limited_position
    
    def update_control_parameters(self, param_dict: Dict[str, Any]) -> bool:
        """
        Actualiza parámetros de control en tiempo real.
        
        Args:
            param_dict: Diccionario con nuevos parámetros
            
        Returns:
            True si la actualización fue exitosa
        """
        try:
            if self.current_mode == ControlMode.OPEN_LOOP:
                if 'smoothing' in param_dict:
                    self.control_params['open_loop']['smoothing'] = param_dict['smoothing']
            else:  # CLOSED_LOOP
                for param in ['kp', 'ki', 'kd', 'integral_limit', 'derivative_filter']:
                    if param in param_dict:
                        self.control_params['closed_loop'][param] = param_dict[param]
            
            print(f"✅ Parámetros actualizados: {param_dict}")
            return True
            
        except Exception as e:
            print(f"❌ Error actualizando parámetros: {e}")
            return False
    
    def get_current_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del controlador.
        
        Returns:
            Diccionario con información del estado
        """
        current_error = np.array([0.0, 0.0, 0.0])
        if len(self.history['errors']) > 0:
            current_error = self.history['errors'][-1]
        
        return {
            'mode': self.current_mode.value,
            'active': self.is_active,
            'current_error': current_error,
            'error_magnitude': np.linalg.norm(current_error),
            'last_position': self.state['last_position'],
            'control_params': self.control_params[self.current_mode.value],
            'history_length': len(self.history['timestamps'])
        }
    
    def get_performance_metrics(self, window_size: int = 100) -> Dict[str, float]:
        """
        Calcula métricas de rendimiento.
        
        Args:
            window_size: Tamaño de ventana para cálculos
            
        Returns:
            Diccionario con métricas
        """
        if len(self.history['errors']) < 2:
            return {'rms_error': 0.0, 'max_error': 0.0, 'mean_error': 0.0}
        
        # Tomar últimos puntos según window_size
        recent_errors = self.history['errors'][-window_size:]
        error_magnitudes = [np.linalg.norm(err) for err in recent_errors]
        
        return {
            'rms_error': np.sqrt(np.mean(np.square(error_magnitudes))),
            'max_error': np.max(error_magnitudes),
            'mean_error': np.mean(error_magnitudes),
            'std_error': np.std(error_magnitudes)
        }
    
    def export_data(self, filename: str) -> bool:
        """
        Exporta datos del historial a archivo.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            True si exportó exitosamente
        """
        try:
            import json
            
            # Convertir arrays numpy a listas para JSON
            export_data = {
                'timestamps': self.history['timestamps'],
                'desired_positions': [pos.tolist() for pos in self.history['desired_positions']],
                'actual_positions': [pos.tolist() for pos in self.history['actual_positions']],
                'control_signals': [sig.tolist() for sig in self.history['control_signals']],
                'errors': [err.tolist() for err in self.history['errors']],
                'mode_changes': self.history['mode_changes'],
                'control_params': self.control_params
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Datos exportados a: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error exportando datos: {e}")
            return False
        
    @property
    def error_data(self) -> List[float]:
        """
        Obtiene datos de error como magnitudes para análisis académico.
        
        Returns:
            Lista de magnitudes de error
        """
        return [np.linalg.norm(error) for error in self.history['errors']]
    
    @property
    def timestamps(self) -> List[float]:
        """
        Obtiene timestamps para análisis académico.
        
        Returns:
            Lista de timestamps
        """
        return self.history['timestamps'].copy()
    
    def get_error_data_for_analysis(self) -> Tuple[List[float], List[float]]:
        """
        Obtiene datos de error y timestamps para análisis académico.
        
        Returns:
            Tupla con (error_magnitudes, timestamps)
        """
        error_magnitudes = [np.linalg.norm(error) for error in self.history['errors']]
        return error_magnitudes, self.history['timestamps'].copy()
