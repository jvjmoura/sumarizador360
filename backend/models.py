from pydantic import BaseModel, Field
from typing import List, Optional

class RespostaDefesa(BaseModel):
    resposta_acusacao: str = Field(..., description="Principais argumentos da resposta à acusação")
    alegacoes_finais: str = Field(..., description="Posição final da defesa")
    advogado_responsavel: str = Field(..., description="Nome do(a) advogado(a)")
    depoimentos_favoraveis: List[str] = Field(default=[], description="Testemunhas pró-defesa")
    teses_defensivas: List[str] = Field(default=[], description="Teses da defesa")
    contradicoes_autos: List[str] = Field(default=[], description="Inconsistências encontradas")
    vicios_processuais: List[str] = Field(default=[], description="Problemas processuais")
    provas_favoraveis: List[str] = Field(default=[], description="Evidências pró-defesa")
    circunstancias_atenuantes: List[str] = Field(default=[], description="Fatores atenuantes")

class RespostaAcusacao(BaseModel):
    denuncia_completa: str = Field(..., description="Resumo da acusação inicial")
    alegacoes_finais_mp: str = Field(..., description="Posição final do MP")
    promotor_responsavel: str = Field(..., description="Nome do(a) promotor(a)")
    tipificacao_penal: str = Field(..., description="Crime imputado")
    materialidade_crime: str = Field(..., description="Provas do fato criminoso")
    autoria: str = Field(..., description="Evidências contra o réu")
    depoimentos_acusacao: List[str] = Field(default=[], description="Testemunhas de acusação")
    laudos_pericias: List[str] = Field(default=[], description="Relatórios técnicos")
    provas_materiais: List[str] = Field(default=[], description="Evidências físicas")
    pedidos_mp: List[str] = Field(default=[], description="Pedidos do MP")

class RespostaPesquisa(BaseModel):
    legislacao_defesa: List[str] = Field(default=[], description="Legislação citada pela defesa")
    legislacao_mp: List[str] = Field(default=[], description="Legislação citada pelo MP")
    legislacao_juiz: List[str] = Field(default=[], description="Legislação citada pelo juiz")
    jurisprudencia_stf: List[str] = Field(default=[], description="Jurisprudências do STF")
    jurisprudencia_stj: List[str] = Field(default=[], description="Jurisprudências do STJ")
    jurisprudencia_tj: List[str] = Field(default=[], description="Jurisprudências de TJ")
    sumulas_aplicaveis: List[str] = Field(default=[], description="Súmulas citadas")
    doutrina_citada: List[str] = Field(default=[], description="Doutrinas referenciadas")
    precedentes_relevantes: List[str] = Field(default=[], description="Precedentes importantes")
    fundamentacao_legal: str = Field(..., description="Base legal geral")

class RespostaDecisoes(BaseModel):
    sentenca_final: str = Field(..., description="Sentença final")
    juiz_responsavel: str = Field(..., description="Nome do magistrado")
    pena_fixada: Optional[str] = Field(None, description="Pena aplicada")
    regime_cumprimento: Optional[str] = Field(None, description="Regime da pena")
    recurso_em_liberdade: Optional[bool] = Field(None, description="Recurso em liberdade")
    manutencao_prisao: Optional[bool] = Field(None, description="Prisão mantida")
    dosimetria_completa: Optional[str] = Field(None, description="Dosimetria da pena")
    decisoes_prisao: List[str] = Field(default=[], description="Decisões sobre prisão")
    fundamentacao_juridica: str = Field(..., description="Fundamentação do juiz")
    analise_provas: str = Field(..., description="Análise das provas")
    despachos_relevantes: List[str] = Field(default=[], description="Despachos importantes")
    recursos_cabiveis: List[str] = Field(default=[], description="Recursos cabíveis")
    medidas_aplicadas: List[str] = Field(default=[], description="Medidas aplicadas")
    cronologia_decisoes: List[str] = Field(default=[], description="Cronologia das decisões")

class RelatorioConsolidado(BaseModel):
    """Relatório consolidado neutro de todos os agentes"""
    # Identificação do Processo
    numero_processo: str = Field(..., description="Número do processo")
    natureza_acao: str = Field(..., description="Natureza da ação penal")

    # Consolidação da Defesa
    defesa_consolidada: str = Field(..., description="Consolidação das manifestações defensivas")
    advogado_identificado: str = Field(..., description="Advogado(a) responsável identificado")
    teses_defensivas_listadas: List[str] = Field(default=[], description="Lista de todas as teses defensivas")
    vicios_alegados: List[str] = Field(default=[], description="Vícios processuais alegados")

    # Consolidação da Acusação
    acusacao_consolidada: str = Field(..., description="Consolidação das manifestações acusatórias")
    promotor_identificado: str = Field(..., description="Promotor(a) responsável identificado")
    tipificacao_consolidada: str = Field(..., description="Tipificação penal consolidada")
    elementos_materialidade: List[str] = Field(default=[], description="Elementos de materialidade apresentados")
    elementos_autoria: List[str] = Field(default=[], description="Elementos de autoria apresentados")

    # Consolidação da Pesquisa Jurídica
    legislacao_consolidada: str = Field(..., description="Toda legislação citada consolidada")
    jurisprudencia_consolidada: str = Field(..., description="Toda jurisprudência citada consolidada")
    sumulas_consolidadas: List[str] = Field(default=[], description="Todas as súmulas citadas")
    doutrina_consolidada: List[str] = Field(default=[], description="Toda doutrina citada")

    # Consolidação das Decisões
    decisoes_consolidadas: str = Field(..., description="Todas as decisões judiciais consolidadas")
    magistrado_identificado: str = Field(..., description="Magistrado(a) responsável identificado")
    penas_aplicadas: List[str] = Field(default=[], description="Todas as penas aplicadas")
    medidas_aplicadas: List[str] = Field(default=[], description="Todas as medidas aplicadas")

    # Cronologia Geral
    cronologia_completa: List[str] = Field(default=[], description="Cronologia completa do processo")

    # Elementos Probatórios
    provas_consolidadas: str = Field(..., description="Consolidação de todas as provas")
    depoimentos_consolidados: str = Field(..., description="Consolidação de todos os depoimentos")
    laudos_consolidados: str = Field(..., description="Consolidação de todos os laudos")

    # Recursos e Medidas
    recursos_identificados: List[str] = Field(default=[], description="Todos os recursos identificados")
    medidas_cautelares: List[str] = Field(default=[], description="Todas as medidas cautelares")

# Modelos para API requests/responses
class AnalysisRequest(BaseModel):
    agents: List[str] = Field(..., description="Lista de agentes a serem executados")

class AnalysisResponse(BaseModel):
    status: str = Field(..., description="Status da análise")
    task_id: str = Field(..., description="ID da tarefa para acompanhamento")
    message: str = Field(..., description="Mensagem informativa")

class AnalysisResult(BaseModel):
    task_id: str = Field(..., description="ID da tarefa")
    status: str = Field(..., description="Status: pending, processing, completed, error")
    progress: int = Field(default=0, description="Progresso de 0 a 100")
    results: dict = Field(default={}, description="Resultados dos agentes")
    error: Optional[str] = Field(None, description="Mensagem de erro, se houver")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Mensagem de erro")
    detail: Optional[str] = Field(None, description="Detalhes do erro")