#!/usr/bin/env python3
"""
Batch Java Project Consolidator
Procesa múltiples entregas de proyectos Java de forma automática
Incluye detección de copias totales y parciales entre proyectos
"""

import os
import sys
import zipfile
import tempfile
import shutil
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Set, Dict, Tuple
from collections import defaultdict


class BatchProjectConsolidator:
    """Clase para consolidar múltiples proyectos Java de entregas de alumnos"""

    # Directorios que siempre se excluyen
    EXCLUDED_DIRS = {
        '.git', '.idea', '.vscode', '.settings',
        'target', 'build', 'out', 'bin',
        'node_modules', '.gradle', '.mvn',
        '__pycache__', '.pytest_cache'
    }

    # Extensiones binarias que se excluyen
    BINARY_EXTENSIONS = {
        '.class', '.jar', '.war', '.ear',
        '.zip', '.tar', '.gz', '.7z',
        '.exe', '.dll', '.so', '.dylib',
        '.png', '.jpg', '.jpeg', '.gif', '.ico',
        '.pdf', '.doc', '.docx'
    }

    # Modos de conversión predefinidos
    CONVERSION_MODES = {
        '1': {
            'name': 'Solo archivos .java',
            'description': 'Incluye únicamente archivos de código fuente Java',
            'extensions': {'.java'}
        },
        '2': {
            'name': 'Proyecto completo',
            'description': 'Incluye código fuente y archivos de configuración',
            'extensions': {
                '.java', '.xml', '.properties', '.yaml', '.yml',
                '.gradle', '.kts', '.md', '.txt', '.json',
                '.sql', '.sh', '.bat', '.cmd'
            }
        },
        '3': {
            'name': 'Personalizado',
            'description': 'Permite seleccionar extensiones específicas',
            'extensions': set()  # Se configurará interactivamente
        }
    }

    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        if not self.project_path.exists():
            raise ValueError(f"La ruta no existe: {project_path}")
        if not self.project_path.is_dir():
            raise ValueError(f"La ruta no es un directorio: {project_path}")

        self.files_to_process: List[Path] = []
        self.project_type = None
        self.stats = {
            'total_files': 0,
            'total_lines': 0,
            'java_files': 0,
            'config_files': 0
        }

    def detect_project_type(self) -> str:
        """Detecta el tipo de proyecto Java"""
        if (self.project_path / 'pom.xml').exists():
            return 'Maven'
        elif any(self.project_path.glob('build.gradle*')):
            return 'Gradle'
        elif (self.project_path / 'build.xml').exists():
            return 'Ant'
        else:
            return 'Simple Java Project'

    def scan_files(self, extensions: Set[str], include_tests: bool = True) -> List[Path]:
        """Escanea el proyecto y retorna lista de archivos a procesar"""
        files = []

        for root, dirs, filenames in os.walk(self.project_path):
            # Filtrar directorios excluidos
            dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS]

            # Si no se incluyen tests, excluir carpetas de test
            if not include_tests:
                dirs[:] = [d for d in dirs if 'test' not in d.lower()]

            for filename in filenames:
                file_path = Path(root) / filename
                extension = file_path.suffix.lower()

                # Excluir archivos binarios
                if extension in self.BINARY_EXTENSIONS:
                    continue

                # Incluir solo las extensiones seleccionadas
                if extension in extensions or filename.lower() in {'pom.xml', 'build.gradle', 'settings.gradle', 'gradlew', 'mvnw'}:
                    files.append(file_path)

        return sorted(files)

    def get_relative_path(self, file_path: Path) -> str:
        """Retorna la ruta relativa al proyecto"""
        try:
            return str(file_path.relative_to(self.project_path))
        except ValueError:
            return str(file_path)

    def read_file_safely(self, file_path: Path) -> str:
        """Lee un archivo de forma segura, manejando diferentes encodings"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue

        return f"[Error: No se pudo leer el archivo con encodings comunes]"

    def calculate_file_hash(self, content: str) -> str:
        """
        Calcula el hash SHA256 de un archivo
        Normaliza el contenido removiendo espacios al inicio/final de líneas y líneas vacías
        """
        # Normalizar contenido: remover espacios al inicio/final de líneas
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        normalized = '\n'.join(lines)

        # Calcular hash SHA256
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    def calculate_project_hash(self, files_dict: Dict[str, str]) -> str:
        """
        Calcula el hash del proyecto completo
        files_dict: {nombre_archivo: contenido}
        """
        # Ordenar archivos alfabéticamente para consistencia
        sorted_files = sorted(files_dict.items())

        # Concatenar todos los contenidos
        combined = ''.join([f"{name}:{content}" for name, content in sorted_files])

        # Calcular hash SHA256
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    def extract_java_files_with_hashes(self, files: List[Path]) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Extrae archivos .java y calcula sus hashes
        Retorna: (archivos_dict, hashes_dict)
        archivos_dict: {nombre_relativo: contenido}
        hashes_dict: {nombre_relativo: hash}
        """
        archivos_dict = {}
        hashes_dict = {}

        for file_path in files:
            if file_path.suffix == '.java':
                relative_path = self.get_relative_path(file_path)
                content = self.read_file_safely(file_path)

                # Calcular hash del archivo
                file_hash = self.calculate_file_hash(content)

                archivos_dict[relative_path] = content
                hashes_dict[relative_path] = file_hash

        return archivos_dict, hashes_dict

    def generate_consolidated_file(self, output_path: str, files: List[Path], mode_name: str, student_name: str = None, project_hash: str = None):
        """Genera el archivo consolidado en formato TXT (con sintaxis Markdown)"""

        with open(output_path, 'w', encoding='utf-8') as out_file:
            # Encabezado
            out_file.write(f"# Proyecto Java Consolidado\n\n")
            out_file.write(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            if student_name:
                out_file.write(f"**Alumno:** {student_name}\n\n")
            out_file.write(f"**Proyecto:** {self.project_path.name}\n\n")
            out_file.write(f"**Ruta:** `{self.project_path}`\n\n")
            out_file.write(f"**Modo de conversión:** {mode_name}\n\n")
            if project_hash:
                out_file.write(f"**Hash del proyecto:** `{project_hash[:16]}...`\n\n")

            # Metadata del proyecto
            out_file.write("## 📋 Metadata del Proyecto\n\n")
            out_file.write(f"- **Tipo de proyecto:** {self.project_type}\n")
            out_file.write(f"- **Total de archivos:** {len(files)}\n")

            # Estructura de directorios
            out_file.write("\n## 📁 Estructura de Directorios\n\n")
            out_file.write("```\n")
            self._write_directory_tree(out_file, files)
            out_file.write("```\n\n")

            # Contenido de archivos
            out_file.write("## 📄 Contenido de Archivos\n\n")
            out_file.write("---\n\n")

            total_lines = 0
            java_files = 0

            for file_path in files:
                relative_path = self.get_relative_path(file_path)
                content = self.read_file_safely(file_path)
                lines = content.count('\n') + 1
                total_lines += lines

                if file_path.suffix == '.java':
                    java_files += 1

                # Detectar el lenguaje para el bloque de código
                extension = file_path.suffix.lower()
                lang_map = {
                    '.java': 'java',
                    '.xml': 'xml',
                    '.properties': 'properties',
                    '.gradle': 'gradle',
                    '.kts': 'kotlin',
                    '.yaml': 'yaml',
                    '.yml': 'yaml',
                    '.json': 'json',
                    '.sql': 'sql',
                    '.md': 'markdown',
                    '.sh': 'bash',
                    '.bat': 'batch',
                    '.txt': 'text'
                }
                lang = lang_map.get(extension, 'text')

                out_file.write(f"### 📄 `{relative_path}`\n\n")
                out_file.write(f"**Líneas:** {lines} | **Tipo:** {extension}\n\n")
                out_file.write(f"```{lang}\n")
                out_file.write(content)
                if not content.endswith('\n'):
                    out_file.write('\n')
                out_file.write("```\n\n")
                out_file.write("---\n\n")

            # Estadísticas finales
            out_file.write("## 📊 Estadísticas del Proyecto\n\n")
            out_file.write(f"- **Total de archivos procesados:** {len(files)}\n")
            out_file.write(f"- **Total de líneas de código:** {total_lines:,}\n")
            out_file.write(f"- **Archivos Java:** {java_files}\n")
            out_file.write(f"- **Otros archivos:** {len(files) - java_files}\n")

            self.stats['total_files'] = len(files)
            self.stats['total_lines'] = total_lines
            self.stats['java_files'] = java_files
            self.stats['config_files'] = len(files) - java_files

    def _write_directory_tree(self, out_file, files: List[Path]):
        """Escribe un árbol de directorios"""
        # Crear estructura de árbol
        dirs = set()
        for file_path in files:
            parts = self.get_relative_path(file_path).split(os.sep)
            for i in range(len(parts)):
                dirs.add(os.sep.join(parts[:i+1]))

        sorted_dirs = sorted(dirs)
        for dir_path in sorted_dirs[:50]:  # Limitar a 50 para no saturar
            level = dir_path.count(os.sep)
            indent = "  " * level
            name = os.path.basename(dir_path) if os.path.basename(dir_path) else dir_path

            # Verificar si es archivo o directorio
            is_file = any(self.get_relative_path(f) == dir_path for f in files)
            prefix = "📄 " if is_file else "📁 "

            out_file.write(f"{indent}{prefix}{name}\n")

        if len(sorted_dirs) > 50:
            out_file.write(f"\n... y {len(sorted_dirs) - 50} elementos más\n")


class SimilarityDetector:
    """Detecta copias totales y parciales entre proyectos"""

    def __init__(self, consolidado_dir: Path):
        self.consolidado_dir = consolidado_dir
        self.database_path = consolidado_dir / "hashes_database.json"
        self.report_path = consolidado_dir / "reporte_similitud.json"
        self.database = self.load_database()

    def load_database(self) -> Dict:
        """Carga la base de datos de hashes o crea una nueva"""
        if self.database_path.exists():
            try:
                with open(self.database_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Advertencia: No se pudo cargar la base de datos existente: {e}")
                print("   Se creará una nueva base de datos.")

        return {
            "version": "1.0",
            "ultima_actualizacion": None,
            "total_proyectos": 0,
            "proyectos": {}
        }

    def save_database(self):
        """Guarda la base de datos de hashes"""
        self.database["ultima_actualizacion"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.database["total_proyectos"] = len(self.database["proyectos"])

        with open(self.database_path, 'w', encoding='utf-8') as f:
            json.dump(self.database, f, indent=2, ensure_ascii=False)

    def add_project(self, student_name: str, project_hash: str, file_hashes: Dict[str, str],
                   total_files: int, total_lines: int):
        """Agrega un proyecto a la base de datos"""
        self.database["proyectos"][student_name] = {
            "fecha_procesado": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "hash_proyecto": project_hash,
            "archivos": file_hashes,
            "total_archivos": total_files,
            "total_lineas": total_lines
        }

    def detect_similarities(self) -> Dict:
        """
        Detecta similitudes entre todos los proyectos en la base de datos
        Retorna un diccionario con proyectos idénticos y copias parciales
        """
        proyectos = self.database["proyectos"]

        # Diccionarios para agrupar resultados
        identical_groups = defaultdict(list)  # {hash_proyecto: [lista_alumnos]}
        file_hash_map = defaultdict(list)     # {hash_archivo: [(alumno, nombre_archivo)]}

        # Agrupar proyectos idénticos por hash
        for student, data in proyectos.items():
            project_hash = data["hash_proyecto"]
            identical_groups[project_hash].append(student)

            # Mapear hashes de archivos individuales
            for file_name, file_hash in data["archivos"].items():
                file_hash_map[file_hash].append((student, file_name))

        # Filtrar solo grupos con más de 1 proyecto (copias)
        proyectos_identicos = []
        for project_hash, students in identical_groups.items():
            if len(students) > 1:
                # Obtener datos del primer proyecto (todos son iguales)
                first_student = students[0]
                project_data = proyectos[first_student]

                proyectos_identicos.append({
                    "hash_proyecto": project_hash,
                    "alumnos": sorted(students),
                    "porcentaje_similitud": 100,
                    "archivos_identicos": project_data["total_archivos"],
                    "total_lineas": project_data["total_lineas"]
                })

        # Detectar copias parciales (archivos en común pero no 100% iguales)
        copias_parciales = []
        students_list = list(proyectos.keys())

        for i, student_a in enumerate(students_list):
            for student_b in students_list[i+1:]:
                # Obtener archivos de ambos estudiantes
                files_a = proyectos[student_a]["archivos"]
                files_b = proyectos[student_b]["archivos"]

                # Encontrar hashes únicos compartidos (no producto cartesiano)
                hashes_a = set(files_a.values())
                hashes_b = set(files_b.values())
                common_hashes = hashes_a & hashes_b  # Intersección de sets

                # Si tienen al menos 3 archivos en común y no son proyectos 100% idénticos
                if len(common_hashes) >= 3:
                    # Verificar que no sean proyectos idénticos (ya detectados)
                    if proyectos[student_a]["hash_proyecto"] != proyectos[student_b]["hash_proyecto"]:
                        # Calcular porcentaje de similitud basado en hashes únicos
                        total_files_min = min(len(hashes_a), len(hashes_b))
                        porcentaje = (len(common_hashes) / total_files_min * 100) if total_files_min > 0 else 0

                        # Construir lista de archivos copiados (un ejemplo por hash)
                        archivos_copiados = []
                        for common_hash in common_hashes:
                            # Encontrar un archivo con este hash en student_a
                            for file_name_a, hash_a in files_a.items():
                                if hash_a == common_hash:
                                    archivos_copiados.append({
                                        "nombre": file_name_a,
                                        "hash": common_hash[:16] + "..."
                                    })
                                    break  # Solo necesitamos un ejemplo por hash

                        copias_parciales.append({
                            "alumnos": [student_a, student_b],
                            "archivos_copiados": archivos_copiados,
                            "porcentaje_similitud": round(porcentaje, 1),
                            "total_archivos_comunes": len(common_hashes)
                        })

        # Archivos más copiados (aparecen en 3 o más proyectos)
        archivos_mas_copiados = []
        for file_hash, occurrences in file_hash_map.items():
            if len(set(student for student, _ in occurrences)) >= 3:  # Al menos 3 alumnos diferentes
                students_with_file = list(set(student for student, _ in occurrences))
                file_names = [name for _, name in occurrences]
                most_common_name = max(set(file_names), key=file_names.count)

                archivos_mas_copiados.append({
                    "archivo": most_common_name,
                    "hash": file_hash[:16] + "...",
                    "aparece_en": sorted(students_with_file),
                    "total_copias": len(students_with_file)
                })

        # Ordenar por número de copias (descendente)
        archivos_mas_copiados.sort(key=lambda x: x["total_copias"], reverse=True)

        return {
            "proyectos_identicos": proyectos_identicos,
            "copias_parciales": copias_parciales,
            "archivos_mas_copiados": archivos_mas_copiados
        }

    def generate_similarity_report(self):
        """Genera el reporte de similitud en formato JSON"""
        similarities = self.detect_similarities()

        report = {
            "generado": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_proyectos_analizados": self.database["total_proyectos"],
            "total_grupos_identicos": len(similarities["proyectos_identicos"]),
            "total_copias_parciales": len(similarities["copias_parciales"]),
            "proyectos_identicos": similarities["proyectos_identicos"],
            "copias_parciales": similarities["copias_parciales"],
            "archivos_mas_copiados": similarities["archivos_mas_copiados"]
        }

        with open(self.report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return similarities

    def print_similarity_summary(self, similarities: Dict):
        """Imprime un resumen de similitudes en consola"""
        print("\n" + "=" * 70)
        print(f"  🔍 ANÁLISIS DE SIMILITUD ({self.database['total_proyectos']} proyectos en total)".center(70))
        print("=" * 70)

        # Proyectos idénticos
        if similarities["proyectos_identicos"]:
            print("\n⚠️  PROYECTOS IDÉNTICOS (100%):")
            print("-" * 70)
            for idx, grupo in enumerate(similarities["proyectos_identicos"], 1):
                alumnos = ", ".join(grupo["alumnos"])
                print(f"  Grupo {idx}: {alumnos}")
                print(f"    • Hash: {grupo['hash_proyecto'][:8]}")
                print(f"    • Archivos: {grupo['archivos_identicos']} idénticos")
                print(f"    • Líneas: {grupo['total_lineas']:,}")
                print()
        else:
            print("\n✅ No se detectaron proyectos 100% idénticos")

        # Copias parciales
        if similarities["copias_parciales"]:
            print("\n⚠️  COPIAS PARCIALES (≥50% similitud):")
            print("-" * 70)
            for copia in similarities["copias_parciales"]:
                if copia["porcentaje_similitud"] >= 50:  # Solo mostrar >= 50%
                    alumnos = " ↔ ".join(copia["alumnos"])
                    print(f"  {alumnos}")
                    print(f"    • Similitud: {copia['porcentaje_similitud']}%")
                    print(f"    • Archivos copiados: {copia['total_archivos_comunes']}")

                    # Mostrar algunos archivos (máximo 5)
                    archivos_mostrar = copia["archivos_copiados"][:5]
                    archivos_nombres = [a["nombre"] for a in archivos_mostrar]
                    print(f"    • Archivos: {', '.join(archivos_nombres)}", end="")
                    if len(copia["archivos_copiados"]) > 5:
                        print(f"... (+{len(copia['archivos_copiados']) - 5} más)")
                    else:
                        print()
                    print()
        else:
            print("\n✅ No se detectaron copias parciales significativas")

        # Archivos más copiados (mostrar top 5)
        if similarities["archivos_mas_copiados"]:
            print("\n📋 ARCHIVOS MÁS COPIADOS (Top 5):")
            print("-" * 70)
            for idx, archivo in enumerate(similarities["archivos_mas_copiados"][:5], 1):
                print(f"  {idx}. {archivo['archivo']}")
                print(f"     • Aparece en {archivo['total_copias']} proyectos")
                alumnos = ", ".join(archivo["aparece_en"][:3])
                if archivo['total_copias'] > 3:
                    alumnos += f"... (+{archivo['total_copias'] - 3} más)"
                print(f"     • Alumnos: {alumnos}")
                print()

        print(f"\n📋 Reporte detallado guardado en: {self.report_path.name}")
        print(f"📋 Base de datos actualizada: {self.database_path.name}")
        print("\n" + "=" * 70)


class BatchProcessor:
    """Procesa múltiples entregas de alumnos automáticamente"""

    def __init__(self, script_dir: Path):
        self.script_dir = script_dir
        self.entregas_dir = script_dir / "entregas"
        self.consolidado_dir = script_dir / "consolidado"
        self.similarity_detector = None

    def sanitize_student_name(self, raw_name: str) -> str:
        """Limpia el nombre de la carpeta de entrega para obtener el nombre del alumno.

        - Remueve sufijos como _<id>_assignsubmission_file o _assignsubmission_file
        - Reemplaza saltos de línea por espacios
        - Colapsa múltiples espacios en uno y hace strip
        - Si el resultado queda vacío, devuelve el raw_name stripped
        """
        if not raw_name:
            return ""

        # Reemplazar saltos de línea y tabs por espacios
        name = re.sub(r"[\r\n\t]+", " ", raw_name)

        # Remover sufijo tipo _123456_assignsubmission_file o _assignsubmission_file
        name = re.sub(r"_[0-9]+_assignsubmission_file$", "", name)
        name = re.sub(r"_assignsubmission_file$", "", name)

        # Reemplazar múltiples espacios por uno y limpiar espacios alrededor
        name = re.sub(r"\s+", " ", name).strip()

        return name or raw_name.strip()

    def find_zip_files(self, student_dir: Path) -> List[Path]:
        """Encuentra archivos ZIP en la carpeta del alumno"""
        zip_files = list(student_dir.glob("*.zip"))
        return zip_files

    def extract_zip(self, zip_path: Path, extract_to: Path) -> Path:
        """Extrae un archivo ZIP y retorna la ruta del proyecto extraído"""
        print(f"   📦 Descomprimiendo: {zip_path.name}")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)

        # Buscar la carpeta raíz del proyecto (puede estar en un subdirectorio)
        extracted_items = list(extract_to.iterdir())

        # Si solo hay un directorio, usarlo como raíz
        if len(extracted_items) == 1 and extracted_items[0].is_dir():
            return extracted_items[0]

        return extract_to

    def process_all_submissions(self, extensions: Set[str], include_tests: bool, mode_name: str):
        """Procesa todas las entregas en la carpeta /entregas/"""

        # Verificar que exista la carpeta entregas
        if not self.entregas_dir.exists():
            print(f"\n❌ Error: No existe la carpeta 'entregas' en {self.script_dir}")
            return

        # Crear carpeta consolidado si no existe
        self.consolidado_dir.mkdir(exist_ok=True)

        # Inicializar detector de similitud
        self.similarity_detector = SimilarityDetector(self.consolidado_dir)
        print(f"\n📊 Base de datos cargada: {self.similarity_detector.database['total_proyectos']} proyectos existentes")

        # Obtener todas las carpetas de alumnos
        student_dirs = [d for d in self.entregas_dir.iterdir() if d.is_dir()]

        if not student_dirs:
            print("\n❌ No se encontraron carpetas de alumnos en /entregas/")
            return

        print(f"\n✅ Se encontraron {len(student_dirs)} entregas para procesar\n")
        print("=" * 70)

        successful = 0
        failed = 0
        results = []

        for student_dir in student_dirs:
            raw_student_name = student_dir.name
            student_name = self.sanitize_student_name(raw_student_name)
            print(f"\n📂 Procesando: {student_name}")
            print("-" * 70)

            try:
                # Buscar archivos ZIP
                zip_files = self.find_zip_files(student_dir)

                if not zip_files:
                    print(f"   ⚠️  No se encontró archivo ZIP en {student_name}")
                    failed += 1
                    results.append((student_name, "No se encontró ZIP", None))
                    continue

                if len(zip_files) > 1:
                    print(f"   ⚠️  Se encontraron múltiples ZIPs, usando el primero: {zip_files[0].name}")

                zip_file = zip_files[0]

                # Crear directorio temporal para extraer
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)

                    # Extraer ZIP
                    project_path = self.extract_zip(zip_file, temp_path)

                    # Crear consolidador para este proyecto
                    consolidator = BatchProjectConsolidator(str(project_path))
                    consolidator.project_type = consolidator.detect_project_type()

                    print(f"   📦 Tipo de proyecto: {consolidator.project_type}")

                    # Escanear archivos
                    files = consolidator.scan_files(extensions, include_tests)

                    if not files:
                        print(f"   ⚠️  No se encontraron archivos con las extensiones seleccionadas")
                        failed += 1
                        results.append((student_name, "Sin archivos válidos", None))
                        continue

                    print(f"   ✅ Archivos encontrados: {len(files)}")

                    # Extraer archivos .java y calcular hashes
                    archivos_dict, file_hashes = consolidator.extract_java_files_with_hashes(files)

                    if not archivos_dict:
                        print(f"   ⚠️  No se encontraron archivos .java para análisis")
                        failed += 1
                        results.append((student_name, "Sin archivos .java", None))
                        continue

                    # Calcular hash del proyecto completo
                    project_hash = consolidator.calculate_project_hash(archivos_dict)
                    hash_corto = project_hash[:8]

                    print(f"   🔑 Hash del proyecto: {hash_corto}")

                    # Agregar a la base de datos de similitud (usar nombre sanitizado)
                    self.similarity_detector.add_project(
                        student_name,
                        project_hash,
                        file_hashes,
                        len(archivos_dict),
                        consolidator.stats.get('total_lines', 0)
                    )

                    # Generar archivo consolidado dentro de una carpeta por alumno
                    # Nombre fijo del archivo de salida: entrega.txt
                    student_output_dir = self.consolidado_dir / student_name
                    student_output_dir.mkdir(parents=True, exist_ok=True)

                    output_path = student_output_dir / "entrega.txt"

                    consolidator.generate_consolidated_file(
                        str(output_path),
                        files,
                        mode_name,
                        student_name,
                        project_hash
                    )

                    # Información del archivo generado
                    file_size_kb = output_path.stat().st_size / 1024

                    print(f"   💾 Archivo generado: {output_path.relative_to(self.consolidado_dir)}")
                    print(f"   📊 Estadísticas:")
                    print(f"      • Archivos procesados: {consolidator.stats['total_files']}")
                    print(f"      • Líneas totales: {consolidator.stats['total_lines']:,}")
                    print(f"      • Archivos Java: {consolidator.stats['java_files']}")
                    print(f"      • Tamaño: {file_size_kb:.2f} KB")

                    successful += 1
                    results.append((student_name, "Exitoso", consolidator.stats))

            except Exception as e:
                # En caso de error, usar el nombre sanitizado para los logs/resultados
                print(f"   ❌ Error procesando {student_name}: {str(e)}")
                failed += 1
                results.append((student_name, f"Error: {str(e)}", None))

        # Resumen final
        print("\n" + "=" * 70)
        print("  📊 RESUMEN DEL PROCESAMIENTO".center(70))
        print("=" * 70)
        print(f"\n✅ Exitosos: {successful}")
        print(f"❌ Fallidos: {failed}")
        print(f"📁 Total procesados: {len(student_dirs)}")
        print(f"\n💾 Archivos generados en: {self.consolidado_dir}")

        # Mostrar detalles
        if results:
            print("\n📋 Detalle por alumno:")
            print("-" * 70)
            for name, status, stats in results:
                status_icon = "✅" if stats else "❌"
                print(f"{status_icon} {name}: {status}")

        print("\n" + "=" * 70)

        # Guardar base de datos y generar reporte de similitud
        if successful > 0:
            print("\n🔍 Analizando similitudes entre proyectos...")
            self.similarity_detector.save_database()
            similarities = self.similarity_detector.generate_similarity_report()
            self.similarity_detector.print_similarity_summary(similarities)


def print_header():
    """Imprime el encabezado del programa"""
    print("=" * 70)
    print("  BATCH JAVA PROJECT CONSOLIDATOR".center(70))
    print("  Procesa múltiples entregas de alumnos automáticamente".center(70))
    print("=" * 70)
    print()


def show_conversion_modes():
    """Muestra los modos de conversión disponibles"""
    print("\n📋 MODOS DE CONVERSIÓN DISPONIBLES:\n")

    for key, mode in BatchProjectConsolidator.CONVERSION_MODES.items():
        print(f"  [{key}] {mode['name']}")
        print(f"      {mode['description']}")
        if mode['extensions']:
            extensions = ', '.join(sorted(mode['extensions']))
            print(f"      Extensiones: {extensions}")
        print()


def get_custom_extensions() -> Set[str]:
    """Permite al usuario ingresar extensiones personalizadas"""
    print("\n📝 MODO PERSONALIZADO")
    print("\nExtensiones comunes disponibles:")
    print("  .java, .xml, .properties, .yaml, .yml, .gradle, .kts")
    print("  .md, .txt, .json, .sql, .sh, .bat, .cmd")
    print("\nIngresa las extensiones separadas por comas (incluye el punto):")
    print("Ejemplo: .java,.xml,.properties")

    while True:
        user_input = input("\n> ").strip()
        if not user_input:
            print("❌ Debes ingresar al menos una extensión.")
            continue

        extensions = {ext.strip() for ext in user_input.split(',')}

        # Validar que tengan el punto
        valid_extensions = set()
        for ext in extensions:
            if not ext.startswith('.'):
                ext = '.' + ext
            valid_extensions.add(ext.lower())

        print(f"\n✅ Extensiones seleccionadas: {', '.join(sorted(valid_extensions))}")
        confirm = input("¿Confirmar? (s/n): ").strip().lower()
        if confirm in ['s', 'si', 'yes', 'y']:
            return valid_extensions


def main():
    """Función principal"""
    # Configurar UTF-8 para Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    print_header()

    # Obtener directorio donde está el script
    script_dir = Path(__file__).parent.resolve()

    print(f"📂 Directorio de trabajo: {script_dir}")
    print(f"📁 Buscando entregas en: {script_dir / 'entregas'}")
    print(f"💾 Salida en: {script_dir / 'consolidado'}")

    # Mostrar modos de conversión
    show_conversion_modes()

    # Seleccionar modo (UNA SOLA VEZ)
    while True:
        mode_choice = input("Selecciona un modo (1-3): ").strip()
        if mode_choice in BatchProjectConsolidator.CONVERSION_MODES:
            break
        print("❌ Opción inválida. Por favor selecciona 1, 2 o 3.")

    mode_config = BatchProjectConsolidator.CONVERSION_MODES[mode_choice]
    mode_name = mode_config['name']
    extensions = mode_config['extensions'].copy()

    # Si es modo personalizado, solicitar extensiones
    if mode_choice == '3':
        extensions = get_custom_extensions()

    # Preguntar si incluir tests (UNA SOLA VEZ)
    print("\n¿Incluir archivos de pruebas/tests? (s/n):")
    include_tests = input("> ").strip().lower() in ['s', 'si', 'yes', 'y']

    print(f"\n✅ Configuración aplicada:")
    print(f"   • Modo: {mode_name}")
    print(f"   • Extensiones: {', '.join(sorted(extensions))}")
    print(f"   • Incluir tests: {'Sí' if include_tests else 'No'}")
    print(f"\n🚀 Iniciando procesamiento de entregas...")

    try:
        # Crear procesador batch
        processor = BatchProcessor(script_dir)

        # Procesar todas las entregas
        processor.process_all_submissions(extensions, include_tests, mode_name)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
