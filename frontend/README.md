# Frontend - Sistema de Análise Jurídica

Interface web moderna e responsiva para o sistema de análise jurídica com IA.

## 🚀 Funcionalidades

### ✨ Interface Principal
- **Upload de arquivos** - Drag & drop ou seleção manual
- **Seleção de agentes** - Interface visual para escolher agentes
- **Progress tracking** - Acompanhamento em tempo real
- **Resultados estruturados** - Exibição organizada dos resultados

### 📱 Design Responsivo
- **Mobile-first** - Otimizado para dispositivos móveis
- **Grid flexível** - Layout que se adapta a qualquer tela
- **Componentes nativos** - Sem dependências externas
- **Performance otimizada** - Carregamento rápido

### 🎨 Componentes Principais

#### 1. Upload Section
- Área de drag & drop para PDFs
- Validação de arquivo (tipo e tamanho)
- Preview das informações do arquivo
- Seleção visual de agentes

#### 2. Progress Section
- Barra de progresso animada
- Status em tempo real
- ID da tarefa para acompanhamento
- Opção de cancelamento

#### 3. Results Section
- Cards organizados por agente
- Resultados estruturados e formatados
- Download individual por agente
- Navegação entre seções

#### 4. Documentation Section
- Links para API docs
- Informações dos agentes
- Guias de uso

## 🔧 Estrutura de Arquivos

```
frontend/
├── index.html          # Página principal
├── styles.css          # Estilos CSS responsivos
├── script.js           # JavaScript para interação
├── README.md           # Esta documentação
└── assets/             # Recursos (futuras imagens/ícones)
```

## 🎯 Como Usar

### 1. Preparação
Certifique-se de que o backend FastAPI está rodando em `http://localhost:8000`

### 2. Acesso
Abra o arquivo `index.html` em um navegador ou acesse via servidor:
```
http://localhost:8000
```

### 3. Upload
1. Arraste um arquivo PDF ou clique para selecionar
2. Escolha os agentes desejados
3. Clique em "Iniciar Análise"

### 4. Acompanhamento
- Monitore o progresso em tempo real
- Acompanhe o status da tarefa
- Cancele se necessário

### 5. Resultados
- Navegue para a aba "Resultados"
- Visualize os dados estruturados
- Faça download individual por agente

## 🔄 Comunicação com API

### Endpoints Utilizados
- `POST /api/v1/upload` - Upload e início da análise
- `GET /api/v1/status/{task_id}` - Status da tarefa
- `GET /api/v1/result/{task_id}` - Resultados completos
- `GET /api/v1/agents` - Lista de agentes

### Fluxo de Dados
1. **Upload** → Envia arquivo + agentes selecionados
2. **Polling** → Verifica status a cada 2 segundos
3. **Results** → Carrega resultados quando concluído
4. **Display** → Formata e exibe dados estruturados

## 🎨 Customização

### Variáveis CSS
O arquivo `styles.css` usa CSS custom properties para fácil customização:

```css
:root {
    --primary-color: #2563eb;
    --success-color: #10b981;
    --error-color: #ef4444;
    /* ... mais variáveis */
}
```

### Temas
- **Cores principais** - Azul profissional
- **Tipografia** - Inter font family
- **Espaçamentos** - Sistema consistente
- **Sombras** - Profundidade sutil

## 📱 Responsividade

### Breakpoints
- **Desktop** - 1200px+
- **Tablet** - 768px - 1199px
- **Mobile** - < 768px

### Adaptações Mobile
- Navigation collapse
- Single column layout
- Touch-optimized buttons
- Reduced spacing

## ⚡ Performance

### Otimizações
- **CSS puro** - Sem frameworks pesados
- **JavaScript vanilla** - Sem bibliotecas externas
- **Lazy loading** - Carregamento sob demanda
- **Caching** - Reutilização de recursos

### Métricas
- **First Paint** < 1s
- **Interactive** < 2s
- **Bundle size** < 100KB
- **Lighthouse score** 90+

## 🔧 Desenvolvimento

### Estrutura do JavaScript
```javascript
// Configurações globais
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Módulos principais
- Navegação entre seções
- Gerenciamento de arquivos
- Comunicação com API
- Exibição de resultados
- Sistema de notificações
```

### Padrões de Código
- **ES6+** - Sintaxe moderna
- **Async/await** - Operações assíncronas
- **Error handling** - Tratamento de erros
- **Clean code** - Código limpo e documentado

## 🎯 Próximas Melhorias

### Funcionalidades Planejadas
- [ ] Histórico de análises
- [ ] Comparação entre resultados
- [ ] Export para diferentes formatos
- [ ] Modo escuro/claro
- [ ] Configurações de usuário

### Otimizações Técnicas
- [ ] Service Worker para offline
- [ ] WebSockets para tempo real
- [ ] Compression de assets
- [ ] PWA capabilities

## 🐛 Troubleshooting

### Problemas Comuns

**Upload não funciona**
- Verifique se o backend está rodando
- Confirme o arquivo é PDF válido
- Verifique o tamanho (máx 50MB)

**Progress não atualiza**
- Verifique conexão com API
- Confirme CORS configurado
- Check network tab no DevTools

**Resultados não carregam**
- Aguarde conclusão da análise
- Verifique ID da tarefa
- Confirme task não teve erro

### Debug
Abra as ferramentas de desenvolvedor:
- **Console** - Para logs e erros
- **Network** - Para requisições API
- **Application** - Para storage local