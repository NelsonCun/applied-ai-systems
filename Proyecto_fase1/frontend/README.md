# Doctor Byte Frontend

React/Vite interface for the Doctor Byte expert system.

## Responsibilities

The frontend allows users to:

- load available symptoms;
- request diagnoses;
- review recommendations;
- inspect diagnostic history;
- administer the knowledge base;
- configure supported operational settings.

The frontend contains no Prolog inference logic and does not expose the Telegram bot token. All operations are delegated to the FastAPI backend.

## Stack

- React
- Vite
- Axios

## Development

Install dependencies:

```bash
npm ci
```

Start the development server:

```bash
npm run dev
```

The backend URL is configured through:

```text
VITE_API_URL
```

See `.env.example` for the local configuration template.

## Production Build

```bash
npm run build
```

For system architecture, Prolog inference, Telegram integration, and backend configuration, see the [Doctor Byte README](../README.md).
