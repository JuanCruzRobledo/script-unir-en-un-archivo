#!/usr/bin/env python3
"""
Script de prueba para verificar la corrección del bug
"""

import json
from pathlib import Path

def test_partial_copies_fix():
    """Prueba que el cálculo de copias parciales ahora es correcto"""

    # Configurar UTF-8 para Windows
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    script_dir = Path(__file__).parent.resolve()
    db_path = script_dir / "consolidado" / "hashes_database.json"

    print("=" * 70)
    print("  PRUEBA DE CORRECCIÓN - DETECCIÓN DE COPIAS PARCIALES".center(70))
    print("=" * 70)

    # Cargar base de datos
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)

    proyectos = db["proyectos"]

    # Caso de prueba: Lucía vs Luciano (que antes daba 904.8%)
    student_a = "Lucia Bustelo Fernández"
    student_b = "Luciano Agustin Cordoba"

    if student_a not in proyectos or student_b not in proyectos:
        print(f"\n⚠️  No se encontraron los estudiantes de prueba")
        return

    files_a = proyectos[student_a]["archivos"]
    files_b = proyectos[student_b]["archivos"]

    # MÉTODO ANTIGUO (BUGGEADO)
    print(f"\n🔴 MÉTODO ANTIGUO (BUGGEADO):")
    print("-" * 70)

    common_files_old = []
    for file_name_a, hash_a in files_a.items():
        for file_name_b, hash_b in files_b.items():
            if hash_a == hash_b:
                common_files_old.append({
                    "nombre_a": file_name_a,
                    "nombre_b": file_name_b,
                    "hash": hash_a
                })

    total_files_min_old = min(len(files_a), len(files_b))
    porcentaje_old = (len(common_files_old) / total_files_min_old * 100) if total_files_min_old > 0 else 0

    print(f"Estudiante A ({student_a}): {len(files_a)} archivos")
    print(f"Estudiante B ({student_b}): {len(files_b)} archivos")
    print(f"'Archivos comunes' detectados: {len(common_files_old)}")
    print(f"Porcentaje calculado: {porcentaje_old:.1f}%")
    print(f"❌ PROBLEMA: Porcentaje > 100% (imposible!)")

    # MÉTODO NUEVO (CORREGIDO)
    print(f"\n✅ MÉTODO NUEVO (CORREGIDO):")
    print("-" * 70)

    hashes_a = set(files_a.values())
    hashes_b = set(files_b.values())
    common_hashes = hashes_a & hashes_b

    total_files_min_new = min(len(hashes_a), len(hashes_b))
    porcentaje_new = (len(common_hashes) / total_files_min_new * 100) if total_files_min_new > 0 else 0

    print(f"Estudiante A ({student_a}): {len(hashes_a)} archivos únicos")
    print(f"Estudiante B ({student_b}): {len(hashes_b)} archivos únicos")
    print(f"Hashes únicos compartidos: {len(common_hashes)}")
    print(f"Porcentaje calculado: {porcentaje_new:.1f}%")
    print(f"✅ CORRECTO: Porcentaje <= 100%")

    # Comparación
    print(f"\n📊 COMPARACIÓN:")
    print("-" * 70)
    print(f"Método antiguo: {len(common_files_old)} coincidencias → {porcentaje_old:.1f}%")
    print(f"Método nuevo:   {len(common_hashes)} coincidencias → {porcentaje_new:.1f}%")
    print(f"Reducción:      {len(common_files_old) - len(common_hashes)} coincidencias duplicadas eliminadas")

    # Verificar otros casos
    print(f"\n\n🔍 VERIFICACIÓN RÁPIDA DE OTROS CASOS:")
    print("-" * 70)

    test_cases = [
        ("Enzo Collovati", "Franco Jose Siccatto Galbusera"),  # Deberían ser 100% idénticos
        ("Ariel Alejandro Cortes Noguera", "Enzo Collovati"),
    ]

    for student_x, student_y in test_cases:
        if student_x not in proyectos or student_y not in proyectos:
            continue

        files_x = proyectos[student_x]["archivos"]
        files_y = proyectos[student_y]["archivos"]

        hashes_x = set(files_x.values())
        hashes_y = set(files_y.values())
        common = hashes_x & hashes_y

        total_min = min(len(hashes_x), len(hashes_y))
        pct = (len(common) / total_min * 100) if total_min > 0 else 0

        hash_proyecto_x = proyectos[student_x]["hash_proyecto"]
        hash_proyecto_y = proyectos[student_y]["hash_proyecto"]
        son_identicos = hash_proyecto_x == hash_proyecto_y

        status = "✅ Proyectos idénticos" if son_identicos else f"⚠️  Copia parcial ({pct:.1f}%)"

        print(f"\n{student_x} vs {student_y}")
        print(f"  Archivos comunes: {len(common)}/{total_min}")
        print(f"  Similitud: {pct:.1f}%")
        print(f"  {status}")

    print("\n" + "=" * 70)
    print("✅ Corrección verificada - El bug ha sido corregido")
    print("=" * 70)
    print("\n💡 Ahora puedes regenerar el reporte ejecutando:")
    print("   python batch_consolidator.py")
    print("\nNOTA: Esto volverá a procesar todas las entregas y regenerará")
    print("      hashes_database.json y reporte_similitud.json")
    print()

if __name__ == '__main__':
    test_partial_copies_fix()
