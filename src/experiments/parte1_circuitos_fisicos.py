#!/usr/bin/env python3
"""
PARTE 1 - CIRCUITOS FÍSICOS
Laboratorio de Teoría de Control - Universidad de Antioquia

Modelado y simulación de sistemas de primer orden:
- Sensor de temperatura
- Motor DC
- Funciones de transferencia G(s) = 1/(τs+1)
- Análisis con entradas impulso, escalón y rampa
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.signal import lti, step, impulse, lsim
import time
from typing import Dict, List, Tuple
import json


class SistemaPrimerOrden:
    """
    Modelo de sistema de primer orden para circuitos físicos.
    """
    
    def __init__(self, K: float, tau: float, nombre: str = "Sistema"):
        """
        Inicializa sistema de primer orden.
        
        Args:
            K: Ganancia del sistema
            tau: Constante de tiempo
            nombre: Nombre descriptivo del sistema
        """
        self.K = K
        self.tau = tau
        self.nombre = nombre
        
        # Crear función de transferencia G(s) = K/(τs+1)
        self.num = [K]
        self.den = [tau, 1]
        self.sistema = lti(self.num, self.den)
        
        print(f"📊 Sistema creado: {nombre}")
        print(f"   G(s) = {K}/({tau}s + 1)")
        print(f"   Ganancia: {K}")
        print(f"   Constante de tiempo: {tau}s")
    
    def respuesta_escalon(self, t_final: float = 20.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcula respuesta al escalón unitario.
        
        Args:
            t_final: Tiempo final de simulación
            
        Returns:
            Tupla (tiempo, respuesta)
        """
        t = np.linspace(0, t_final, 1000)
        t_out, y_out = step(self.sistema, T=t)
        return t_out, y_out
    
    def respuesta_impulso(self, t_final: float = 20.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcula respuesta al impulso.
        
        Args:
            t_final: Tiempo final de simulación
            
        Returns:
            Tupla (tiempo, respuesta)
        """
        t = np.linspace(0, t_final, 1000)
        t_out, y_out = impulse(self.sistema, T=t)
        return t_out, y_out
    
    def respuesta_rampa(self, t_final: float = 20.0, pendiente: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calcula respuesta a entrada rampa.
        
        Args:
            t_final: Tiempo final de simulación
            pendiente: Pendiente de la rampa
            
        Returns:
            Tupla (tiempo, respuesta)
        """
        t = np.linspace(0, t_final, 1000)
        # Entrada rampa: u(t) = pendiente * t
        u = pendiente * t
        t_out, y_out, _ = lsim(self.sistema, u, t)
        return t_out, y_out
    
    def analizar_respuesta_escalon(self) -> Dict[str, float]:
        """
        Analiza las características de la respuesta al escalón.
        
        Returns:
            Diccionario con métricas de rendimiento
        """
        t, y = self.respuesta_escalon(t_final=10*self.tau)
        
        # Valor final
        valor_final = y[-1]
        
        # Tiempo de subida (10% a 90%)
        y_10 = 0.1 * valor_final
        y_90 = 0.9 * valor_final
        
        idx_10 = np.argmax(y >= y_10)
        idx_90 = np.argmax(y >= y_90)
        
        tiempo_subida = t[idx_90] - t[idx_10] if idx_90 > idx_10 else 0
        
        # Tiempo de establecimiento (2% del valor final)
        tolerancia = 0.02 * abs(valor_final)
        indices_establecimiento = np.where(np.abs(y - valor_final) <= tolerancia)[0]
        tiempo_establecimiento = t[indices_establecimiento[0]] if len(indices_establecimiento) > 0 else t[-1]
        
        # Sobreimpulso
        pico_maximo = np.max(y)
        sobreimpulso = ((pico_maximo - valor_final) / valor_final) * 100 if valor_final != 0 else 0
        
        # Tiempo del pico
        idx_pico = np.argmax(y)
        tiempo_pico = t[idx_pico]
        
        # Error en estado estacionario para escalón unitario
        error_estado_estacionario = abs(1 - valor_final)
        
        return {
            'valor_final': valor_final,
            'tiempo_subida': tiempo_subida,
            'tiempo_establecimiento': tiempo_establecimiento,
            'sobreimpulso_porcentaje': sobreimpulso,
            'tiempo_pico': tiempo_pico,
            'error_estado_estacionario': error_estado_estacionario
        }


class ControlLazoCerrado:
    """
    Sistema de control en lazo cerrado para circuitos físicos.
    """
    
    def __init__(self, sistema: SistemaPrimerOrden, Kc: float):
        """
        Inicializa control en lazo cerrado.
        
        Args:
            sistema: Sistema de primer orden a controlar
            Kc: Ganancia del controlador
        """
        self.sistema_abierto = sistema
        self.Kc = Kc
        
        # Función de transferencia en lazo cerrado
        # G_cl(s) = Kc*G(s) / (1 + Kc*G(s))
        
        K = sistema.K
        tau = sistema.tau
        
        # Numerador: Kc * K
        num_cl = [Kc * K]
        
        # Denominador: τs + 1 + Kc*K = τs + (1 + Kc*K)
        den_cl = [tau, 1 + Kc * K]
        
        self.sistema_cerrado = lti(num_cl, den_cl)
        
        print(f"🔄 Control lazo cerrado creado:")
        print(f"   Kc = {Kc}")
        print(f"   G_cl(s) = {Kc * K}/({tau}s + {1 + Kc * K})")
    
    def comparar_respuestas(self, t_final: float = 20.0):
        """
        Compara respuestas en lazo abierto vs cerrado.
        
        Args:
            t_final: Tiempo final de simulación
        """
        t = np.linspace(0, t_final, 1000)
        
        # Respuesta lazo abierto
        _, y_abierto = step(self.sistema_abierto.sistema, T=t)
        
        # Respuesta lazo cerrado
        _, y_cerrado = step(self.sistema_cerrado, T=t)
        
        return t, y_abierto, y_cerrado


class ExperimentosParte1:
    """
    Experimentos completos para la Parte 1 del laboratorio.
    """
    
    def __init__(self):
        """Inicializa los experimentos."""
        self.resultados = {}
        self.fig = None
        
    def experimento_variacion_K(self, tau: float = 1.0):
        """
        Experimento variando ganancia K = 0.5, 1.0, 2.0.
        
        Args:
            tau: Constante de tiempo fija
        """
        print(f"\n🧪 EXPERIMENTO 1: Variación de Ganancia (τ = {tau})")
        print("=" * 50)
        
        valores_K = [0.5, 1.0, 2.0]
        sistemas = []
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'Respuesta con diferentes ganancias K (τ = {tau})', fontsize=14, fontweight='bold')
        
        colores = ['blue', 'red', 'green']
        
        for i, K in enumerate(valores_K):
            # Crear sistema
            sistema = SistemaPrimerOrden(K, tau, f"Sensor K={K}")
            sistemas.append(sistema)
            
            # Analizar respuesta
            metricas = sistema.analizar_respuesta_escalon()
            self.resultados[f'K_{K}_tau_{tau}'] = metricas
            
            print(f"\n📊 Resultados para K = {K}:")
            for metrica, valor in metricas.items():
                print(f"   {metrica}: {valor:.4f}")
            
            # Graficar respuestas
            color = colores[i]
            
            # Escalón
            t_step, y_step = sistema.respuesta_escalon()
            axes[0,0].plot(t_step, y_step, color=color, label=f'K={K}', linewidth=2)
            
            # Impulso
            t_imp, y_imp = sistema.respuesta_impulso()
            axes[0,1].plot(t_imp, y_imp, color=color, label=f'K={K}', linewidth=2)
            
            # Rampa
            t_ramp, y_ramp = sistema.respuesta_rampa()
            axes[1,0].plot(t_ramp, y_ramp, color=color, label=f'K={K}', linewidth=2)
            
            # Comparación con lazo cerrado (Kc = 1.0)
            control = ControlLazoCerrado(sistema, Kc=1.0)
            t_comp, y_abierto, y_cerrado = control.comparar_respuestas()
            
            axes[1,1].plot(t_comp, y_abierto, '--', color=color, alpha=0.7, label=f'Abierto K={K}')
            axes[1,1].plot(t_comp, y_cerrado, '-', color=color, linewidth=2, label=f'Cerrado K={K}')
        
        # Configurar gráficos
        axes[0,0].set_title('Respuesta al Escalón')
        axes[0,0].set_xlabel('Tiempo (s)')
        axes[0,0].set_ylabel('Amplitud')
        axes[0,0].grid(True, alpha=0.3)
        axes[0,0].legend()
        
        axes[0,1].set_title('Respuesta al Impulso')
        axes[0,1].set_xlabel('Tiempo (s)')
        axes[0,1].set_ylabel('Amplitud')
        axes[0,1].grid(True, alpha=0.3)
        axes[0,1].legend()
        
        axes[1,0].set_title('Respuesta a la Rampa')
        axes[1,0].set_xlabel('Tiempo (s)')
        axes[1,0].set_ylabel('Amplitud')
        axes[1,0].grid(True, alpha=0.3)
        axes[1,0].legend()
        
        axes[1,1].set_title('Lazo Abierto vs Cerrado')
        axes[1,1].set_xlabel('Tiempo (s)')
        axes[1,1].set_ylabel('Amplitud')
        axes[1,1].grid(True, alpha=0.3)
        axes[1,1].legend()
        
        plt.tight_layout()
        self.fig = fig
        return fig
    
    def experimento_variacion_tau(self, K: float = 1.0):
        """
        Experimento variando constante de tiempo τ = 1, 3, 5.
        
        Args:
            K: Ganancia fija
        """
        print(f"\n🧪 EXPERIMENTO 2: Variación de Constante de Tiempo (K = {K})")
        print("=" * 60)
        
        valores_tau = [1.0, 3.0, 5.0]
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f'Respuesta con diferentes constantes de tiempo τ (K = {K})', fontsize=14, fontweight='bold')
        
        colores = ['purple', 'orange', 'brown']
        
        for i, tau in enumerate(valores_tau):
            # Crear sistema
            sistema = SistemaPrimerOrden(K, tau, f"Motor τ={tau}")
            
            # Analizar respuesta
            metricas = sistema.analizar_respuesta_escalon()
            self.resultados[f'K_{K}_tau_{tau}'] = metricas
            
            print(f"\n📊 Resultados para τ = {tau}:")
            for metrica, valor in metricas.items():
                print(f"   {metrica}: {valor:.4f}")
            
            # Graficar respuestas
            color = colores[i]
            
            # Escalón
            t_step, y_step = sistema.respuesta_escalon()
            axes[0,0].plot(t_step, y_step, color=color, label=f'τ={tau}', linewidth=2)
            
            # Impulso
            t_imp, y_imp = sistema.respuesta_impulso()
            axes[0,1].plot(t_imp, y_imp, color=color, label=f'τ={tau}', linewidth=2)
            
            # Rampa
            t_ramp, y_ramp = sistema.respuesta_rampa()
            axes[1,0].plot(t_ramp, y_ramp, color=color, label=f'τ={tau}', linewidth=2)
            
            # Entrada rampa teórica
            if i == 0:  # Solo mostrar una vez
                axes[1,0].plot(t_ramp, t_ramp, 'k--', alpha=0.5, label='Entrada rampa')
            
            # Comparación con lazo cerrado
            control = ControlLazoCerrado(sistema, Kc=2.0)
            t_comp, y_abierto, y_cerrado = control.comparar_respuestas()
            
            axes[1,1].plot(t_comp, y_abierto, '--', color=color, alpha=0.7, label=f'Abierto τ={tau}')
            axes[1,1].plot(t_comp, y_cerrado, '-', color=color, linewidth=2, label=f'Cerrado τ={tau}')
        
        # Configurar gráficos
        axes[0,0].set_title('Respuesta al Escalón')
        axes[0,0].set_xlabel('Tiempo (s)')
        axes[0,0].set_ylabel('Amplitud')
        axes[0,0].grid(True, alpha=0.3)
        axes[0,0].legend()
        
        axes[0,1].set_title('Respuesta al Impulso')
        axes[0,1].set_xlabel('Tiempo (s)')
        axes[0,1].set_ylabel('Amplitud')
        axes[0,1].grid(True, alpha=0.3)
        axes[0,1].legend()
        
        axes[1,0].set_title('Respuesta a la Rampa')
        axes[1,0].set_xlabel('Tiempo (s)')
        axes[1,0].set_ylabel('Amplitud')
        axes[1,0].grid(True, alpha=0.3)
        axes[1,0].legend()
        
        axes[1,1].set_title('Lazo Abierto vs Cerrado (Kc=2.0)')
        axes[1,1].set_xlabel('Tiempo (s)')
        axes[1,1].set_ylabel('Amplitud')
        axes[1,1].grid(True, alpha=0.3)
        axes[1,1].legend()
        
        plt.tight_layout()
        return fig
    
    def generar_tabla_comparativa(self):
        """Genera tabla comparativa de resultados."""
        print(f"\n📋 TABLA COMPARATIVA DE RESULTADOS")
        print("=" * 80)
        
        # Cabecera
        print(f"{'Sistema':<15} {'K':<5} {'τ':<5} {'T_subida':<10} {'T_estab':<10} {'Sobreimpulso':<12} {'Error_ss':<10}")
        print("-" * 80)
        
        for nombre, resultados in self.resultados.items():
            # Extraer K y tau del nombre
            partes = nombre.split('_')
            K = partes[1]
            tau = partes[3]
            
            t_subida = resultados['tiempo_subida']
            t_estab = resultados['tiempo_establecimiento']
            sobreimpulso = resultados['sobreimpulso_porcentaje']
            error_ss = resultados['error_estado_estacionario']
            
            print(f"{'Sistema':<15} {K:<5} {tau:<5} {t_subida:<10.3f} {t_estab:<10.3f} {sobreimpulso:<12.2f}% {error_ss:<10.4f}")
    
    def exportar_resultados(self, filename: str = "resultados_parte1.json"):
        """
        Exporta resultados a archivo JSON.
        
        Args:
            filename: Nombre del archivo
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename_con_timestamp = f"{timestamp}_{filename}"
        
        datos_exportar = {
            'metadata': {
                'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
                'laboratorio': 'Parte 1 - Circuitos Físicos',
                'universidad': 'Universidad de Antioquia'
            },
            'resultados': self.resultados
        }
        
        with open(filename_con_timestamp, 'w') as f:
            json.dump(datos_exportar, f, indent=2)
        
        print(f"💾 Resultados exportados a: {filename_con_timestamp}")
    
    def ejecutar_experimentos_completos(self):
        """Ejecuta todos los experimentos de la Parte 1."""
        print("🚀 INICIANDO EXPERIMENTOS PARTE 1 - CIRCUITOS FÍSICOS")
        print("Universidad de Antioquia - Laboratorio de Teoría de Control")
        print("=" * 70)
        
        # Experimento 1: Variación de K
        fig1 = self.experimento_variacion_K(tau=1.0)
        plt.savefig('parte1_variacion_K.png', dpi=300, bbox_inches='tight')
        
        # Experimento 2: Variación de τ
        fig2 = self.experimento_variacion_tau(K=1.0)
        plt.savefig('parte1_variacion_tau.png', dpi=300, bbox_inches='tight')
        
        # Tabla comparativa
        self.generar_tabla_comparativa()
        
        # Exportar resultados
        self.exportar_resultados()
        
        print(f"\n✅ EXPERIMENTOS COMPLETADOS")
        print("📊 Gráficos guardados:")
        print("   - parte1_variacion_K.png")
        print("   - parte1_variacion_tau.png")
        print("💾 Datos exportados en formato JSON")
        
        plt.show()


def main():
    """Función principal para ejecutar experimentos de la Parte 1."""
    print("🎓 UNIVERSIDAD DE ANTIOQUIA")
    print("📚 LABORATORIO DE TEORÍA DE CONTROL")
    print("🔬 PARTE 1 - CIRCUITOS FÍSICOS")
    print()
    
    # Verificar dependencias
    try:
        import scipy.signal
        print("✅ scipy.signal disponible")
    except ImportError:
        print("❌ Error: scipy no está instalado")
        print("   Ejecuta: pip install scipy")
        return
    
    # Ejecutar experimentos
    experimentos = ExperimentosParte1()
    experimentos.ejecutar_experimentos_completos()


if __name__ == "__main__":
    main()
