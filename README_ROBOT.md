# 🤖 Control Simple de Brazo Robótico

## 🚀 Inicio Rápido

### 1. Instalar dependencias
```bash
make install-robot
```

### 2. Configurar CoppeliaSim
1. Abrir CoppeliaSim
2. Cargar escena: `File > Open scene > models > robots > non-mobile > UR5.ttt`
3. Iniciar servidor: `Add-ons > Remote API server > Start`

### 3. Probar configuración
```bash
make test-robot
```

### 4. Ejecutar control
```bash
make run-robot
```

## 🎮 ¿Cómo usar?

1. **Ejecuta el programa** - aparecerá una ventana con la cámara
2. **Muestra tu mano** frente a la cámara
3. **Mueve la mano** - el robot UR5 seguirá tus movimientos
4. **Controles:**
   - `q` - Salir
   - `d` - Mostrar/ocultar debug
   - `r` - Resetear robot al centro

## 🎯 Características

- ✅ **Control intuitivo** - solo mueve tu mano
- ✅ **Tiempo real** - respuesta inmediata del robot
- ✅ **Seguro** - movimientos limitados a un área segura
- ✅ **Suave** - movimientos filtrados para evitar sacudidas

## 🔧 Configuración Avanzada

### Ajustar área de trabajo
Edita `simple_hand_robot_control.py`:
```python
# Cambiar el rango de movimiento
self.robot_x_range = (-0.5, 0.5)  # Más amplio
self.robot_y_range = (-0.3, 0.3)  # Más estrecho
self.robot_z_fixed = 0.6          # Más alto
```

### Ajustar suavidad
```python
# Movimientos más suaves (0.0-0.9)
self.smoothing = 0.8  # Más suave
self.smoothing = 0.3  # Más directo
```

## 🆘 Solución de Problemas

**Problema:** Robot no se mueve
- ✅ Verificar que CoppeliaSim esté ejecutándose
- ✅ Verificar que la simulación esté iniciada
- ✅ Verificar que el servidor ZMQ esté activo

**Problema:** No detecta la mano
- ✅ Verificar permisos de cámara
- ✅ Mejorar iluminación
- ✅ Usar fondo simple

## 🎓 Que aprenderás

- Control de robots en tiempo real
- Visión por computadora aplicada
- Interfaces humano-robot
- Mapeo de coordenadas
- Sistemas de control

¡Disfruta controlando tu robot! 🤖✨
