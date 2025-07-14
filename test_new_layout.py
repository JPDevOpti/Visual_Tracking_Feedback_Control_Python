#!/usr/bin/env python3
"""
Script para probar la nueva distribución de interfaz simplificada
"""

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import RadioButtons, Slider, Button
import numpy as np

def test_new_layout():
    """Prueba la nueva distribución simplificada."""
    # Crear figura principal
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('Sistema de Control - Lazo Abierto vs Cerrado (Nueva Distribución)', 
                 fontsize=16, fontweight='bold', y=0.95)
    
    # Layout: 3 filas, 2 columnas
    # Fila 1: Gráfico Error | Cámara
    # Fila 2: Gráfico Velocidad | (Controles están en coordenadas absolutas)
    # Fila 3: Métricas | (vacío)
    gs = GridSpec(3, 2, figure=fig, 
                 height_ratios=[2, 2, 1],  # Gráficos grandes, métricas pequeñas
                 width_ratios=[2, 1.5],    # Gráficos más anchos que cámara
                 hspace=0.3, wspace=0.3,
                 left=0.08, right=0.95, top=0.90, bottom=0.15)
    
    # Gráfico de error (superior izquierdo)
    ax_error = fig.add_subplot(gs[0, 0])
    ax_error.set_title('Error vs Tiempo', fontweight='bold', fontsize=12)
    ax_error.set_xlabel('Tiempo (s)', fontsize=10)
    ax_error.set_ylabel('Error (m)', fontsize=10)
    ax_error.grid(True, alpha=0.3)
    
    # Datos de ejemplo para error
    t = np.linspace(0, 10, 100)
    error_data = 0.05 * np.exp(-0.5*t) * np.sin(3*t) + 0.01 * np.random.randn(100)
    ax_error.plot(t, error_data, 'r-', linewidth=2, label='Error')
    ax_error.legend()
    
    # Gráfico de velocidad (medio izquierdo)
    ax_velocity = fig.add_subplot(gs[1, 0])
    ax_velocity.set_title('Velocidad de Corrección', fontweight='bold', fontsize=12)
    ax_velocity.set_xlabel('Tiempo (s)', fontsize=10)
    ax_velocity.set_ylabel('Velocidad (m/s)', fontsize=10)
    ax_velocity.grid(True, alpha=0.3)
    
    # Datos de ejemplo para velocidad
    velocity_data = 0.02 * np.cos(2*t) + 0.005 * np.random.randn(100)
    ax_velocity.plot(t, velocity_data, 'b-', linewidth=2, label='Velocidad')
    ax_velocity.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    ax_velocity.legend()
    
    # Panel de video (superior derecho)
    ax_video = fig.add_subplot(gs[0, 1])
    ax_video.set_title('Vista de Cámara', fontweight='bold', fontsize=12)
    ax_video.text(0.5, 0.5, 'CÁMARA\n640x480\n(Superior Derecha)', 
                 ha='center', va='center', fontsize=12, 
                 bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
    ax_video.set_xlim(0, 1)
    ax_video.set_ylim(0, 1)
    
    # Panel de información (inferior izquierdo)
    ax_info = fig.add_subplot(gs[2, 0])
    ax_info.set_title('Métricas del Sistema', fontweight='bold', fontsize=11)
    ax_info.axis('off')
    
    info_text = """
Error Actual: 0.0156 m        Velocidad: 0.0089 m/s
Error RMS: 0.0234 m          Error Máximo: 0.0445 m
Modo: Lazo Cerrado           Puntos: 85
    """
    ax_info.text(0.1, 0.5, info_text, fontsize=10, 
                verticalalignment='center', fontfamily='monospace')
    
    # CONTROLES debajo de la cámara
    # Radio buttons para modo de control
    ax_mode = plt.axes([0.65, 0.45, 0.25, 0.15])
    ax_mode.set_title('Modo de Control', fontsize=10, fontweight='bold')
    radio_mode = RadioButtons(ax_mode, ('Lazo Abierto', 'Lazo Cerrado'))
    
    # Botones de control principales
    button_width = 0.1
    button_height = 0.04
    button_x_start = 0.65
    button_y_start = 0.35
    
    # Botón Iniciar/Detener
    ax_start = plt.axes([button_x_start, button_y_start, button_width, button_height])
    btn_start = Button(ax_start, 'Iniciar', color='lightgreen')
    
    # Botón Reset
    ax_reset = plt.axes([button_x_start + 0.12, button_y_start, button_width, button_height])
    btn_reset = Button(ax_reset, 'Reset', color='orange')
    
    # Botón Exportar
    ax_export = plt.axes([button_x_start, button_y_start - 0.06, button_width, button_height])
    btn_export = Button(ax_export, 'Exportar', color='lightblue')
    
    # Sliders PID (más compactos, debajo de los botones)
    slider_width = 0.2
    slider_height = 0.025
    slider_x = 0.65
    slider_y_start = 0.22
    
    # Kp
    ax_kp = plt.axes([slider_x, slider_y_start, slider_width, slider_height])
    slider_kp = Slider(ax_kp, 'Kp', 0.1, 5.0, valinit=2.0, 
                      valfmt='%.1f', color='lightblue')
    
    # Ki
    ax_ki = plt.axes([slider_x, slider_y_start - 0.04, slider_width, slider_height])
    slider_ki = Slider(ax_ki, 'Ki', 0.0, 1.0, valinit=0.1,
                      valfmt='%.2f', color='lightgreen')
    
    # Kd
    ax_kd = plt.axes([slider_x, slider_y_start - 0.08, slider_width, slider_height])
    slider_kd = Slider(ax_kd, 'Kd', 0.0, 0.2, valinit=0.05,
                      valfmt='%.3f', color='lightcoral')
    
    # Suavizado
    ax_smooth = plt.axes([slider_x, slider_y_start - 0.12, slider_width, slider_height])
    slider_smooth = Slider(ax_smooth, 'Suavizado', 0.1, 0.95, valinit=0.7,
                          valfmt='%.2f', color='lightyellow')
    
    # Agregar anotaciones para explicar la distribución
    fig.text(0.02, 0.8, '← Gráfico Error vs Tiempo', fontsize=9, color='red', rotation=90)
    fig.text(0.02, 0.4, '← Gráfico Velocidad', fontsize=9, color='blue', rotation=90)
    fig.text(0.02, 0.15, '← Panel Métricas', fontsize=9, color='green', rotation=90)
    
    fig.text(0.65, 0.62, 'Cámara ↑', fontsize=9, color='purple', ha='center')
    fig.text(0.75, 0.38, 'Controles ↓', fontsize=9, color='orange', ha='center')
    
    plt.show()

if __name__ == "__main__":
    print("🎨 Probando nueva distribución simplificada...")
    print("📍 Distribución:")
    print("   • Superior izquierda: Error vs Tiempo")
    print("   • Medio izquierda: Velocidad de Corrección")
    print("   • Inferior izquierda: Métricas del Sistema")
    print("   • Superior derecha: Cámara")
    print("   • Medio derecha: Controles (debajo de cámara)")
    print("   • Eliminados: Distribución de Error y Trayectoria X-Y")
    test_new_layout()
