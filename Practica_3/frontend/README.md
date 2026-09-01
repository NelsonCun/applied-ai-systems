# SmartInvoice Frontend

React/Vite administrative interface for the SmartInvoice document-processing platform.

## Responsibilities

The frontend provides authenticated access to:

- dashboard metrics;
- supplier management;
- invoice upload and batch upload;
- invoice processing state;
- OCR results;
- manual review;
- report generation;
- RPA execution evidence;
- email delivery history.

All persistent operations are performed through the FastAPI backend.

## Stack

- React
- Vite
- Axios
- React Router
- Recharts
- Lucide

## Recommended Execution

The complete SmartInvoice environment is designed to run from the parent directory with Docker Compose:

```bash
cd ..
cp .env.example .env
docker compose up -d --build
```

The frontend is then available at the port documented in the main SmartInvoice README.

## Standalone Development

```bash
npm ci
npm run dev
```

The API base URL is configured through `VITE_API_URL`.

## Production Build

```bash
npm run build
```

For complete architecture, infrastructure, OCR pipeline, and deployment information, see the [SmartInvoice README](../README.md).
