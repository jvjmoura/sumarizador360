# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-agent legal document analysis system for automated analysis of criminal legal processes using AI. The system employs specialized agents to extract specific information from legal documents, providing detailed analysis from defense, prosecution, legal research, and judicial decisions perspectives.

## Architecture

**Backend (FastAPI)**: `backend/`
- `main.py` - FastAPI application entry point with CORS, static file serving, and API routes
- `agents.py` - Core agent configuration using Agno framework with OpenAI GPT-4o-mini
- `models.py` - Pydantic models for all agent responses and API contracts
- `routers/analysis.py` - Analysis endpoints for PDF upload and background processing
- `services/pdf_service.py` - PDF processing utilities

**Frontend (Vanilla HTML/CSS/JS)**: `frontend/`
- Static web interface served by FastAPI
- Real-time progress monitoring for analysis tasks

**Agent System**:
- 4 specialized agents running in parallel: Defense, Prosecution, Legal Research, Judicial Decisions
- 1 consolidator agent (Relator) that synthesizes results from other agents
- Uses LanceDB for vector storage with OCR support for digitized PDFs

## Development Commands

### Start Application
```bash
python start.py
```
This starts the FastAPI server on port 8000 with hot reload enabled.

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Setup
Create `backend/.env` file with:
```
OPENAI_API_KEY=your_openai_key_here
TAVILY_API_KEY=your_tavily_key_here
```

Note: The web research agent uses Tavily for intelligent web search. Get API key at [tavily.com](https://tavily.com)

## Key Technical Details

### Agent Configuration
- **Model**: GPT-4o-mini (optimized for speed/cost)
- **Embeddings**: text-embedding-3-large for knowledge base
- **Vector DB**: LanceDB with OCR support
- **Chunk size**: 1500 tokens with 150 token overlap
- **Retrieved documents**: 12 per query

### API Endpoints
- `POST /api/v1/upload` - Upload PDF and start background analysis
- `GET /api/v1/status/{task_id}` - Check analysis progress
- `GET /api/v1/result/{task_id}` - Get complete results
- `GET /api/v1/result/{task_id}/agent/{agent_name}` - Get specific agent results

### Agent Specializations
1. **Defense Agent** (`defesa`) - Extracts defense arguments, final allegations, attorney identification
2. **Prosecution Agent** (`acusacao`) - Analyzes accusations, prosecutor statements, evidence
3. **Legal Research Agent** (`pesquisa`) - Extracts legal citations, jurisprudence, applicable precedents
4. **Judicial Decisions Agent** (`decisoes`) - Analyzes sentences, sentence dosimetry, judicial reasoning
5. **Web Research Agent** (`web`) - Searches current jurisprudence, recent legal doctrine, and legislative changes via Tavily API
6. **Consolidator Agent** (`relator`) - Synthesizes all other agent results into neutral report

### Background Processing
Uses FastAPI BackgroundTasks for async PDF processing with in-memory task storage. Each analysis generates a unique task_id for progress tracking.

## File Structure Notes
- Temporary files stored in `backend/tmp/` (gitignored)
- Vector database persists in `backend/tmp/lancedb_stf_ocr_otimizado/`
- Upload files are processed and immediately cleaned up
- Cache files (`__pycache__/`) are gitignored

## URLs
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc