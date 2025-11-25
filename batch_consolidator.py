#!/usr/bin/env python3
"""
Batch Java Project Consolidator
Procesa múltiples entregas de proyectos Java de forma automática
"""

import os
import sys
import zipfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Set, Dict


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

    def generate_consolidated_file(self, output_path: str, files: List[Path], mode_name: str, student_name: str = None):
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


class BatchProcessor:
    """Procesa múltiples entregas de alumnos automáticamente"""

    def __init__(self, script_dir: Path):
        self.script_dir = script_dir
        self.entregas_dir = script_dir / "entregas"
        self.consolidado_dir = script_dir / "consolidado"

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
            student_name = student_dir.name
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

                    # Generar archivo consolidado en formato TXT
                    output_filename = f"{student_name}.txt"
                    output_path = self.consolidado_dir / output_filename

                    consolidator.generate_consolidated_file(
                        str(output_path),
                        files,
                        mode_name,
                        student_name
                    )

                    # Información del archivo generado
                    file_size_kb = output_path.stat().st_size / 1024

                    print(f"   💾 Archivo generado: {output_filename}")
                    print(f"   📊 Estadísticas:")
                    print(f"      • Archivos procesados: {consolidator.stats['total_files']}")
                    print(f"      • Líneas totales: {consolidator.stats['total_lines']:,}")
                    print(f"      • Archivos Java: {consolidator.stats['java_files']}")
                    print(f"      • Tamaño: {file_size_kb:.2f} KB")

                    successful += 1
                    results.append((student_name, "Exitoso", consolidator.stats))

            except Exception as e:
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
