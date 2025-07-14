#!/usr/bin/env python3
"""
Pruebas básicas para el sistema de tracking de mano.
"""

import unittest
import sys
import os

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestHandTracking(unittest.TestCase):
    """
    Pruebas unitarias para el sistema de tracking.
    """
    
    def test_camera_manager_creation(self):
        """
        Prueba la creación del manager de cámara.
        """
        try:
            from utils.camera_manager import CameraManager
            camera = CameraManager()
            self.assertIsNotNone(camera)
            self.assertEqual(camera.width, 640)
            self.assertEqual(camera.height, 480)
        except ImportError as e:
            self.skipTest(f"Dependencias no disponibles: {e}")
    
    def test_mediapipe_detector_creation(self):
        """
        Prueba la creación del detector de MediaPipe.
        """
        try:
            from tracking.mediapipe_detector import MediaPipeHandDetector
            detector = MediaPipeHandDetector()
            self.assertIsNotNone(detector)
            self.assertEqual(detector.max_hands, 1)
            detector.cleanup()
        except ImportError as e:
            self.skipTest(f"Dependencias no disponibles: {e}")
    
    def test_config_files_exist(self):
        """
        Verifica que los archivos de configuración existan.
        """
        config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
        
        camera_config = os.path.join(config_dir, 'camera_config.json')
        detection_config = os.path.join(config_dir, 'detection_config.json')
        
        self.assertTrue(os.path.exists(camera_config))
        self.assertTrue(os.path.exists(detection_config))


if __name__ == '__main__':
    print("Ejecutando pruebas del sistema de tracking...")
    unittest.main()
