"""
=============================================================================
EJEMPLO 6: Diagnostico y Comparacion de Modos de Escaneo
=============================================================================

OBJETIVO:
    Herramienta de diagnostico que analiza el rendimiento del LIDAR capturando
    multiples revoluciones y mostrando estadisticas detalladas del modo de
    escaneo configurado (Standard o Express).

REQUISITOS PREVIOS:
    - Haber completado los ejemplos basicos
    - Entender la diferencia entre modo Standard y Express
    - Conocer conceptos de estadisticas basicas (promedio, porcentaje)

CONCEPTOS QUE APRENDERAS:
    - Diferencias practicas entre Standard Scan y Express Scan
    - Como medir rendimiento del LIDAR (frecuencia, densidad)
    - Por que la primera revolucion siempre tarda mas (warmup)
    - Calcular cobertura angular y densidad de puntos
    - Promediar multiples mediciones para mayor precision

CASOS DE USO PRACTICOS:
    - Verificar que el LIDAR funciona correctamente
    - Comparar rendimiento entre modos de escaneo
    - Diagnosticar problemas de cobertura o densidad
    - Validar configuracion antes de usar en produccion
    - Educacion: entender especificaciones del sensor

ESPECIFICACIONES RPLIDAR A1:
    - Standard Scan: ~360 puntos/revolucion, incluye calidad
    - Express Scan: ~720 puntos/revolucion, sin calidad
    - Velocidad: 5-10 Hz (revoluciones por segundo)
    - Rango: 0.15m - 12m

TIEMPO ESTIMADO: 20 minutos
=============================================================================
"""

import time

from lidarclient import ConfigError, LidarClient, load_config


def analyze_scan(scan, mode_name):
    """
    Analiza una revolucion y muestra estadisticas detalladas.

    Esta funcion calcula metricas clave del escaneo LIDAR para evaluar
    su calidad y rendimiento, incluyendo:
    - Numero total de puntos y porcentaje de puntos validos
    - Calidad promedio (solo en modo Standard)
    - Cobertura angular (deberia estar cerca de 360 grados)
    - Rango de distancias detectadas
    - Densidad de puntos por grado

    Args:
        scan: Lista de tuplas (quality, angle, distance)
              - quality: int 0-15 (Standard) o None (Express)
              - angle: float 0-360 grados
              - distance: float en milimetros (0 = invalido)
        mode_name: String descriptivo para el titulo (ej: "Revolucion #1")

    Muestra:
        Reporte formateado con todas las estadisticas calculadas
    """

    # =========================================================================
    # PASO 1: Contar Puntos Totales y Validos
    # =========================================================================
    # Total de puntos: todos los elementos en el scan
    # Puntos validos: solo aquellos con distance > 0 (objeto detectado)

    total_points = len(scan)
    valid_points = sum(1 for _, _, d in scan if d > 0)

    # =========================================================================
    # PASO 2: Verificar si Hay Datos Validos para Analizar
    # =========================================================================
    # Si no hay puntos validos, no podemos calcular estadisticas.
    # Posibles causas: area vacia, sensor desconectado, error temporal.

    if valid_points > 0:
        # =====================================================================
        # PASO 3: Extraer Datos de Puntos Validos
        # =====================================================================
        # Separamos quality, distances y angles para calculos independientes.
        # Filtramos solo puntos con d > 0 para evitar datos invalidos.

        # Quality: puede ser None en Express, asi que filtramos None tambien
        qualities = [q for q, _, d in scan if d > 0 and q is not None]

        # Distances: en milimetros
        distances = [d for _, _, d in scan if d > 0]

        # Angles: en grados (0-360)
        angles = [a for _, a, d in scan if d > 0]

        # Porcentaje de puntos validos vs totales
        valid_pct = valid_points / total_points * 100

        # =====================================================================
        # PASO 4: Calcular Calidad Promedio (Solo Standard Mode)
        # =====================================================================
        # En modo Express, quality es None para todos los puntos.
        # Solo calculamos promedio si hay datos de calidad disponibles.
        #
        # Calidad en Standard: 0 (baja confianza) a 15 (maxima confianza)

        if qualities:
            avg_quality = sum(qualities) / len(qualities)
        else:
            # Modo Express o datos sin calidad
            avg_quality = None

        # =====================================================================
        # PASO 5: Calcular Cobertura Angular
        # =====================================================================
        # La cobertura angular indica que rango de angulos fue escaneado.
        # Idealmente deberia ser ~360 grados (revolucion completa).
        #
        # Si es menor, puede indicar:
        # - Sincronizacion incompleta
        # - Revolucion parcial
        # - Problema con el motor del LIDAR

        min_angle = min(angles)
        max_angle = max(angles)
        angular_coverage = max_angle - min_angle

        # =====================================================================
        # PASO 6: Calcular Densidad de Puntos
        # =====================================================================
        # Densidad = puntos por grado de rotacion
        # Util para comparar Standard (~1 punto/grado) vs Express (~2 puntos/grado)
        #
        # Mayor densidad = mayor resolucion angular = mejor deteccion de objetos
        #       pequeños

        density = valid_points / angular_coverage if angular_coverage > 0 else 0

        # =====================================================================
        # PASO 7: Mostrar Reporte Formateado
        # =====================================================================

        print(f"\n{'=' * 60}")
        print(f"   {mode_name}")
        print(f"{'=' * 60}")
        print(f" Total de puntos:    {total_points}")
        print(f" Puntos validos:     {valid_points} ({valid_pct:.1f}%)")

        # Mostrar calidad solo si esta disponible (Standard mode)
        if avg_quality is not None:
            print(f" Calidad promedio:   {avg_quality:.2f} / 15")
        else:
            print(" Calidad promedio:   No disponible (modo Express)")

        print(f" Cobertura angular:  {angular_coverage:.1f}")
        print(f" Distancia minima:   {min(distances):.1f} mm")
        print(f" Distancia maxima:   {max(distances):.1f} mm")
        print(f" Densidad:           {density:.2f} puntos/grado")
        print(f"{'=' * 60}")

    else:
        # Sin puntos validos en este scan
        print(f"\n{mode_name}: Sin datos validos")
        print("  Posibles causas:")
        print("    - Area completamente vacia")
        print("    - Objetos fuera del rango del sensor (>12m)")
        print("    - Problema de conexion temporal")


def main():
    """
    Funcion principal que ejecuta el diagnostico completo del LIDAR.

    Flujo del diagnostico:
        1. Cargar configuracion y conectar al servidor
        2. Descartar primera revolucion (warmup del sistema)
        3. Capturar 3 revoluciones cronometradas
        4. Analizar cada revolucion individualmente
        5. Calcular y mostrar promedios
        6. Mostrar informacion sobre modos de escaneo

    Nota sobre warmup:
        La primera revolucion tras conectar siempre tarda mas (~1 segundo)
        debido a la sincronizacion inicial entre servidor y sensor LIDAR.
        Este script la descarta automaticamente para obtener mediciones reales.
    """

    print("\n" + "=" * 60)
    print("   COMPARACION DE MODOS DE ESCANEO RPLIDAR A1")
    print("=" * 60)

    # =========================================================================
    # PASO 1: Cargar Configuracion
    # =========================================================================
    try:
        config = load_config()
    except ConfigError as e:
        print(f" Error de configuracion: {e}")
        return

    # =========================================================================
    # PASO 2: Crear Cliente LIDAR
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
        # PASO 3: Conectar al Servidor
        # =====================================================================
        print(f"\nConectando a {config['host']}:{config['port']}")
        client.connect()
        print("Conectado\n")

        # =====================================================================
        # PASO 4: Descartar Primera Revolucion (Warmup)
        # =====================================================================
        # IMPORTANTE: La primera revolucion siempre tarda significativamente
        # mas (~1 segundo) debido a la sincronizacion inicial del sistema:
        # 1. El servidor debe establecer comunicacion con el LIDAR via USB
        # 2. El motor del LIDAR debe estabilizarse
        # 3. Buffers de red deben llenarse
        #
        # Descartamos esta revolucion para obtener mediciones representativas
        # del rendimiento real del sistema.

        print("Descartando primera revolucion (warmup)...")
        _ = client.get_scan()
        print("Warmup completado\n")

        # =====================================================================
        # PASO 5: Capturar 3 Revoluciones para Analisis
        # =====================================================================
        # Capturamos multiples revoluciones (3) para:
        # - Calcular promedios mas precisos
        # - Detectar variaciones entre revoluciones
        # - Validar estabilidad del sistema
        #
        # Cronometramos cada revolucion para calcular frecuencia real.

        print("Capturando 3 revoluciones para analisis...")

        scans = []
        for i in range(3):
            # Usar \r para sobrescribir la linea (progreso en misma linea)
            print(f"   Revolucion {i + 1}/3...", end="\r")

            # Cronometrar tiempo de captura
            start_time = time.time()
            scan = client.get_scan()
            elapsed = time.time() - start_time

            # Guardar scan y tiempo transcurrido
            scans.append((scan, elapsed))

        print("\n")

        # =====================================================================
        # PASO 6: Analizar Cada Revolucion Individualmente
        # =====================================================================
        # Mostramos estadisticas detalladas de cada revolucion para poder
        # comparar y detectar anomalias o variaciones.

        for idx, (scan, elapsed) in enumerate(scans, 1):
            analyze_scan(scan, f"Revolucion #{idx} (Tiempo: {elapsed:.3f}s)")

        # =====================================================================
        # PASO 7: Calcular Promedios de las 3 Revoluciones
        # =====================================================================
        # Los promedios dan una vision mas precisa del rendimiento tipico.

        avg_points = sum(len(s) for s, _ in scans) / len(scans)
        avg_valid = sum(sum(1 for _, _, d in s if d > 0) for s, _ in scans) / len(scans)
        avg_time = sum(t for _, t in scans) / len(scans)

        # Frecuencia en Hz (revoluciones por segundo)
        frequency = 1 / avg_time if avg_time > 0 else 0

        print(f"\n{'=' * 60}")
        print("  PROMEDIOS DE 3 REVOLUCIONES")
        print(f"{'=' * 60}")
        print(f"  Puntos promedio:      {avg_points:.1f}")
        print(f"  Validos promedio:     {avg_valid:.1f}")
        print(f"  Tiempo promedio:      {avg_time:.3f}s")
        print(f"  Frecuencia:           {frequency:.2f} Hz")
        print(f"{'=' * 60}\n")

        # =====================================================================
        # PASO 8: Informacion Educativa sobre Modos de Escaneo
        # =====================================================================

        print("\nINFORMACION SOBRE MODOS DE ESCANEO:")
        print("\n   El servidor actual usa el modo configurado en config.ini.")
        print("   Puedes cambiar entre 'Standard' y 'Express' editando scan_mode.")

        print("\nNOTA SOBRE LA PRIMERA REVOLUCION:")
        print("   La primera revolucion tras conectar siempre tarda mas (~1s).")
        print("   Esto es normal: el sistema se sincroniza con el LIDAR.")
        print("   Este script descarta automaticamente esa primera revolucion.")

        print("\nRPLIDAR A1 ESPECIFICACIONES TIPICAS:")
        print("  - Standard Scan:  ~360 muestras/revolucion, incluye calidad")
        print("  - Express Scan:   ~720 muestras/revolucion, sin calidad")
        print("  - Velocidad:      5-10 Hz (revoluciones/segundo)")
        print("  - Rango:          0.15m - 12m")
        print("  - Precision:      <1% del rango medido")

        print("\nCOMPARACION DE MODOS:")
        print("  Standard: Menor densidad pero incluye datos de calidad")
        print("            Util para filtrar mediciones ruidosas")
        print("  Express:  Mayor densidad (2x) sin datos de calidad")
        print("            Util para maxima resolucion angular")

    except KeyboardInterrupt:
        print("\n\nInterrupcion detectada")

    except Exception as e:
        print(f"\nError: {e}")
        print("\nSoluciones posibles:")
        print("  - Verifica que el servidor LIDAR esta corriendo")
        print("  - Verifica la conexion de red al servidor")
        print("  - Aumenta el timeout en config.ini si la red es lenta")

    finally:
        client.disconnect()
        print("\nAnalisis finalizado\n")


# =============================================================================
# EJERCICIOS SUGERIDOS PARA PRACTICAR:
# =============================================================================
#
# 1. BASICO: Modifica el script para capturar 10 revoluciones en lugar de 3.
#    Observa si los promedios son mas estables con mas muestras.
#
# 2. INTERMEDIO: Añade calculo de desviacion estandar del numero de puntos
#    entre revoluciones. Formula: sqrt(sum((x - media)^2) / n)
#    Una desviacion alta indica variabilidad en el rendimiento.
#
# 3. AVANZADO: Ejecuta este script dos veces: una con scan_mode=Standard
#    y otra con scan_mode=Express. Guarda los resultados en archivos CSV
#    y compara graficamente la densidad y cobertura.
#
# 4. INVESTIGACION: Añade medicion de "jitter" (variacion en tiempo entre
#    revoluciones). Calcula la diferencia entre tiempo maximo y minimo.
#    Jitter alto puede indicar problemas de red o CPU.
#
# 5. DIAGNOSTICO AVANZADO: Crea un modo "stress test" que capture 100
#    revoluciones continuas y detecte:
#    - Perdidas de conexion
#    - Revoluciones con <50% de puntos validos
#    - Degradacion de rendimiento con el tiempo
#
# =============================================================================

if __name__ == "__main__":
    main()
