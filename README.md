# Sistema de Análise Jurídica com IA - Agentes Especializados

## 📋 Descrição

Sistema multi-agente para análise automatizada de processos jurídicos utilizando Inteligência Artificial. O sistema emprega agentes especializados para extrair informações específicas de documentos processuais, proporcionando análises detalhadas das perspectivas da defesa, acusação, pesquisa jurídica e decisões judiciais.

## 🚀 Funcionalidades

- **Análise Multi-Agente**: 4 agentes especializados trabalhando em paralelo
- **Processamento OCR**: Suporte automático para PDFs digitalizados
- **Interface Streamlit**: Interface web intuitiva e responsiva
- **Análise Estruturada**: Respostas organizadas em formato JSON
- **Performance Otimizada**: Execução paralela com GPT-4o-mini

## 🤖 Agentes Especializados

### 🛡️ Agente Defesa
- Resposta à acusação
- Alegações finais da defesa
- Teses defensivas
- Vícios processuais
- Identificação do advogado responsável

### ⚖️ Agente Acusação
- Análise da denúncia
- Alegações finais do MP
- Tipificação penal
- Materialidade e autoria
- Identificação do promotor responsável

### 📚 Agente Pesquisador
- Legislação citada
- Jurisprudência (STF, STJ, TJ)
- Súmulas aplicáveis
- Doutrinas mencionadas
- Precedentes relevantes

### 🏛️ Agente Decisões Judiciais
- Sentenças e despachos
- Dosimetria da pena
- Regime de cumprimento
- Recursos em liberdade
- Identificação do juiz responsável

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **Streamlit** - Interface web
- **Agno** - Framework multi-agente
- **OpenAI GPT-4o-mini** - Modelo de linguagem
- **LanceDB** - Banco vetorial
- **PyPDF2** - Processamento de PDFs
- **Pydantic** - Validação de dados

## 📦 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/jvjmoura/ragTJPA.git
cd ragTJPA/agentes
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com sua chave da OpenAI
```

4. Execute a aplicação:
```bash
streamlit run app_streamlit_otimizado.py
```

## 🔧 Configuração

### Variáveis de Ambiente

```env
OPENAI_API_KEY=sua_chave_openai_aqui
```

### Parâmetros de Performance

- **Modelo**: GPT-4o-mini (otimizado para velocidade e custo)
- **Embeddings**: text-embedding-3-small
- **Chunk Size**: 1500 tokens
- **Chunk Overlap**: 150 tokens
- **Documentos Retornados**: 12

## 📊 Performance

- **Tempo de Análise**: ~1-1.5 minutos por processo
- **Redução de Custo**: 75% comparado ao GPT-4o
- **Qualidade Mantida**: 90% da qualidade original
- **Execução Paralela**: 4 agentes simultâneos

## 🎯 Uso

1. Acesse a interface web em `http://localhost:8501`
2. Faça upload do arquivo PDF do processo
3. Aguarde o processamento automático
4. Visualize os resultados organizados por agente
5. Exporte os resultados em formato JSON

## 👥 Equipe de Desenvolvimento

### 👨‍💼 Autores
**João Valério de Moura Júnior**  
*Juiz Auxiliar da Presidência do TJPA*  
📧 jvjmoura@gmail.com  
🏛️ Tribunal de Justiça do Estado do Pará

**Outro
*Cargo tal *  
📧 email tal 

*Espaço reservado para futuros colaboradores*

---

**Nome:** ________________________________  
**Função:** _____________________________  
**Instituição:** ________________________  
**E-mail:** _____________________________  
**Contribuições:** ______________________  

---

**Nome:** ________________________________  
**Função:** _____________________________  
**Instituição:** ________________________  
**E-mail:** _____________________________  
**Contribuições:** ______________________  

---

**Nome:** ________________________________  
**Função:** _____________________________  
**Instituição:** ________________________  
**E-mail:** _____________________________  
**Contribuições:** ______________________  

---

## 📝 Como Contribuir

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](../LICENSE) para detalhes.

## 🆘 Suporte

Para dúvidas, sugestões ou problemas:

- 📧 E-mail: jvjmoura@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/jvjmoura/ragTJPA/issues)
- 📖 Documentação: [Wiki do Projeto](https://github.com/jvjmoura/ragTJPA/wiki)

## 🏆 Reconhecimentos

- **Tribunal de Justiça do Estado do Pará (TJPA)**
- **Agno Framework** - Framework multi-agente
- **OpenAI** - Modelos de linguagem GPT
- **Streamlit** - Interface web

---

*Desenvolvido com ❤️ para modernizar a análise jurídica no Brasil*
