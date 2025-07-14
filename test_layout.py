#!/usr/bin/env python3
"""
Script de verificación del layout de la interfaz
"""

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.widgets import RadioButtons, Slider, Button
import numpy as np

def test_layout():
    """Prueba el layout de la interfaz."""
    # Crear figura principal con más espacio
    fig = plt.figure(figsize=(18, 12))
    fig.suptitle('Sistema de Control - Lazo Abierto vs Cerrado', fontsize=16, fontweight='bold', y=0.95)
    
    # Layout: 3 filas, 4 columnas con espaciado personalizado
    gs = GridSpec(3, 4, figure=fig, 
                 height_ratios=[2, 2, 1],  # Video y gráficos grandes, controles pequeños
                 width_ratios=[2, 1.5, 1.5, 1.5],  # Video más ancho
                 hspace=0.4, wspace=0.4,
                 left=0.08, right=0.95, top=0.90, bottom=0.15)
    
    # Panel de video (ocupa 2 filas y 1 columna)
    ax_video = fig.add_subplot(gs[0:2, 0])
    ax_video.set_title('Vista de Cámara', fontweight='bold', fontsize=12)
    ax_video.text(0.5, 0.5, 'CÁMARA\n640x480', ha='center', va='center', 
                 fontsize=14, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
    ax_video.set_xlim(0, 1)
    ax_video.set_ylim(0, 1)
    
    # Gráfico de error (superior derecho)
    ax_error = fig.add_subplot(gs[0, 1])
    ax_error.set_title('Error vs Tiempo', fontweight='bold', fontsize=10)
    ax_error.set_xlabel('Tiempo (s)', fontsize=9)
    ax_error.set_ylabel('Error (m)', fontsize=9)
    ax_error.grid(True, alpha=0.3)
    ax_error.plot([0, 5], [0, 0.1], 'r-', linewidth=2, label='Error')
    ax_error.legend()
    
    # Gráfico de velocidad
    ax_velocity = fig.add_subplot(gs[0, 2])
    ax_velocity.set_title('Velocidad de Corrección', fontweight='bold', fontsize=10)
    ax_velocity.set_xlabel('Tiempo (s)', fontsize=9)
    ax_velocity.set_ylabel('Velocidad (m/s)', fontsize=9)
    ax_velocity.grid(True, alpha=0.3)
    ax_velocity.plot([0, 5], [0, 0.05], 'b-', linewidth=2, label='Velocidad')
    ax_velocity.legend()
    
    # Histograma
    ax_hist = fig.add_subplot(gs[0, 3])
    ax_hist.set_title('Distribución de Error', fontweight='bold', fontsize=10)
    ax_hist.set_xlabel('Error (m)', fontsize=9)
    ax_hist.set_ylabel('Frecuencia', fontsize=9)
    ax_hist.grid(True, alpha=0.3)
    data = np.random.normal(0.02, 0.01, 100)
    ax_hist.hist(data, bins=15, alpha=0.7, color='skyblue')
    
    # Trayectoria X-Y
    ax_position = fig.add_subplot(gs[1, 1:3])
    ax_position.set_title('Trayectoria X-Y', fontweight='bold', fontsize=10)
    ax_position.set_xlabel('X (m)', fontsize=9)
    ax_position.set_ylabel('Y (m)', fontsize=9)
    ax_position.grid(True, alpha=0.3)
    ax_position.set_xlim(-0.35, 0.35)
    ax_position.set_ylim(-0.35, 0.35)
    ax_position.set_aspect('equal')
    
    # Datos de ejemplo
    t = np.linspace(0, 4*np.pi, 100)
    x_desired = 0.2 * np.cos(t/2)
    y_desired = 0.2 * np.sin(t/2)
    x_actual = x_desired + 0.05 * np.random.randn(100)
    y_actual = y_desired + 0.05 * np.random.randn(100)
    
    ax_position.plot(x_desired, y_desired, 'g-', linewidth=2, label='Deseada', alpha=0.7)
    ax_position.plot(x_actual, y_actual, 'orange', linewidth=2, label='Real')
    ax_position.scatter([x_actual[-1]], [y_actual[-1]], c='red', s=100, label='Actual', zorder=5)
    ax_position.legend()
    
    # Panel de información
    ax_info = fig.add_subplot(gs[1, 3])
    ax_info.set_title('Métricas del Sistema', fontweight='bold', fontsize=10)
    ax_info.axis('off')
    
    info_text = """
Error Actual: 0.0234 m
Velocidad: 0.0156 m/s
Error RMS: 0.0189 m
Error Máximo: 0.0567 m
Modo: Lazo Cerrado
Puntos: 142
    """
    ax_info.text(0.1, 0.5, info_text, fontsize=9, 
                verticalalignment='center', fontfamily='monospace')
    
    # Controles
    control_height = 0.12
    control_y_start = 0.02
    
    # Radio buttons
    ax_mode = plt.axes([0.05, control_y_start + 0.06, 0.12, 0.08])
    ax_mode.set_title('Modo de Control', fontsize=9, fontweight='bold')
    radio_mode = RadioButtons(ax_mode, ('Lazo Abierto', 'Lazo Cerrado'))
    
    # Sliders
    slider_width = 0.15
    slider_height = 0.02
    slider_y = control_y_start + 0.03
    
    ax_kp = plt.axes([0.22, slider_y, slider_width, slider_height])
    slider_kp = Slider(ax_kp, 'Kp', 0.1, 5.0, valinit=2.0, 
                      valfmt='%.1f', color='lightblue')
    
    ax_ki = plt.axes([0.40, slider_y, slider_width, slider_height])
    slider_ki = Slider(ax_ki, 'Ki', 0.0, 1.0, valinit=0.1,
                      valfmt='%.2f', color='lightgreen')
    
    ax_kd = plt.axes([0.58, slider_y, slider_width, slider_height])
    slider_kd = Slider(ax_kd, 'Kd', 0.0, 0.2, valinit=0.05,
                      valfmt='%.3f', color='lightcoral')
    
    ax_smooth = plt.axes([0.76, slider_y, slider_width, slider_height])
    slider_smooth = Slider(ax_smooth, 'Suavizado', 0.1, 0.95, valinit=0.7,
                          valfmt='%.2f', color='lightyellow')
    
    # Botones
    button_width = 0.08
    button_height = 0.03
    button_y = control_y_start
    
    ax_start = plt.axes([0.22, button_y, button_width, button_height])
    btn_start = Button(ax_start, 'Iniciar', color='lightgreen')
    
    ax_reset = plt.axes([0.32, button_y, button_width, button_height])
    btn_reset = Button(ax_reset, 'Reset', color='orange')
    
    ax_export = plt.axes([0.42, button_y, button_width, button_height])
    btn_export = Button(ax_export, 'Exportar', color='lightblue')
    
    # Mostrar
    plt.show()

if __name__ == "__main__":
    print("🎨 Probando layout de la interfaz...")
    test_layout()
