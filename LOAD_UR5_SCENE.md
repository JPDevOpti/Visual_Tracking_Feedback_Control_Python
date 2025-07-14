# 🤖 Configuración de la Escena UR5 en CoppeliaSim

## ✅ Estado Actual
- ✅ **CoppeliaSim está ejecutándose** (versión 4.1.0)
- ✅ **Servidor ZMQ activo** (puerto 23000)  
- ✅ **Python puede conectarse**
- ❌ **Falta cargar la escena del UR5**

## 🎯 Lo que necesitas hacer:

### 1. **Cargar la escena del UR5**

**Opción A - Desde el menú File:**
```
File → Open scene... → models → robots → non-mobile → UR5.ttt
```

**Opción B - Desde el navegador de modelos:**
```
1. En CoppeliaSim, buscar el panel "Model browser" 
2. Expandir "robots" → "non-mobile"
3. Hacer doble clic en "UR5"
```

**Opción C - Arrastrar y soltar:**
```
1. Ir a la carpeta de instalación de CoppeliaSim
2. Buscar: models/robots/non-mobile/UR5.ttt
3. Arrastrar el archivo a la ventana de CoppeliaSim
```

### 2. **Verificar que está cargado**

Después de cargar, debes ver:
- ✅ **El brazo UR5** en la ventana de simulación
- ✅ **Objetos UR5** en la lista del lado izquierdo:
  - UR5
  - UR5_joint1, UR5_joint2, ..., UR5_joint6
  - UR5_connection (tip del brazo)

### 3. **Ejecutar el control**

Una vez que veas el UR5 en la escena:
```bash
make run-robot
```

O directamente:
```bash
PYTHONPATH=src python3 simple_hand_robot_control.py
```

## 🎮 ¿Qué esperar después?

1. **Se abrirá una ventana** con tu cámara
2. **Muestra tu mano** frente a la cámara  
3. **El brazo UR5** seguirá los movimientos de tu mano
4. **¡Disfruta del control intuitivo!**

## 🔧 Controles:
- **'q'** - Salir
- **'d'** - Mostrar/ocultar debug
- **'r'** - Resetear robot al centro

---

**💡 Tip:** Si no encuentras el UR5, busca en la documentación de tu versión de CoppeliaSim o usa `Help > User Manual` para encontrar los modelos disponibles.
