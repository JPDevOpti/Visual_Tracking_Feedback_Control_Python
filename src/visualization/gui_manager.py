"""
Gestor de Interfaz Gráfica Principal
Maneja la ventana principal con controles y visualización integrada
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import numpy as np
from typing import Optional, Dict, Callable, Any
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cv2
from PIL import Image, ImageTk


class ControlPanel:
    """
    Panel de control principal para el sistema.
    """
    
    def __init__(self, master):
        """
        Inicializa el panel de control.
        
        Args:
            master: Ventana padre de tkinter
        """
        print("🖥️ Inicializando Control Panel...")
        
        self.master = master
        self.master.title("Sistema de Control - Lazo Abierto vs Cerrado")
        self.master.geometry("1400x900")
        self.master.configure(bg='#f0f0f0')
        
        # Variables de control
        self.control_mode = tk.StringVar(value="open_loop")
        self.is_running = tk.BooleanVar(value=False)
        self.show_debug = tk.BooleanVar(value=True)
        
        # Variables para parámetros PID
        self.kp_var = tk.DoubleVar(value=2.0)
        self.ki_var = tk.DoubleVar(value=0.1)
        self.kd_var = tk.DoubleVar(value=0.05)
        self.smoothing_var = tk.DoubleVar(value=0.7)
        
        # Callbacks externos
        self.on_mode_change = None
        self.on_parameter_change = None
        self.on_reset_system = None
        self.on_start_stop = None
        self.on_export_data = None
        
        # Variables de estado
        self.current_metrics = {}
        self.system_status = "Detenido"
        
        # Configurar interfaz
        self.setup_ui()
        
        print("✅ Control Panel inicializado")
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Frame principal
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel superior: Controles
        self.setup_control_panel(main_frame)
        
        # Panel central: Video y gráficos
        self.setup_display_panel(main_frame)
        
        # Panel inferior: Información y métricas
        self.setup_info_panel(main_frame)
    
    def setup_control_panel(self, parent):
        """Configura el panel de controles superiores."""
        control_frame = ttk.LabelFrame(parent, text="Panel de Control", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame izquierdo: Modo de control
        mode_frame = ttk.Frame(control_frame)
        mode_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        ttk.Label(mode_frame, text="Modo de Control:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Radio buttons para modo
        ttk.Radiobutton(mode_frame, text="🔵 Lazo Abierto", 
                       variable=self.control_mode, value="open_loop",
                       command=self.on_mode_changed).pack(anchor=tk.W, pady=2)
        
        ttk.Radiobutton(mode_frame, text="🟢 Lazo Cerrado", 
                       variable=self.control_mode, value="closed_loop",
                       command=self.on_mode_changed).pack(anchor=tk.W, pady=2)
        
        # Frame central: Parámetros
        param_frame = ttk.Frame(control_frame)
        param_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        ttk.Label(param_frame, text="Parámetros:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Parámetros en grid
        param_grid = ttk.Frame(param_frame)
        param_grid.pack(fill=tk.X, pady=5)
        
        # PID Parameters
        ttk.Label(param_grid, text="Kp:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        kp_scale = ttk.Scale(param_grid, from_=0.1, to=5.0, variable=self.kp_var, 
                            orient=tk.HORIZONTAL, length=100, command=self.on_param_changed)
        kp_scale.grid(row=0, column=1, padx=5)
        self.kp_label = ttk.Label(param_grid, text="2.0")
        self.kp_label.grid(row=0, column=2, padx=5)
        
        ttk.Label(param_grid, text="Ki:").grid(row=0, column=3, sticky=tk.W, padx=(20, 5))
        ki_scale = ttk.Scale(param_grid, from_=0.0, to=1.0, variable=self.ki_var, 
                            orient=tk.HORIZONTAL, length=100, command=self.on_param_changed)
        ki_scale.grid(row=0, column=4, padx=5)
        self.ki_label = ttk.Label(param_grid, text="0.1")
        self.ki_label.grid(row=0, column=5, padx=5)
        
        ttk.Label(param_grid, text="Kd:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        kd_scale = ttk.Scale(param_grid, from_=0.0, to=0.2, variable=self.kd_var, 
                            orient=tk.HORIZONTAL, length=100, command=self.on_param_changed)
        kd_scale.grid(row=1, column=1, padx=5)
        self.kd_label = ttk.Label(param_grid, text="0.05")
        self.kd_label.grid(row=1, column=2, padx=5)
        
        ttk.Label(param_grid, text="Suavizado:").grid(row=1, column=3, sticky=tk.W, padx=(20, 5))
        smooth_scale = ttk.Scale(param_grid, from_=0.1, to=0.95, variable=self.smoothing_var, 
                               orient=tk.HORIZONTAL, length=100, command=self.on_param_changed)
        smooth_scale.grid(row=1, column=4, padx=5)
        self.smooth_label = ttk.Label(param_grid, text="0.7")
        self.smooth_label.grid(row=1, column=5, padx=5)
        
        # Frame derecho: Botones de acción
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.start_button = ttk.Button(button_frame, text="▶️ Iniciar", 
                                      command=self.on_start_stop_clicked, width=12)
        self.start_button.pack(pady=2)
        
        ttk.Button(button_frame, text="🔄 Reset", 
                  command=self.on_reset_clicked, width=12).pack(pady=2)
        
        ttk.Button(button_frame, text="💾 Exportar", 
                  command=self.on_export_clicked, width=12).pack(pady=2)
        
        ttk.Checkbutton(button_frame, text="Debug", 
                       variable=self.show_debug).pack(pady=2)
    
    def setup_display_panel(self, parent):
        """Configura el panel de visualización central."""
        display_frame = ttk.Frame(parent)
        display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Frame izquierdo: Video de cámara
        video_frame = ttk.LabelFrame(display_frame, text="Vista de Cámara", padding="5")
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # Canvas para video
        self.video_canvas = tk.Canvas(video_frame, width=640, height=480, bg='black')
        self.video_canvas.pack()
        
        # Frame derecho: Gráficos
        plot_frame = ttk.LabelFrame(display_frame, text="Análisis en Tiempo Real", padding="5")
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Placeholder para matplotlib
        self.plot_frame = plot_frame
        self.matplotlib_canvas = None
    
    def setup_info_panel(self, parent):
        """Configura el panel de información inferior."""
        info_frame = ttk.LabelFrame(parent, text="Información del Sistema", padding="10")
        info_frame.pack(fill=tk.X)
        
        # Frame izquierdo: Estado del sistema
        status_frame = ttk.Frame(info_frame)
        status_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        ttk.Label(status_frame, text="Estado:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        self.status_label = ttk.Label(status_frame, text="⏹️ Detenido", foreground='red')
        self.status_label.pack(anchor=tk.W)
        
        ttk.Label(status_frame, text="Modo:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(10, 0))
        self.mode_label = ttk.Label(status_frame, text="🔵 Lazo Abierto")
        self.mode_label.pack(anchor=tk.W)
        
        # Frame central: Métricas en tiempo real
        metrics_frame = ttk.Frame(info_frame)
        metrics_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(metrics_frame, text="Métricas en Tiempo Real:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        
        # Grid para métricas
        metrics_grid = ttk.Frame(metrics_frame)
        metrics_grid.pack(fill=tk.X, pady=5)
        
        # Labels para métricas
        self.error_label = ttk.Label(metrics_grid, text="Error: --- m")
        self.error_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.velocity_label = ttk.Label(metrics_grid, text="Velocidad: --- m/s")
        self.velocity_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        self.rms_label = ttk.Label(metrics_grid, text="RMS: --- m")
        self.rms_label.grid(row=0, column=2, sticky=tk.W)
        
        self.position_label = ttk.Label(metrics_grid, text="Posición: (---, ---, ---)")
        self.position_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 20))
        
        self.settling_label = ttk.Label(metrics_grid, text="T. Estab.: --- s")
        self.settling_label.grid(row=1, column=1, sticky=tk.W, padx=(0, 20))
        
        self.overshoot_label = ttk.Label(metrics_grid, text="Overshoot: ---%")
        self.overshoot_label.grid(row=1, column=2, sticky=tk.W)
    
    def set_matplotlib_figure(self, figure):
        """
        Integra una figura de matplotlib en la interfaz.
        
        Args:
            figure: Figura de matplotlib
        """
        if self.matplotlib_canvas:
            self.matplotlib_canvas.get_tk_widget().destroy()
        
        self.matplotlib_canvas = FigureCanvasTkAgg(figure, self.plot_frame)
        self.matplotlib_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.matplotlib_canvas.draw()
    
    def update_video_frame(self, cv_image):
        """
        Actualiza el frame de video en la interfaz.
        
        Args:
            cv_image: Imagen de OpenCV en formato BGR
        """
        # Convertir BGR a RGB
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        
        # Redimensionar si es necesario
        height, width = rgb_image.shape[:2]
        if width != 640 or height != 480:
            rgb_image = cv2.resize(rgb_image, (640, 480))
        
        # Convertir a formato PIL
        pil_image = Image.fromarray(rgb_image)
        
        # Convertir a PhotoImage
        photo = ImageTk.PhotoImage(pil_image)
        
        # Actualizar canvas
        self.video_canvas.delete("all")
        self.video_canvas.create_image(320, 240, image=photo)
        self.video_canvas.image = photo  # Mantener referencia
    
    def update_metrics_display(self, metrics: Dict[str, Any]):
        """
        Actualiza la visualización de métricas.
        
        Args:
            metrics: Diccionario con métricas actuales
        """
        self.current_metrics = metrics
        
        # Actualizar labels
        error = metrics.get('current_error_magnitude', 0)
        self.error_label.config(text=f"Error: {error:.4f} m")
        
        velocity = metrics.get('current_correction_velocity', 0)
        velocity_icon = "⬇️" if velocity > 0 else "⬆️" if velocity < 0 else "➡️"
        self.velocity_label.config(text=f"Velocidad: {velocity_icon} {velocity:.4f} m/s")
        
        rms = metrics.get('rms_error', 0)
        self.rms_label.config(text=f"RMS: {rms:.4f} m")
        
        # Posición (si está disponible)
        if 'last_position' in metrics:
            pos = metrics['last_position']
            self.position_label.config(text=f"Posición: ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f})")
        
        settling = metrics.get('settling_time', None)
        if settling is not None:
            self.settling_label.config(text=f"T. Estab.: {settling:.2f} s")
        else:
            self.settling_label.config(text="T. Estab.: --- s")
        
        overshoot = metrics.get('overshoot_percentage', 0)
        self.overshoot_label.config(text=f"Overshoot: {overshoot:.1f}%")
    
    def update_system_status(self, status: str, is_running: bool):
        """
        Actualiza el estado del sistema.
        
        Args:
            status: Texto del estado
            is_running: Si el sistema está corriendo
        """
        self.system_status = status
        self.is_running.set(is_running)
        
        if is_running:
            self.status_label.config(text=f"▶️ {status}", foreground='green')
            self.start_button.config(text="⏹️ Detener")
        else:
            self.status_label.config(text=f"⏹️ {status}", foreground='red')
            self.start_button.config(text="▶️ Iniciar")
        
        # Actualizar etiqueta de modo
        mode_text = "🟢 Lazo Cerrado" if self.control_mode.get() == "closed_loop" else "🔵 Lazo Abierto"
        self.mode_label.config(text=mode_text)
    
    def on_mode_changed(self):
        """Callback cuando cambia el modo de control."""
        if self.on_mode_change:
            self.on_mode_change(self.control_mode.get())
        
        # Actualizar interfaz
        self.update_system_status(self.system_status, self.is_running.get())
    
    def on_param_changed(self, *args):
        """Callback cuando cambian los parámetros."""
        # Actualizar labels
        self.kp_label.config(text=f"{self.kp_var.get():.2f}")
        self.ki_label.config(text=f"{self.ki_var.get():.3f}")
        self.kd_label.config(text=f"{self.kd_var.get():.3f}")
        self.smooth_label.config(text=f"{self.smoothing_var.get():.2f}")
        
        # Notificar cambio
        if self.on_parameter_change:
            params = {
                'kp': self.kp_var.get(),
                'ki': self.ki_var.get(),
                'kd': self.kd_var.get(),
                'smoothing': self.smoothing_var.get()
            }
            self.on_parameter_change(params)
    
    def on_start_stop_clicked(self):
        """Callback para botón de inicio/parada."""
        if self.on_start_stop:
            self.on_start_stop(not self.is_running.get())
    
    def on_reset_clicked(self):
        """Callback para botón de reset."""
        if self.on_reset_system:
            self.on_reset_system()
    
    def on_export_clicked(self):
        """Callback para botón de exportar."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Exportar datos del sistema"
        )
        
        if filename and self.on_export_data:
            self.on_export_data(filename)
    
    def show_error_message(self, title: str, message: str):
        """Muestra mensaje de error."""
        messagebox.showerror(title, message)
    
    def show_info_message(self, title: str, message: str):
        """Muestra mensaje informativo."""
        messagebox.showinfo(title, message)
    
    def set_callbacks(self, **callbacks):
        """
        Configura los callbacks externos.
        
        Args:
            **callbacks: Diccionario con callbacks
        """
        self.on_mode_change = callbacks.get('on_mode_change')
        self.on_parameter_change = callbacks.get('on_parameter_change')
        self.on_reset_system = callbacks.get('on_reset_system')
        self.on_start_stop = callbacks.get('on_start_stop')
        self.on_export_data = callbacks.get('on_export_data')


class GUIManager:
    """
    Gestor principal de la interfaz gráfica.
    """
    
    def __init__(self):
        """Inicializa el gestor de GUI."""
        print("🖼️ Inicializando GUI Manager...")
        
        self.root = tk.Tk()
        self.control_panel = ControlPanel(self.root)
        
        # Thread para actualización de GUI
        self.update_thread = None
        self.is_updating = False
        
        print("✅ GUI Manager inicializado")
    
    def start(self):
        """Inicia la interfaz gráfica."""
        print("🚀 Iniciando interfaz gráfica...")
        
        # Configurar cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Iniciar loop principal
        self.root.mainloop()
    
    def on_closing(self):
        """Callback al cerrar la ventana."""
        print("🛑 Cerrando interfaz gráfica...")
        
        self.is_updating = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
        
        self.root.quit()
        self.root.destroy()
    
    def get_control_panel(self) -> ControlPanel:
        """Retorna el panel de control."""
        return self.control_panel
    
    def update_gui_safe(self, update_func):
        """
        Ejecuta actualización de GUI de manera thread-safe.
        
        Args:
            update_func: Función para actualizar GUI
        """
        try:
            self.root.after_idle(update_func)
        except tk.TclError:
            # La ventana ya fue cerrada
            pass
