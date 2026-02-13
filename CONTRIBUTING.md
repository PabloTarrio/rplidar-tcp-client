# Guía de Contribución

¡Gracias por tu interés en contribuir a `rplidar-tcp-client`! 

Este proyecto está diseñado para ser accesible a estudiantes e investigadores. Toda contribución es bienvenida, desde correcciones de documentación hasta nuevas funcionalidades.

---

## Cómo Empezar

### 1. Fork y Clonación

```bash
# Fork el repositorio en GitHub (botón "Fork")
# Luego clona tu fork:
git clone https://github.com/TU-USUARIO/rplidar-tcp-client.git
cd rplidar-tcp-client
```

### 2. Configurar el Entorno de Desarrollo

```bash
# Fork el repositorio en gitHub (botón "Fork")
# Luego clona tu fork:
git clone https://https://github.com/TU-USUARIO/rplidar-tcp-client.git
cd rplidar-tcp-client
```

### 3. Configurar Entorno de Desarrollo

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate

# Instalar en modo desarrollo
pip install -e .

# Instalar herramientas de desarollo
pip install pytest ruff
```

### 4. Verificar que todo funciona

```bash
# Ejecutar tests
python tests/

# Ejecutar linting
ruff check .
```

## Workflow de Desarrollo

### Estructura de Branches

Usamos Conventional Commits para branches y commits:
```bash
# Para nuevas funcionalidades
git checkout -b feat/nombre-descriptivo

# Para correcciones de bugs
git checkout -b fix/descripcion-del-bug

# Para documentación
git checkout -b docs/tema-documentacion

# Para refactorización
git checkout -b refactor/area-refactorizada
```

Ejemplos:
```text
feat/add-distance-filter
fix/timeout-handling
docs/update-quickstart
refactor/client-error-handling
```

### Conveciones de commits
Seguimos [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/):
```text
<tipo>: <descripción corta>
<descripción detallada opcional>
```

Tipos principales:

* feat: Nueva funcionalidad
* fix: Correción de bug
* docs: Cambios en documentación
* test: Añadir o modificar test
* refactor: Cambios de código sin afectar funcionalidad
* style: Formato, linting (sin cambios de lógica)
* chore: Tareas de mantenimiento (dependencias, config)

Ejemplos:

```bash
git commit -m "feat: Add filter_by_distance method to LidarClient"
git commit -m "docs: Update Quick Start with config.ini example"
git commit -m "fix: Handle quality=None in Express mode correctly"
```

## Checklist antes de Pull Request

Antes de crear un Pull Request (PR), verifica:

* [ ] Test pasan: `pytest test/ -v`

* [ ] Linting limpio: `ruff check .`

* [ ] Formato correcto: `ruff format .`

* [ ] Cobertura mantenida: Idealmente >80%

* [ ] Documentación actualizada: README, docstrings, ejemplos

* [ ] Coomits siguen convenciones: Conventional Commits

* [ ] Branch actualizado con main: `git rebase main` si es necesario

## Ejecutar test

```bash
# Todos los tests
pytest tests/ -v

# Tests con cobertura
pytest tests/ --cov=src/lidar_client --cov-report=term-missing

# Test específico
pytest tests/test_client.py::TestLidarClient::test_connect_success -v
```

## Estilo de código

### Python Style Guide

* Seguimos PEP 8
* Usamos ruff para linting y formateo
* Máximo 88 caracteres por linea (Black style)
* Type hints recomendados para funciones públicas

#### Ejecutar Linting

```bash
# Verificar errores
ruff check .

# Autoformatear código
ruff format .

# Verificar un archivo específico
ruff check src/lidar_client/client.py
```

#### Docstrings

Usamos formato Google Style:
```python
def filter_by_distance(scan, min_dist=0, max_dist=float('inf')):
    """
    Filtra puntos por rango de distancia.
    
    Args:
        scan: Lista de tuplas (quality, angle, distance)
        min_dist: Distancia mínima en mm (default: 0)
        max_dist: Distancia máxima en mm (default: infinito)
    
    Returns:
        Lista filtrada de tuplas
    
    Raises:
        ValueError: Si min_dist > max_dist
    
    Example:
        >>> scan = [(15, 90.0, 1500), (14, 180.0, 3000)]
        >>> filtered = filter_by_distance(scan, 1000, 2000)
        >>> len(filtered)
        1
    """
```

## Tipos de contribución

### 1. Reportar Bugs

#### Abre un Issue con:

* Descripción clara del problema
* Pasos para reproducir
* Comportamiento esperado vs actual
* Versión de Python, SO, logs relevantes

### 2. Sugerir funcionalidades

#### Abre un Issue con:

* Descripción de la funcionalidad
* Cada de uso (¿Por qué es útil?)
* Ejeplo de API propuesta (si aplica)

### 3. Mejorar documentación

* Corregir typos, errores
* Añadir ejemplos prácticos
* Mejorar claridad de explicaciones
* Traducir documentación (futuro)

### 4. Contribuir con código

* Escoge un Issue o una funcionalidad
* Comenta en el Issue que trabajarás en ello
* Sigue el workflow de desarrollo
* Crea PR con descripción clara

## Proceso de Pull Request

### 1. Preparar tu Branch
```bash
# Asegúrate de estar actualizado con main
git checkout main
git pull upstream main  # Si configuraste upstream

# Vuelve a tu branch y rebase si es necesario
git checkout feat/tu-funcionalidad
git rebase main
```

### 2. Crear Pull Request

#### En GitHub:
* Crea PR desde tu branch hacia `main`
* Título: Sigue Conventional Commits (ej: `feat: Add obstacle detection example`)
* Descripción: Explica qué, por qué y cómo
* Enlaza Issues relacionados (`Closes #123`)

### 3. Review y Aprobación

* Los checks de CI deben pasar (tests, linting)
* Un mantenedor revisará tu código
* Responde a comentarios y haz ajustes si se solicitan
* Una vez aprobado, el mantenedor hará merge.

## Para estudiantes

### Primeras contribuciones

Si es tu primera contribución considera:

* Documentación: Corregir typos, mejorar ejemplos.
* Tests: Añadir tests para funcionalidad existente
* Ejemplos: Crear scripts de ejemplo para casos de uso
* Issues etiquetados: Busca issues con `good first issue`

### Proyectos de investigación

Si usas esta librería en tu TFG/TFM:

* Comparte tus scripts de ejemplo (anonimiza datos si es necesario)
* Documenta tu caso de uso en la Wiki.
* Contribuye funcionalidades que necesitaste

## Contacto y soporte

* Issues: Pra bugs, sugerencias, preguntas técnicas
* Dicussions: Para preguntas generales, casos de uso
* Email: [Laboratorio UIE - Coruña](mailto:pablo.tarrio@uie.edu) para temas privados.

## Licencia

Al contribuir aceptas que tus contribuciones se licencien bajo la licencia MIT del Proyecto.

¡Gracias por hacer `rplidar-tcp-client` mejor!