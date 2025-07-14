import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, List, Dict

class MediaPipeHandDetector:
    """
    Detector de manos usando MediaPipe.
    Detecta hasta 2 manos y proporciona 21 landmarks por mano.
    """
    
    def __init__(self, max_hands: int = 1, min_detection_confidence: float = 0.7,
                 min_tracking_confidence: float = 0.5):
        """
        Inicializa el detector de manos de MediaPipe.
        
        Args:
            max_hands: Número máximo de manos a detectar
            min_detection_confidence: Confianza mínima para detección
            min_tracking_confidence: Confianza mínima para tracking
        """
        self.max_hands = max_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        
        # Inicializar MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Crear el objeto detector
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.min_detection_confidence,
            min_tracking_confidence=self.min_tracking_confidence
        )
        
        # Variables de estado
        self.last_detection = None
        self.detection_confidence = 0.0
        self.is_hand_detected = False
        
    def detect(self, image: np.ndarray) -> Optional[Dict]:
        """
        Detecta manos en la imagen.
        
        Args:
            image: Imagen en formato BGR
            
        Returns:
            Dict con información de detección o None si no se detecta mano
        """
        # Convertir BGR a RGB (MediaPipe usa RGB)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Procesar la imagen
        results = self.hands.process(rgb_image)
        
        # Resetear estado
        self.is_hand_detected = False
        self.last_detection = None
        
        if results.multi_hand_landmarks:
            # Tomar la primera mano detectada
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Calcular centro de la palma (landmark 9 = base del dedo medio)
            palm_landmark = hand_landmarks.landmark[9]
            
            # Convertir coordenadas normalizadas a píxeles
            height, width = image.shape[:2]
            palm_x = int(palm_landmark.x * width)
            palm_y = int(palm_landmark.y * height)
            
            # Calcular confianza (basada en visibilidad de landmarks clave)
            key_landmarks = [0, 5, 9, 13, 17]  # Muñeca y base de dedos
            confidence = sum(hand_landmarks.landmark[i].visibility for i in key_landmarks if 
                           hasattr(hand_landmarks.landmark[i], 'visibility')) / len(key_landmarks)
            
            # Si no hay atributo visibility, usar confianza por defecto
            if confidence == 0:
                confidence = 0.8
            
            self.detection_confidence = confidence
            self.is_hand_detected = True
            
            # Crear diccionario con información de detección
            detection_info = {
                'position': (palm_x, palm_y),
                'confidence': confidence,
                'landmarks': hand_landmarks.landmark,
                'raw_landmarks': hand_landmarks
            }
            
            self.last_detection = detection_info
            return detection_info
        
        return None
    
    def get_palm_position(self, image: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Obtiene solo la posición del centro de la palma.
        
        Args:
            image: Imagen en formato BGR
            
        Returns:
            Tupla (x, y) con la posición del centro de la palma o None
        """
        detection = self.detect(image)
        if detection:
            return detection['position']
        return None
    
    def get_fingertip_positions(self, image: np.ndarray) -> Optional[List[Tuple[int, int]]]:
        """
        Obtiene las posiciones de las puntas de los dedos.
        
        Args:
            image: Imagen en formato BGR
            
        Returns:
            Lista de tuplas (x, y) con posiciones de puntas de dedos o None
        """
        detection = self.detect(image)
        if not detection:
            return None
        
        # Índices de las puntas de los dedos en MediaPipe
        fingertip_indices = [4, 8, 12, 16, 20]  # Pulgar, índice, medio, anular, meñique
        
        height, width = image.shape[:2]
        fingertips = []
        
        for idx in fingertip_indices:
            landmark = detection['landmarks'][idx]
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            fingertips.append((x, y))
        
        return fingertips
    
    def draw_landmarks(self, image: np.ndarray, draw_connections: bool = True) -> np.ndarray:
        """
        Dibuja los landmarks de la mano detectada en la imagen.
        
        Args:
            image: Imagen donde dibujar
            draw_connections: Si dibujar las conexiones entre landmarks
            
        Returns:
            Imagen con landmarks dibujados
        """
        if not self.last_detection:
            return image
        
        # Dibujar landmarks y conexiones
        if draw_connections:
            self.mp_drawing.draw_landmarks(
                image,
                self.last_detection['raw_landmarks'],
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
        else:
            self.mp_drawing.draw_landmarks(
                image,
                self.last_detection['raw_landmarks'],
                None,
                self.mp_drawing_styles.get_default_hand_landmarks_style()
            )
        
        return image
    
    def get_hand_info(self) -> Dict:
        """
        Obtiene información del estado actual del detector.
        
        Returns:
            Diccionario con información del estado
        """
        return {
            'is_detected': self.is_hand_detected,
            'confidence': self.detection_confidence,
            'last_position': self.last_detection['position'] if self.last_detection else None,
            'max_hands': self.max_hands,
            'min_detection_confidence': self.min_detection_confidence,
            'min_tracking_confidence': self.min_tracking_confidence
        }
    
    def cleanup(self):
        """
        Limpia los recursos de MediaPipe.
        """
        if self.hands:
            self.hands.close()
