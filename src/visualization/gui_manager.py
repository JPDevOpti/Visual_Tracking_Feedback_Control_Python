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
        self.on_start_step_analysis = None
        self.on_stop_step_analysis = None
        
        # Variables de estado
        self.current_metrics = {}
        self.system_status = "Detenido"
        self.current_photo_reference = None  # Para mantener referencia de imágenes
        
        # Configurar interfaz
        self.setup_ui()
        
        print("✅ Control Panel inicializado")
    
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        # Frame principal con grid para mejor distribución
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=0)

        # Panel superior: Controles (más compacto)
        self.setup_control_panel(main_frame)
        self.control_panel_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Panel central: Video y gráficos (más grande y central)
        self.setup_display_panel(main_frame)
        self.display_panel_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # Panel inferior: Información y métricas
        self.setup_info_panel(main_frame)
        self.info_panel_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
    
    def setup_control_panel(self, parent):
        """Configura el panel de controles superiores."""
        self.control_panel_frame = ttk.LabelFrame(parent, text="Panel de Control", padding="10")

        # Usar grid para mejor distribución
        self.control_panel_frame.columnconfigure(0, weight=1)
        self.control_panel_frame.columnconfigure(1, weight=2)
        self.control_panel_frame.columnconfigure(2, weight=1)

        # Frame izquierdo: Modo de control
        mode_frame = ttk.Frame(self.control_panel_frame)
        mode_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ttk.Label(mode_frame, text="Modo de Control:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="🔵 Lazo Abierto", variable=self.control_mode, value="open_loop", command=self.on_mode_changed).pack(anchor=tk.W, pady=2)
        ttk.Radiobutton(mode_frame, text="🟢 Lazo Cerrado", variable=self.control_mode, value="closed_loop", command=self.on_mode_changed).pack(anchor=tk.W, pady=2)

        # Frame central: Parámetros PID más compacto
        param_frame = ttk.Frame(self.control_panel_frame)
        param_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10))
        ttk.Label(param_frame, text="PID & Suavizado", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        param_grid = ttk.Frame(param_frame)
        param_grid.pack(fill=tk.X, pady=5)

        # Kp
        ttk.Label(param_grid, text="Kp:").grid(row=0, column=0, sticky=tk.W, padx=(0, 2))
        kp_scale = ttk.Scale(param_grid, from_=0.1, to=5.0, variable=self.kp_var, orient=tk.HORIZONTAL, length=80, command=self.on_param_changed)
        kp_scale.grid(row=0, column=1, padx=2)
        self.kp_label = ttk.Label(param_grid, text="2.0")
        self.kp_label.grid(row=0, column=2, padx=2)

        # Ki
        ttk.Label(param_grid, text="Ki:").grid(row=0, column=3, sticky=tk.W, padx=(10, 2))
        ki_scale = ttk.Scale(param_grid, from_=0.0, to=1.0, variable=self.ki_var, orient=tk.HORIZONTAL, length=80, command=self.on_param_changed)
        ki_scale.grid(row=0, column=4, padx=2)
        self.ki_label = ttk.Label(param_grid, text="0.1")
        self.ki_label.grid(row=0, column=5, padx=2)

        # Kd
        ttk.Label(param_grid, text="Kd:").grid(row=1, column=0, sticky=tk.W, padx=(0, 2))
        kd_scale = ttk.Scale(param_grid, from_=0.0, to=0.2, variable=self.kd_var, orient=tk.HORIZONTAL, length=80, command=self.on_param_changed)
        kd_scale.grid(row=1, column=1, padx=2)
        self.kd_label = ttk.Label(param_grid, text="0.05")
        self.kd_label.grid(row=1, column=2, padx=2)

        # Suavizado
        ttk.Label(param_grid, text="Suavizado:").grid(row=1, column=3, sticky=tk.W, padx=(10, 2))
        smooth_scale = ttk.Scale(param_grid, from_=0.1, to=0.95, variable=self.smoothing_var, orient=tk.HORIZONTAL, length=80, command=self.on_param_changed)
        smooth_scale.grid(row=1, column=4, padx=2)
        self.smooth_label = ttk.Label(param_grid, text="0.7")
        self.smooth_label.grid(row=1, column=5, padx=2)

        # Frame derecho: Botones de acción
        button_frame = ttk.Frame(self.control_panel_frame)
        button_frame.grid(row=0, column=2, sticky="nsew")
        self.start_button = ttk.Button(button_frame, text="▶️ Iniciar", command=self.on_start_stop_clicked, width=12)
        self.start_button.pack(pady=2)
        ttk.Button(button_frame, text="🔄 Reset", command=self.on_reset_clicked, width=12).pack(pady=2)
        ttk.Button(button_frame, text="💾 Exportar", command=self.on_export_clicked, width=12).pack(pady=2)
        ttk.Checkbutton(button_frame, text="Debug", variable=self.show_debug).pack(pady=2)
        ttk.Separator(button_frame, orient='horizontal').pack(fill='x', pady=5)
        ttk.Label(button_frame, text="Análisis Académico:", font=('Arial', 8, 'bold')).pack()
        ttk.Button(button_frame, text="🎯 Iniciar Escalón", command=self.on_start_step_clicked, width=12).pack(pady=1)
        ttk.Button(button_frame, text="⏹️ Detener Escalón", command=self.on_stop_step_clicked, width=12).pack(pady=1)
    
    def setup_display_panel(self, parent):
        """Configura el panel de visualización central."""
        self.display_panel_frame = ttk.Frame(parent)
        self.display_panel_frame.columnconfigure(0, weight=1)
        self.display_panel_frame.columnconfigure(1, weight=2)

        # Frame izquierdo: Video de cámara (más grande)
        video_frame = ttk.LabelFrame(self.display_panel_frame, text="Vista de Cámara", padding="5")
        video_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.video_canvas = tk.Canvas(video_frame, width=720, height=540, bg='black')
        self.video_canvas.pack(fill=tk.BOTH, expand=True)

        # Frame derecho: Gráficos (más grande)
        plot_frame = ttk.LabelFrame(self.display_panel_frame, text="Análisis en Tiempo Real", padding="5")
        plot_frame.grid(row=0, column=1, sticky="nsew")
        self.plot_frame = plot_frame
        self.matplotlib_canvas = None
    
    def setup_info_panel(self, parent):
        """Configura el panel de información inferior."""
        self.info_panel_frame = ttk.LabelFrame(parent, text="Información del Sistema", padding="10")
        self.info_panel_frame.columnconfigure(0, weight=1)
        self.info_panel_frame.columnconfigure(1, weight=2)
        self.info_panel_frame.columnconfigure(2, weight=1)

        # Frame izquierdo: Estado del sistema
        status_frame = ttk.Frame(self.info_panel_frame)
        status_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ttk.Label(status_frame, text="Estado:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        self.status_label = ttk.Label(status_frame, text="⏹️ Detenido", foreground='red')
        self.status_label.pack(anchor=tk.W)
        ttk.Label(status_frame, text="Modo:", font=('Arial', 9, 'bold')).pack(anchor=tk.W, pady=(10, 0))
        self.mode_label = ttk.Label(status_frame, text="🔵 Lazo Abierto")
        self.mode_label.pack(anchor=tk.W)

        # Frame central: Métricas en tiempo real
        metrics_frame = ttk.Frame(self.info_panel_frame)
        metrics_frame.grid(row=0, column=1, sticky="nsew")
        ttk.Label(metrics_frame, text="Métricas en Tiempo Real:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        metrics_grid = ttk.Frame(metrics_frame)
        metrics_grid.pack(fill=tk.X, pady=5)
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

        # Frame derecho: Métricas académicas
        academic_frame = ttk.Frame(self.info_panel_frame)
        academic_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
        ttk.Label(academic_frame, text="Métricas Académicas:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        academic_grid = ttk.Frame(academic_frame)
        academic_grid.pack(fill=tk.X, pady=5)
        self.rise_time_label = ttk.Label(academic_grid, text="Tiempo Subida: --- s", foreground='blue')
        self.rise_time_label.grid(row=0, column=0, sticky=tk.W, pady=1)
        self.academic_settling_label = ttk.Label(academic_grid, text="T. Establecimiento: --- s", foreground='blue')
        self.academic_settling_label.grid(row=1, column=0, sticky=tk.W, pady=1)
        self.academic_overshoot_label = ttk.Label(academic_grid, text="Sobreimpulso: --- %", foreground='blue')
        self.academic_overshoot_label.grid(row=2, column=0, sticky=tk.W, pady=1)
        self.ss_error_label = ttk.Label(academic_grid, text="Error Est. Est.: --- m", foreground='blue')
        self.ss_error_label.grid(row=3, column=0, sticky=tk.W, pady=1)
        self.analysis_status_label = ttk.Label(academic_grid, text="Estado: Inactivo", foreground='gray')
        self.analysis_status_label.grid(row=4, column=0, sticky=tk.W, pady=5)
    
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
        
        # Mantener referencia para evitar que sea recolectada por garbage collector
        self.current_photo_reference = photo
    
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
        
        # Actualizar métricas académicas si están disponibles
        self._update_academic_metrics(metrics)
    
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
    
    def on_start_step_clicked(self):
        """Callback para iniciar análisis de escalón."""
        if self.on_start_step_analysis:
            self.on_start_step_analysis()
    
    def on_stop_step_clicked(self):
        """Callback para detener análisis de escalón."""
        if self.on_stop_step_analysis:
            self.on_stop_step_analysis()
    
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
        self.on_start_step_analysis = callbacks.get('on_start_step_analysis')
        self.on_stop_step_analysis = callbacks.get('on_stop_step_analysis')
    
    def _update_academic_metrics(self, metrics: Dict[str, Any]):
        """
        Actualiza las métricas académicas en la interfaz.
        
        Args:
            metrics: Diccionario con métricas del sistema
        """
        # Verificar si hay análisis de escalón activo
        step_analysis_active = any(key.startswith('step_') for key in metrics.keys())
        
        if step_analysis_active:
            self.analysis_status_label.config(text="Estado: Analizando...", foreground='orange')
            
            # Actualizar métricas específicas de escalón
            rise_time = metrics.get('step_rise_time')
            if rise_time is not None:
                self.rise_time_label.config(text=f"Tiempo Subida: {rise_time:.3f} s")
            else:
                self.rise_time_label.config(text="Tiempo Subida: Calculando...")
            
            settling_time = metrics.get('step_settling_time')
            if settling_time is not None:
                self.academic_settling_label.config(text=f"T. Establecimiento: {settling_time:.3f} s")
            else:
                self.academic_settling_label.config(text="T. Establecimiento: Calculando...")
            
            overshoot = metrics.get('step_overshoot_percentage')
            if overshoot is not None:
                self.academic_overshoot_label.config(text=f"Sobreimpulso: {overshoot:.2f} %")
            else:
                self.academic_overshoot_label.config(text="Sobreimpulso: Calculando...")
            
            ss_error = metrics.get('step_steady_state_error')
            if ss_error is not None:
                self.ss_error_label.config(text=f"Error Est. Est.: {ss_error:.4f} m")
            else:
                self.ss_error_label.config(text="Error Est. Est.: Calculando...")
                
            # Verificar si el análisis es válido
            if metrics.get('step_analysis_valid', False):
                self.analysis_status_label.config(text="Estado: Completado", foreground='green')
        
        else:
            # No hay análisis activo
            self.analysis_status_label.config(text="Estado: Inactivo", foreground='gray')
            self.rise_time_label.config(text="Tiempo Subida: --- s")
            self.academic_settling_label.config(text="T. Establecimiento: --- s")
            self.academic_overshoot_label.config(text="Sobreimpulso: --- %")
            self.ss_error_label.config(text="Error Est. Est.: --- m")

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
