"""
=============================================================================
EJEMPLO 5: Visualizacion Grafica en Tiempo Real del LIDAR
=============================================================================

OBJETIVO:
    Mostrar los datos del LIDAR en un grafico polar 2D animado que se
    actualiza en tiempo real, permitiendo visualizar intuitivamente como
    "ve" el sensor su entorno.

REQUISITOS PREVIOS:
    - Haber completado los ejemplos basicos
    - Entender coordenadas polares (angulo, distancia)
    - Tener instaladas las bibliotecas de visualizacion

CONCEPTOS QUE APRENDERAS:
    - Visualizacion de datos en coordenadas polares
    - Animacion en tiempo real con matplotlib.FuncAnimation
    - Conversion de grados a radianes
    - Mapas de colores para representar distancias
    - Manejo de señales (Ctrl+C) para cierre limpio
    - Configuracion de graficos con fondo oscuro

REQUISITOS DE INSTALACION:
    pip install matplotlib numpy

    O si instalaste con dependencias opcionales:
    pip install -e .[visualization]

CASOS DE USO PRACTICOS:
    - Visualizacion intuitiva del entorno escaneado
    - Debugging visual de cobertura y alcance del LIDAR
    - Demostraciones y presentaciones educativas
    - Detectar problemas de hardware visualmente
    - Entender como "ve" el LIDAR su entorno
    - Verificar campo de vision antes de experimentos

INTERPRETACION DEL GRAFICO:
    - Centro: Posicion del LIDAR
    - Angulo: Direccion de la medicion (0º arriba, sentido horario)
    - Distancia radial: Distancia al objeto detectado
    - Color: Rojo=cerca, Azul=lejos (mapa jet_r)
    - Ausencia de puntos: Sin objetos detectados en esa direccion

TIEMPO ESTIMADO: 20 minutos

CONTROLES:
    - Cerrar ventana: Detiene la visualizacion
    - Ctrl+C: Detiene limpiamente desde terminal
=============================================================================
"""

import signal
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from lidarclient import LidarClient
from lidarclient.config import ConfigError, load_config


class LidarVisualizer:
    """
    Visualizador en tiempo real de datos LIDAR en grafico polar.
    
    Esta clase encapsula toda la logica de visualizacion:
    - Configuracion del grafico matplotlib
    - Actualizacion de datos en cada frame
    - Calculo de colores por distancia
    - Estadisticas en el titulo
    
    Attributes:
        client: Instancia de LidarClient para obtener datos
        fig: Figura de matplotlib
        ax: Axes polar de matplotlib
        scatter: Objeto scatter plot para los puntos
        revolution_count: Contador de revoluciones procesadas
    """
    
    def __init__(self, client):
        """
        Inicializa el visualizador con configuracion del grafico.
        
        Args:
            client: Instancia de LidarClient ya conectada al servidor
        
        Crea:
            - Figura matplotlib 10x10 pulgadas
            - Axes con proyeccion polar
            - Scatter plot vacio inicial
            - Configuracion visual (colores, limites, grid)
        """
        self.client = client
        
        # =====================================================================
        # Crear Figura y Axes Polar
        # =====================================================================
        # subplot_kw={'projection': 'polar'}: Crea grafico en coordenadas polares
        # - Eje angular (theta): angulos 0-360 grados
        # - Eje radial (r): distancias desde el centro
        # figsize=(10, 10): Ventana cuadrada de 10x10 pulgadas
        
        self.fig, self.ax = plt.subplots(
            subplot_kw={"projection": "polar"}, figsize=(10, 10)
        )
        
        self.scatter = None
        self.revolution_count = 0
        
        # Configurar aspecto visual
        self.setup_plot()
    
    def setup_plot(self):
        """
        Configura el aspecto visual del grafico polar.
        
        Configuraciones aplicadas:
            - Fondo negro (mejor contraste con puntos de colores)
            - Titulo en blanco
            - 0° arriba (Norte), rotacion horaria (sentido LIDAR)
            - Rango radial 0-6000mm (0-6 metros)
            - Grid sutil en gris
            - Etiquetas y bordes en blanco
        
        Nota sobre orientacion:
            set_theta_zero_location('N'): 0° arriba
            set_theta_direction(-1): Sentido horario
            
            Esto coincide con la orientacion del LIDAR:
            - 0° = Frente del sensor
            - 90° = Derecha
            - 180° = Atras
            - 270° = Izquierda
        """
        
        # =====================================================================
        # Colores de Fondo
        # =====================================================================
        # Fondo negro para mejor contraste con puntos de colores brillantes
        self.fig.patch.set_facecolor("black")
        self.ax.set_facecolor("black")
        
        # =====================================================================
        # Titulo
        # =====================================================================
        self.ax.set_title(
            "RPLIDAR A1 - Visualizacion en Tiempo Real",
            fontsize=16,
            pad=20,
            color="white",
        )
        
        # =====================================================================
        # Configuracion de Orientacion Polar
        # =====================================================================
        # set_theta_zero_location('N'): Coloca 0° en la parte superior (Norte)
        # set_theta_direction(-1): Rotacion horaria (sentido agujas del reloj)
        #
        # Por que horario?
        # El RPLIDAR A1 gira en sentido horario, asi que reflejamos eso
        # en la visualizacion para que coincida con la realidad.
        
        self.ax.set_theta_zero_location("N")  # 0° arriba
        self.ax.set_theta_direction(-1)  # Sentido horario
        
        # =====================================================================
        # Limites del Eje Radial (Distancia)
        # =====================================================================
        # set_ylim(0, 6000): Muestra distancias de 0 a 6000mm (0 a 6 metros)
        #
        # Por que 6 metros?
        # - El RPLIDAR A1 tiene alcance maximo de 12m
        # - En ambientes interiores tipicos, 6m es suficiente
        # - Mejora la visualizacion al no mostrar rango vacio
        #
        # Puedes ajustar segun tu entorno:
        # - Interiores pequeños: 3000mm (3m)
        # - Exteriores: 12000mm (12m)
        
        self.ax.set_ylim(0, 6000)  # Rango 0-6 metros
        
        # =====================================================================
        # Etiquetas y Grid
        # =====================================================================
        self.ax.set_xlabel("Distancia (mm)", fontsize=13, color="white")
        self.ax.grid(True, alpha=0.3, color="gray")  # Grid sutil
        
        # Cambiar color de ticks y bordes a blanco
        self.ax.tick_params(axis="both", colors="white")
        self.ax.spines["polar"].set_color("white")
        
        # =====================================================================
        # Crear Scatter Plot Inicial Vacio
        # =====================================================================
        # scatter(): Grafico de puntos dispersos
        # - s=5: Tamaño pequeño de puntos (pixeles)
        # - alpha=0.8: Ligeramente transparentes
        # - edgecolors='white': Borde blanco para cada punto
        # - linewidth=0.5: Borde fino
        #
        # Inicialmente vacio ([], []), se actualizara en cada frame
        
        self.scatter = self.ax.scatter(
            [], [], s=5, alpha=0.8, edgecolors="white", linewidth=0.5
        )
    
    def update(self, frame):
        """
        Funcion de actualizacion llamada por FuncAnimation en cada frame.
        
        Esta funcion se ejecuta repetidamente (cada 100ms por defecto):
        1. Obtiene nueva revolucion del LIDAR
        2. Filtra puntos validos (distance > 0)
        3. Convierte angulos a radianes
        4. Asigna colores segun distancia (rojo=cerca, azul=lejos)
        5. Actualiza scatter plot y titulo
        
        Args:
            frame: Numero de frame (requerido por FuncAnimation, no usado)
        
        Returns:
            tuple: Objetos del plot actualizados (requerido por blit=False)
        
        Raises:
            KeyboardInterrupt: Si se presiona Ctrl+C, cierra limpiamente
            Exception: Cualquier error cierra el visualizador
        """
        
        try:
            # =================================================================
            # PASO 1: Obtener Revolucion del LIDAR
            # =================================================================
            scan = self.client.get_scan()
            self.revolution_count += 1
            
            # =================================================================
            # PASO 2: Filtrar y Extraer Datos Validos
            # =================================================================
            # scan es lista de tuplas: (quality, angle, distance)
            # Solo procesamos puntos con distance > 0 (mediciones validas)
            
            angles = []
            distances = []
            
            for quality, angle, distance in scan:
                # Filtrar mediciones invalidas (distance=0)
                # Comentado: filtro por quality para incluir modo Express
                # if distance > 0 and quality > 0:  # Solo Standard con calidad
                if distance > 0:  # Standard y Express
                    # ---------------------------------------------------------
                    # Conversion de Grados a Radianes
                    # ---------------------------------------------------------
                    # matplotlib.polar requiere angulos en radianes
                    # Formula: radianes = grados * (π / 180)
                    # numpy.deg2rad() hace esta conversion automaticamente
                    
                    angle_rad = np.deg2rad(angle)
                    angles.append(angle_rad)
                    distances.append(distance)
            
            # =================================================================
            # PASO 3: Actualizar Scatter Plot con Nuevos Datos
            # =================================================================
            if angles and distances:
                # -------------------------------------------------------------
                # 3.1: Actualizar Posiciones de los Puntos
                # -------------------------------------------------------------
                # set_offsets(): Actualiza coordenadas (theta, r) de los puntos
                # np.c_[angles, distances]: Combina listas en array 2D columnar
                #   [[angle1, dist1],
                #    [angle2, dist2],
                #    ...]
                
                self.scatter.set_offsets(np.c_[angles, distances])
                
                # -------------------------------------------------------------
                # 3.2: Calcular Colores por Distancia
                # -------------------------------------------------------------
                # Estrategia de coloreo:
                # - Objetos cercanos: ROJO (alerta, importante)
                # - Objetos medios: AMARILLO/VERDE
                # - Objetos lejanos: AZUL (menos criticos)
                #
                # Proceso:
                # 1. Normalizar distancias entre 0 y 1
                # 2. Aplicar mapa de colores jet_r (jet invertido)
                #    jet_r: azul -> verde -> amarillo -> rojo (distancia decrece)
                
                max_distance = max(distances)
                
                # Normalizar: 0.0 (cerca) a 1.0 (lejos)
                normalized_distances = np.array(distances) / max_distance
                
                # Aplicar mapa de colores
                # plt.cm.jet_r: Colormap jet invertido
                # Retorna array RGBA (Red, Green, Blue, Alpha)
                colors = plt.cm.jet_r(normalized_distances)
                
                # Actualizar colores de los puntos
                self.scatter.set_color(colors)
            
            # =================================================================
            # PASO 4: Actualizar Titulo con Estadisticas
            # =================================================================
            valid_points = len(angles)
            
            if valid_points > 0:
                min_dist = min(distances)
                max_dist = max(distances)
                
                # Opcion avanzada: ajustar rango dinamicamente
                # self.ax.set_ylim(0, max(max_dist * 1.1, 150))
                
                title = (
                    f"RPLIDAR A1 - Revolucion #{self.revolution_count}\n"
                    f"Puntos: {valid_points} | "
                    f"Distancia min: {min_dist:.0f}mm | "
                    f"Distancia max: {max_dist:.0f}mm"
                )
            else:
                # Revolucion sin puntos validos (area vacia o error)
                title = (
                    f"RPLIDAR A1 - Revolucion #{self.revolution_count}\n"
                    f"Sin datos validos"
                )
            
            self.ax.set_title(title, fontsize=14, pad=20, color="white")
            
            # Retornar tupla de objetos actualizados (requerido por FuncAnimation)
            return (self.scatter,)
        
        except KeyboardInterrupt:
            # =================================================================
            # Manejo de Ctrl+C desde el loop de animacion
            # =================================================================
            print("\nInterrupcion detectada")
            plt.close(self.fig)
            sys.exit(0)
        
        except Exception as e:
            # =================================================================
            # Manejo de Errores Generales
            # =================================================================
            print(f"\nError al obtener datos: {e}")
            plt.close(self.fig)
            sys.exit(1)
    
    def start(self, interval=100):
        """
        Inicia la animacion en tiempo real.
        
        Args:
            interval: Intervalo de actualizacion en milisegundos (default: 100ms)
                      100ms = 10 FPS (frames por segundo)
                      50ms = 20 FPS (mas fluido pero mas CPU)
                      200ms = 5 FPS (menos fluido pero menos CPU)
        
        Nota sobre interval:
            - El LIDAR captura a ~5-10 Hz (revoluciones/segundo)
            - interval=100ms (10 FPS) es suficiente para mostrar todas las revoluciones
            - Reducir interval no mejora la visualizacion (el LIDAR es el cuello de botella)
        
        FuncAnimation parametros:
            - fig: Figura a animar
            - update: Funcion callback a llamar en cada frame
            - interval: Milisegundos entre frames
            - blit=False: Redibujar toda la figura (necesario para polar)
            - cache_frame_data=False: No cachear frames (datos cambian siempre)
        """
        
        print("Iniciando visualizacion en tiempo real...")
        print("- Cierra la ventana o presiona Ctrl+C para detener")
        print()
        
        # =====================================================================
        # Crear Animacion con FuncAnimation
        # =====================================================================
        # FuncAnimation: Motor de animacion de matplotlib
        # - Llama a self.update() cada 'interval' milisegundos
        # - Maneja el event loop de matplotlib automaticamente
        # - blit=False: Necesario para graficos polares (no soportan blitting)
        
        self.anim = FuncAnimation(
            self.fig,
            self.update,
            interval=interval,
            blit=False,
            cache_frame_data=False,
        )
        
        # =====================================================================
        # Mostrar Ventana (Bloqueante)
        # =====================================================================
        # plt.show(): Bloquea hasta que se cierra la ventana
        # Mientras esta abierta, FuncAnimation llama a update() repetidamente
        
        plt.show()


def signal_handler(sig, frame):
    """
    Manejador de señal SIGINT (Ctrl+C) para cierre limpio.
    
    Args:
        sig: Numero de señal (SIGINT = 2)
        frame: Frame de ejecucion actual (no usado)
    
    Este handler se registra con signal.signal() para capturar Ctrl+C
    y cerrar el programa limpiamente sin traceback feo.
    """
    print("\n\nInterrupcion detectada. Cerrando...")
    sys.exit(0)


def main():
    """
    Funcion principal que orquesta la visualizacion.
    
    Flujo:
        1. Registrar handler de Ctrl+C
        2. Cargar configuracion desde config.ini
        3. Crear y conectar LidarClient
        4. Crear LidarVisualizer
        5. Iniciar animacion (bloqueante hasta cerrar ventana)
        6. Desconectar limpiamente al finalizar
    """
    
    # =========================================================================
    # PASO 1: Registrar Manejador de Señal para Ctrl+C
    # =========================================================================
    signal.signal(signal.SIGINT, signal_handler)
    
    # =========================================================================
    # PASO 2: Cargar Configuracion
    # =========================================================================
    try:
        config = load_config()
    except ConfigError as e:
        print(f"Error de configuracion: {e}")
        sys.exit(1)
    
    # =========================================================================
    # PASO 3: Crear Cliente LIDAR
    # =========================================================================
    client = LidarClient(
        config["host"],
        port=config["port"],
        timeout=config["timeout"],
        max_retries=config["max_retries"],
        retry_delay=config["retry_delay"],
        scan_mode=config["scan_mode"],
    )
    
    try:
        # =====================================================================
        # PASO 4: Conectar al Servidor
        # =====================================================================
        print(f"Conectando a {config['host']}:{config['port']}...")
        client.connect_with_retry()
        print("Conectado correctamente\n")
        
        # =====================================================================
        # PASO 5: Crear Visualizador
        # =====================================================================
        visualizer = LidarVisualizer(client)
        
        # =====================================================================
        # PASO 6: Iniciar Animacion (Bloqueante)
        # =====================================================================
        # start() bloquea hasta que se cierra la ventana o Ctrl+C
        visualizer.start(interval=100)  # Actualizar cada 100ms (10 FPS)
    
    except KeyboardInterrupt:
        print("\nInterrupcion detectada")
    
    except Exception as e:
        print(f"\nError: {e}")
        print("\nSoluciones posibles:")
        print("  - Verifica que matplotlib y numpy estan instalados:")
        print("    pip install matplotlib numpy")
        print("  - Si ejecutas por SSH, necesitas X11 forwarding:")
        print("    ssh -X usuario@servidor")
        print("  - O ejecuta localmente en un entorno con display grafico")
    
    finally:
        client.disconnect()
        print("\nVisualizacion finalizada")


# =============================================================================
# EJERCICIOS SUGERIDOS PARA PRACTICAR:
# =============================================================================
#
# 1. BASICO: Añade una leyenda al grafico mostrando el mapa de colores
#    (rojo=cerca, azul=lejos) con colorbar de matplotlib.
#    Pista: fig.colorbar(mappable, ax=ax)
#
# 2. INTERMEDIO: Añade modo "trail" que muestre las ultimas N revoluciones
#    superpuestas con diferentes alfas (mas reciente = mas opaco).
#    Permite visualizar movimiento de objetos.
#
# 3. AVANZADO: Añade deteccion de sectores libres/ocupados:
#    - Divide el circulo en 12 sectores (30° cada uno)
#    - Colorea el fondo de cada sector: verde=libre, rojo=ocupado
#    - Util para navegacion: mostrar donde puede moverse un robot
#
# 4. INTERACTIVO: Añade controles de teclado con mpl_connect():
#    - 'r': Reset contador de revoluciones
#    - '+'/'-': Aumentar/reducir rango radial
#    - 's': Guardar frame actual como imagen PNG
#    - 'p': Pausar/reanudar animacion
#
# 5. EXPORTACION: Añade opcion para grabar la visualizacion como video MP4
#    usando matplotlib.animation.FFMpegWriter.
#    Requiere ffmpeg instalado en el sistema.
#
# =============================================================================

if __name__ == "__main__":
    main()
