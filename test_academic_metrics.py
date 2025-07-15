#!/usr/bin/env python3
"""
Script de prueba para las métricas académicas
Verifica que el sistema funcione correctamente con las nuevas funcionalidades
"""

import sys
import os
import time
import numpy as np

# Agregar el directorio src al path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

def test_step_response_analyzer():
    """Prueba el analizador de respuesta al escalón."""
    print("🧪 Probando Step Response Analyzer...")
    
    try:
        from analysis.step_response_analyzer import StepResponseAnalyzer
        
        # Crear analizador
        analyzer = StepResponseAnalyzer()
        print("✅ StepResponseAnalyzer creado exitosamente")
        
        # Simular datos de escalón
        initial_pos = np.array([0.0, 0.0, 0.5])
        analyzer.start_step_analysis(initial_pos)
        print("✅ Análisis iniciado")
        
        # Simular evolución temporal
        target_magnitude = 0.2  # 20cm de magnitud
        timestamps = np.linspace(0, 5, 100)  # 5 segundos, 100 puntos
        
        for i, t in enumerate(timestamps):
            # Simular respuesta de segundo orden sub-amortiguada
            zeta = 0.7  # Factor de amortiguamiento
            wn = 4.0    # Frecuencia natural
            
            # Respuesta teórica al escalón
            if t > 0:
                response = target_magnitude * (1 - np.exp(-zeta*wn*t) * 
                          (np.cos(wn*np.sqrt(1-zeta**2)*t) + 
                           (zeta/np.sqrt(1-zeta**2))*np.sin(wn*np.sqrt(1-zeta**2)*t)))
            else:
                response = 0.0
            
            # Añadir ruido realista
            noise = np.random.normal(0, 0.002)  # 2mm de ruido
            response += noise
            
            # Crear posiciones simuladas
            desired_pos = np.array([target_magnitude, 0.0, 0.5])
            actual_pos = np.array([response, 0.0, 0.5])
            
            # Actualizar análisis
            current_time = time.time() + t
            metrics = analyzer.update_analysis(desired_pos, actual_pos, current_time)
            
            # Mostrar progreso cada 20 puntos
            if i % 20 == 0:
                print(f"   Progreso: {i/len(timestamps)*100:.0f}% (t={t:.1f}s, response={response:.3f})")
        
        # Finalizar y mostrar resultados
        analyzer.stop_analysis()
        final_metrics = analyzer.get_metrics()
        
        print("\n📊 Resultados del análisis:")
        for key, value in final_metrics.items():
            if value is not None and key not in ['analysis_timestamp', 'analysis_valid']:
                if 'time' in key:
                    print(f"   {key}: {value:.3f} s")
                elif 'percentage' in key:
                    print(f"   {key}: {value:.2f} %")
                elif isinstance(value, (int, float)):
                    print(f"   {key}: {value:.4f}")
                else:
                    print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Prueba la integración con el sistema principal."""
    print("\n🔗 Probando integración con sistema principal...")
    
    try:
        # Verificar imports
        from analysis.error_calculator import ErrorCalculator
        from analysis.step_response_analyzer import StepResponseAnalyzer
        print("✅ Imports exitosos")
        
        # Crear componentes
        error_calc = ErrorCalculator()
        step_analyzer = StepResponseAnalyzer()
        print("✅ Componentes creados")
        
        # Simular integración
        desired_pos = np.array([0.1, 0.1, 0.5])
        actual_pos = np.array([0.05, 0.08, 0.5])
        current_time = time.time()
        
        # Actualizar error calculator
        error_metrics = error_calc.update(desired_pos, actual_pos, current_time)
        print("✅ ErrorCalculator funcionando")
        
        # Iniciar análisis de escalón
        step_analyzer.start_step_analysis(actual_pos)
        step_metrics = step_analyzer.update_analysis(desired_pos, actual_pos, current_time)
        print("✅ StepResponseAnalyzer funcionando")
        
        # Combinar métricas
        combined_metrics = {**error_metrics}
        combined_metrics.update({f"step_{k}": v for k, v in step_metrics.items() if v is not None})
        
        print(f"✅ Métricas combinadas: {len(combined_metrics)} métricas disponibles")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal de pruebas."""
    print("=" * 70)
    print("🧪 PRUEBAS DE MÉTRICAS ACADÉMICAS")
    print("📊 Verificando implementación de análisis de escalón")
    print("=" * 70)
    
    # Ejecutar pruebas
    test1_passed = test_step_response_analyzer()
    test2_passed = test_integration()
    
    # Resumen
    print("\n" + "=" * 70)
    print("📋 RESUMEN DE PRUEBAS:")
    print(f"   🧪 Análisis de Escalón: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   🔗 Integración: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ El sistema está listo para análisis académico")
        print("\n📋 Próximos pasos:")
        print("   1. Ejecutar el sistema principal")
        print("   2. Usar los botones 'Iniciar Escalón' y 'Detener Escalón'")
        print("   3. Mover la mano para crear un escalón")
        print("   4. Observar las métricas académicas en la interfaz")
        print("   5. Exportar los datos para el informe")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        print("🔧 Revisa los errores antes de continuar")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
