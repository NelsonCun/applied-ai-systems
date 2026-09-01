# Applied AI & Backend Systems Portfolio

A collection of end-to-end software systems focused on **backend engineering, applied artificial intelligence, automation, symbolic reasoning, document processing, and algorithmic search**.

The repository contains five independent projects implemented with technologies such as **Python, FastAPI, PostgreSQL, Redis, Celery, React, Docker, SWI-Prolog, OpenCV, Tesseract OCR, Playwright, and Telegram APIs**.

> These systems originated as Artificial Intelligence coursework and are preserved here as engineering case studies. The portfolio presentation focuses on architecture, implementation decisions, integrations, reproducibility, and software quality.

## Portfolio Projects

| Project | Engineering focus | Main technologies |
|---|---|---|
| [Rutas Guatemala](Practica_1/) | Symbolic route inference and Python–Prolog integration | FastAPI, Python, SWI-Prolog, PySwip, JavaScript |
| [SmartBot Hospital](Practica_2/) | API-centric chatbot platform with persistence and administration | FastAPI, PostgreSQL, React, Telegram, Docker Compose |
| [SmartInvoice](Practica_3/) | Asynchronous document-processing and automation pipeline | FastAPI, PostgreSQL, Redis, Celery, OpenCV, Tesseract, Playwright, React |
| [RoboMaze](Practica_4/) | Search algorithms, visualization, metrics, and automated testing | Python, FastAPI, BFS, DFS, A*, Pytest, JavaScript |
| [Doctor Byte](Proyecto_fase1/) | Rule-based expert system with web and Telegram interfaces | SWI-Prolog, FastAPI, React, Telegram API |

## Featured Engineering Work

### SmartInvoice — Document Intelligence Pipeline

SmartInvoice is the most infrastructure-intensive system in the repository. It processes digital invoices through a complete asynchronous workflow:

```text
Document upload
      │
      ▼
   FastAPI
      │
      ├── PostgreSQL
      │
      ▼
    Redis
      │
      ▼
    Celery
      │
      ├── OpenCV preprocessing
      ├── Tesseract OCR
      ├── Structured data extraction
      ├── Administrative validation
      ├── PDF / XLSX / CSV reporting
      ├── Playwright RPA
      └── SMTP delivery
```

Key engineering elements include:

- asynchronous processing for CPU- and I/O-intensive operations;
- OCR and Computer Vision preprocessing;
- PostgreSQL persistence and processing logs;
- Redis as Celery broker and result backend;
- human review for rejected document extraction;
- duplicate detection;
- automated report generation;
- browser automation using Playwright;
- development and production Docker Compose configurations;
- reproducible validation with a 20-document evaluation batch.

[Explore SmartInvoice](Practica_3/)

---

### RoboMaze — Search Algorithms and Testing

RoboMaze provides an interactive environment for comparing classical search strategies over two-dimensional mazes.

Implemented algorithms:

- Breadth-First Search;
- Depth-First Search;
- A* search.

The system exposes the algorithms through FastAPI and provides a browser-based visualization of explored nodes, paths, execution metrics, predefined scenarios, generated mazes, and exported results.

RoboMaze includes a dedicated automated test suite covering:

- API behavior;
- BFS;
- DFS;
- A*;
- maze generation;
- validations;
- report generation.

[Explore RoboMaze](Practica_4/)

---

### Doctor Byte — Rule-Based Expert System

Doctor Byte is a computer-diagnostics expert system whose inference engine is implemented in **SWI-Prolog**.

Python and FastAPI provide the application layer while Prolog remains responsible for knowledge representation and rule evaluation.

The project demonstrates:

- facts and rules;
- unification;
- recursive list processing;
- deterministic diagnosis selection;
- knowledge-base administration;
- React integration;
- bidirectional Telegram interaction.

[Explore Doctor Byte](Proyecto_fase1/)

---

### SmartBot Hospital — API-Centric Chatbot Platform

SmartBot Hospital combines a Telegram bot with an administrative web platform and a PostgreSQL-backed knowledge base.

The architecture deliberately centralizes access through the REST API rather than allowing the frontend or bot to query the database directly.

Engineering topics include:

- layered backend architecture;
- repository and service patterns;
- JWT authentication;
- PostgreSQL persistence;
- configurable FAQ knowledge;
- exact and approximate question matching;
- Telegram long polling;
- Docker Compose orchestration.

[Explore SmartBot Hospital](Practica_2/)

---

### Rutas Guatemala — Symbolic Route Inference

Rutas Guatemala demonstrates integration between a conventional web backend and a symbolic reasoning engine.

Route discovery, distance calculation, ordering, and shortest-route selection are implemented in **Prolog**. Python does not reproduce the search logic; it provides validation, API integration, and result serialization through FastAPI and PySwip.

[Explore Rutas Guatemala](Practica_1/)

## Engineering Themes

Across the repository, the projects explore several recurring engineering concerns:

- REST API design with FastAPI;
- layered application architecture;
- relational persistence with PostgreSQL;
- asynchronous job execution with Celery and Redis;
- symbolic AI with SWI-Prolog;
- Computer Vision and OCR pipelines;
- browser automation and RPA;
- authentication and secret management;
- Docker-based reproducibility;
- external API integrations;
- automated and documented validation strategies.

## Repository Structure

```text
.
├── Practica_1/       # Rutas Guatemala
├── Practica_2/       # SmartBot Hospital
├── Practica_3/       # SmartInvoice
├── Practica_4/       # RoboMaze
└── Proyecto_fase1/   # Doctor Byte
```

Each directory is an independent system with its own source code, configuration, documentation, and execution instructions.

## Validation and Quality Evidence

| Project | Evidence currently included |
|---|---|
| Rutas Guatemala | Technical and user documentation, architecture and execution evidence |
| SmartBot Hospital | Requirements, architecture, manuals, persistence model and functional evidence |
| SmartInvoice | 20-document validation batch, architecture, deployment documentation and processing evidence |
| RoboMaze | Automated Pytest suite plus technical and user documentation |
| Doctor Byte | 27 documented functional test cases, architecture and technical documentation |

## Security

Sensitive runtime configuration is intentionally kept outside version control.

The repository uses:

- ignored `.env` files;
- versioned `.env.example` templates;
- placeholders instead of production credentials;
- environment-based application configuration;
- Git history and working-tree secret scanning during portfolio preparation.

Never commit real API tokens, passwords, SMTP credentials, private keys, or deployment secrets.

## Running the Projects

The projects use different execution models. Refer to the README or technical documentation inside each project directory for exact instructions.

Docker Compose is available for the systems that require multiple infrastructure services, while the smaller symbolic-AI and algorithm projects can be executed directly with Python and their documented dependencies.

## Professional Focus

This portfolio is intended to demonstrate capabilities relevant to roles such as:

- Backend Developer;
- Software Engineer;
- Python Developer;
- Applied AI Engineer;
- Automation Engineer.

The emphasis is on building complete systems around AI techniques rather than treating the model or algorithm as an isolated component.
