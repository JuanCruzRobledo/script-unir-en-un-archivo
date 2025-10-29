#!/usr/bin/env python3
"""
Java Project Consolidator
Consolida un proyecto Java en un único archivo para análisis por IA
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Set, Dict
import argparse


class ProjectConsolidator:
    """Clase principal para consolidar proyectos Java"""

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

    def generate_consolidated_file(self, output_path: str, files: List[Path], mode_name: str):
        """Genera el archivo consolidado en formato Markdown"""

        with open(output_path, 'w', encoding='utf-8') as out_file:
            # Encabezado
            out_file.write(f"# Proyecto Java Consolidado\n\n")
            out_file.write(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
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


def print_header():
    """Imprime el encabezado del programa"""
    print("=" * 70)
    print("  JAVA PROJECT CONSOLIDATOR".center(70))
    print("  Convierte tu proyecto Java en un único archivo".center(70))
    print("=" * 70)
    print()


def show_conversion_modes():
    """Muestra los modos de conversión disponibles"""
    print("\n📋 MODOS DE CONVERSIÓN DISPONIBLES:\n")

    for key, mode in ProjectConsolidator.CONVERSION_MODES.items():
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


def interactive_mode():
    """Modo interactivo con menú"""
    print_header()

    # Solicitar ruta del proyecto
    print("📂 Ingresa la ruta del proyecto Java:")
    print("   (Puedes arrastrar la carpeta aquí o escribir la ruta)")
    project_path = input("\n> ").strip().strip('"').strip("'")

    if not project_path:
        print("❌ No se ingresó ninguna ruta.")
        return

    try:
        consolidator = ProjectConsolidator(project_path)
        print(f"\n✅ Proyecto encontrado: {consolidator.project_path.name}")

        # Detectar tipo de proyecto
        consolidator.project_type = consolidator.detect_project_type()
        print(f"📦 Tipo de proyecto detectado: {consolidator.project_type}")

        # Mostrar modos de conversión
        show_conversion_modes()

        # Seleccionar modo
        while True:
            mode_choice = input("Selecciona un modo (1-3): ").strip()
            if mode_choice in ProjectConsolidator.CONVERSION_MODES:
                break
            print("❌ Opción inválida. Por favor selecciona 1, 2 o 3.")

        mode_config = ProjectConsolidator.CONVERSION_MODES[mode_choice]
        mode_name = mode_config['name']
        extensions = mode_config['extensions'].copy()

        # Si es modo personalizado, solicitar extensiones
        if mode_choice == '3':
            extensions = get_custom_extensions()

        # Preguntar si incluir tests
        print("\n¿Incluir archivos de pruebas/tests? (s/n):")
        include_tests = input("> ").strip().lower() in ['s', 'si', 'yes', 'y']

        # Escanear archivos
        print("\n🔍 Escaneando proyecto...")
        files = consolidator.scan_files(extensions, include_tests)

        if not files:
            print("❌ No se encontraron archivos con las extensiones seleccionadas.")
            return

        print(f"✅ Se encontraron {len(files)} archivo(s) para procesar.")

        # Nombre del archivo de salida
        default_output = f"{consolidator.project_path.name}_consolidated.md"
        print(f"\n💾 Nombre del archivo de salida (Enter para usar '{default_output}'):")
        output_name = input("> ").strip()
        if not output_name:
            output_name = default_output

        if not output_name.endswith('.md'):
            output_name += '.md'

        output_path = consolidator.project_path.parent / output_name

        # Generar archivo consolidado
        print(f"\n⚙️  Generando archivo consolidado...")
        consolidator.generate_consolidated_file(str(output_path), files, mode_name)

        # Mostrar resultados
        print("\n" + "=" * 70)
        print("  ✅ CONSOLIDACIÓN COMPLETADA".center(70))
        print("=" * 70)
        print(f"\n📊 Estadísticas:")
        print(f"   • Archivos procesados: {consolidator.stats['total_files']}")
        print(f"   • Líneas totales: {consolidator.stats['total_lines']:,}")
        print(f"   • Archivos Java: {consolidator.stats['java_files']}")
        print(f"   • Otros archivos: {consolidator.stats['config_files']}")
        print(f"\n💾 Archivo generado: {output_path}")
        print(f"   Tamaño: {output_path.stat().st_size / 1024:.2f} KB")
        print()

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Consolida un proyecto Java en un único archivo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Modo interactivo (recomendado)
  python consolidator.py

  # Modo CLI - Solo archivos Java
  python consolidator.py /ruta/proyecto -m 1 -o salida.md

  # Modo CLI - Proyecto completo
  python consolidator.py /ruta/proyecto -m 2 --include-tests
        """
    )

    parser.add_argument('project_path', nargs='?', help='Ruta del proyecto Java')
    parser.add_argument('-m', '--mode', choices=['1', '2', '3'],
                       help='Modo de conversión (1: solo .java, 2: completo, 3: personalizado)')
    parser.add_argument('-o', '--output', help='Archivo de salida')
    parser.add_argument('--include-tests', action='store_true',
                       help='Incluir archivos de pruebas')
    parser.add_argument('-e', '--extensions',
                       help='Extensiones personalizadas separadas por comas (ej: .java,.xml)')

    args = parser.parse_args()

    # Si no hay argumentos, usar modo interactivo
    if not args.project_path:
        interactive_mode()
        return

    # Modo CLI
    try:
        consolidator = ProjectConsolidator(args.project_path)
        consolidator.project_type = consolidator.detect_project_type()

        # Determinar extensiones según el modo
        if args.mode == '3' and args.extensions:
            extensions = {('.' + ext if not ext.startswith('.') else ext).lower()
                         for ext in args.extensions.split(',')}
        elif args.mode:
            extensions = ProjectConsolidator.CONVERSION_MODES[args.mode]['extensions']
        else:
            extensions = ProjectConsolidator.CONVERSION_MODES['2']['extensions']

        mode_name = ProjectConsolidator.CONVERSION_MODES.get(args.mode or '2',
                                                             ProjectConsolidator.CONVERSION_MODES['2'])['name']

        files = consolidator.scan_files(extensions, args.include_tests)

        if not files:
            print("No se encontraron archivos para procesar.")
            return

        output_path = args.output or f"{consolidator.project_path.name}_consolidated.md"
        consolidator.generate_consolidated_file(output_path, files, mode_name)

        print(f"✅ Archivo generado: {output_path}")
        print(f"📊 {len(files)} archivos procesados")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
