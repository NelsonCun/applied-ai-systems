# Doctor Byte

A rule-based expert system for preliminary computer-failure diagnosis using **SWI-Prolog**, exposed through a **FastAPI** backend and consumed by a **React** frontend and Telegram integration.

## Engineering Focus

Doctor Byte separates application orchestration from symbolic inference.

Prolog owns the knowledge model and inference logic while Python coordinates HTTP requests, persistence, validation, administration, and external communication.

## Stack

- SWI-Prolog
- Python
- FastAPI
- Pydantic
- React
- Vite
- Axios
- Telegram Bot API

## Knowledge Model

The system represents:

- symptoms;
- failures;
- recommendations;
- diagnostic rules.

Rules associate failures with symptom lists. Recursive Prolog predicates count matches and choose the best diagnostic candidate.

## Architecture

```text
React ───────┐
             │
Telegram ────┼──► FastAPI ───► Prolog inference
             │        │
             │        ├──► History persistence
             │        └──► Knowledge administration
             │
             └─────────────────────────────
```

## Capabilities

- diagnostic inference from selected symptoms;
- configurable Prolog knowledge base;
- diagnostic history;
- CRUD administration for knowledge entities;
- direct Telegram Bot API integration;
- guided and direct Telegram diagnosis commands;
- integrity rules for knowledge administration.

## Validation

The project includes **27 documented functional test cases** covering inference, CRUD behavior, error handling, knowledge integrity, web integration, and Telegram interaction.

## Documentation

- [Architecture](docs/arquitectura.md)
- [Technical manual](docs/manual_tecnico.md)
- [User manual](docs/manual_usuario.md)
- [Test cases](docs/casos_prueba.md)
