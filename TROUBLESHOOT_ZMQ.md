# 🔌 Guía para Activar el Servidor ZMQ en CoppeliaSim

## 🎯 ¿Dónde Encontrar el Servidor ZMQ?

La ubicación del servidor ZMQ varía según la versión de CoppeliaSim. Aquí tienes todas las ubicaciones posibles:

### 📍 **Versión 4.3+ (Más Reciente)**
```
Add-ons → Remote API server → Start
```

### 📍 **Versión 4.1/4.2 (Intermedia)**
```
Tools → Remote API server → Start
```

### 📍 **Versiones Anteriores**
```
Modules → Remote API → Start server
```

### 📍 **Si NO encuentras ninguna opción anterior**
```
1. Simulation → Start simulation (puede activar automáticamente)
2. O buscar en File → Scripts → Add script
```

## 🔍 **Método de Búsqueda Visual**

Si no encuentras el servidor, sigue estos pasos:

### 1. **Explorar todos los menús:**
- **File** (Archivo)
- **Edit** (Editar) 
- **Add-ons** (Complementos) ← **MÁS PROBABLE**
- **Tools** (Herramientas) ← **SEGUNDA OPCIÓN**
- **Modules** (Módulos) ← **TERCERA OPCIÓN**
- **Simulation** (Simulación)
- **Help** (Ayuda)

### 2. **Buscar palabras clave:**
- "Remote API"
- "ZMQ"
- "API server"
- "Remote"
- "Server"

## ✅ **Cómo Saber que está Funcionando**

Una vez que hagas clic en "Start", debes ver **exactamente este mensaje** en la consola de CoppeliaSim:

```
ZMQ remote API server started on port 23000
```

### Si ves otros mensajes:
- ❌ "Port already in use" → Reinicia CoppeliaSim
- ❌ "Could not start server" → Verifica permisos
- ❌ Nada aparece → El servidor NO se activó

## 🚨 **Métodos Alternativos**

### **Método 1: Script Manual**
Si no encuentras el menú, puedes agregar este script:

1. En CoppeliaSim: `Add script` → `Non-threaded child script`
2. Pegar este código:
```lua
function sysCall_init()
    simRemoteApi.start(23000)
end
```

### **Método 2: Configuración Automática**
Algunas versiones inician el servidor automáticamente al:
1. Iniciar la simulación (`Simulation → Start`)
2. Cargar una escena con robots

### **Método 3: Línea de Comandos**
Al abrir CoppeliaSim desde terminal:
```bash
# En macOS/Linux
./coppeliaSim.app/Contents/MacOS/coppeliaSim -GzmqRemoteApiAutoStart
```

## 🔧 **Verificación desde Terminal**

Para confirmar que el puerto 23000 está activo:

```bash
# En macOS/Linux:
netstat -an | grep 23000

# Debe mostrar:
tcp4       0      0  *.23000                *.*                    LISTEN
```

## 🆘 **Si Nada Funciona**

### **Último Recurso:**
1. **Actualizar CoppeliaSim** a la versión más reciente
2. **Descargar una escena pre-configurada** con servidor activo
3. **Usar un archivo de configuración personalizado**

### **Alternativa Simple:**
Si tienes problemas persistentes, puedes usar **robot real** o **otro simulador** como:
- Gazebo
- PyBullet  
- MuJoCo

## 📞 **Obtener Ayuda**

Si sigues teniendo problemas:
1. **Ejecuta:** `python3 test_coppeliasim_setup.py`
2. **Copia el mensaje de error completo**
3. **Verifica tu versión de CoppeliaSim:** `Help → About`

---

**💡 Tip:** La clave es ver el mensaje "ZMQ remote API server started on port 23000" en la consola de CoppeliaSim. Sin este mensaje, Python no podrá conectarse al robot.
