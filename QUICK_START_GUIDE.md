
# Guía de Inicio Rápido - Parte 3

## Objetivo
Comparar el rendimiento entre control de lazo abierto y lazo cerrado
en un sistema de seguimiento visual de mano.

## Pasos Rápidos

### 1. Verificación del Sistema
```bash
python3 run_complete_demo.py
```

### 2. Ejecutar Sistema Recomendado
```bash
python3 matplotlib_control_system.py
```

### 3. Operación del Sistema
- **Modo Lazo Abierto**: Control directo sin realimentación
- **Modo Lazo Cerrado**: Control PID con realimentación
- **Controles**: Usa sliders para ajustar Kp, Ki, Kd
- **Análisis**: Observa gráficas de error, velocidad, trayectoria

### 4. Recolección de Datos
- Ejecuta cada modo por 2-3 minutos
- Usa el botón "Exportar Datos" 
- Compara métricas de rendimiento

### 5. Para el Reporte
- Error RMS: Precisión del control
- Tiempo de establecimiento: Velocidad de respuesta
- Overshoot: Estabilidad del sistema
- Suavidad de trayectoria: Calidad del movimiento

## Archivos Generados
- `data/open_loop_data_YYYYMMDD_HHMMSS.csv`
- `data/closed_loop_data_YYYYMMDD_HHMMSS.csv`
- `data/performance_metrics_YYYYMMDD_HHMMSS.json`

## Problemas Comunes
- **Cámara no detectada**: Verificar conexión USB
- **Mano no detectada**: Mejorar iluminación
- **Lag en gráficas**: Reducir frecuencia de actualización
- **Error tkinter**: Usar versión matplotlib
