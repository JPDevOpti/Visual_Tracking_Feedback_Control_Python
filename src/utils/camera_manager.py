import cv2
import time
from typing import Optional, Tuple

class CameraManager:
    """
    Clase para manejar la captura de video desde la cámara web.
    """
    
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        """
        Inicializa el manager de cámara.
        
        Args:
            camera_index: Índice de la cámara (0 para cámara por defecto)
            width: Ancho de la resolución
            height: Alto de la resolución
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """
        Inicializa la conexión con la cámara.
        
        Returns:
            bool: True si la inicialización fue exitosa
        """
        try:
            # Primero intentar encontrar cámaras disponibles
            available_cameras = self._find_available_cameras()
            
            if not available_cameras:
                print("Error: No se encontraron cámaras disponibles")
                print("Posibles causas:")
                print("1. No hay cámaras conectadas")
                print("2. Permisos de cámara no otorgados")
                print("3. Cámara en uso por otra aplicación")
                return False
            
            print(f"Cámaras disponibles: {available_cameras}")
            
            # Intentar con el índice especificado primero
            if self.camera_index in available_cameras:
                camera_to_use = self.camera_index
            else:
                # Usar la primera cámara disponible
                camera_to_use = available_cameras[0]
                print(f"Cámara {self.camera_index} no disponible, usando cámara {camera_to_use}")
            
            # Intentar abrir la cámara
            self.cap = cv2.VideoCapture(camera_to_use)
            
            if not self.cap.isOpened():
                print(f"Error: No se pudo abrir la cámara {camera_to_use}")
                print("Soluciones posibles:")
                print("1. Ir a Configuración del Sistema > Privacidad y Seguridad > Cámara")
                print("2. Habilitar el acceso a la cámara para Terminal o Python")
                print("3. Reiniciar la aplicación después de otorgar permisos")
                return False
            
            # Verificar que podemos capturar frames
            ret, test_frame = self.cap.read()
            if not ret or test_frame is None:
                print("Error: No se puede capturar video de la cámara")
                self.cap.release()
                return False
                
            # Configurar resolución
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            # Configurar FPS a 60 para máxima fluidez
            self.cap.set(cv2.CAP_PROP_FPS, 60)
            
            # Obtener resolución real
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            self.camera_index = camera_to_use
            self.is_initialized = True
            print(f"Cámara {camera_to_use} inicializada: {actual_width}x{actual_height}")
            return True
            
        except Exception as e:
            print(f"Error al inicializar cámara: {e}")
            return False
    
    def _find_available_cameras(self) -> list:
        """
        Encuentra las cámaras disponibles en el sistema.
        
        Returns:
            List[int]: Lista de índices de cámaras disponibles
        """
        available_cameras = []
        
        # Probar hasta 5 cámaras
        for i in range(5):
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    # Intentar leer un frame para verificar que funciona
                    ret, _ = cap.read()
                    if ret:
                        available_cameras.append(i)
                cap.release()
            except:
                continue
        
        return available_cameras
    
    def capture_frame(self) -> Optional[Tuple[bool, any]]:
        """
        Captura un frame de la cámara.
        
        Returns:
            Tuple: (success, frame) donde success indica si la captura fue exitosa
        """
        if not self.is_initialized or self.cap is None:
            return None
            
        ret, frame = self.cap.read()
        return ret, frame
    
    def get_fps(self) -> float:
        """
        Obtiene los FPS configurados de la cámara.
        
        Returns:
            float: FPS de la cámara
        """
        if self.cap is not None:
            return self.cap.get(cv2.CAP_PROP_FPS)
        return 0.0
    
    def get_resolution(self) -> Tuple[int, int]:
        """
        Obtiene la resolución actual de la cámara.
        
        Returns:
            Tuple: (width, height)
        """
        if self.cap is not None:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return width, height
        return self.width, self.height
    
    def release(self):
        """
        Libera los recursos de la cámara.
        """
        if self.cap is not None:
            self.cap.release()
            self.is_initialized = False
            print("Cámara liberada")
