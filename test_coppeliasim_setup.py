#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración de CoppeliaSim.
Ejecuta pruebas básicas de conectividad y funcionalidad.
"""

import sys
import os

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from control.coppeliasim_robot_arm import test_coppeliasim_connection
except ImportError:
    print("⚠️  Módulo de control no encontrado, usando función de prueba básica")
    def test_coppeliasim_connection():
        try:
            from coppeliasim_zmqremoteapi_client import RemoteAPIClient
            client = RemoteAPIClient()
            sim = client.getObject('sim')
            version = sim.getInt32Param(sim.intparam_program_version)
            print(f"✅ Conectado a CoppeliaSim versión: {version}")
            return True
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False


def main():
    """Función principal de prueba."""
    print("=" * 60)
    print("🧪 PRUEBA DE CONFIGURACIÓN COPPELIASIM")
    print("=" * 60)
    
    print("\n📋 Verificando dependencias...")
    
    # Verificar que las dependencias estén instaladas
    try:
        import zmq
        print("✅ pyzmq instalado correctamente")
    except ImportError:
        print("❌ pyzmq no está instalado")
        return False
    
    try:
        import msgpack
        print("✅ msgpack instalado correctamente")
    except ImportError:
        print("❌ msgpack no está instalado")
        return False
    
    try:
        from coppeliasim_zmqremoteapi_client import RemoteAPIClient
        print("✅ coppeliasim-zmqremoteapi-client instalado correctamente")
    except ImportError:
        print("❌ coppeliasim-zmqremoteapi-client no está instalado")
        return False
    
    print("\n🔌 Probando conexión con CoppeliaSim...")
    
    # Primero intentar la conexión
    try:
        result = test_coppeliasim_connection()
        if result:
            print("✅ Conexión exitosa con CoppeliaSim")
        else:
            print("❌ No se pudo conectar con CoppeliaSim")
            print_zmq_help()
    except Exception as e:
        print(f"❌ Error al probar conexión: {e}")
        print_zmq_help()


def print_zmq_help():
    """Imprime ayuda para configurar el servidor ZMQ."""
    print("\n" + "=" * 60)
    print("🆘 AYUDA PARA CONFIGURAR EL SERVIDOR ZMQ")
    print("=" * 60)
    print()
    print("Si no se pudo conectar, verifica que el servidor ZMQ esté activo.")
    print("Busca en CoppeliaSim uno de estos menús:")
    print()
    print("📍 Opción 1: Add-ons → Remote API server → Start")
    print("📍 Opción 2: Tools → Remote API server → Start") 
    print("📍 Opción 3: Modules → Remote API → Start server")
    print("📍 Opción 4: Simulation → Start simulation")
    print()
    print("✅ Debe aparecer: 'ZMQ remote API server started on port 23000'")
    print()
    print("📖 Para más ayuda detallada:")
    print("   cat TROUBLESHOOT_ZMQ.md")
    print()
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    main()
