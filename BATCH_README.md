# Batch Java Project Consolidator

Script para procesar automáticamente múltiples entregas de proyectos Java de alumnos.

## 📁 Estructura Requerida

```
📁 [carpeta raíz]
  📄 batch_consolidator.py
  📁 entregas/
    📁 juancruzRobledo_submit_424242/
      📄 proyecto.zip
    📁 RobertoRoch_submit_5252/
      📄 proyecto.zip
    📁 mariaGomez_submit_787878/
      📄 proyecto.zip
  📁 consolidado/  (se crea automáticamente)
    📄 juancruzRobledo_submit_424242.txt
    📄 RobertoRoch_submit_5252.txt
    📄 mariaGomez_submit_787878.txt
```

## 🚀 Uso

### 1. Preparación

Coloca el script `batch_consolidator.py` en la carpeta raíz donde trabajarás.

### 2. Estructura de entregas

Crea una carpeta `entregas/` en la misma ubicación que el script.

Dentro de `entregas/`, coloca las carpetas de cada alumno. Cada carpeta debe contener el archivo ZIP con el proyecto:

```
entregas/
  ├── alumno1_submit_123/
  │   └── proyecto.zip
  ├── alumno2_submit_456/
  │   └── proyecto.zip
  └── alumno3_submit_789/
      └── proyecto.zip
```

### 3. Ejecución

Ejecuta el script:

```bash
python batch_consolidator.py
```

### 4. Configuración interactiva (UNA SOLA VEZ)

El script te pedirá:

1. **Modo de conversión** (se aplica a TODAS las entregas):
   - `1`: Solo archivos `.java`
   - `2`: Proyecto completo (Java + configs)
   - `3`: Personalizado (tú eliges las extensiones)

2. **Incluir tests**: ¿Incluir archivos de pruebas? (s/n)

3. Si elegiste modo 3, especifica las extensiones:
   - Ejemplo: `.java,.xml,.properties`

### 5. Procesamiento automático

El script procesará automáticamente TODAS las entregas con la misma configuración:

```
📂 Procesando: juancruzRobledo_submit_424242
----------------------------------------------------------------------
   📦 Descomprimiendo: proyecto.zip
   📦 Tipo de proyecto: Maven
   ✅ Archivos encontrados: 25
   💾 Archivo generado: juancruzRobledo_submit_424242.txt
   📊 Estadísticas:
      • Archivos procesados: 25
      • Líneas totales: 1,234
      • Archivos Java: 18
      • Tamaño: 45.67 KB

📂 Procesando: RobertoRoch_submit_5252
----------------------------------------------------------------------
   📦 Descomprimiendo: proyecto.zip
   📦 Tipo de proyecto: Gradle
   ✅ Archivos encontrados: 30
   ...
```

### 6. Resultados

Los archivos consolidados se guardarán en la carpeta `consolidado/` con formato `.txt`:

```
consolidado/
  ├── juancruzRobledo_submit_424242.txt
  ├── RobertoRoch_submit_5252.txt
  └── mariaGomez_submit_787878.txt
```

## 📊 Formato de Salida

Cada archivo `.txt` contiene:

```
# Proyecto Java Consolidado

**Generado:** 2025-11-24 10:30:00
**Alumno:** juancruzRobledo_submit_424242
**Proyecto:** mi-proyecto
**Modo de conversión:** Solo archivos .java

## 📋 Metadata del Proyecto
- Tipo de proyecto: Maven
- Total de archivos: 25

## 📁 Estructura de Directorios
[árbol de directorios]

## 📄 Contenido de Archivos
[código completo de cada archivo]

## 📊 Estadísticas del Proyecto
- Total de archivos procesados: 25
- Total de líneas de código: 1,234
- Archivos Java: 18
- Otros archivos: 7
```

## ⚙️ Modos de Conversión

### Modo 1: Solo archivos .java
- Ideal para revisar solo el código fuente
- Extensiones: `.java`

### Modo 2: Proyecto completo
- Incluye código y configuraciones
- Extensiones: `.java`, `.xml`, `.properties`, `.yaml`, `.yml`, `.gradle`, `.kts`, `.md`, `.txt`, `.json`, `.sql`, `.sh`, `.bat`, `.cmd`

### Modo 3: Personalizado
- Tú eliges qué extensiones incluir
- Ejemplo: Solo `.java` y `.xml`

## 🔧 Características

✅ **Procesamiento batch**: Una sola ejecución procesa todas las entregas
✅ **Descompresión automática**: Maneja archivos ZIP automáticamente
✅ **Configuración única**: Pregunta una vez, aplica a todos
✅ **Formato TXT**: Archivos de texto plano con sintaxis Markdown
✅ **Detección de proyecto**: Identifica Maven, Gradle, Ant automáticamente
✅ **Manejo de errores**: Si una entrega falla, continúa con las demás
✅ **Estadísticas detalladas**: Resumen completo al finalizar

## ❌ Manejo de Errores

El script maneja automáticamente:

- ✅ Carpetas sin archivos ZIP → Reporta advertencia y continúa
- ✅ Múltiples ZIPs en una carpeta → Usa el primero
- ✅ Proyectos sin archivos válidos → Reporta advertencia y continúa
- ✅ Errores de descompresión → Reporta error y continúa con el siguiente
- ✅ Archivos con encoding especial → Intenta múltiples encodings

## 📝 Ejemplo de Resumen Final

```
======================================================================
  📊 RESUMEN DEL PROCESAMIENTO
======================================================================

✅ Exitosos: 8
❌ Fallidos: 2
📁 Total procesados: 10

💾 Archivos generados en: E:\ESCRITORIO\consolidado

📋 Detalle por alumno:
----------------------------------------------------------------------
✅ juancruzRobledo_submit_424242: Exitoso
✅ RobertoRoch_submit_5252: Exitoso
❌ mariaGomez_submit_787878: No se encontró ZIP
✅ carlosPeez_submit_999999: Exitoso
...

======================================================================
```

## 🛠️ Requisitos

- Python 3.8 o superior
- No requiere librerías externas (solo biblioteca estándar)

## 💡 Consejos

1. **Nombres consistentes**: Los nombres de las carpetas de alumnos se usan para los archivos de salida
2. **Un ZIP por carpeta**: Si hay múltiples ZIPs, el script usa el primero que encuentra
3. **Revisar el resumen**: Al final, revisa el resumen para ver si hubo errores
4. **Archivos grandes**: Los proyectos muy grandes generarán archivos TXT grandes

## 🆚 Diferencias con el script original

| Característica | consolidator.py | batch_consolidator.py |
|---|---|---|
| Procesamiento | Un proyecto a la vez | Múltiples proyectos |
| Entrada | Ruta manual | Carpeta /entregas/ |
| Descompresión | No | Sí (automático) |
| Salida | .md | .txt |
| Ubicación salida | Donde se especifique | /consolidado/ |
| Interacción | Por cada proyecto | Una sola vez |

## 📄 Licencia

MIT License - Uso libre para proyectos educativos y comerciales.
