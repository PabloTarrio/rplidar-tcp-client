"""
Visualización en tiempo real de datos del SLAMTEC RPLIDAR A1

Muestra en un plot polar 2D que se actualiza con cada revolución del LIDAR.
Los puntos representan obstáculos detectados (ángulo y distancia)

Controles:
    - Cierra la ventana o presiona Ctrl+C para detener.

Requisitos:
Instalar las siguientes bibliotecas:

    pip install matplotlib numpy

    - matplotlib
    - numpy
"""
import sys
import signal
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from lidarclient import LidarClient
from lidarclient.config import load_config, ConfigError

class LidarVisualizer:
    """ Visualizador en tiempo real de datos LIDAR en plot polar. """
    def __init__(self, client):
        """
        Inicializa el visualizador

        Args:
            client: Instancia de LidarClient ya conectada
        """
        self.client = client
        self.fig, self.ax = plt.subplots(subplot_kw={'projection':'polar'},
                                         figsize= (10, 10))
        self.scatter= None
        self.revolution_count = 0

        # Configurar el gráfico
        self.setup_plot()
    
    def setup_plot(self):
        """ Configura el aspecto visual del gráfico polar. """
        # Configurar fondo negro
        self.fig.patch.set_facecolor('black')
        self.ax.set_facecolor('black')
        # Título en blanco
        self.ax.set_title('RPLIDAR A1 - Visualización en Tiempo Real',
                          fontsize= 16, pad= 20, color='white')
        # Configuración del plot polar
        self.ax.set_theta_zero_location('N') # 0º Arriba
        self.ax.set_theta_direction(-1)      # Sentido horario
        self.ax.set_ylim(0, 6000)            # Rango máximo 6 metros
        # Etiquetas en blanco
        self.ax.set_xlabel('Distancia (mm)', fontsize= 13, color='white')
        # Grid en gris claro
        self.ax.grid(True, alpha=0.3, color='gray')
        
        # Cambiar color de los bordes y etiquetas del eje a blanco
        self.ax.tick_params(axis='both', colors='white')
        self.ax.spines['polar'].set_color('white')
        
        # Crear scatter plot inicial vacío
        self.scatter = self.ax.scatter([], [], s=5, alpha=0.8, 
                                    edgecolors='white', linewidth=0.5)

    def update(self, frame):
        """ 
        Función de actualización llamada por FuncAnimation

        Args:
            frame: Número de frame (no usado, requerido por FuncAnimation)
        
        Returns:
            tuple: Objetos actualizados del plot
        """
        try:
            # Obtener una revolución completa
            scan = self.client.get_scan()
            self.revolution_count += 1

            # Extraer ángulos y distancias
            # scan es una lista de tuplas: (calidad, ángulo, distancia)
            angles = []
            distances = []

            for quality, angle, distance in scan:
                # Filtrar mediciones inválidas
                #if distance > 0 and quality > 0:
                if distance > 0:
                    # Convertir ángulo de grados a radianes
                    angle_rad = np.deg2rad(angle)
                    angles.append(angle_rad)
                    distances.append(distance)
            
            # Actualizar el scatter plot
            if angles and distances:
                self.scatter.set_offsets(np.c_[angles, distances])
                # Colorear puntos por distancia: cerca=rojo, lejos=azul
                max_distance = max(distances)
                # Normalizar distancias entre 0 y 1
                normalized_distances = np.array(distances) / max_distance
                # Crear mapa de colores (jet: rojo->amarillo->verde->azul)
                colors = plt.cm.jet_r(normalized_distances)
                self.scatter.set_color(colors)

            # Actualizar título con estadísticas
            valid_points = len (angles)
            if valid_points > 0:
                min_dist = min(distances)
                max_dist = max(distances)
                range_limit = max_dist * 1.2 # Añadir 20% de margen
                #self.ax.set_ylim(0, max(range_limit, 150))  # Mínimo 15 cm.
                title = (f'RPLIDAR A1 - Revolución #{self.revolution_count}\n'
                         f'Puntos: {valid_points} | '
                         f'Distancia min: {min_dist}mm | '
                         f'Distancia max: {max_dist}mm')
            else:
                title = (f'RPLIDAR A1 - Revolución #{self.revolution_count}\n'
                         f'. Sin datos válidos')
            
            self.ax.set_title (title, fontsize= 14, pad= 20)
            
            return self.scatter,

        except KeyboardInterrupt:
            print ("\n Interrupción detectada")
            plt.close(self.fig)
            sys.exit(0)
        
        except Exception as e:
            print (f"\n Error al obtener datos: {e}")
            plt.close(self.fig)
            sys.exit(1)

    def start(self, interval= 100):
        """
        Inicia la animación en tiempo real.

        Args:
            interval: Intervalo de actualización en milisegundos (default: 100ms)
        """

        print ("Iniciando visualización en tiempo real...")
        print ("- Cierra la ventana o presiona Ctrl+C para detener")
        print ()

        # Crear animación
        self.anim = FuncAnimation(
            self.fig,
            self.update,
            interval=interval,
            blit=False,
            cache_frame_data=False
        )

        # Mostrar ventana
        plt.show()

def signal_handler(sig, frame):
    """ Manejador de señal para cierre limpio con Ctrl+C """
    print ("\n\nInterrupción detectada. Cerrando...")
    sys.exit(0)


def main():
    """ Función principal."""
    # Registrar manejador de señal
    signal.signal(signal.SIGINT, signal_handler)

    # Cargar configuración
    try:
        config = load_config()
    except ConfigError as e:
        print (f"Error de configuración: {e}")

    # Crear un cliente
    client = LidarClient(
        config['host'],
        port= config['port'],
        timeout= config['timeout'],
        max_retries= config['max_retries'],
        retry_delay=config['retry_delay']
    )

    try:
        # Conectar al servidor
        print (f"Conectando a {config['host']}:{config['port']}...")
        client.connect_with_retry()
        print (f"Conectado correctamente\n")

        # Crear visualizador
        visualizer = LidarVisualizer(client)

        # Iniciar animación
        visualizer.start(interval=100)   # Actualizar cada 100ms

    except KeyboardInterrupt:
        print("Interrupción detectada")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.disconnect()
        print("Visualización finalizada")

if __name__ == "__main__":
    main()
