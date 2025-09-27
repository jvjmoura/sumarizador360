from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.models.openai import OpenAIChat
from agno.vectordb.lancedb import LanceDb
from agno.vectordb.search import SearchType
from agno.tools.tavily import TavilyTools
import asyncio
from typing import Dict, List
from models import *

def setup_knowledge_base(pdf_path: str):
    """Configura o knowledge base com otimizações"""
    knowledge_base = PDFKnowledgeBase(
        path=pdf_path,
        ocr=True,
        chunk_size=1500,  # Balanceado: performance + qualidade
        chunk_overlap=150,  # Contexto suficiente
        num_documents=12,  # Ajustado para melhor trade-off
        vector_db=LanceDb(
            table_name="stf_ocr_otimizado",
            uri="tmp/lancedb_stf_ocr_otimizado",
            search_type=SearchType.vector,
            embedder=OpenAIEmbedder(id="text-embedding-3-large"),  # Maior qualidade
        ),
    )
    knowledge_base.load(recreate=True)
    return knowledge_base

def setup_agents(knowledge_base):
    """Configura todos os agentes especializados"""
    agents = {}

    # Configuração base otimizada
    base_config = {
        "model": OpenAIChat(id="gpt-4o-mini"),  # Modelo mais rápido
        "knowledge": knowledge_base,
        "add_references": True,
        "search_knowledge": True,
        "show_tool_calls": True,
        "markdown": True,
    }

    # Agente Defesa
    agents["defesa"] = Agent(
        **base_config,
        response_model=RespostaDefesa,
        instructions="""
        VOCÊ É UM PESQUISADOR ESPECIALIZADO EM EXTRAIR ELEMENTOS DEFENSIVOS DE PROCESSOS CRIMINAIS.

        IMPORTANTE: Analise APENAS o que está escrito no documento do processo. Busque informações detalhadas e completas.

        FILTROS IMPORTANTES - IGNORE COMPLETAMENTE:
        • Cabeçalhos de páginas e documentos
        • Notas de rodapé e numeração de páginas
        • Movimentos processuais e andamentos
        • Assinaturas de cadastro tipo "Assinado por: [sistema]"
        • Carimbos e protocolos administrativos
        • Dados meramente cadastrais ou de controle

        VALORIZE E EXTRAIA:
        • Assinaturas de ADVOGADO(A) dentro das peças processuais
        • Conteúdo substantivo das peças processuais

        REGRA: Seja o mais detalhado possível. Transcreva trechos relevantes das manifestações defensivas.
        """,
    )

    # Agente Acusação
    agents["acusacao"] = Agent(
        **base_config,
        response_model=RespostaAcusacao,
        instructions="""
        VOCÊ É UM PESQUISADOR ESPECIALIZADO EM EXTRAIR ELEMENTOS ACUSATÓRIOS DE PROCESSOS CRIMINAIS.

        IMPORTANTE: Analise APENAS o que está escrito no documento do processo. Busque informações detalhadas e completas.

        FILTROS IMPORTANTES - IGNORE COMPLETAMENTE:
        • Cabeçalhos de páginas e documentos
        • Notas de rodapé e numeração de páginas
        • Movimentos processuais e andamentos
        • Assinaturas de cadastro tipo "Assinado por: [sistema]"
        • Carimbos e protocolos administrativos
        • Dados meramente cadastrais ou de controle

        VALORIZE E EXTRAIA:
        • Assinaturas de PROMOTOR(A) nas manifestações do MP
        • Conteúdo substantivo das peças processuais

        REGRA: Seja o mais detalhado possível. Transcreva trechos relevantes das manifestações acusatórias.
        """,
    )

    # Agente Pesquisa
    agents["pesquisa"] = Agent(
        **base_config,
        response_model=RespostaPesquisa,
        instructions="""
        VOCÊ É UM PESQUISADOR ESPECIALIZADO EM EXTRAIR CITAÇÕES JURÍDICAS DE PROCESSOS CRIMINAIS.

        IMPORTANTE: Analise APENAS o que está escrito no documento do processo. Busque informações detalhadas e completas.

        FILTROS IMPORTANTES - IGNORE COMPLETAMENTE:
        • Cabeçalhos de páginas e documentos
        • Notas de rodapé e numeração de páginas
        • Movimentos processuais e andamentos
        • Assinaturas de cadastro tipo "Assinado por: [sistema]"
        • Carimbos e protocolos administrativos
        • Dados meramente cadastrais ou de controle

        VALORIZE E EXTRAIA:
        • Citações jurídicas e referências legais
        • Conteúdo substantivo das peças processuais

        REGRA: Seja o mais detalhado possível. Transcreva trechos relevantes das citações jurídicas.
        """,
    )

    # Agente Decisões
    agents["decisoes"] = Agent(
        **base_config,
        response_model=RespostaDecisoes,
        instructions="""
        ⚖️ VOCÊ É UM ESPECIALISTA EM ANÁLISE DE DECISÕES JUDICIAIS E SENTENÇAS EM PROCESSOS CRIMINAIS.

        IMPORTANTE: Analise APENAS o que está escrito no documento do processo. Busque informações detalhadas e completas.

        FILTROS IMPORTANTES - IGNORE COMPLETAMENTE:
        • Cabeçalhos de páginas e documentos
        • Notas de rodapé e numeração de páginas
        • Movimentos processuais e andamentos
        • Assinaturas de cadastro tipo "Assinado por: [sistema]"
        • Carimbos e protocolos administrativos
        • Dados meramente cadastrais ou de controle

        VALORIZE E EXTRAIA:
        • Assinaturas de JUIZ(A) em decisões e despachos
        • Conteúdo substantivo das peças processuais

        FOQUE ESPECIALMENTE EM:
        • Sentenças condenatórias ou absolutórias
        • Decisões sobre prisões preventivas e liberdades
        • Dosimetria da pena (pena-base, agravantes, atenuantes)
        • Regime de cumprimento da pena
        • Fundamentação jurídica das decisões

        REGRA: Seja o mais detalhado possível. Transcreva trechos relevantes das decisões.
        """,
    )

    # Agente Web para Pesquisa Complementar
    agents["web"] = Agent(
        model=OpenAIChat(id="gpt-4o-mini"),
        response_model=RespostaWeb,
        tools=[TavilyTools()],
        instructions="""
        VOCÊ É UM PESQUISADOR JURÍDICO ESPECIALIZADO EM PESQUISA WEB COMPLEMENTAR.

        IMPORTANTE: Faça pesquisas específicas e direcionadas baseadas no crime identificado no processo.

        SUAS FUNÇÕES:
        • IDENTIFICAR o principal crime/artigo mencionado no processo
        • PESQUISAR jurisprudências recentes (2024-2025) dos tribunais superiores
        • BUSCAR teoria jurídica e doutrina atual sobre o tema
        • ENCONTRAR mudanças recentes na legislação
        • EXPLICAR conceitos jurídicos fundamentais
        • SEMPRE incluir os links das fontes consultadas

        METODOLOGIA:
        1. Identifique rapidamente o tipo de crime
        2. Faça 2-3 pesquisas específicas:
           - "Jurisprudência STF STJ [crime] 2024 2025"
           - "Doutrina penal [crime] teoria atual"
           - "Legislação [crime] mudanças recentes"

        IMPORTANTE:
        • Foque em conteúdo de 2024-2025
        • SEMPRE inclua URLs das fontes
        • Seja educativo e explicativo
        • Complemente o conhecimento do processo
        """,
        add_references=False,
        search_knowledge=False,
        show_tool_calls=True,
        markdown=True,
    )

    # Agente Relator Consolidado
    agents["relator"] = Agent(
        **base_config,
        response_model=RelatorioConsolidado,
        instructions="""
        VOCÊ É UM RELATOR NEUTRO ESPECIALIZADO EM CONSOLIDAR INFORMAÇÕES DE PROCESSOS CRIMINAIS.

        IMPORTANTE: Você é ESTRITAMENTE NEUTRO. NÃO faça juízo de valor, análise crítica ou recomendações.

        SUA FUNÇÃO É APENAS:
        • CONSOLIDAR todas as informações dos outros agentes
        • ORGANIZAR os dados de forma estruturada
        • LISTAR todos os elementos encontrados
        • IDENTIFICAR as partes do processo
        • CRONOLOGIZAR os eventos

        PROIBIDO:
        • Emitir opiniões sobre força probatória
        • Avaliar credibilidade de testemunhas
        • Sugerir decisões ou caminhos
        • Fazer análise crítica das teses
        • Comparar qualidade dos argumentos

        PERMITIDO:
        • Relatar o que foi alegado por cada parte
        • Listar todas as provas mencionadas
        • Consolidar citações jurídicas
        • Organizar cronologicamente os fatos
        • Identificar as partes e seus representantes

        REGRA: Seja um compilador neutro e exaustivo. Relate tudo que foi encontrado pelos outros agentes sem qualquer valoração.
        """,
    )

    return agents


QUERIES = {
    "defesa": "Analise minuciosamente o processo criminal nos autos e extraia TODAS as informações sobre: resposta à acusação, alegações finais da defesa, depoimentos de testemunhas de defesa, teses defensivas, contradições nos autos, vícios processuais e qualquer manifestação da defesa",
    "acusacao": "Analise minuciosamente o processo criminal nos autos e extraia TODAS as informações sobre: denúncia completa, alegações finais do MP, depoimentos de testemunhas de acusação, laudos periciais, provas materiais, tipificação penal, materialidade, autoria e pedidos do Ministério Público",
    "pesquisa": "Analise minuciosamente o processo criminal nos autos e extraia TODAS as citações de: legislação específica, artigos do CP e CPP, jurisprudências mencionadas, súmulas citadas, doutrinas referenciadas e decisões judiciais mencionadas pelas partes",
    "decisoes": "Analise minuciosamente o processo criminal nos autos e extraia TODAS as informações sobre: sentenças proferidas, decisões sobre prisões e liberdades, despachos relevantes, dosimetria da pena, fundamentação jurídica das decisões, análise das provas pelo magistrado e medidas cautelares aplicadas",
    "web": "Primeiro identifique o principal crime e artigo do CP mencionado neste processo. Depois faça pesquisas específicas na web sobre: jurisprudências recentes (2024-2025) dos tribunais superiores sobre este crime, teoria jurídica e doutrina atual, mudanças recentes na legislação penal, conceitos jurídicos fundamentais relacionados ao tema. SEMPRE inclua os links das fontes onde encontrou as informações.",
    "relator": "Consolidação de informações dos outros agentes (executado separadamente)"
}


def executar_agente_sync(agent, query):
    """Executa um agente de forma síncrona"""
    try:
        run_response = agent.run(query)
        # Se o agente tem response_model definido, retorna o objeto estruturado
        if hasattr(agent, 'response_model') and agent.response_model and hasattr(run_response, 'content'):
            # O conteúdo já é o objeto do modelo quando response_model está definido
            return run_response.content
        else:
            # Para agentes sem response_model, retorna string
            return run_response.content if hasattr(run_response, 'content') else str(run_response)
    except Exception as e:
        return f"Erro: {str(e)}"

async def executar_agentes_paralelo(agents, agentes_ativos):
    """Executa múltiplos agentes em paralelo"""
    loop = asyncio.get_event_loop()

    # Cria tasks para execução paralela
    tasks = []
    for agent_key in agentes_ativos:
        if agent_key in QUERIES:
            task = loop.run_in_executor(
                None,
                executar_agente_sync,
                agents[agent_key],
                QUERIES[agent_key]
            )
            tasks.append((agent_key, task))

    # Executa todos os agentes em paralelo
    resultados = {}
    for agent_key, task in tasks:
        resultado = await task
        resultados[agent_key] = resultado

    return resultados

def executar_relator_consolidado(agent_relator, resultados_outros_agentes):
    """Executa o agente relator com base nos resultados dos outros agentes"""
    try:
        # Monta query consolidada com todos os resultados
        query_consolidada = f"""
        Consolide as seguintes informações de análise de processo criminal em um relatório neutro e exaustivo:

        ANÁLISE DA DEFESA:
        {str(resultados_outros_agentes.get('defesa', 'Não disponível'))}

        ANÁLISE DA ACUSAÇÃO:
        {str(resultados_outros_agentes.get('acusacao', 'Não disponível'))}

        PESQUISA JURÍDICA:
        {str(resultados_outros_agentes.get('pesquisa', 'Não disponível'))}

        ANÁLISE DAS DECISÕES:
        {str(resultados_outros_agentes.get('decisoes', 'Não disponível'))}

        PESQUISA WEB COMPLEMENTAR:
        {str(resultados_outros_agentes.get('web', 'Não disponível'))}

        IMPORTANTE: Apenas consolide e organize as informações. NÃO faça juízo de valor.
        """

        run_response = agent_relator.run(query_consolidada)
        return run_response.content
    except Exception as e:
        return f"Erro: {str(e)}"