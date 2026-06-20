# Phase 3: Multimodal Frontend

## Objective
Build a React Native mobile app with voice, vision, and text input for rural users in regional Indian languages.

## Screens

```
┌─────────────────────────────────────┐
│           Home Screen                │
│                                     │
│   Arth-Sutradhar                    │
│   The Economic Narrator             │
│   ● API connected                   │
│                                     │
│   ┌─────────────────────────────┐   │
│   │ Ask about land records,     │   │
│   │ inflation, crops...         │   │
│   └─────────────────────────────┘   │
│                                     │
│   ┌────────┐ ┌────────┐ ┌────────┐ │
│   │  Ask   │ │ Voice  │ │ Camera │ │
│   └────────┘ └────────┘ └────────┘ │
│                                     │
│         Loading...                   │
│    Agent is analyzing...            │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│          Query Screen                │
│                                     │
│   [Listen] [Share]                  │
│   Iterations: 1 | Feedback: 4 steps │
│                                     │
│   --- Land Records ---              │
│   Found 10 records...               │
│                                     │
│   --- Macroeconomic Data ---        │
│   CPI Index: 198.5                  │
│                                     │
│   Agent Reasoning Log               │
│   1. Plan created                   │
│   2. BigQuery returned 10 records   │
│   3. Context is sufficient          │
└─────────────────────────────────────┘
```

## Input Modes

| Mode | Method | Languages |
|------|--------|-----------|
| Text | Type query | Any (backend handles translation) |
| Voice | Speak via mic | Gujarati (gu-IN), Hindi (hi-IN) |
| Vision | Camera capture | Document OCR via backend Vision API |

## How to Run

```bash
cd frontend/mobile
npm install
npx expo start
```

## Configuration
- **API_URL** in `src/services/api.ts` — set to your backend address
  - Android emulator: `http://10.0.2.2:8080`
  - iOS simulator: `http://localhost:8080`
  - Physical device: your machine's local network IP

## Dependencies
- expo, react-native
- @react-navigation/native (navigation)
- expo-image-picker (camera upload)
- expo-speech (text-to-speech)
- @react-native-voice/voice (speech-to-text)
- axios (HTTP client)
