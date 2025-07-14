#!/usr/bin/env python3
"""
Script de diagnóstico para ver todos los objetos en CoppeliaSim.
Esto nos ayudará a identificar los nombres exactos del robot UR5.
"""

import sys
import os

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from coppeliasim_zmqremoteapi_client import RemoteAPIClient
except ImportError:
    print("❌ Error: coppeliasim-zmqremoteapi-client no está instalado")
    sys.exit(1)


def scan_coppeliasim_objects():
    """Escanea todos los objetos en CoppeliaSim para encontrar el UR5."""
    try:
        print("🔍 Escaneando objetos en CoppeliaSim...")
        
        # Conectar
        client = RemoteAPIClient()
        sim = client.getObject('sim')
        
        print(f"✅ Conectado a CoppeliaSim")
        
        # Obtener todos los objetos en la escena
        all_objects = sim.getObjectsInTree(sim.handle_scene)
        
        print(f"\n📋 Objetos encontrados en la escena ({len(all_objects)} total):")
        print("=" * 60)
        
        ur5_related = []
        joint_related = []
        
        for obj_handle in all_objects:
            try:
                obj_name = sim.getObjectName(obj_handle)
                obj_type = sim.getObjectType(obj_handle)
                
                # Filtrar objetos relacionados con UR5
                if 'ur5' in obj_name.lower() or 'joint' in obj_name.lower() or 'connection' in obj_name.lower():
                    info = f"Handle: {obj_handle:3d} | Tipo: {obj_type:2d} | Nombre: '{obj_name}'"
                    print(f"🤖 {info}")
                    
                    if 'ur5' in obj_name.lower():
                        ur5_related.append((obj_handle, obj_name))
                    if 'joint' in obj_name.lower():
                        joint_related.append((obj_handle, obj_name))
                
            except Exception as e:
                continue
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN:")
        
        if ur5_related:
            print(f"\n🤖 Objetos UR5 encontrados ({len(ur5_related)}):")
            for handle, name in ur5_related:
                print(f"  - '{name}' (Handle: {handle})")
        
        if joint_related:
            print(f"\n🔧 Joints encontrados ({len(joint_related)}):")
            for handle, name in joint_related:
                print(f"  - '{name}' (Handle: {handle})")
        
        # Intentar detectar estructura jerárquica
        print(f"\n🌳 ESTRUCTURA JERÁRQUICA:")
        try:
            # Buscar objeto raíz del UR5
            possible_roots = ['UR5', 'ur5', 'UR3', 'robot']
            
            for root_name in possible_roots:
                try:
                    root_handle = sim.getObject(root_name)
                    print(f"\n📁 Objeto raíz encontrado: '{root_name}' (Handle: {root_handle})")
                    
                    # Obtener hijos
                    children = sim.getObjectsInTree(root_handle)
                    print(f"   Tiene {len(children)} objetos hijo:")
                    
                    for child_handle in children[:10]:  # Mostrar solo primeros 10
                        try:
                            child_name = sim.getObjectName(child_handle)
                            print(f"   └── '{child_name}' (Handle: {child_handle})")
                        except:
                            continue
                            
                    if len(children) > 10:
                        print(f"   └── ... y {len(children) - 10} más")
                    
                    break
                        
                except:
                    continue
        
        except Exception as e:
            print(f"❌ Error en análisis jerárquico: {e}")
        
        print("\n" + "=" * 60)
        print("💡 RECOMENDACIONES:")
        print("Usa estos nombres exactos en el código Python para conectar al robot.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error escaneando CoppeliaSim: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE OBJETOS EN COPPELIASIM")
    print("=" * 60)
    
    if scan_coppeliasim_objects():
        print("\n✅ Diagnóstico completado")
    else:
        print("\n❌ Error en diagnóstico")
        print("💡 Asegúrate de que CoppeliaSim esté ejecutándose")
