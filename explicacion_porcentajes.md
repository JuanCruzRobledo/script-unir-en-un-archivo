# 📊 Explicación: ¿Por qué cada caso tiene un porcentaje diferente?

## 🎯 Respuesta Corta
**Cada par de estudiantes tiene diferente cantidad de archivos compartidos**, por eso cada caso tiene su propio porcentaje de similitud.

---

## 📐 Fórmula Utilizada

```
Porcentaje de Similitud = (Archivos Compartidos / Total Mínimo) × 100

Donde:
- Archivos Compartidos = número de archivos con el mismo hash
- Total Mínimo = mínimo entre archivos de A y archivos de B
```

---

## 🔍 Ejemplos Visuales

### Ejemplo 1: Ariel vs Enzo = **100% similitud**

```
Ariel:  [A1] [A2] [A3] [A4] [A5] ... [A16]  (16 archivos)
Enzo:   [A1] [A2] [A3] [A4] [A5] ... [A16]  (16 archivos)
         ✓    ✓    ✓    ✓    ✓   ...   ✓

Compartidos: 16 de 16
Cálculo: 16 / min(16, 16) × 100 = 16/16 × 100 = 100%
```

**Resultado**: Todos los archivos son idénticos = **100%**

---

### Ejemplo 2: Celeste vs Florencia = **73.7% similitud**

```
Celeste:   [C1] [C2] [C3] [C4] [C5] ... [C14] [C15] [C16] [C17] [C18] [C19]
Florencia: [F1] [F2] [F3] [F4] [F5] ... [F14] [F15] [F16] [F17] [F18] [F19]
            ✓    ✓    ✓    ✓    ✓   ...   ✓     ✗     ✗     ✗     ✗     ✗

Compartidos: 14 de 19
No compartidos: 5 archivos únicos en cada uno

Cálculo: 14 / min(19, 19) × 100 = 14/19 × 100 = 73.7%
```

**Resultado**: 14 archivos iguales, 5 diferentes = **73.7%**

---

### Ejemplo 3: Ariel vs Iván = **62.5% similitud**

```
Ariel: [A1] [A2] [A3] [A4] [A5] ... [A10] [A11] [A12] [A13] [A14] [A15] [A16]
Iván:  [I1] [I2] [I3] [I4] [I5] ... [I10] [I11] [I12] [I13] [I14] [I15] [I16]
        ✓    ✓    ✓    ✓    ✓   ...   ✓     ✗     ✗     ✗     ✗     ✗     ✗

Compartidos: 10 de 16
No compartidos: 6 archivos diferentes en cada uno

Cálculo: 10 / min(16, 16) × 100 = 10/16 × 100 = 62.5%
```

**Resultado**: 10 archivos iguales, 6 diferentes = **62.5%**

---

## 🤔 Entonces, ¿por qué hay 19 casos con >50% pero todos tienen % diferente?

Porque **cada pareja de estudiantes compartió una cantidad diferente de archivos**:

| Caso | Estudiantes | Archivos Compartidos | Total | Porcentaje |
|------|-------------|---------------------|-------|------------|
| 1 | Ariel vs Enzo | 16 de 16 | 16 | **100.0%** |
| 2 | Ariel vs Franco | 16 de 16 | 16 | **100.0%** |
| 3 | Celeste vs Florencia | 14 de 19 | 19 | **73.7%** |
| 4 | Ariel vs Iván | 10 de 16 | 16 | **62.5%** |
| 5 | Facundo vs Nicolas | 12 de 19 | 19 | **63.2%** |
| ... | ... | ... | ... | ... |

---

## 📈 Casos Especiales

### ¿Por qué hay varios casos con 100%?

Hay **8 casos con 100%** porque hay múltiples pares de estudiantes donde **todos los archivos son idénticos**:

```
- Ariel vs Enzo        → 16/16 = 100%
- Ariel vs Franco      → 16/16 = 100%
- Ariel vs Luciano     → 16/16 = 100%
- Ariel vs Nicolas     → 16/16 = 100%
- atias vs Macarena    → 18/18 = 100%
- Carolina vs Valentina → 18/18 = 100%
...
```

Esto indica que **Ariel compartió su código con Enzo, Franco, Luciano y Nicolas** (probablemente todos copiaron del mismo proyecto).

---

### ¿Estudiantes con diferentes cantidades de archivos?

**Sí, también pasa**. Ejemplo:

```
Estudiante A: 20 archivos
Estudiante B: 15 archivos
Compartidos:  10 archivos

Porcentaje = 10 / min(20, 15) × 100 = 10/15 × 100 = 66.7%
```

Usamos el **mínimo** porque queremos saber "¿qué porcentaje del proyecto más pequeño está copiado?"

---

## 💡 Conclusión

**Cada caso tiene un % diferente porque:**

1. ✅ Cada par de estudiantes tiene **diferente cantidad de archivos totales**
2. ✅ Cada par compartió **diferente cantidad de archivos**
3. ✅ La fórmula calcula el porcentaje basándose en estos dos números

**Es completamente normal que todos los porcentajes sean diferentes.** Lo que importa es:
- **>90%**: Casi todo el proyecto está copiado
- **70-90%**: La mayoría del proyecto está copiado
- **50-70%**: Más de la mitad está copiado
- **<50%**: Menos de la mitad (puede ser código común)

---

## 🎓 Ejemplo Académico Realista

Imagina que todos los estudiantes tenían que implementar un proyecto de "Detector de Mutantes":

- **Ariel, Enzo, Franco, Luciano, Nicolas**: Todos copiaron el mismo proyecto completo → **100% similitud** entre todos ellos
- **Celeste y Florencia**: Compartieron la mayoría de los archivos pero cada una hizo algunos propios → **73.7% similitud**
- **Ariel e Iván**: Iván copió algunos archivos de Ariel pero hizo el resto por su cuenta → **62.5% similitud**

Por eso cada caso tiene un porcentaje diferente: **reflejan diferentes niveles de copia**.
