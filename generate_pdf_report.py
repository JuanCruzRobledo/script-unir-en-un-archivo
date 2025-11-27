#!/usr/bin/env python3
"""
Generador de Reporte PDF de Similitud
Crea un reporte visual en PDF del análisis de copias entre proyectos
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas


class SimilarityPDFGenerator:
    """Generador de PDF para reportes de similitud"""

    def __init__(self, report_path: Path, output_path: Path):
        self.report_path = report_path
        self.output_path = output_path
        self.report_data = None
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configura estilos personalizados para el PDF"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))

        # Sección de advertencia
        self.styles.add(ParagraphStyle(
            name='Warning',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#c0392b'),
            leftIndent=20,
            rightIndent=20,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))

        # Texto normal con mejor formato
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=8,
            leading=14
        ))

        # Info box
        self.styles.add(ParagraphStyle(
            name='InfoBox',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#27ae60'),
            leftIndent=15,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        ))

    def load_report(self):
        """Carga el reporte JSON"""
        try:
            with open(self.report_path, 'r', encoding='utf-8') as f:
                self.report_data = json.load(f)
            return True
        except Exception as e:
            print(f"❌ Error cargando reporte: {e}")
            return False

    def _create_header_footer(self, canvas_obj, doc):
        """Crea encabezado y pie de página"""
        canvas_obj.saveState()

        # Pie de página
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawString(
            inch,
            0.5 * inch,
            f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        canvas_obj.drawRightString(
            doc.pagesize[0] - inch,
            0.5 * inch,
            f"Página {doc.page}"
        )

        canvas_obj.restoreState()

    def _create_summary_section(self):
        """Crea la sección de resumen"""
        elements = []

        # Título
        elements.append(Paragraph(
            "📊 Reporte de Similitud de Proyectos",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 0.3*inch))

        # Información general
        total = self.report_data['total_proyectos_analizados']
        identicos = self.report_data['total_grupos_identicos']
        parciales = self.report_data['total_copias_parciales']

        # Cuadro resumen con tabla
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de proyectos analizados', str(total)],
            ['Grupos con proyectos 100% idénticos', str(identicos)],
            ['Casos de copias parciales detectados', str(parciales)],
            ['Fecha de generación', self.report_data['generado']]
        ]

        summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Contenido
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')])
        ]))

        elements.append(summary_table)
        elements.append(Spacer(1, 0.4*inch))

        # Indicador de severidad
        if identicos > 0 or parciales > 5:
            elements.append(Paragraph(
                "⚠️ ALERTA: Se detectaron casos significativos de similitud entre proyectos",
                self.styles['Warning']
            ))
            elements.append(Spacer(1, 0.2*inch))

        return elements

    def _create_identical_projects_section(self):
        """Crea la sección de proyectos idénticos"""
        elements = []

        proyectos_identicos = self.report_data.get('proyectos_identicos', [])

        if not proyectos_identicos:
            elements.append(Paragraph(
                "✅ Proyectos 100% Idénticos",
                self.styles['CustomHeading2']
            ))
            elements.append(Paragraph(
                "No se detectaron proyectos completamente idénticos.",
                self.styles['InfoBox']
            ))
            elements.append(Spacer(1, 0.3*inch))
            return elements

        elements.append(Paragraph(
            f"⚠️ Proyectos 100% Idénticos ({len(proyectos_identicos)} grupos)",
            self.styles['CustomHeading2']
        ))
        elements.append(Spacer(1, 0.2*inch))

        for idx, grupo in enumerate(proyectos_identicos, 1):
            # Datos del grupo
            alumnos = grupo['alumnos']
            hash_proyecto = grupo['hash_proyecto'][:16] + "..."
            archivos = grupo['archivos_identicos']

            # Crear tabla para cada grupo
            grupo_data = [
                ['Grupo ' + str(idx), ''],
                ['Alumnos involucrados', f"{len(alumnos)} estudiantes"],
                ['Hash del proyecto', hash_proyecto],
                ['Archivos idénticos', str(archivos)],
            ]

            # Agregar nombres de alumnos
            for i, alumno in enumerate(alumnos, 1):
                grupo_data.append([f'  {i}.', alumno])

            grupo_table = Table(grupo_data, colWidths=[1.5*inch, 4.5*inch])
            grupo_table.setStyle(TableStyle([
                # Primera fila (título del grupo)
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('SPAN', (0, 0), (-1, 0)),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

                # Información del grupo
                ('BACKGROUND', (0, 1), (-1, 3), colors.HexColor('#fadbd8')),
                ('FONTNAME', (0, 1), (0, 3), 'Helvetica-Bold'),

                # Lista de alumnos
                ('BACKGROUND', (0, 4), (-1, -1), colors.HexColor('#fff5f5')),
                ('LEFTPADDING', (0, 4), (0, -1), 20),

                # General
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))

            elements.append(KeepTogether(grupo_table))
            elements.append(Spacer(1, 0.2*inch))

        elements.append(PageBreak())
        return elements

    def _create_partial_copies_section(self):
        """Crea la sección de copias parciales"""
        elements = []

        copias_parciales = self.report_data.get('copias_parciales', [])

        if not copias_parciales:
            elements.append(Paragraph(
                "✅ Copias Parciales",
                self.styles['CustomHeading2']
            ))
            elements.append(Paragraph(
                "No se detectaron copias parciales significativas.",
                self.styles['InfoBox']
            ))
            return elements

        # Filtrar solo las más relevantes (≥50% similitud)
        copias_relevantes = [c for c in copias_parciales if c['porcentaje_similitud'] >= 50]

        elements.append(Paragraph(
            f"⚠️ Copias Parciales (≥50% similitud) - {len(copias_relevantes)} casos",
            self.styles['CustomHeading2']
        ))
        elements.append(Spacer(1, 0.2*inch))

        if not copias_relevantes:
            elements.append(Paragraph(
                "No se detectaron copias parciales con similitud ≥50%.",
                self.styles['CustomBody']
            ))
            elements.append(Spacer(1, 0.2*inch))

        for idx, copia in enumerate(copias_relevantes, 1):
            alumnos = copia['alumnos']
            porcentaje = copia['porcentaje_similitud']
            archivos_comunes = copia['total_archivos_comunes']

            # Determinar color según severidad
            if porcentaje >= 80:
                bg_color = colors.HexColor('#e74c3c')  # Rojo
            elif porcentaje >= 65:
                bg_color = colors.HexColor('#e67e22')  # Naranja
            else:
                bg_color = colors.HexColor('#f39c12')  # Amarillo

            # Tabla del caso
            caso_data = [
                [f'Caso {idx}', ''],
                ['Estudiantes', f"{alumnos[0]} ↔ {alumnos[1]}"],
                ['Similitud', f"{porcentaje}%"],
                ['Archivos copiados', f"{archivos_comunes} archivos"],
            ]

            # Agregar lista de algunos archivos (máximo 5)
            archivos_mostrar = copia['archivos_copiados'][:5]
            if archivos_mostrar:
                caso_data.append(['Archivos detectados:', ''])
                for archivo in archivos_mostrar:
                    nombre = archivo['nombre'].split('\\')[-1]  # Solo nombre del archivo
                    caso_data.append(['', f"• {nombre}"])

                if len(copia['archivos_copiados']) > 5:
                    caso_data.append(['', f"... y {len(copia['archivos_copiados']) - 5} más"])

            caso_table = Table(caso_data, colWidths=[1.5*inch, 4.5*inch])
            caso_table.setStyle(TableStyle([
                # Encabezado
                ('BACKGROUND', (0, 0), (-1, 0), bg_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('SPAN', (0, 0), (-1, 0)),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

                # Info principal
                ('BACKGROUND', (0, 1), (-1, 3), colors.HexColor('#fef5e7')),
                ('FONTNAME', (0, 1), (0, 3), 'Helvetica-Bold'),

                # Lista de archivos
                ('BACKGROUND', (0, 4), (-1, -1), colors.white),
                ('FONTNAME', (0, 4), (0, 4), 'Helvetica-Bold'),
                ('LEFTPADDING', (1, 5), (1, -1), 15),

                # General
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))

            elements.append(KeepTogether(caso_table))
            elements.append(Spacer(1, 0.15*inch))

            # Salto de página cada 3 casos para mejor lectura
            if idx % 3 == 0 and idx < len(copias_relevantes):
                elements.append(PageBreak())

        elements.append(PageBreak())
        return elements

    def _create_most_copied_files_section(self):
        """Crea la sección de archivos más copiados"""
        elements = []

        archivos = self.report_data.get('archivos_mas_copiados', [])[:10]  # Top 10

        if not archivos:
            return elements

        elements.append(Paragraph(
            f"📋 Archivos Más Copiados (Top 10)",
            self.styles['CustomHeading2']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # Crear tabla
        table_data = [['#', 'Archivo', 'Copias', 'Estudiantes (muestra)']]

        for idx, archivo in enumerate(archivos, 1):
            nombre = archivo['archivo'].split('\\')[-1]  # Solo nombre
            copias = archivo['total_copias']
            estudiantes = ', '.join(archivo['aparece_en'][:3])
            if copias > 3:
                estudiantes += f"... (+{copias - 3})"

            table_data.append([
                str(idx),
                nombre,
                str(copias),
                estudiantes
            ])

        files_table = Table(table_data, colWidths=[0.5*inch, 2*inch, 0.8*inch, 2.7*inch])
        files_table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9b59b6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Contenido
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Número
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Copias
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elements.append(files_table)
        elements.append(Spacer(1, 0.3*inch))

        return elements

    def generate_pdf(self):
        """Genera el PDF completo"""
        print(f"\n📄 Generando reporte PDF...")

        if not self.load_report():
            return False

        # Crear documento
        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=1*inch,
        )

        # Construir contenido
        story = []

        # Agregar secciones
        story.extend(self._create_summary_section())
        story.extend(self._create_identical_projects_section())
        story.extend(self._create_partial_copies_section())
        story.extend(self._create_most_copied_files_section())

        # Footer final
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(
            "—— Fin del Reporte ——",
            self.styles['CustomBody']
        ))

        # Generar PDF
        try:
            doc.build(story, onFirstPage=self._create_header_footer,
                     onLaterPages=self._create_header_footer)
            print(f"✅ PDF generado exitosamente: {self.output_path.name}")
            print(f"📂 Ubicación: {self.output_path}")
            return True
        except Exception as e:
            print(f"❌ Error generando PDF: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Función principal"""
    # Configurar UTF-8 para Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    print("=" * 70)
    print("  GENERADOR DE REPORTE PDF - ANÁLISIS DE SIMILITUD".center(70))
    print("=" * 70)

    # Rutas
    script_dir = Path(__file__).parent.resolve()
    report_path = script_dir / "consolidado" / "reporte_similitud.json"
    output_path = script_dir / "consolidado" / "reporte_similitud.pdf"

    # Verificar que existe el reporte JSON
    if not report_path.exists():
        print(f"\n❌ Error: No se encuentra el reporte JSON en {report_path}")
        print("   Ejecuta primero batch_consolidator.py para generar el reporte.")
        sys.exit(1)

    print(f"\n📂 Archivo de entrada: {report_path.name}")
    print(f"💾 Archivo de salida: {output_path.name}")

    # Generar PDF
    generator = SimilarityPDFGenerator(report_path, output_path)

    if generator.generate_pdf():
        # Mostrar estadísticas del archivo generado
        file_size_kb = output_path.stat().st_size / 1024
        print(f"\n📊 Tamaño del archivo: {file_size_kb:.2f} KB")
        print("\n" + "=" * 70)
        print("✅ Proceso completado exitosamente")
        print("=" * 70)
    else:
        print("\n❌ No se pudo generar el PDF")
        sys.exit(1)


if __name__ == '__main__':
    main()
