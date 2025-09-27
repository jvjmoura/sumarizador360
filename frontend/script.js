// ===== CONFIGURAÇÕES GLOBAIS =====
const API_BASE_URL = 'http://localhost:8000/api/v1';
let currentTaskId = null;
let progressInterval = null;

// ===== NAVEGAÇÃO =====
function showSection(sectionId) {
    // Remove active de todas as seções
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Remove active de todos os nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });

    // Ativa a seção selecionada
    document.getElementById(sectionId).classList.add('active');

    // Ativa o nav link correspondente
    document.querySelector(`[onclick="showSection('${sectionId}')"]`).classList.add('active');
}

// ===== SISTEMA DE NOTIFICAÇÕES =====
function showNotification(message, type = 'info', duration = 5000) {
    const container = document.getElementById('notificationContainer');
    const notification = document.createElement('div');

    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" style="
                background: none;
                border: none;
                font-size: 16px;
                cursor: pointer;
                margin-left: auto;
                opacity: 0.7;
            ">×</button>
        </div>
    `;

    container.appendChild(notification);

    // Auto remove após duração especificada
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, duration);
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'fa-check-circle',
        'error': 'fa-exclamation-circle',
        'warning': 'fa-exclamation-triangle',
        'info': 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

// ===== GERENCIAMENTO DE ARQUIVOS =====
let selectedFile = null;

function dragOverHandler(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
}

function dragEnterHandler(event) {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
}

function dragLeaveHandler(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
}

function dropHandler(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');

    const files = event.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    // Validar tipo de arquivo
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showNotification('Apenas arquivos PDF são aceitos!', 'error');
        return;
    }

    // Validar tamanho (50MB)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
        showNotification('Arquivo muito grande! Máximo 50MB.', 'error');
        return;
    }

    selectedFile = file;
    showFileInfo(file);
    updateUploadButton();
}

function showFileInfo(file) {
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');

    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);

    fileInfo.style.display = 'block';
    document.getElementById('fileUpload').style.display = 'none';
}

function removeFile() {
    selectedFile = null;
    document.getElementById('fileInfo').style.display = 'none';
    document.getElementById('fileUpload').style.display = 'block';
    document.getElementById('fileInput').value = '';
    updateUploadButton();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// ===== GERENCIAMENTO DE AGENTES =====
function selectAllAgents() {
    document.querySelectorAll('input[name="agents"]').forEach(checkbox => {
        checkbox.checked = true;
    });
    updateUploadButton();
}

function clearAllAgents() {
    document.querySelectorAll('input[name="agents"]').forEach(checkbox => {
        checkbox.checked = false;
    });
    updateUploadButton();
}

function getSelectedAgents() {
    const checkboxes = document.querySelectorAll('input[name="agents"]:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

function updateUploadButton() {
    const uploadBtn = document.getElementById('uploadBtn');
    const hasFile = selectedFile !== null;
    const hasAgents = getSelectedAgents().length > 0;

    uploadBtn.disabled = !hasFile || !hasAgents;
}

// Event listeners para checkboxes
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input[name="agents"]').forEach(checkbox => {
        checkbox.addEventListener('change', updateUploadButton);
    });
});

// ===== ANÁLISE DE DOCUMENTO =====
async function startAnalysis() {
    if (!selectedFile) {
        showNotification('Selecione um arquivo PDF primeiro!', 'error');
        return;
    }

    const selectedAgents = getSelectedAgents();
    if (selectedAgents.length === 0) {
        showNotification('Selecione pelo menos um agente!', 'error');
        return;
    }

    try {
        // Preparar FormData
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('agents', selectedAgents.join(','));

        // Mostrar seção de progresso
        document.getElementById('progressSection').style.display = 'block';
        document.querySelector('.upload-card').style.display = 'none';

        // Fazer upload
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erro no upload');
        }

        const result = await response.json();
        currentTaskId = result.task_id;

        // Atualizar UI
        document.getElementById('taskId').textContent = currentTaskId;
        showNotification(`Upload realizado com sucesso! ID: ${currentTaskId}`, 'success');

        // Iniciar monitoramento do progresso
        startProgressMonitoring();

    } catch (error) {
        console.error('Erro no upload:', error);
        showNotification(`Erro no upload: ${error.message}`, 'error');
        resetUploadSection();
    }
}

function startProgressMonitoring() {
    progressInterval = setInterval(async () => {
        try {
            await updateProgress();
        } catch (error) {
            console.error('Erro ao verificar progresso:', error);
            clearInterval(progressInterval);
            showNotification('Erro ao acompanhar progresso', 'error');
        }
    }, 2000); // Verificar a cada 2 segundos
}

async function updateProgress() {
    if (!currentTaskId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/status/${currentTaskId}`);

        if (!response.ok) {
            throw new Error('Erro ao verificar status');
        }

        const status = await response.json();

        // Atualizar UI
        updateProgressUI(status);

        // Verificar se completou
        if (status.status === 'completed') {
            clearInterval(progressInterval);
            await loadResults();
            showNotification('Análise concluída com sucesso!', 'success');
            resetUploadSection();
        } else if (status.status === 'error') {
            clearInterval(progressInterval);
            showNotification(`Erro na análise: ${status.error}`, 'error');
            resetUploadSection();
        }

    } catch (error) {
        console.error('Erro ao verificar progresso:', error);
        clearInterval(progressInterval);
    }
}

function updateProgressUI(status) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const progressPercent = document.getElementById('progressPercent');
    const taskStatus = document.getElementById('taskStatus');

    // Atualizar barra de progresso
    progressFill.style.width = `${status.progress}%`;
    progressPercent.textContent = `${status.progress}%`;

    // Atualizar status
    taskStatus.textContent = status.status;

    // Atualizar texto baseado no progresso
    if (status.progress <= 10) {
        progressText.textContent = 'Preparando análise...';
    } else if (status.progress <= 40) {
        progressText.textContent = 'Carregando documento...';
    } else if (status.progress <= 70) {
        progressText.textContent = 'Executando agentes especializados...';
    } else if (status.progress <= 90) {
        progressText.textContent = 'Gerando relatório consolidado...';
    } else {
        progressText.textContent = 'Finalizando análise...';
    }
}

function cancelAnalysis() {
    if (progressInterval) {
        clearInterval(progressInterval);
    }
    currentTaskId = null;
    resetUploadSection();
    showNotification('Análise cancelada', 'warning');
}

function resetUploadSection() {
    document.getElementById('progressSection').style.display = 'none';
    document.querySelector('.upload-card').style.display = 'block';
}

// ===== RESULTADOS =====
async function loadResults() {
    if (!currentTaskId) return;

    try {
        const response = await fetch(`${API_BASE_URL}/result/${currentTaskId}`);

        if (!response.ok) {
            throw new Error('Erro ao carregar resultados');
        }

        const data = await response.json();
        displayResults(data.results);

        // Navegar para seção de resultados
        showSection('results');

    } catch (error) {
        console.error('Erro ao carregar resultados:', error);
        showNotification(`Erro ao carregar resultados: ${error.message}`, 'error');
    }
}

function displayResults(results) {
    const container = document.getElementById('resultsContainer');

    if (!results || Object.keys(results).length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Nenhum resultado encontrado</h3>
                <p>A análise não retornou resultados</p>
            </div>
        `;
        return;
    }

    let html = '';

    // Botão para baixar todos os resultados
    html += `
        <div class="download-all-section">
            <button class="btn-download-all" onclick="downloadCombinedPDF()">
                <i class="fas fa-download"></i>
                Baixar Relatório Completo
            </button>
        </div>
    `;

    html += '<div class="results-grid">';

    // Ordem de exibição dos agentes
    const agentOrder = ['defesa', 'acusacao', 'pesquisa', 'decisoes', 'web', 'relator'];
    const agentNames = {
        'defesa': '🛡️ Agente Defesa',
        'acusacao': '⚖️ Agente Acusação',
        'pesquisa': '📚 Agente Pesquisa Jurídica',
        'decisoes': '⚖️ Agente Decisões Judiciais',
        'web': '🌐 Agente Pesquisa Web',
        'relator': '📋 Agente Relator Consolidado'
    };

    for (const agentKey of agentOrder) {
        if (results[agentKey]) {
            html += createAgentResultCard(agentKey, agentNames[agentKey], results[agentKey]);
        }
    }

    html += '</div>';
    container.innerHTML = html;
}

function createAgentResultCard(agentKey, agentName, result) {
    // Se resultado é um erro
    if (typeof result === 'string' && result.startsWith('Erro:')) {
        return `
            <div class="result-card error">
                <h3>${agentName}</h3>
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>${result}</p>
                </div>
            </div>
        `;
    }

    return `
        <div class="result-card">
            <div class="result-header">
                <h3>${agentName}</h3>
                <button class="btn-download" onclick="downloadAgentPDF('${agentKey}', '${agentName}')" title="Baixar PDF do ${agentName}">
                    <i class="fas fa-file-pdf"></i>
                </button>
            </div>
            <div class="result-content">
                ${formatAgentResult(agentKey, result)}
            </div>
        </div>
    `;
}

function formatAgentResult(agentKey, result) {
    if (typeof result === 'string') {
        return `<pre class="result-text">${result}</pre>`;
    }

    // Se é um objeto estruturado
    if (typeof result === 'object') {
        let html = '<div class="structured-result">';

        for (const [key, value] of Object.entries(result)) {
            // Incluir campos com valores null, boolean ou não vazios
            if (value !== undefined && value !== '' && !(Array.isArray(value) && value.length === 0)) {
                html += `
                    <div class="result-field">
                        <h4>${formatFieldName(key)}</h4>
                        ${formatFieldValue(value)}
                    </div>
                `;
            }
        }

        html += '</div>';
        return html;
    }

    return `<pre class="result-text">${JSON.stringify(result, null, 2)}</pre>`;
}

function formatFieldName(key) {
    const fieldNames = {
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
        'natureza_acao': 'Natureza da Ação',
        'pena_fixada': 'Pena Fixada',
        'regime_cumprimento': 'Regime de Cumprimento',
        'recurso_em_liberdade': 'Recurso em Liberdade',
        'manutencao_prisao': 'Manutenção da Prisão',
        'dosimetria_completa': 'Dosimetria da Pena',
        'decisoes_prisao': 'Decisões sobre Prisão',
        'fundamentacao_juridica': 'Fundamentação Jurídica',
        'analise_provas': 'Análise das Provas',
        'despachos_relevantes': 'Despachos Relevantes',
        'recursos_cabiveis': 'Recursos Cabíveis',
        'medidas_aplicadas': 'Medidas Aplicadas',
        'cronologia_decisoes': 'Cronologia das Decisões'
    };

    return fieldNames[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatFieldValue(value) {
    if (Array.isArray(value)) {
        if (value.length === 0) return '<p class="empty-field">Nenhum item encontrado</p>';

        return `
            <ul class="result-list">
                ${value.map(item => `<li>${item}</li>`).join('')}
            </ul>
        `;
    }

    if (value === null) {
        return '<p class="empty-field">Não informado</p>';
    }

    if (typeof value === 'boolean') {
        return `<p class="result-text">${value ? 'Sim' : 'Não'}</p>`;
    }

    if (typeof value === 'string') {
        return `<p class="result-text">${value}</p>`;
    }

    return `<p class="result-text">${value}</p>`;
}

async function downloadAgentPDF(agentKey, agentName) {
    if (!currentTaskId) return;

    try {
        showNotification(`Gerando PDF do ${agentName}...`, 'info');

        const response = await fetch(`${API_BASE_URL}/result/${currentTaskId}/agent/${agentKey}/pdf`);

        if (!response.ok) {
            throw new Error('Erro ao gerar PDF');
        }

        // Criar blob do PDF
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        // Criar link de download
        const a = document.createElement('a');
        a.href = url;
        a.download = `${agentKey}_${currentTaskId}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showNotification(`PDF do ${agentName} baixado com sucesso`, 'success');

    } catch (error) {
        console.error('Erro no download do PDF:', error);
        showNotification(`Erro ao baixar PDF: ${error.message}`, 'error');
    }
}

async function downloadCombinedPDF() {
    if (!currentTaskId) return;

    try {
        showNotification('Gerando relatório completo...', 'info');

        const response = await fetch(`${API_BASE_URL}/result/${currentTaskId}/pdf`);

        if (!response.ok) {
            throw new Error('Erro ao gerar PDF consolidado');
        }

        // Criar blob do PDF
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        // Criar link de download
        const a = document.createElement('a');
        a.href = url;
        a.download = `analise_completa_${currentTaskId}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showNotification('Relatório completo baixado com sucesso', 'success');

    } catch (error) {
        console.error('Erro no download do PDF consolidado:', error);
        showNotification(`Erro ao baixar relatório: ${error.message}`, 'error');
    }
}

// ===== DOCUMENTAÇÃO =====
async function loadAgentsInfo() {
    try {
        const response = await fetch(`${API_BASE_URL}/agents`);

        if (!response.ok) {
            throw new Error('Erro ao carregar informações dos agentes');
        }

        const data = await response.json();
        displayAgentsInfo(data.agents);

    } catch (error) {
        console.error('Erro ao carregar agentes:', error);
        showNotification(`Erro ao carregar agentes: ${error.message}`, 'error');
    }
}

function displayAgentsInfo(agents) {
    const container = document.getElementById('agentsInfo');

    let html = '<div class="agents-info-grid">';

    for (const [key, agent] of Object.entries(agents)) {
        html += `
            <div class="agent-info-card">
                <h4>${agent.name}</h4>
                <p>${agent.description}</p>
                <div class="agent-capabilities">
                    <h5>Capacidades:</h5>
                    <p>Este agente analisa automaticamente o documento e extrai informações específicas da sua área de especialização.</p>
                </div>
            </div>
        `;
    }

    html += '</div>';
    container.innerHTML = html;
    container.style.display = 'block';
}

// ===== INICIALIZAÇÃO =====
document.addEventListener('DOMContentLoaded', function() {
    // Configurar event listeners
    updateUploadButton();

    // Adicionar estilos CSS para os novos componentes
    addDynamicStyles();
});

function addDynamicStyles() {
    const styles = `
        .results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: var(--spacing-6);
        }

        .result-card {
            background: var(--bg-primary);
            border-radius: var(--border-radius-lg);
            padding: var(--spacing-6);
            box-shadow: var(--shadow-md);
            border: 1px solid var(--gray-200);
        }

        .result-card.error {
            border-left: 4px solid var(--error-color);
        }

        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--spacing-4);
            padding-bottom: var(--spacing-3);
            border-bottom: 1px solid var(--gray-200);
        }

        .result-header h3 {
            margin: 0;
            color: var(--gray-900);
        }

        .btn-download {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: var(--spacing-2) var(--spacing-3);
            border-radius: var(--border-radius-sm);
            cursor: pointer;
            transition: var(--transition-fast);
            font-size: 12px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .btn-download:hover {
            background: var(--primary-dark);
        }

        .download-all-section {
            margin-bottom: var(--spacing-6);
            text-align: center;
        }

        .btn-download-all {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: var(--spacing-4) var(--spacing-6);
            border-radius: var(--border-radius-lg);
            cursor: pointer;
            transition: var(--transition-fast);
            font-size: 16px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            box-shadow: var(--shadow-md);
        }

        .btn-download-all:hover {
            background: linear-gradient(135deg, #5a67d8 0%, #6a4c93 100%);
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }

        .result-content {
            max-height: 400px;
            overflow-y: auto;
        }

        .structured-result {
            space-y: var(--spacing-4);
        }

        .result-field {
            margin-bottom: var(--spacing-4);
        }

        .result-field h4 {
            color: var(--gray-700);
            font-size: var(--font-size-sm);
            font-weight: 600;
            margin-bottom: var(--spacing-2);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .result-text {
            color: var(--gray-800);
            line-height: 1.6;
            margin: 0;
            white-space: pre-wrap;
        }

        .result-list {
            margin: 0;
            padding-left: var(--spacing-4);
        }

        .result-list li {
            margin-bottom: var(--spacing-1);
            color: var(--gray-700);
        }

        .empty-field {
            color: var(--gray-500);
            font-style: italic;
            margin: 0;
        }

        .error-message {
            display: flex;
            align-items: center;
            gap: var(--spacing-2);
            color: var(--error-color);
        }

        .agents-info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: var(--spacing-4);
            margin-top: var(--spacing-6);
        }

        .agent-info-card {
            background: var(--bg-primary);
            padding: var(--spacing-4);
            border-radius: var(--border-radius-md);
            border: 1px solid var(--gray-200);
        }

        .agent-info-card h4 {
            color: var(--primary-color);
            margin-bottom: var(--spacing-2);
        }

        .agent-capabilities {
            margin-top: var(--spacing-3);
            padding-top: var(--spacing-3);
            border-top: 1px solid var(--gray-200);
        }

        .agent-capabilities h5 {
            color: var(--gray-700);
            margin-bottom: var(--spacing-1);
        }
    `;

    const styleElement = document.createElement('style');
    styleElement.textContent = styles;
    document.head.appendChild(styleElement);
}