# FastAPI Backend

REST API bridging the React Native frontend to the ADK agent.

## Endpoints
- `POST /query` — Submit text/voice query
- `POST /query/upload` — Submit image document
- `GET /health` — Health check

## Integration
- Receives transcribed text from frontend
- Invokes ADK agent orchestrator
- Returns grounded response + supporting citations
