from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import os
from dotenv import load_dotenv

# Importar routers e modelos
from routers.analysis import router as analysis_router
from models import AnalysisResponse, ErrorResponse

# Carregar variáveis de ambiente
load_dotenv()

# Criar instância do FastAPI
app = FastAPI(
    title="⚖️ Sistema de Análise Jurídica API",
    description="API para análise automatizada de processos jurídicos com IA",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    # Aumentar limite de tamanho de arquivo para 100MB
    max_request_size=100 * 1024 * 1024
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos do frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Servir arquivos CSS e JS diretamente
@app.get("/styles.css")
async def get_styles():
    return FileResponse("../frontend/styles.css", media_type="text/css")

@app.get("/script.js")
async def get_script():
    return FileResponse("../frontend/script.js", media_type="application/javascript")

@app.get("/favicon.ico")
async def get_favicon():
    # Retorna um favicon simples ou 404
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Favicon not found")

# Incluir routers
app.include_router(analysis_router, prefix="/api/v1", tags=["análise"])

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Servir página principal do frontend"""
    try:
        return FileResponse("../frontend/index.html")
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
            <body>
                <h1>⚖️ Sistema de Análise Jurídica API</h1>
                <p>Frontend em desenvolvimento...</p>
                <p><a href="/docs">📖 Documentação da API</a></p>
            </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Verificação de saúde da API"""
    return {
        "status": "healthy",
        "service": "Sistema de Análise Jurídica",
        "version": "2.0.0"
    }

@app.get("/api/v1/agents")
async def list_agents():
    """Lista todos os agentes disponíveis"""
    return {
        "agents": {
            "defesa": {
                "name": "🛡️ Agente Defesa",
                "description": "Analisa argumentos defensivos, teses e alegações da defesa"
            },
            "acusacao": {
                "name": "⚖️ Agente Acusação",
                "description": "Analisa denúncia, alegações do MP e elementos acusatórios"
            },
            "pesquisa": {
                "name": "📚 Agente Pesquisa Jurídica",
                "description": "Extrai legislação, jurisprudências e citações legais"
            },
            "decisoes": {
                "name": "⚖️ Agente Decisões Judiciais",
                "description": "Analisa sentenças, decisões e fundamentação do juiz"
            },
            "web": {
                "name": "🌐 Agente Pesquisa Web",
                "description": "Pesquisa jurisprudências recentes, doutrina e teoria jurídica atual na web"
            },
            "relator": {
                "name": "📋 Agente Relator Consolidado",
                "description": "Consolida informações de todos os agentes em relatório único"
            }
        }
    }

# Handler para erros não tratados
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return ErrorResponse(
        error="Erro interno do servidor",
        detail=str(exc)
    )

if __name__ == "__main__":
    # Configurações para desenvolvimento
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )