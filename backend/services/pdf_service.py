import os
import tempfile
from typing import Optional
import PyPDF2
import pymupdf  # fitz
import pytesseract
from PIL import Image
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue, gray
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from io import BytesIO
import json
from datetime import datetime
from typing import Dict, Any

class PDFProcessingService:
    """Serviço para processamento de PDFs de entrada"""

    @staticmethod
    def validate_pdf(file_path: str) -> bool:
        """Valida se o arquivo é um PDF válido"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                return len(reader.pages) > 0
        except Exception:
            return False

    @staticmethod
    def extract_text_pypdf2(file_path: str) -> str:
        """Extrai texto usando PyPDF2"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            raise Exception(f"Erro ao extrair texto com PyPDF2: {str(e)}")

    @staticmethod
    def extract_text_pymupdf(file_path: str) -> str:
        """Extrai texto usando PyMuPDF (melhor para OCR)"""
        try:
            doc = pymupdf.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            return text
        except Exception as e:
            raise Exception(f"Erro ao extrair texto com PyMuPDF: {str(e)}")

    @staticmethod
    def extract_text_with_ocr(file_path: str) -> str:
        """Extrai texto usando OCR para PDFs digitalizados"""
        try:
            doc = pymupdf.open(file_path)
            text = ""

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)

                # Converter página para imagem
                pix = page.get_pixmap()
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))

                # Aplicar OCR
                page_text = pytesseract.image_to_string(img, lang='por')
                text += page_text + "\n"

            doc.close()
            return text
        except Exception as e:
            raise Exception(f"Erro ao extrair texto com OCR: {str(e)}")

    @staticmethod
    def get_pdf_info(file_path: str) -> dict:
        """Obtém informações do PDF"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                info = {
                    "pages": len(reader.pages),
                    "metadata": reader.metadata,
                    "encrypted": reader.is_encrypted
                }
                return info
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def extract_text_smart(file_path: str, use_ocr: bool = True) -> str:
        """
        Extração inteligente de texto:
        1. Tenta PyMuPDF primeiro (mais rápido)
        2. Se texto é muito pequeno e use_ocr=True, aplica OCR
        3. Fallback para PyPDF2
        """
        try:
            # Primeira tentativa: PyMuPDF
            text = PDFProcessingService.extract_text_pymupdf(file_path)

            # Se texto é muito pequeno e OCR está habilitado
            if len(text.strip()) < 100 and use_ocr:
                try:
                    ocr_text = PDFProcessingService.extract_text_with_ocr(file_path)
                    if len(ocr_text.strip()) > len(text.strip()):
                        return ocr_text
                except Exception:
                    pass  # Continua com o texto original

            return text

        except Exception:
            # Fallback para PyPDF2
            try:
                return PDFProcessingService.extract_text_pypdf2(file_path)
            except Exception as e:
                raise Exception(f"Falha em todos os métodos de extração: {str(e)}")

class PDFGenerationService:
    """Serviço para geração de PDFs dos resultados da análise"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configurar estilos personalizados para o PDF"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Title'],
            fontSize=20,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=blue
        ))

        # Título de seção
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=24,
            textColor=blue
        ))

        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=6,
            spaceBefore=12,
            textColor=black
        ))

        # Texto normal justificado
        self.styles.add(ParagraphStyle(
            name='JustifiedBody',
            parent=self.styles['Normal'],
            alignment=TA_JUSTIFY,
            spaceAfter=6
        ))

    def generate_agent_pdf(self, agent_name: str, agent_data: Dict[str, Any], task_id: str) -> BytesIO:
        """Gerar PDF para um agente específico"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)

        # Conteúdo do PDF
        story = []

        # Cabeçalho
        story.append(Paragraph("⚖️ Sistema de Análise Jurídica", self.styles['MainTitle']))
        story.append(Spacer(1, 20))

        # Informações do relatório
        info_data = [
            ['Agente:', self._get_agent_display_name(agent_name)],
            ['ID da Tarefa:', task_id],
            ['Data/Hora:', datetime.now().strftime("%d/%m/%Y às %H:%M:%S")],
            ['Tipo de Relatório:', 'Análise Individual por Agente']
        ]

        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(info_table)
        story.append(Spacer(1, 30))

        # Conteúdo da análise
        story.append(Paragraph(f"Resultado da Análise - {self._get_agent_display_name(agent_name)}",
                              self.styles['SectionTitle']))

        if isinstance(agent_data, dict):
            for key, value in agent_data.items():
                if value and value != '' and not (isinstance(value, list) and len(value) == 0):
                    # Título do campo
                    field_title = self._format_field_name(key)
                    story.append(Paragraph(field_title, self.styles['SubTitle']))

                    # Conteúdo do campo
                    if isinstance(value, list):
                        for item in value:
                            story.append(Paragraph(f"• {str(item)}", self.styles['JustifiedBody']))
                    else:
                        story.append(Paragraph(str(value), self.styles['JustifiedBody']))

                    story.append(Spacer(1, 12))
        else:
            story.append(Paragraph(str(agent_data), self.styles['JustifiedBody']))

        # Rodapé
        story.append(Spacer(1, 30))
        story.append(Paragraph("Sistema de Análise Jurídica - Relatório gerado automaticamente",
                              self.styles['Normal']))

        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_combined_pdf(self, all_results: Dict[str, Any], task_id: str) -> BytesIO:
        """Gerar PDF consolidado com todos os resultados"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)

        story = []

        # Cabeçalho
        story.append(Paragraph("⚖️ Sistema de Análise Jurídica", self.styles['MainTitle']))
        story.append(Paragraph("Relatório Consolidado de Análise", self.styles['Title']))
        story.append(Spacer(1, 20))

        # Informações do relatório
        info_data = [
            ['ID da Tarefa:', task_id],
            ['Data/Hora:', datetime.now().strftime("%d/%m/%Y às %H:%M:%S")],
            ['Tipo de Relatório:', 'Análise Completa Multi-Agente'],
            ['Agentes Executados:', ', '.join([self._get_agent_display_name(agent) for agent in all_results.keys()])]
        ]

        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(info_table)
        story.append(Spacer(1, 30))

        # Sumário executivo
        story.append(Paragraph("Sumário Executivo", self.styles['SectionTitle']))
        story.append(Paragraph(
            f"Este relatório apresenta a análise automatizada de um processo jurídico realizada por "
            f"{len(all_results)} agentes especializados. Cada agente analisou o documento sob sua "
            f"perspectiva específica, extraindo informações relevantes para uma compreensão abrangente do caso.",
            self.styles['JustifiedBody']
        ))
        story.append(Spacer(1, 20))

        # Ordem de exibição dos agentes
        agent_order = ['defesa', 'acusacao', 'pesquisa', 'decisoes', 'web', 'relator']

        # Processar cada agente
        for agent_key in agent_order:
            if agent_key in all_results:
                agent_data = all_results[agent_key]

                # Título do agente
                story.append(Paragraph(self._get_agent_display_name(agent_key),
                                     self.styles['SectionTitle']))

                if isinstance(agent_data, dict):
                    for key, value in agent_data.items():
                        if value and value != '' and not (isinstance(value, list) and len(value) == 0):
                            # Título do campo
                            field_title = self._format_field_name(key)
                            story.append(Paragraph(field_title, self.styles['SubTitle']))

                            # Conteúdo do campo
                            if isinstance(value, list):
                                for item in value:
                                    story.append(Paragraph(f"• {str(item)}", self.styles['JustifiedBody']))
                            else:
                                story.append(Paragraph(str(value), self.styles['JustifiedBody']))

                            story.append(Spacer(1, 8))
                else:
                    story.append(Paragraph(str(agent_data), self.styles['JustifiedBody']))

                story.append(Spacer(1, 20))

        # Rodapé
        story.append(Spacer(1, 30))
        story.append(Paragraph("Sistema de Análise Jurídica - Relatório consolidado gerado automaticamente",
                              self.styles['Normal']))

        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def _get_agent_display_name(self, agent_key: str) -> str:
        """Obter nome de exibição do agente"""
        agent_names = {
            'defesa': '🛡️ Agente Defesa',
            'acusacao': '⚖️ Agente Acusação',
            'pesquisa': '📚 Agente Pesquisa Jurídica',
            'decisoes': '⚖️ Agente Decisões Judiciais',
            'web': '🌐 Agente Pesquisa Web',
            'relator': '📋 Agente Relator Consolidado'
        }
        return agent_names.get(agent_key, f'Agente {agent_key.title()}')

    def _format_field_name(self, key: str) -> str:
        """Formatar nome do campo para exibição"""
        field_names = {
            'resposta_acusacao': 'Resposta à Acusação',
            'alegacoes_finais': 'Alegações Finais',
            'advogado_responsavel': 'Advogado Responsável',
            'teses_defensivas': 'Teses Defensivas',
            'vicios_processuais': 'Vícios Processuais',
            'denuncia_completa': 'Denúncia Completa',
            'promotor_responsavel': 'Promotor Responsável',
            'tipificacao_penal': 'Tipificação Penal',
            'sentenca_final': 'Sentença Final',
            'juiz_responsavel': 'Juiz Responsável',
            'fundamentacao_legal': 'Fundamentação Legal',
            'jurisprudencia_stf': 'Jurisprudência STF',
            'numero_processo': 'Número do Processo',
            'natureza_acao': 'Natureza da Ação'
        }

        return field_names.get(key, key.replace('_', ' ').title())

# Manter as classes originais para compatibilidade
PDFService = PDFProcessingService

class FileService:
    """Serviço para gerenciamento de arquivos"""

    @staticmethod
    def save_uploaded_file(file_content: bytes, suffix: str = '.pdf') -> str:
        """Salva arquivo uploadado temporariamente"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(file_content)
                return tmp_file.name
        except Exception as e:
            raise Exception(f"Erro ao salvar arquivo: {str(e)}")

    @staticmethod
    def cleanup_file(file_path: str) -> bool:
        """Remove arquivo temporário"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Obtém tamanho do arquivo em bytes"""
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0

class ValidationService:
    """Serviço para validações"""

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

    @staticmethod
    def validate_file_size(file_size: int) -> bool:
        """Valida tamanho do arquivo"""
        return file_size <= ValidationService.MAX_FILE_SIZE

    @staticmethod
    def validate_file_type(filename: str) -> bool:
        """Valida tipo do arquivo"""
        return filename.lower().endswith('.pdf')

    @staticmethod
    def validate_agents(agent_list: list) -> tuple[bool, str]:
        """Valida lista de agentes"""
        valid_agents = ["defesa", "acusacao", "pesquisa", "decisoes", "relator"]

        for agent in agent_list:
            if agent not in valid_agents:
                return False, f"Agente '{agent}' não é válido"

        if len(agent_list) == 0:
            return False, "Pelo menos um agente deve ser selecionado"

        return True, "Agentes válidos"