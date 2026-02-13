"""
=============================================================================
EJEMPLO 3: Stream Continuo con Estadisticas en Tiempo Real
=============================================================================

OBJETIVO:
    Capturar revoluciones del LIDAR continuamente y mostrar estadisticas
    actualizadas en tiempo real hasta que el usuario presione Ctrl+C.

REQUISITOS PREVIOS:
    - Haber completado simple_scan.py y understanding_data.py
    - Entender el ciclo basico de captura de datos
    - Conocer que es un bucle infinito (while True)

CONCEPTOS QUE APRENDERAS:
    - Como capturar datos en bucle infinito
    - Manejo de interrupciones con Ctrl+C (KeyboardInterrupt)
    - Calcular estadisticas en tiempo real de forma eficiente
    - Contador de revoluciones para seguimiento
    - Uso de time.sleep() para control de flujo

CASOS DE USO PRACTICOS:
    - Monitoreo continuo del entorno en robotica movil
    - Detectar cambios dinamicos en el espacio escaneado
    - Verificar estabilidad del sistema a largo plazo
    - Aplicaciones en tiempo real (navegacion autonoma, SLAM)
    - Logging de datos para analisis posterior

TIEMPO ESTIMADO: 15 minutos

DETENER: Presiona Ctrl+C para finalizar limpiamente
=============================================================================
"""

import time

from lidarclient import LidarClient
from lidarclient.config import ConfigError, load_config


def main():
    """
    Funcion principal que captura revoluciones continuamente hasta Ctrl+C.

    Flujo del programa:
        1. Cargar configuracion desde config.ini
        2. Crear y conectar cliente LIDAR
        3. Bucle infinito de captura:
           - Obtener revolucion completa
           - Filtrar puntos validos
           - Calcular estadisticas (media, min, max)
           - Mostrar resumen en una linea
           - Pausa breve (100ms)
        4. Al presionar Ctrl+C: desconectar limpiamente y mostrar total
    """

    # =========================================================================
    # PASO 1: Cargar Configuracion desde config.ini
    # =========================================================================
    # La configuracion contiene todos los parametros de conexion necesarios.
    # Si falla, mostramos error y salimos (no podemos continuar sin config).

    try:
        config = load_config()
    except ConfigError as e:
        print(f"Error de configuracion: {e}")
        print("\nSolucion:")
        print("  1. Verifica que existe config.ini")
        print("  2. Si no: cp config.ini.example config.ini")
        print("  3. Edita config.ini con la IP de tu LIDAR")
        return

    # =========================================================================
    # PASO 2: Crear Cliente LIDAR con Parametros del Config
    # =========================================================================
    # El cliente maneja la comunicacion TCP, serializacion de datos,
    # timeouts y reintentos automaticos de conexion.

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
        # PASO 3: Conectar al Servidor con Reintentos Automaticos
        # =====================================================================
        # connect_with_retry() intenta conectar varias veces (max_retries)
        # esperando retry_delay segundos entre intentos. Util si el servidor
        # tarda en arrancar o hay problemas temporales de red.

        client.connect_with_retry()
        print("Conectado al servidor LIDAR")
        print(f"Servidor: {config['host']}:{config['port']}")
        print("Presiona Ctrl+C para detener\n")

        # Contador de revoluciones procesadas (empieza en 0)
        revolution_count = 0

        # =====================================================================
        # PASO 4: Bucle Infinito de Captura (while True)
        # =====================================================================
        # Este bucle continuara hasta que:
        # - El usuario presione Ctrl+C (KeyboardInterrupt)
        # - Ocurra un error irrecuperable

        while True:
            # -----------------------------------------------------------------
            # 4.1: Obtener una Revolucion Completa
            # -----------------------------------------------------------------
            # get_scan() bloquea hasta recibir una revolucion completa (~0.1s)
            # Devuelve una lista de tuplas: [(quality, angle, distance), ...]

            scan = client.get_scan()
            revolution_count += 1

            # -----------------------------------------------------------------
            # 4.2: Filtrar Puntos Validos (distance > 0)
            # -----------------------------------------------------------------
            # Los puntos con distance=0 indican que el LIDAR no detecto
            # ningun objeto en esa direccion (fuera de rango o transparente).
            # Solo procesamos puntos con mediciones validas.

            valid = [(q, a, d) for q, a, d in scan if d > 0]

            # -----------------------------------------------------------------
            # 4.3: Calcular y Mostrar Estadisticas
            # -----------------------------------------------------------------
            # Mostramos estadisticas basicas en formato compacto (una linea)
            # para facilitar el monitoreo continuo sin saturar la terminal.

            if valid:
                # Extraer solo las distancias para calculos
                distances = [d for _, _, d in valid]

                # Calcular media aritmetica de distancias
                avg_dist = sum(distances) / len(distances)

                # Mostrar resumen en formato compacto
                print(
                    f"Rev #{revolution_count:3d}: "
                    f"Puntos={len(scan):3d} "
                    f"Validos={len(valid):3d} "
                    f"Dist.Media={avg_dist:7.1f}mm "
                    f"Min={min(distances):6.1f}mm "
                    f"Max={max(distances):7.1f}mm"
                )
            else:
                # Revolucion sin mediciones validas
                # Posibles causas: area vacia, objetos fuera de rango
                print(f"Rev #{revolution_count:3d}: Sin puntos validos")

            # -----------------------------------------------------------------
            # 4.4: Pausa Breve entre Revoluciones
            # -----------------------------------------------------------------
            # time.sleep(0.1) pausa 100ms entre revoluciones.
            #
            # Razones para la pausa:
            # 1. Evitar saturar la CPU procesando revoluciones sin parar
            # 2. Dar tiempo al sistema operativo para otras tareas
            # 3. Limitar la frecuencia de actualizacion (~10 Hz)
            # 4. Reducir carga en el servidor TCP
            #
            # Nota: El LIDAR captura a ~5-10 Hz, asi que 100ms es razonable.
            # Si necesitas maxima frecuencia, puedes reducir o eliminar el sleep.

            time.sleep(0.1)

    except KeyboardInterrupt:
        # =====================================================================
        # PASO 5: Manejo de Ctrl+C (Interrupcion por Usuario)
        # =====================================================================
        # KeyboardInterrupt se lanza cuando el usuario presiona Ctrl+C.
        # Capturamos la excepcion para desconectar limpiamente y mostrar
        # estadisticas finales antes de salir.

        print("\n\nInterrupcion detectada por usuario.")
        print(f"Total revoluciones procesadas: {revolution_count}")

    finally:
        # =====================================================================
        # PASO 6: Desconexion Limpia (Siempre se Ejecuta)
        # =====================================================================
        # El bloque finally se ejecuta SIEMPRE, incluso si hay excepciones.
        # Garantiza que la conexion TCP se cierre correctamente, liberando
        # recursos y evitando conexiones colgadas en el servidor.

        client.disconnect()
        print("Desconectado del servidor")


# =============================================================================
# EJERCICIOS SUGERIDOS PARA PRACTICAR:
# =============================================================================
#
# 1. BASICO: Modifica el codigo para mostrar tambien el numero de puntos
#    invalidos (distance=0) en cada revolucion.
#    Pista: invalid_count = len(scan) - len(valid)
#
# 2. INTERMEDIO: Añade un contador de tiempo total transcurrido usando time.time()
#    Muestra: "Tiempo total: XXs, Frecuencia promedio: YY Hz"
#    Pista: freq = revolution_count / tiempo_transcurrido
#
# 3. AVANZADO: Detecta cambios bruscos en la distancia promedio entre
#    revoluciones consecutivas (>10%). Imprime una alerta si ocurre.
#    Aplicacion: Detectar objetos que entran/salen del campo de vision.
#
# 4. INVESTIGACION: Guarda estadisticas cada 10 revoluciones en un CSV
#    Columnas: revolucion, timestamp, puntos_validos, dist_media, dist_min, dist_max
#    Analiza despues la estabilidad de las mediciones.
#
# 5. VISUALIZACION: Añade un "grafico ASCII" simple mostrando la distancia
#    promedio con caracteres (ej: barra horizontal proporcional a distancia).
#    Ejemplo: "Dist.Media: ######### 1234mm"
#
# =============================================================================

if __name__ == "__main__":
    main()
