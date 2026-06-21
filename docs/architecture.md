# Arth-Sutradhar Architecture

## Overview
Arth-Sutradhar (The Economic Narrator) is a multi-agent, multimodal synthesis engine that bridges micro-level rural land records with macro-level government statistics. It is built for the "RAG Over Bharat" track on GCP.

## System Architecture

```
User Input (Voice/Text/Image)
        │
        ▼
┌───────────────────────────────┐
│   Frontend (React Native)     │
│   Speech-to-Text / OCR / TTS  │
└───────────┬───────────────────┘
            │ HTTP/REST
            ▼
┌──────────────────────────────────────────────────┐
│           Cloud Run (FastAPI Backend)             │
│  ┌────────────────────────────────────────────┐   │
│  │         ADK Agent Orchestrator             │   │
│  │  ┌─────────┐ ┌──────────┐ ┌────────────┐  │   │
│  │  │Planner  │ │Search    │ │Sufficient  │  │   │
│  │  │Agent    │ │Fanout    │ │Context     │  │   │
│  │  └─────────┘ │Agent     │ │Agent       │  │   │
│  │              └──────────┘ └────────────┘  │   │
│  │  ┌─────────┐ ┌──────────┐                  │   │
│  │  │Query    │ │Synthesis │                  │   │
│  │  │Rewriter │ │Agent     │                  │   │
│  │  └─────────┘ └──────────┘                  │   │
│  └────────────────────────────────────────────┘   │
└───────────┬──────────────────────┬────────────────┘
            │                      │
            ▼                      ▼
┌───────────────────┐  ┌──────────────────────────┐
│   BigQuery Vector  │  │   e-Sankhyiki MCP Server │
│   Search           │  │   (MoSPI Live Data)      │
│                    │  │                          │
│   - Land Records   │  │   - PLFS (wages)         │
│   - Crop Patterns  │  │   - CPIALRL (inflation)  │
│   - Ownership Data │  │   - ASUSE (informal econ)│
└───────────────────┘  └──────────────────────────┘
            │                      │
            ▼                      ▼
┌─────────────────────┐
│  Report Formatter   │
│  (Concatenates      │
│   retrieved data)   │
└─────────────────────┘
```

## Data Sources

| Category | Source | Format | Access Method |
|----------|--------|--------|---------------|
| Macro Stats | e-Sankhyiki (MoSPI) | Structured JSON | MCP Protocol |
| Micro Records | AnyROR Gujarat 7/12 | PDF (Gujarati) | Document AI + BigQuery |
| Speech | VAANI Dataset | Audio | Fine-tuned STT |
| Vision | Chitrakshara Dataset | Image+Text | Multimodal LLM |

## Agentic Loop (5-Phase Sufficient Context)

1. **Orchestration**: Planner Agent decomposes query
2. **Search**: Fanout Agent queries BigQuery + MCP in parallel
3. **Context Check**: Sufficient Context Agent validates completeness
4. **Iteration**: Query Rewriter fixes gaps, re-queries
5. **Synthesis**: Formats retrieved data into structured report

## GCP Stack

- **Compute**: Cloud Run (FastAPI + ADK agent)
- **Storage**: Cloud Storage (raw docs), BigQuery (vectors + metadata)
- **AI/ML**: Vertex AI (embeddings), Document AI (parsing), Speech-to-Text, Translation
- **Orchestration**: Vertex AI ADK + RAG Engine
- **Infrastructure**: Terraform (IaC)
