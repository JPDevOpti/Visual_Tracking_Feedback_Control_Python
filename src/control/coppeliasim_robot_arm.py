"""
Interfaz simple para controlar un brazo robótico UR5 en CoppeliaSim.
Versión simplificada para control directo.
"""

import time
import numpy as np

try:
    from coppeliasim_zmqremoteapi_client import RemoteAPIClient
except ImportError:
    print("❌ Error: coppeliasim-zmqremoteapi-client no está instalado")
    print("Instalar con: pip3 install coppeliasim-zmqremoteapi-client")
    RemoteAPIClient = None


class CoppeliaSimRobotArm:
    """
    Interfaz simple para controlar el brazo UR5 en CoppeliaSim.
    """
    
    def __init__(self):
        """Inicializa la interfaz del robot."""
        self.client = None
        self.sim = None
        self.is_connected = False
        
        # Handles de los joints del UR5 (se detectarán automáticamente)
        self.joint_handles = []
        self.tip_handle = None
        
        # Posición actual
        self.current_position = np.array([0.0, 0.0, 0.5])
        
        print("🤖 CoppeliaSimRobotArm inicializado")
    
    def connect(self) -> bool:
        """
        Conecta con CoppeliaSim.
        
        Returns:
            True si la conexión fue exitosa
        """
        if RemoteAPIClient is None:
            print("❌ API de CoppeliaSim no disponible")
            return False
        
        try:
            print("🔌 Conectando a CoppeliaSim...")
            
            # Crear cliente
            self.client = RemoteAPIClient()
            self.sim = self.client.getObject('sim')
            
            # Verificar conexión
            version = self.sim.getInt32Param(self.sim.intparam_program_version)
            print(f"✅ Conectado a CoppeliaSim versión: {version}")
            
            # Detectar robot UR5
            if not self._detect_ur5():
                return False
            
            self.is_connected = True
            return True
            
        except Exception as e:
            print(f"❌ Error conectando: {e}")
            print("💡 Asegúrate de que CoppeliaSim esté ejecutándose")
            return False
    
    def _detect_ur5(self) -> bool:
        """Detecta y configura el robot UR5."""
        try:
            print("🔍 Detectando robot UR5...")
            
            # Usar handles directos según el diagnóstico
            # Handles de joints según diagnóstico: 18, 21, 24, 27, 30, 32
            joint_handles_direct = [18, 21, 24, 27, 30, 32]
            joint_names = ['UR5_joint1', 'UR5_joint2', 'UR5_joint3', 
                          'UR5_joint4', 'UR5_joint5', 'UR5_joint6']
            
            self.joint_handles = []
            
            # Verificar que los handles son válidos
            for i, (handle, name) in enumerate(zip(joint_handles_direct, joint_names)):
                try:
                    # Verificar que el handle existe y tiene el nombre correcto
                    actual_name = self.sim.getObjectName(handle)
                    if actual_name == name:
                        self.joint_handles.append(handle)
                        print(f"  ✅ {name}: Handle {handle}")
                    else:
                        print(f"  ⚠️ Handle {handle} tiene nombre '{actual_name}', esperaba '{name}'")
                        # Intentar buscar por nombre
                        try:
                            correct_handle = self.sim.getObject(name)
                            self.joint_handles.append(correct_handle)
                            print(f"  ✅ {name}: Handle {correct_handle} (encontrado por nombre)")
                        except:
                            print(f"  ❌ No se encontró {name}")
                            return False
                except Exception as e:
                    print(f"  ❌ Error con handle {handle}: {e}")
                    return False
            
            if len(self.joint_handles) != 6:
                print(f"  ❌ Solo se encontraron {len(self.joint_handles)} de 6 joints")
                return False
            
            # Buscar tip del robot - Handle 35 según diagnóstico
            try:
                tip_name = self.sim.getObjectName(35)
                if tip_name == 'UR5_connection':
                    self.tip_handle = 35
                    print(f"  ✅ Tip encontrado: UR5_connection (Handle 35)")
                else:
                    print(f"  ⚠️ Handle 35 tiene nombre '{tip_name}', esperaba 'UR5_connection'")
                    # Buscar por nombre
                    try:
                        self.tip_handle = self.sim.getObject('UR5_connection')
                        print(f"  ✅ Tip encontrado por nombre: UR5_connection")
                    except:
                        print("  ⚠️ Tip no encontrado, usando último joint")
                        self.tip_handle = self.joint_handles[-1]
            except:
                print("  ⚠️ Tip no encontrado, usando último joint") 
                self.tip_handle = self.joint_handles[-1]
            
            # Obtener posición inicial
            if self.tip_handle:
                pos = self.sim.getObjectPosition(self.tip_handle, -1)
                self.current_position = np.array(pos)
                print(f"📍 Posición inicial: [{pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f}]")
            
            print("✅ Robot UR5 detectado correctamente")
            print(f"  📋 6 joints configurados")
            print(f"  📍 Tip configurado")
            return True
            
        except Exception as e:
            print(f"❌ Error detectando UR5: {e}")
            return False
    
    def start_simulation(self) -> bool:
        """Inicia la simulación."""
        try:
            sim_state = self.sim.getSimulationState()
            if sim_state == 0:  # Detenida
                print("🚀 Iniciando simulación...")
                self.sim.startSimulation()
                time.sleep(1.0)
                print("✅ Simulación iniciada")
            return True
        except Exception as e:
            print(f"❌ Error iniciando simulación: {e}")
            return False
    
    def is_simulation_running(self) -> bool:
        """Verifica si la simulación está corriendo."""
        try:
            return self.sim.getSimulationState() == 17  # Running
        except:
            return False
    
    def set_target_position(self, x: float, y: float, z: float) -> bool:
        """
        Mueve el robot a la posición especificada.
        
        Args:
            x, y, z: Coordenadas en metros
            
        Returns:
            True si el comando fue enviado
        """
        if not self.is_connected or not self.joint_handles:
            return False
        
        # Validar límites básicos
        if not (-0.5 <= x <= 0.5 and -0.5 <= y <= 0.5 and 0.1 <= z <= 1.0):
            print(f"⚠️ Posición fuera de límites: ({x:.3f}, {y:.3f}, {z:.3f})")
            return False
        
        try:
            # Cinemática inversa simplificada para UR5
            # Joint 1: Rotación base
            theta1 = np.arctan2(y, x) if (abs(x) > 0.001 or abs(y) > 0.001) else 0.0
            
            # Joint 2 y 3: Posición vertical (simplificado)
            r = np.sqrt(x*x + y*y)
            if r > 0.8:  # Limitar alcance
                r = 0.8
            
            theta2 = np.arctan2(z - 0.2, r) if r > 0.001 else 0.0
            theta3 = -theta2 * 0.8
            
            # Joints 4, 5, 6: Orientación (simplificada)
            theta4 = 0.0
            theta5 = np.pi/2
            theta6 = 0.0
            
            angles = [theta1, theta2, theta3, theta4, theta5, theta6]
            
            # Enviar comandos a los joints
            for i, (handle, angle) in enumerate(zip(self.joint_handles, angles)):
                self.sim.setJointTargetPosition(handle, angle)
            
            print(f"🎯 Moviendo a: ({x:.3f}, {y:.3f}, {z:.3f})")
            return True
            
        except Exception as e:
            print(f"❌ Error moviendo robot: {e}")
            return False
    
    def get_current_position(self):
        """Obtiene la posición actual del tip."""
        try:
            if self.tip_handle:
                pos = self.sim.getObjectPosition(self.tip_handle, -1)
                self.current_position = np.array(pos)
                return pos
        except:
            pass
        return tuple(self.current_position)
    
    def disconnect(self):
        """Desconecta del simulador."""
        print("🔌 Desconectando...")
        self.is_connected = False
        self.client = None
        self.sim = None
        print("✅ Desconectado")


def test_coppeliasim_connection():
    """Función de prueba básica."""
    print("🧪 Probando conexión con CoppeliaSim...")
    
    robot = CoppeliaSimRobotArm()
    
    if robot.connect():
        print("✅ Conexión exitosa!")
        
        if robot.start_simulation():
            print("✅ Simulación iniciada!")
            
            # Prueba de movimiento
            robot.set_target_position(0.2, 0.1, 0.4)
            time.sleep(1)
            
            pos = robot.get_current_position()
            print(f"📍 Posición actual: {pos}")
        
        robot.disconnect()
        return True
    else:
        print("❌ No se pudo conectar")
        print("💡 Asegúrate de que CoppeliaSim esté ejecutándose con el UR5")
        return False


if __name__ == "__main__":
    test_coppeliasim_connection()
