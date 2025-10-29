# Java Project Consolidator

Herramienta en Python para consolidar proyectos Java en un único archivo Markdown, facilitando el análisis por IA o la revisión de código completa.

## Características

- **Múltiples modos de conversión:**
  - Solo archivos `.java` (código fuente únicamente)
  - Proyecto completo (incluye configuraciones, properties, gradle, maven, etc.)
  - Modo personalizado (selecciona las extensiones que necesites)

- **Interfaz amigable:**
  - Modo interactivo con menú de consola
  - Modo CLI para automatización

- **Detección inteligente:**
  - Identifica tipo de proyecto (Maven, Gradle, Ant, Simple)
  - Excluye automáticamente carpetas de build y archivos binarios
  - Opción para incluir o excluir tests

- **Formato optimizado para IA:**
  - Salida en Markdown con sintaxis resaltada
  - Metadata del proyecto incluida
  - Estructura de directorios visible
  - Estadísticas detalladas

## Requisitos

- Python 3.8 o superior
- No requiere librerías externas (solo usa la biblioteca estándar de Python)

## Instalación

1. Descarga el archivo `consolidator.py`
2. Asegúrate de tener Python instalado:
   ```bash
   python --version
   ```

## Uso

### Modo Interactivo (Recomendado)

Simplemente ejecuta el script sin argumentos:

```bash
python consolidator.py
```

El programa te guiará paso a paso:

1. Ingresa la ruta del proyecto Java (puedes arrastrar la carpeta)
2. Selecciona el modo de conversión (1, 2 o 3)
3. Decide si incluir archivos de pruebas
4. Elige el nombre del archivo de salida

### Modo CLI

Para uso avanzado o automatización:

```bash
# Solo archivos .java
python consolidator.py /ruta/al/proyecto -m 1 -o salida.md

# Proyecto completo con tests
python consolidator.py /ruta/al/proyecto -m 2 --include-tests

# Modo personalizado
python consolidator.py /ruta/al/proyecto -m 3 -e .java,.xml,.properties
```

#### Argumentos disponibles:

- `project_path`: Ruta del proyecto Java (requerido en modo CLI)
- `-m, --mode`: Modo de conversión (1, 2 o 3)
  - `1`: Solo archivos `.java`
  - `2`: Proyecto completo
  - `3`: Personalizado (requiere `-e`)
- `-o, --output`: Nombre del archivo de salida
- `--include-tests`: Incluir archivos en carpetas de test
- `-e, --extensions`: Extensiones personalizadas separadas por comas

## Modos de Conversión

### Modo 1: Solo archivos .java

Incluye únicamente el código fuente Java. Ideal para:
- Análisis de código por IA
- Revisiones de lógica de negocio
- Comprimir el proyecto al mínimo

**Extensiones incluidas:** `.java`

### Modo 2: Proyecto completo

Incluye código fuente y archivos de configuración. Ideal para:
- Análisis completo del proyecto
- Entender configuración y dependencias
- Exportar proyecto para documentación

**Extensiones incluidas:**
- `.java`, `.xml`, `.properties`
- `.yaml`, `.yml`, `.json`
- `.gradle`, `.kts` (Gradle)
- `.md`, `.txt` (documentación)
- `.sql`, `.sh`, `.bat`, `.cmd`

### Modo 3: Personalizado

Permite seleccionar exactamente qué extensiones incluir. Ideal para:
- Casos específicos
- Filtrar solo ciertos tipos de archivo
- Crear exportaciones personalizadas

## Formato del Archivo de Salida

El archivo generado incluye:

```markdown
# Proyecto Java Consolidado

**Generado:** 2025-10-28 14:30:00
**Proyecto:** MiProyecto
**Modo de conversión:** Proyecto completo

## 📋 Metadata del Proyecto
- Tipo de proyecto: Maven
- Total de archivos: 45

## 📁 Estructura de Directorios
[Árbol de directorios]

## 📄 Contenido de Archivos

### 📄 `src/main/java/com/example/Main.java`
**Líneas:** 50 | **Tipo:** .java

```java
[contenido del archivo]
```

## 📊 Estadísticas del Proyecto
- Total de archivos procesados: 45
- Total de líneas de código: 2,345
- Archivos Java: 30
- Otros archivos: 15
```

## Carpetas y Archivos Excluidos

El script automáticamente excluye:

**Carpetas:**
- `.git`, `.idea`, `.vscode`, `.settings`
- `target`, `build`, `out`, `bin`
- `node_modules`, `.gradle`, `.mvn`

**Archivos binarios:**
- `.class`, `.jar`, `.war`, `.ear`
- `.zip`, `.tar`, `.gz`
- Imágenes (`.png`, `.jpg`, etc.)
- Ejecutables (`.exe`, `.dll`, etc.)

## Ejemplos de Uso

### Ejemplo 1: Exportar solo código Java

```bash
python consolidator.py
# Seleccionar modo 1
# No incluir tests
```

### Ejemplo 2: Proyecto completo para documentación

```bash
python consolidator.py /home/user/MiProyecto -m 2 --include-tests -o documentacion.md
```

### Ejemplo 3: Solo código y configuración XML

```bash
python consolidator.py /home/user/MiProyecto -m 3 -e .java,.xml
```

## Casos de Uso

1. **Análisis por IA:** Consolidar el proyecto para subirlo a ChatGPT, Claude u otras IA
2. **Code Review:** Generar un archivo único para revisar todo el código
3. **Documentación:** Crear snapshot del proyecto en un momento específico
4. **Backup legible:** Alternativa legible a archivos ZIP
5. **Migración de código:** Facilitar la transferencia de proyectos

## Limitaciones

- El archivo de salida puede ser grande para proyectos muy extensos
- Los archivos binarios son excluidos automáticamente
- Requiere que los archivos sean legibles (texto plano)

## Solución de Problemas

### "La ruta no existe"
Verifica que la ruta sea correcta y que el directorio exista.

### "No se encontraron archivos"
- Verifica que el modo seleccionado incluya las extensiones de tu proyecto
- Usa el modo personalizado para especificar extensiones específicas

### Caracteres extraños en el output
El script intenta múltiples encodings (UTF-8, Latin-1, CP1252). Si persiste el problema, verifica el encoding de tus archivos fuente.

## Contribuciones

Sugerencias y mejoras son bienvenidas. Este es un proyecto de código abierto para la comunidad de desarrolladores.

## Licencia

MIT License - Uso libre para proyectos personales y comerciales.

## Autor

Creado para facilitar el análisis de proyectos Java por IA y herramientas de revisión de código.

---

**Versión:** 1.0.0
**Última actualización:** 2025-10-28
