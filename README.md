# Visual Tracking and Feedback Control with Python

Este proyecto implementa un sistema de tracking de manos usando MediaPipe y sistemas de control de realimentación.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

Para ejecutar el tracking básico de manos:

```bash
make run
```

Para diagnosticar problemas de cámara:

```bash
make diagnose
```

Para ver todos los comandos disponibles:

```bash
make help
```

## Solución de Problemas

### Error de permisos de cámara en macOS

Si obtienes un error como "OpenCV: not authorized to capture video", sigue estos pasos:

1. **Verificar diagnóstico:**
   ```bash
   make diagnose
   ```

2. **Otorgar permisos de cámara:**
   - Abrir "Configuración del Sistema" (System Settings)
   - Ir a "Privacidad y Seguridad" (Privacy & Security)
   - Buscar "Cámara" en la lista
   - Habilitar acceso para Terminal, Python o VS Code

3. **Reiniciar la aplicación** después de otorgar permisos

### Error "No se pudo abrir la cámara"

- Verificar que no hay otras aplicaciones usando la cámara
- Probar con diferentes índices de cámara
- Ejecutar el diagnóstico para ver cámaras disponibles

## Estructura del Proyecto

- `src/tracking/` - Módulos de detección y tracking
- `src/utils/` - Utilidades y manejo de cámara
- `config/` - Archivos de configuración
- `tests/` - Pruebas unitarias

## Controles

- `q` - Salir del programa
- `c` - Calibrar/resetear tracking
- `Espacio` - Pausar/reanudar

## Dependencias

- OpenCV
- MediaPipe
- NumPy
- Matplotlib
- SciPy
