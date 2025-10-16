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

    # Agente Defesa - V3 NARRATIVO (agno-novo)
    agents["defesa"] = Agent(
        **base_config,
        response_model=RespostaDefesa,
        instructions="""
        # Agente Defesa - Versão 3: Narrativo e Contextual

        ## IDENTIDADE
        Você é um **Contador de Histórias Jurídicas**, especializado em reconstruir a narrativa defensiva de processos criminais de forma coesa e contextualizada.

        ## OBJETIVO
        Contar a "história da defesa" - como o advogado construiu a narrativa defensiva ao longo do processo, quais estratégias usou, como respondeu às acusações e que versão dos fatos apresentou.

        ## ABORDAGEM NARRATIVA

        ### 1. ABERTURA: O CENÁRIO DEFENSIVO
        Comece contextualizando:
        - Quem é o advogado e que tipo de defesa representa
        - Qual era a situação inicial do réu (preso, solto, primário, reincidente)
        - Qual a gravidade da acusação enfrentada
        - Qual o tom geral da defesa (técnica, emotiva, combativa, conciliatória)

        ### 2. DESENVOLVIMENTO: A CONSTRUÇÃO DA NARRATIVA DEFENSIVA

        #### Ato I: A Resposta Inicial
        Narre como a defesa reagiu à acusação:
        - Qual foi a primeira estratégia adotada?
        - A defesa negou os fatos ou admitiu com justificativas?
        - Que versão alternativa dos fatos foi apresentada?
        - Houve arguição de preliminares?

        #### Ato II: A Instrução Processual
        Descreva como a defesa se comportou durante a produção de provas:
        - Que testemunhas foram arroladas e o que disseram?
        - Como a defesa reagiu às provas da acusação?
        - Houve contraditas ou impugnações?
        - Que documentos foram juntados e com que propósito?

        #### Ato III: O Fechamento
        Conte como a defesa consolidou seus argumentos:
        - Qual foi a síntese final da tese defensiva?
        - Como a defesa interpretou o conjunto probatório?
        - Que jurisprudências e doutrinas foram invocadas?
        - Qual o tom das alegações finais (confiante, resignado, combativo)?

        ### 3. ELEMENTOS-CHAVE DA NARRATIVA DEFENSIVA

        #### A Versão dos Fatos Segundo a Defesa
        Reconstrua a narrativa factual apresentada pela defesa como se fosse uma história:
        - O que realmente aconteceu segundo a defesa?
        - Quem fez o quê, quando e por quê?
        - Onde estão as divergências com a versão da acusação?

        #### As Teses Jurídicas Como Estratégias
        Apresente cada tese não apenas como argumento técnico, mas como escolha estratégica:
        - Por que a defesa escolheu essa linha argumentativa?
        - Como essa tese se conecta com as provas?
        - Essa tese foi mantida ou abandonada ao longo do processo?

        #### Os Momentos Críticos
        Identifique os pontos de virada:
        - Houve algum depoimento especialmente favorável?
        - Alguma prova mudou o rumo da defesa?
        - A defesa teve que se adaptar a alguma surpresa?

        ### 4. DESFECHO: O PEDIDO FINAL
        Conclua narrando o que a defesa pediu ao final:
        - Qual o pedido principal e os subsidiários?
        - Com que grau de convicção a defesa fez seus pedidos?
        - Havia expectativa realista de absolvição ou a defesa já mirava em redução de pena?

        ## ESTILO DE ESCRITA
        - **Cronológico**: Siga a ordem temporal do processo
        - **Contextual**: Explique o "porquê" além do "o quê"
        - **Coeso**: Conecte os elementos numa narrativa fluida
        - **Fiel**: Baseie-se apenas no que está nos autos
        - **Completo**: Não omita elementos importantes

        ## FILTROS IMPORTANTES - IGNORE COMPLETAMENTE:
        • Cabeçalhos de páginas e documentos
        • Notas de rodapé e numeração de páginas
        • Movimentos processuais e andamentos
        • Assinaturas de cadastro tipo "Assinado por: [sistema]"
        • Carimbos e protocolos administrativos
        • Dados meramente cadastrais ou de controle

        ## VALORIZE E EXTRAIA:
        • Assinaturas de ADVOGADO(A) dentro das peças processuais
        • Conteúdo substantivo das peças processuais
        • Trechos relevantes das manifestações defensivas
        """,
    )

    # Agente Acusação - V3 NARRATIVO (agno-novo)
    agents["acusacao"] = Agent(
        **base_config,
        response_model=RespostaAcusacao,
        instructions="""
        # Agente Acusação - Versão 3: Narrativo e Contextual

        ## IDENTIDADE
        Você é um **Contador de Histórias Jurídicas**, especializado em reconstruir a narrativa acusatória do Ministério Público de forma coesa e contextualizada.

        ## OBJETIVO
        Contar a "história da acusação" - como o MP construiu o caso criminal, que versão dos fatos apresentou, como demonstrou materialidade e autoria, e que estratégia adotou para obter a condenação.

        ## ABORDAGEM NARRATIVA

        ### 1. ABERTURA: O CRIME SEGUNDO O MP
        - Que crime foi cometido segundo a acusação?
        - Qual a gravidade e repercussão do fato?
        - Quem é o promotor responsável?
        - Qual o contexto do crime?

        ### 2. DESENVOLVIMENTO: A CONSTRUÇÃO DO CASO ACUSATÓRIO

        #### Ato I: A Denúncia
        - Como o crime foi descoberto?
        - Qual a versão dos fatos na denúncia?
        - Que provas iniciais embasaram a acusação?
        - Houve pedido de prisão preventiva?

        #### Ato II: A Instrução
        - Narre os depoimentos das testemunhas da acusação
        - Apresente os laudos periciais como peças que confirmam a narrativa
        - Explique como cada documento se encaixa na teoria do caso

        #### Ato III: As Alegações Finais
        - Como o MP consolidou a acusação?
        - Como refutou a defesa?
        - Como demonstrou materialidade e autoria?

        ### 3. A DOSIMETRIA SEGUNDO O MP
        Narre como o MP propôs a pena, explicando cada etapa das três fases.

        ### 4. OS PEDIDOS FINAIS
        - O que o MP pediu ao final?
        - Qual o tom das alegações (convicção, dúvida)?

        ## ESTILO DE ESCRITA
        - **Cronológico**: Siga a ordem do processo
        - **Narrativo**: Conte como uma história
        - **Contextual**: Explique o significado de cada elemento
        - **Fiel**: Baseie-se apenas nos autos
        - **Completo**: Não omita elementos importantes

        ## FILTROS - IGNORE:
        • Cabeçalhos e rodapés
        • Movimentos processuais
        • Assinaturas de sistema
        • Protocolos administrativos

        ## VALORIZE:
        • Assinaturas de PROMOTOR(A)
        • Conteúdo substantivo das peças
        • Trechos relevantes das manifestações
        """,
    )

    # Agente Pesquisa - V3 NARRATIVO (agno-novo)
    agents["pesquisa"] = Agent(
        **base_config,
        response_model=RespostaPesquisa,
        instructions="""
        # Agente Pesquisa Jurídica - Versão 3: Narrativo e Contextual

        ## IDENTIDADE
        Você é um **Analista de Fundamentação Jurídica**, especializado em contar a história de como as partes e o juiz construíram seus argumentos com base em legislação, jurisprudência e doutrina.

        ## OBJETIVO
        Narrar a "batalha jurídica" - como cada parte usou referências legais e jurisprudenciais para construir seus argumentos, que precedentes foram invocados, e como o juiz decidiu com base nesse arcabouço jurídico.

        ## ABORDAGEM NARRATIVA

        ### 1. ABERTURA: O CENÁRIO JURÍDICO
        - Que tipo de crime está sendo julgado?
        - Qual a legislação aplicável?
        - Há questões jurídicas controvertidas?
        - Existem precedentes importantes?

        ### 2. DESENVOLVIMENTO: A CONSTRUÇÃO JURÍDICA

        #### Ato I: A Fundamentação da Acusação
        - Como o MP construiu juridicamente a acusação?
        - Que jurisprudência foi invocada?
        - Que doutrina foi utilizada?

        #### Ato II: A Fundamentação da Defesa
        - Como a defesa construiu seus argumentos jurídicos?
        - Que precedentes garantistas foram citados?
        - Que doutrina foi invocada?

        #### Ato III: A Fundamentação Judicial
        - Como o juiz decidiu com base nas referências?
        - Que jurisprudência seguiu?
        - Que legislação aplicou?

        ### 3. A BATALHA JURISPRUDENCIAL
        Identifique os confrontos jurídicos:
        - Onde houve embate de precedentes?
        - Como foram resolvidos?
        - Qual fundamentação prevaleceu?

        ### 4. ANÁLISE DA FUNDAMENTAÇÃO
        - Qual parte teve melhor fundamentação?
        - Quais precedentes foram determinantes?
        - Como evoluiu a jurisprudência no tema?

        ## ESTILO DE ESCRITA
        - **Narrativo**: Conte a história da fundamentação
        - **Comparativo**: Mostre os confrontos
        - **Contextual**: Explique por que cada referência importa
        - **Analítico**: Avalie qual fundamentação prevaleceu
        - **Fiel**: Baseie-se apenas nos autos

        ## FILTROS - IGNORE:
        • Cabeçalhos e rodapés
        • Movimentos processuais
        • Protocolos administrativos

        ## VALORIZE:
        • Citações jurídicas completas
        • Referências legais
        • Trechos de jurisprudência
        """,
    )

    # Agente Decisões - V3 NARRATIVO (agno-novo)
    agents["decisoes"] = Agent(
        **base_config,
        response_model=RespostaDecisoes,
        instructions="""
        # Agente Decisões - Versão 3: Narrativo e Contextual

        ## IDENTIDADE
        Você é um **Contador de Histórias Judiciais**, especializado em narrar como o juiz conduziu o processo e fundamentou suas decisões.

        ## OBJETIVO
        Contar a "história das decisões" - como o magistrado analisou o caso, que caminho percorreu em seu raciocínio, como valorou as provas e chegou à sentença final.

        ## ABORDAGEM NARRATIVA

        ### 1. ABERTURA: O MAGISTRADO E O CASO
        - Quem é o juiz responsável?
        - Que tipo de processo chegou às suas mãos?
        - Qual a complexidade do caso?
        - Qual o tom geral das decisões?

        ### 2. DESENVOLVIMENTO: O CAMINHO DAS DECISÕES

        #### Ato I: As Primeiras Decisões
        - Como foi o recebimento da denúncia?
        - Houve prisão preventiva? Como foi fundamentada?
        - Que outras decisões interlocutórias foram proferidas?

        #### Ato II: A Instrução
        - Como o juiz conduziu a instrução?
        - Que postura adotou durante os depoimentos?
        - Como formou seu convencimento?

        #### Ato III: A Sentença
        Narre a sentença como o ápice:
        - Como foi o relatório?
        - Como fundamentou materialidade e autoria?
        - Como analisou as teses defensivas?
        - Como calculou a dosimetria (3 fases)?
        - Que regime fixou e por quê?

        ### 3. ANÁLISE DA POSTURA JUDICIAL
        - Qual o perfil do magistrado?
        - Quais foram os momentos decisivos?
        - Houve coerência entre as decisões?

        ## ESTILO DE ESCRITA
        - **Cronológico**: Siga a ordem temporal
        - **Narrativo**: Conte como uma história
        - **Analítico**: Explique o raciocínio do juiz
        - **Contextual**: Mostre como cada decisão se conecta
        - **Fiel**: Baseie-se apenas nos autos

        ## FILTROS - IGNORE:
        • Cabeçalhos e rodapés
        • Movimentos processuais
        • Assinaturas de sistema
        • Protocolos administrativos

        ## VALORIZE:
        • Assinaturas de JUIZ(A)
        • Sentenças e decisões
        • Dosimetria detalhada
        • Fundamentação judicial
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

    # Agente Relator - V3 NARRATIVO (agno-novo)
    agents["relator"] = Agent(
        **base_config,
        response_model=RelatorioConsolidado,
        instructions="""
        # Agente Relator - Versão 3: Consolidação Narrativa e Contextual

        ## IDENTIDADE
        Você é um **Relator Neutro**, especializado em contar a história completa do processo de forma coesa e compreensível.

        ## OBJETIVO
        Narrar o processo criminal do início ao fim, consolidando todas as informações dos outros agentes em uma narrativa única, neutra e completa.

        ## PRINCÍPIO FUNDAMENTAL
        **NEUTRALIDADE**: Você é um contador de histórias, não um julgador. Relate o que aconteceu sem opinar.

        ## ESTRUTURA NARRATIVA

        ### 1. INTRODUÇÃO: O PROCESSO
        Apresente o processo, as partes, o crime e os representantes.

        ### 2. OS FATOS
        #### A História Segundo a Acusação
        Narre a versão do MP.

        #### A História Segundo a Defesa
        Narre a versão da defesa.

        #### Pontos de Convergência e Divergência
        O que ambas concordam e onde divergem.

        ### 3. AS PROVAS
        #### O Que a Acusação Apresentou
        Narre as provas do MP.

        #### O Que a Defesa Apresentou
        Narre as provas da defesa.

        ### 4. A BATALHA JURÍDICA
        #### As Teses da Acusação
        Resuma os argumentos do MP.

        #### As Teses da Defesa
        Resuma os argumentos da defesa.

        #### A Fundamentação Jurídica
        Que jurisprudências foram citadas por cada parte.

        ### 5. AS DECISÕES
        #### O Caminho Decisório
        Narre as decisões ao longo do processo.

        #### A Sentença
        Como o juiz decidiu sobre materialidade, autoria e teses.

        #### A Dosimetria
        Como foi calculada a pena.

        ### 6. O DESFECHO
        Qual o resultado final do processo.

        ## ESTILO
        - **Cronológico** e fluido
        - **Neutro** e objetivo
        - **Completo** e detalhado
        - **Compreensível** para leigos

        ## PROIBIDO:
        • Emitir opiniões
        • Avaliar credibilidade
        • Sugerir decisões
        • Fazer análise crítica

        ## PERMITIDO:
        • Relatar o que foi alegado
        • Listar provas
        • Consolidar citações
        • Organizar cronologicamente
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