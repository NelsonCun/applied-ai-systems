# Rutas Guatemala

A web application for route discovery between Guatemalan cities using **SWI-Prolog as the reasoning engine** and **FastAPI as the integration layer**.

## Engineering Focus

The core route logic is deliberately implemented in Prolog:

- city and connection representation;
- path discovery;
- cycle prevention;
- total-distance calculation;
- route ordering;
- shortest-route selection.

Python does not duplicate these algorithms. The backend uses PySwip to query the Prolog knowledge base and exposes the results through REST endpoints.

## Stack

- Python
- FastAPI
- SWI-Prolog
- PySwip
- HTML
- CSS
- JavaScript

## Architecture

```text
Browser
   │
   ▼
FastAPI
   │
   ▼
Application Services
   │
   ▼
Prolog Repository
   │
   ▼
SWI-Prolog Knowledge Base
```

## Main Capabilities

- find the shortest route between two cities;
- enumerate possible routes;
- calculate route distances;
- add cities;
- add connections;
- preserve user-added facts separately from the original knowledge base.

## Documentation

- [Technical manual](docs/manual_tecnico.md)
- [User manual](docs/manual_usuario.md)
- [Architecture image](docs/img/arquitectura.png)

The technical manual contains installation requirements, API endpoints, Prolog predicates, architecture details, validations, and execution instructions.
