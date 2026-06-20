# Arth-Sutradhar: Pitch Deck Outline

## Slide 1: Title
- **Arth-Sutradhar (The Economic Narrator)**
- Multi-Agent RAG for Indian Public Data
- Hackday 2.0 — Gemini + GCP Track

## Slide 2: The Problem
- Indian public data is **fragmented**
- Micro land records (AnyROR) and macro govt stats (MoSPI) are **siloed**
- Policymakers/extension workers can't easily cross-reference
- *"How will CPI inflation impact cotton farmers in Gujarat's Gandhinagar taluka?"*
- This query is **computationally impossible** for standard RAG

## Slide 3: The Solution — Arth-Sutradhar
- **Multi-agent, multimodal synthesis engine**
- Bridges micro-level rural land records ↔ macro-level govt statistics
- Voice + Vision + Text input for rural accessibility
- 5-phase **Sufficient Context Agent** loop (self-correcting)

## Slide 4: Architecture Overview
```
User (Voice/Text/Image)
    │
    ▼
┌─────────────────────────────────────┐
│    5-Phase Agentic Loop (ADK)       │
│  Planner → Search → Context Check   │
│  → Rewriter → Synthesis             │
└──────┬──────────────────┬───────────┘
       │                  │
       ▼                  ▼
┌──────────────┐  ┌─────────────────┐
│ BigQuery      │  │ e-Sankhyiki MCP │
│ Vector Store  │  │ (Live Gov Data) │
└──────────────┘  └─────────────────┘
```

## Slide 5: Data Sources
| Source | Type | Content |
|--------|------|---------|
| AnyROR Gujarat 7/12 | Land Records | Ownership, crops, irrigation |
| e-Sankhyiki (MoSPI) | Live API | PLFS, CPIALRL, ASUSE |
| VAANI Dataset | Speech | 21,500 hrs, 86 languages |
| Chitrakshara | Vision | 193M images, 11 Indic langs |

## Slide 6: The Sufficient Context Agent
```
Query: "How will inflation affect cotton farmers?"
       │
       ▼
[1] Planner: Decompose → needs land records + inflation data
[2] Search: BigQuery VECTOR_SEARCH + MCP CPIALRL query
[3] Context Check: "Found land records, but MCP data failed"
[4] Rewriter: Fixes MCP state code, re-queries ✓
[5] Synthesis: Generates grounded, cited analysis
```

- **34% improvement** in factuality (Google Research benchmark)
- **90.1% accuracy** in cross-corpus settings
- Self-correcting — agent knows when it doesn't know

## Slide 7: GCP Stack
| Service | Role |
|---------|------|
| BigQuery Vector Search | Land record embeddings |
| Vertex AI (ADK) | Agent orchestration |
| Cloud Run | API deployment |
| Document AI | Gujarati OCR |
| Vertex AI Speech/TTS | Voice input/output |
| Artifact Registry | Docker images |
| Terraform | Infrastructure as Code |

## Slide 8: Live Demo
1. **Voice query** in Gujarati: *"ખેડૂતો પર ફુગાવાની શું અસર?"*
2. **Document upload**: Photo of handwritten 7/12 extract
3. **Complex cross-query**: *"CPIALRL inflation impact on cotton farmers holding <2 hectares in Gandhinagar"*
4. **Agent self-correction**: Intentionally trigger missing data → watch agent rewrite query

## Slide 9: Why We Win
- **Not vanilla RAG** — full Agentic RAG with Sufficient Context
- **Not static CSVs** — live MCP integration with MoSPI
- **Not English-only** — voice in 86 languages, vision for handwritten docs
- **Not third-party dependent** — pure GCP stack (BigQuery, Vertex AI, ADK)

## Slide 10: Team & Thank You
- Questions?
- GitHub: github.com/Amitk003/Arth-Sutradhar
- Try it: [deployed URL]
