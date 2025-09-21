import os
import tempfile
from typing import Optional
import PyPDF2
import pymupdf  # fitz
import pytesseract
from PIL import Image
import io

class PDFService:
    """Serviço para processamento de PDFs"""

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
            text = PDFService.extract_text_pymupdf(file_path)

            # Se texto é muito pequeno e OCR está habilitado
            if len(text.strip()) < 100 and use_ocr:
                try:
                    ocr_text = PDFService.extract_text_with_ocr(file_path)
                    if len(ocr_text.strip()) > len(text.strip()):
                        return ocr_text
                except Exception:
                    pass  # Continua com o texto original

            return text

        except Exception:
            # Fallback para PyPDF2
            try:
                return PDFService.extract_text_pypdf2(file_path)
            except Exception as e:
                raise Exception(f"Falha em todos os métodos de extração: {str(e)}")

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