# Batch Java Project Consolidator

Script para procesar automáticamente múltiples entregas de proyectos Java de alumnos con **detección inteligente de copias**.

## 🎯 Características Principales

✅ **Procesamiento batch**: Una sola ejecución procesa todas las entregas
✅ **Descompresión automática**: Maneja archivos ZIP automáticamente
✅ **Configuración única**: Pregunta una vez, aplica a todos
✅ **Detección de copias**: Identifica proyectos idénticos y copias parciales
✅ **Persistencia multi-sesión**: Compara entregas de diferentes ejecuciones
✅ **Formato TXT**: Archivos de texto plano con sintaxis Markdown
✅ **Reportes JSON**: Reportes detallados de similitud
✅ **Hashes únicos**: Cada proyecto tiene un identificador único

---

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
    📄 juancruzRobledo_submit_424242_abc12345.txt
    📄 RobertoRoch_submit_5252_def67890.txt
    📄 mariaGomez_submit_787878_ghi54321.txt
    📄 hashes_database.json           ← Base de datos persistente
    📄 reporte_similitud.json          ← Reporte de copias
```

---

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
📊 Base de datos cargada: 0 proyectos existentes

✅ Se encontraron 3 entregas para procesar

======================================================================

📂 Procesando: juancruzRobledo_submit_424242
----------------------------------------------------------------------
   📦 Descomprimiendo: proyecto.zip
   📦 Tipo de proyecto: Maven
   ✅ Archivos encontrados: 25
   🔑 Hash del proyecto: abc12345
   💾 Archivo generado: juancruzRobledo_submit_424242_abc12345.txt
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
   🔑 Hash del proyecto: def67890
   ...
```

### 6. Análisis de Similitud

Al finalizar, el script automáticamente:

1. **Guarda la base de datos** de hashes en `hashes_database.json`
2. **Genera reporte** de similitudes en `reporte_similitud.json`
3. **Muestra resumen** en consola con:
   - Proyectos 100% idénticos
   - Copias parciales (≥50% similitud)
   - Archivos más copiados

```
======================================================================
  🔍 ANÁLISIS DE SIMILITUD (3 proyectos en total)
======================================================================

⚠️  PROYECTOS IDÉNTICOS (100%):
----------------------------------------------------------------------
  Grupo 1: juan_submit_1, maria_submit_2
    • Hash: abc12345
    • Archivos: 18 idénticos
    • Líneas: 1,234

⚠️  COPIAS PARCIALES (≥50% similitud):
----------------------------------------------------------------------
  pedro_submit_3 ↔ ana_submit_4
    • Similitud: 67%
    • Archivos copiados: 6
    • Archivos: Main.java, Usuario.java, Conexion.java...

📋 ARCHIVOS MÁS COPIADOS (Top 5):
----------------------------------------------------------------------
  1. Main.java
     • Aparece en 4 proyectos
     • Alumnos: juan_submit_1, maria_submit_2, pedro_submit_3

📋 Reporte detallado guardado en: reporte_similitud.json
📋 Base de datos actualizada: hashes_database.json

======================================================================
```

---

## 🔍 Detección de Copias

### Cómo Funciona

El sistema utiliza **hashes criptográficos SHA256** para identificar copias:

#### 1. **Hash por archivo individual**
- Cada archivo `.java` tiene un hash único
- Se normaliza el contenido (se eliminan espacios en blanco)
- Permite detectar archivos idénticos incluso con nombres diferentes

#### 2. **Hash del proyecto completo**
- Hash de todos los archivos `.java` concatenados
- Detecta proyectos 100% idénticos instantáneamente

#### 3. **Análisis de similitud**
- **Copias totales**: Mismo hash de proyecto (100% idénticos)
- **Copias parciales**: Al menos 3 archivos `.java` idénticos
- **Porcentaje de similitud**: `(archivos_comunes / min(archivos_A, archivos_B)) * 100`

### Base de Datos Persistente

El archivo `hashes_database.json` almacena:

```json
{
  "version": "1.0",
  "ultima_actualizacion": "2025-11-26 14:30:00",
  "total_proyectos": 100,
  "proyectos": {
    "juan_submit_123": {
      "fecha_procesado": "2025-11-26 10:00:00",
      "hash_proyecto": "abc123def456...",
      "archivos": {
        "Main.java": "hash1...",
        "Usuario.java": "hash2...",
        "Conexion.java": "hash3..."
      },
      "total_archivos": 15,
      "total_lineas": 1234
    }
  }
}
```

### Reporte de Similitud

El archivo `reporte_similitud.json` contiene:

```json
{
  "generado": "2025-11-26 14:30:00",
  "total_proyectos_analizados": 100,
  "total_grupos_identicos": 2,
  "total_copias_parciales": 5,

  "proyectos_identicos": [
    {
      "hash_proyecto": "abc123...",
      "alumnos": ["juan_submit_1", "maria_submit_2"],
      "porcentaje_similitud": 100,
      "archivos_identicos": 18,
      "total_lineas": 1234
    }
  ],

  "copias_parciales": [
    {
      "alumnos": ["pedro_submit_3", "ana_submit_4"],
      "archivos_copiados": [
        {"nombre": "Main.java", "hash": "def456..."},
        {"nombre": "Usuario.java", "hash": "ghi789..."}
      ],
      "porcentaje_similitud": 67.0,
      "total_archivos_comunes": 6
    }
  ],

  "archivos_mas_copiados": [
    {
      "archivo": "Main.java",
      "hash": "def456...",
      "aparece_en": ["juan_submit_1", "maria_submit_2", "pedro_submit_3"],
      "total_copias": 3
    }
  ]
}
```

---

## 🔄 Análisis Multi-Sesión

### Caso de Uso: Múltiples Grupos de Alumnos

El sistema permite analizar entregas de **diferentes ejecuciones**:

#### **Sesión 1:** Procesar 50 alumnos del Grupo A (Lunes)

```bash
python batch_consolidator.py
# Procesa 50 entregas
# Crea hashes_database.json con 50 proyectos
# Detecta copias entre esos 50
```

#### **Sesión 2:** Procesar 50 alumnos del Grupo B (Martes)

```bash
python batch_consolidator.py
# Carga hashes_database.json existente (50 proyectos)
# Procesa 50 entregas nuevas
# Actualiza la base de datos a 100 proyectos
# ✨ Detecta copias entre TODOS los 100 proyectos
```

#### **Resultado:**

- Detecta si un alumno del Grupo A copió de uno del Grupo B
- Compara entregas de diferentes días/sesiones
- Mantiene historial completo de todas las entregas

### Ventajas del Sistema Multi-Sesión

✅ **Análisis acumulativo**: Cada ejecución suma a la base de datos
✅ **Detección cross-grupo**: Identifica copias entre grupos diferentes
✅ **Persistencia**: Los datos se mantienen entre ejecuciones
✅ **Escalabilidad**: Puedes procesar 10, 50, 100+ proyectos sin límite
✅ **Evidencia histórica**: Fecha de procesamiento de cada proyecto

---

## 📊 Formato de Salida

### Archivos Consolidados

Cada archivo `.txt` tiene el formato: `alumno_hashXXXX.txt`

**Ejemplo:** `juancruzRobledo_submit_424242_abc12345.txt`

Contenido:

```
# Proyecto Java Consolidado

**Generado:** 2025-11-26 10:30:00
**Alumno:** juancruzRobledo_submit_424242
**Proyecto:** mi-proyecto
**Modo de conversión:** Solo archivos .java
**Hash del proyecto:** `abc123def456...`

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

### Archivos Generados en `/consolidado/`

```
consolidado/
  ├── alumno1_submit_123_a1b2c3d4.txt      ← Proyecto consolidado
  ├── alumno2_submit_456_e5f6g7h8.txt      ← Proyecto consolidado
  ├── alumno3_submit_789_i9j0k1l2.txt      ← Proyecto consolidado
  ├── hashes_database.json                  ← Base de datos de hashes
  └── reporte_similitud.json                ← Reporte de similitudes
```

---

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

---

## 📈 Interpretación de Reportes

### Proyectos Idénticos (100%)

**Indicador:** Hash de proyecto idéntico

**Significado:**
- Todos los archivos `.java` son exactamente iguales
- Muy alta probabilidad de copia directa
- Acción recomendada: Confrontar a los alumnos

### Copias Parciales (≥50%)

**Indicador:** 3+ archivos `.java` idénticos

**Significado:**
- Algunos archivos fueron copiados
- Pueden haber modificado otros archivos
- Revisar los archivos específicos copiados

**Ejemplo:**
```
pedro_submit_3 ↔ ana_submit_4
  • Similitud: 67%
  • Archivos copiados: 6/9
  • Main.java, Usuario.java, Conexion.java...
```

### Archivos Más Copiados

**Indicador:** Mismo archivo aparece en 3+ proyectos

**Significado:**
- Archivos "plantilla" que circularon entre alumnos
- Puede indicar colaboración no permitida
- Útil para identificar "fuentes" de copia

---

## ❌ Manejo de Errores

El script maneja automáticamente:

- ✅ Carpetas sin archivos ZIP → Reporta advertencia y continúa
- ✅ Múltiples ZIPs en una carpeta → Usa el primero
- ✅ Proyectos sin archivos `.java` → Reporta advertencia y continúa
- ✅ Errores de descompresión → Reporta error y continúa con el siguiente
- ✅ Archivos con encoding especial → Intenta múltiples encodings
- ✅ Base de datos corrupta → Crea una nueva

---

## 🛠️ Requisitos

- Python 3.8 o superior
- No requiere librerías externas (solo biblioteca estándar)

---

## 💡 Consejos y Mejores Prácticas

### Para Profesores

1. **Nombres consistentes**: Los nombres de las carpetas de alumnos se usan para identificación
2. **Un ZIP por carpeta**: Si hay múltiples ZIPs, el script usa el primero
3. **Revisar el reporte JSON**: Contiene más detalles que el resumen en consola
4. **Preservar la base de datos**: No elimines `hashes_database.json` entre sesiones
5. **Backups**: Respalda la carpeta `/consolidado/` periódicamente

### Para Análisis Forense

1. **Fecha de procesamiento**: Cada proyecto tiene timestamp en la base de datos
2. **Hashes como evidencia**: Los hashes son prueba criptográfica de identidad
3. **Revisar "archivos_mas_copiados"**: Identifica patrones de colaboración
4. **Comparar nombres de archivos**: Archivos idénticos con nombres diferentes son sospechosos

### Limitar Falsos Positivos

- **Código muy simple** (< 5 líneas) puede ser idéntico sin copia
- **Código de ejemplo** del profesor puede aparecer como copiado
- **Librerías estándar**: Excluir carpetas como `/lib/` si es necesario

---

## 🔧 Solución de Problemas

### "No se encontró archivo ZIP"
**Causa:** La carpeta del alumno no contiene un archivo `.zip`
**Solución:** Verifica que cada carpeta en `/entregas/` tenga un archivo ZIP

### "No se encontraron archivos .java"
**Causa:** El proyecto no contiene archivos Java o están en carpetas excluidas
**Solución:** Verifica que el ZIP contenga archivos `.java` válidos

### "Base de datos corrupta"
**Causa:** El archivo `hashes_database.json` está dañado
**Solución:** El script automáticamente crea uno nuevo. Si quieres preservar datos, restaura un backup

### "Reporte vacío de similitudes"
**Causa:** Solo hay 1 proyecto procesado, o todos son únicos
**Solución:** Normal si es la primera entrega. Las similitudes aparecen con 2+ proyectos

---

## 🆚 Diferencias con el Script Original

| Característica | consolidator.py | batch_consolidator.py |
|---|---|---|
| Procesamiento | Un proyecto a la vez | Múltiples proyectos |
| Entrada | Ruta manual | Carpeta /entregas/ |
| Descompresión | No | Sí (automático) |
| Salida | .md | .txt con hash |
| Ubicación salida | Donde se especifique | /consolidado/ |
| Interacción | Por cada proyecto | Una sola vez |
| **Detección de copias** | ❌ No | ✅ Sí |
| **Base de datos persistente** | ❌ No | ✅ Sí |
| **Análisis multi-sesión** | ❌ No | ✅ Sí |
| **Reportes JSON** | ❌ No | ✅ Sí |
| **Hash en nombre** | ❌ No | ✅ Sí |

---

## 📝 Ejemplos de Uso

### Ejemplo 1: Primera Ejecución (Grupo A - 30 alumnos)

```bash
$ python batch_consolidator.py

Modo: 1 (Solo .java)
Tests: No

✅ Procesados: 30 exitosos
📊 Base de datos: 30 proyectos

🔍 ANÁLISIS:
✅ No se detectaron copias
```

### Ejemplo 2: Segunda Ejecución (Grupo B - 30 alumnos)

```bash
$ python batch_consolidator.py

📊 Base de datos cargada: 30 proyectos existentes

Modo: 1 (Solo .java)
Tests: No

✅ Procesados: 30 exitosos
📊 Base de datos: 60 proyectos

🔍 ANÁLISIS:
⚠️  PROYECTOS IDÉNTICOS: 2 grupos
  - juan_submit_1 (Grupo A) ↔ pedro_submit_45 (Grupo B)
  - maria_submit_12 (Grupo A) ↔ ana_submit_50 (Grupo B)
```

### Ejemplo 3: Análisis con Copias Parciales

```bash
🔍 ANÁLISIS:
⚠️  COPIAS PARCIALES:
  luis_submit_20 ↔ carlos_submit_35
    • Similitud: 78%
    • 7 de 9 archivos idénticos
    • Main.java, Producto.java, Cliente.java...
```

---

## 📄 Licencia

MIT License - Uso libre para proyectos educativos y comerciales.

---

## 🤝 Contribuciones

Sugerencias y mejoras son bienvenidas en:
- Detección más sofisticada de similitud
- Exportación de reportes a Excel
- Interfaz web para visualizar copias
- Análisis de similitud semántica (no solo exacta)

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisa la sección "Solución de Problemas"
2. Verifica que Python ≥ 3.8 esté instalado
3. Asegúrate que la estructura de carpetas sea correcta
4. Revisa los archivos JSON generados para más detalles

---

**Versión:** 2.0.0 (con detección de copias)
**Última actualización:** 2025-11-26
