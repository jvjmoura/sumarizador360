from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import tempfile
import os
import uuid
import asyncio
from typing import Dict, List
import json

# Importar serviços e modelos
from models import *
from agents import setup_knowledge_base, setup_agents, executar_agentes_paralelo, executar_relator_consolidado

router = APIRouter()

# Armazenamento em memória para tarefas (em produção, usar Redis ou banco de dados)
tasks_storage: Dict[str, AnalysisResult] = {}

@router.post("/upload", response_model=AnalysisResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    agents: str = "defesa,acusacao,pesquisa,decisoes"
):
    """
    Upload de arquivo PDF e início da análise em background
    """
    # Validar arquivo
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos")

    # Validar agentes
    agent_list = [agent.strip() for agent in agents.split(',')]
    valid_agents = ["defesa", "acusacao", "pesquisa", "decisoes", "relator"]

    for agent in agent_list:
        if agent not in valid_agents:
            raise HTTPException(
                status_code=400,
                detail=f"Agente '{agent}' não é válido. Agentes válidos: {valid_agents}"
            )

    # Criar ID da tarefa
    task_id = str(uuid.uuid4())

    # Inicializar status da tarefa
    tasks_storage[task_id] = AnalysisResult(
        task_id=task_id,
        status="pending",
        progress=0,
        results={}
    )

    # Salvar arquivo temporário
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            pdf_path = tmp_file.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {str(e)}")

    # Iniciar processamento em background
    background_tasks.add_task(process_document, task_id, pdf_path, agent_list)

    return AnalysisResponse(
        status="accepted",
        task_id=task_id,
        message=f"Arquivo '{file.filename}' recebido. Processamento iniciado com agentes: {agent_list}"
    )

async def process_document(task_id: str, pdf_path: str, agent_list: List[str]):
    """
    Processa o documento em background
    """
    try:
        # Atualizar status
        tasks_storage[task_id].status = "processing"
        tasks_storage[task_id].progress = 10

        # Setup do knowledge base
        knowledge_base = setup_knowledge_base(pdf_path)
        tasks_storage[task_id].progress = 30

        # Setup dos agentes
        agents = setup_agents(knowledge_base)
        tasks_storage[task_id].progress = 40

        # Separar agentes normais do relator
        agentes_normais = [agent for agent in agent_list if agent != "relator"]
        incluir_relator = "relator" in agent_list

        resultados = {}

        # Executar agentes normais em paralelo
        if agentes_normais:
            tasks_storage[task_id].progress = 50
            resultados = await executar_agentes_paralelo(agents, agentes_normais)
            tasks_storage[task_id].progress = 70

        # Executar relator se solicitado
        if incluir_relator and resultados:
            tasks_storage[task_id].progress = 80
            relatorio_resultado = executar_relator_consolidado(agents["relator"], resultados)
            resultados["relator"] = relatorio_resultado
            tasks_storage[task_id].progress = 90

        # Converter resultados para formato serializável
        serialized_results = {}
        for agent_key, resultado in resultados.items():
            if hasattr(resultado, 'dict'):
                serialized_results[agent_key] = resultado.dict()
            else:
                serialized_results[agent_key] = str(resultado)

        # Finalizar
        tasks_storage[task_id].status = "completed"
        tasks_storage[task_id].progress = 100
        tasks_storage[task_id].results = serialized_results

    except Exception as e:
        tasks_storage[task_id].status = "error"
        tasks_storage[task_id].error = str(e)

    finally:
        # Limpar arquivo temporário
        try:
            os.unlink(pdf_path)
        except:
            pass

@router.get("/status/{task_id}", response_model=AnalysisResult)
async def get_task_status(task_id: str):
    """
    Obter status de uma tarefa de análise
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    return tasks_storage[task_id]

@router.get("/result/{task_id}")
async def get_task_result(task_id: str):
    """
    Obter resultado completo de uma tarefa
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    task = tasks_storage[task_id]

    if task.status == "completed":
        return {
            "task_id": task_id,
            "status": task.status,
            "results": task.results
        }
    elif task.status == "error":
        return {
            "task_id": task_id,
            "status": task.status,
            "error": task.error
        }
    else:
        return {
            "task_id": task_id,
            "status": task.status,
            "progress": task.progress,
            "message": "Processamento em andamento..."
        }

@router.get("/result/{task_id}/agent/{agent_name}")
async def get_agent_result(task_id: str, agent_name: str):
    """
    Obter resultado de um agente específico
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    task = tasks_storage[task_id]

    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Tarefa ainda não foi concluída")

    if agent_name not in task.results:
        raise HTTPException(status_code=404, detail=f"Resultado do agente '{agent_name}' não encontrado")

    return {
        "task_id": task_id,
        "agent": agent_name,
        "result": task.results[agent_name]
    }

@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """
    Remover uma tarefa do storage
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    del tasks_storage[task_id]

    return {"message": f"Tarefa {task_id} removida com sucesso"}

@router.get("/tasks")
async def list_tasks():
    """
    Listar todas as tarefas
    """
    return {
        "tasks": [
            {
                "task_id": task_id,
                "status": task.status,
                "progress": task.progress
            }
            for task_id, task in tasks_storage.items()
        ]
    }