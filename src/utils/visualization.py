import cv2
import numpy as np
from typing import Tuple, Optional

def draw_landmarks(image: np.ndarray, landmarks: list, connections: list = None) -> np.ndarray:
    """
    Dibuja los landmarks de la mano en la imagen.
    
    Args:
        image: Imagen donde dibujar
        landmarks: Lista de landmarks de la mano
        connections: Conexiones entre landmarks (opcional)
    
    Returns:
        Imagen con landmarks dibujados
    """
    height, width = image.shape[:2]
    
    # Dibujar puntos de landmarks
    for landmark in landmarks:
        x = int(landmark.x * width)
        y = int(landmark.y * height)
        cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
    
    return image

def draw_tracking_point(image: np.ndarray, position: Tuple[int, int], 
                       color: Tuple[int, int, int] = (0, 0, 255), 
                       radius: int = 10) -> np.ndarray:
    """
    Dibuja un punto de tracking en la imagen.
    
    Args:
        image: Imagen donde dibujar
        position: Coordenadas (x, y) del punto
        color: Color del punto en formato BGR
        radius: Radio del círculo
    
    Returns:
        Imagen con el punto dibujado
    """
    cv2.circle(image, position, radius, color, -1)
    cv2.circle(image, position, radius + 2, (255, 255, 255), 2)
    return image

def draw_tracking_info(image: np.ndarray, position: Tuple[int, int], 
                      confidence: float, fps: float) -> np.ndarray:
    """
    Dibuja información del tracking en la imagen.
    
    Args:
        image: Imagen donde dibujar
        position: Posición actual (x, y)
        confidence: Nivel de confianza de la detección
        fps: FPS actual
    
    Returns:
        Imagen con información dibujada
    """
    # Configuración del texto
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    color = (255, 255, 255)
    thickness = 2
    
    # Información a mostrar
    info_lines = [
        f"Posicion: ({position[0]}, {position[1]})",
        f"Confianza: {confidence:.2f}",
        f"FPS: {fps:.1f}"
    ]
    
    # Dibujar cada línea
    y_offset = 30
    for i, line in enumerate(info_lines):
        y_pos = y_offset + (i * 25)
        cv2.putText(image, line, (10, y_pos), font, font_scale, color, thickness)
    
    return image

def draw_crosshair(image: np.ndarray, position: Tuple[int, int], 
                  size: int = 20, color: Tuple[int, int, int] = (0, 255, 255)) -> np.ndarray:
    """
    Dibuja una cruz centrada en la posición especificada.
    
    Args:
        image: Imagen donde dibujar
        position: Posición central (x, y)
        size: Tamaño de la cruz
        color: Color de la cruz
    
    Returns:
        Imagen con la cruz dibujada
    """
    x, y = position
    
    # Línea horizontal
    cv2.line(image, (x - size, y), (x + size, y), color, 2)
    # Línea vertical
    cv2.line(image, (x, y - size), (x, y + size), color, 2)
    
    return image
