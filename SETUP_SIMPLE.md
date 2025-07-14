# 🤖 Guía de Configuración Simple - Control de Brazo Robótico

## 🎯 Objetivo
Controlar un brazo robótico UR5 en CoppeliaSim usando movimientos de tu mano detectados por la cámara.

## 📋 Requisitos Previos

### 1. CoppeliaSim
- Descargar CoppeliaSim EDU desde: https://www.coppeliarobotics.com/
- Versión recomendada: 4.1.0 o superior
- Instalar siguiendo las instrucciones del sitio web

### 2. Python y dependencias
```bash
# Instalar dependencias automáticamente
./install_robot_deps.sh

# O instalar manualmente:
pip3 install pyzmq msgpack coppeliasim-zmqremoteapi-client
```

## 🚀 Configuración Paso a Paso

### Paso 1: Preparar CoppeliaSim
1. **Abrir CoppeliaSim**
2. **Cargar escena con UR5:**
   - Ir a `File > Open scene...`
   - Navegar a `models > robots > non-mobile > UR5.ttt`
   - Abrir la escena

### Paso 2: Configurar la escena
1. **Verificar que el UR5 esté visible** en la escena
2. **Iniciar el servidor ZMQ (IMPORTANTE):**
   
   **Opción A - CoppeliaSim 4.3+:**
   - `Add-ons > Remote API server > Start`
   
   **Opción B - CoppeliaSim 4.1/4.2:**
   - `Tools > Remote API server > Start`
   
   **Opción C - Si no encuentras las opciones anteriores:**
   - `Simulation > Start simulation` (esto puede activar automáticamente el servidor)
   - O buscar en `Modules > Remote API`
   
   **Verificación exitosa:**
   - Debe aparecer en la consola: "ZMQ remote API server started on port 23000"
   - Si no aparece este mensaje, el servidor NO está activo

### Paso 3: Verificar configuración
```bash
# Probar la conexión
python3 test_coppeliasim_setup.py
```

### Paso 4: Ejecutar control simple
```bash
# Ejecutar el sistema de control
python3 simple_hand_robot_control.py
```

## 🎮 Controles del Sistema

### Controles de teclado:
- **'q'** - Salir del programa
- **'d'** - Activar/desactivar información de debug
- **'r'** - Resetear robot al centro

### Control con la mano:
- **Mostrar la mano** frente a la cámara
- **Mover la mano** - El robot seguirá el movimiento
- **Mano izquierda/derecha** → Robot se mueve izquierda/derecha
- **Mano arriba/abajo** → Robot se mueve arriba/abajo

## 🔧 Solución de Problemas

### Problema: "No se pudo conectar al robot"
**Solución:**
1. Verificar que CoppeliaSim esté ejecutándose
2. Verificar que el servidor ZMQ esté activo (puerto 23000)
3. Verificar que la escena tenga el robot UR5 cargado

### Problema: "No se pudo inicializar la cámara"
**Solución:**
1. Verificar permisos de cámara en macOS:
   - Sistema → Privacidad y Seguridad → Cámara
   - Habilitar para Terminal/Python/VS Code
2. Cerrar otras aplicaciones que usen la cámara

### Problema: "Robot no se mueve"
**Solución:**
1. Verificar que la simulación esté iniciada en CoppeliaSim
2. Verificar que los joints del UR5 estén configurados correctamente
3. Reiniciar la simulación en CoppeliaSim

## 🎯 Cómo Funciona

1. **Detección de mano:** MediaPipe detecta la posición de tu mano en la cámara
2. **Mapeo de coordenadas:** Las coordenadas de píxeles se convierten a coordenadas del robot
3. **Control del robot:** El robot UR5 se mueve a la posición correspondiente
4. **Suavizado:** Los movimientos se suavizan para evitar movimientos bruscos

## 📊 Configuración del Workspace

El robot se mueve en un área limitada por seguridad:
- **X:** -30cm a +30cm (izquierda-derecha)
- **Y:** -30cm a +30cm (adelante-atrás)  
- **Z:** 50cm (altura fija)

## 🔄 Próximos Pasos

Una vez que funcione el control básico, puedes:
1. Ajustar el área de trabajo del robot
2. Modificar la sensibilidad del control
3. Agregar control de orientación
4. Implementar diferentes modos de control

## 💡 Tips

- **Iluminación:** Asegúrate de tener buena iluminación para la detección de manos
- **Fondo:** Un fondo simple mejora la detección
- **Velocidad:** Los movimientos lentos son más precisos
- **Calibración:** Usa 'r' para resetear si el robot se sale del área de trabajo
