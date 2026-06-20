import html
import os
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    RedirectResponse,
)


DATABASE_PATH = Path(
    os.getenv(
        "RPA_DATABASE_PATH",
        "/data/rpa_target.db",
    )
)

RPA_USERNAME = os.getenv(
    "RPA_USERNAME",
    "robot",
)

RPA_PASSWORD = os.getenv(
    "RPA_PASSWORD",
    "robot123",
)

SESSION_VALUE = "smartinvoice-rpa-authenticated"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT NOT NULL,
            invoice_date TEXT NOT NULL,
            provider_name TEXT NOT NULL,
            nit TEXT NOT NULL,
            subtotal TEXT NOT NULL,
            tax TEXT NOT NULL,
            total TEXT NOT NULL,
            currency TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


def is_authenticated(
    request: Request,
) -> bool:
    return (
        request.cookies.get("rpa_session")
        == SESSION_VALUE
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Sistema Administrativo Simulado",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "healthy",
        "application": "RPA Target",
    }


@app.get(
    "/",
    response_class=HTMLResponse,
)
def root() -> RedirectResponse:
    return RedirectResponse(
        url="/login",
        status_code=302,
    )


@app.get(
    "/login",
    response_class=HTMLResponse,
)
def login_page() -> str:
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Sistema Administrativo</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #eef2f5;
                margin: 0;
            }

            .container {
                width: 420px;
                margin: 90px auto;
                padding: 32px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 6px 20px rgba(0,0,0,.12);
            }

            input, button {
                box-sizing: border-box;
                width: 100%;
                padding: 12px;
                margin-top: 10px;
            }

            button {
                color: white;
                background: #263238;
                border: 0;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <main class="container">
            <h1>Sistema Administrativo</h1>
            <p>Acceso para automatización de facturas.</p>

            <form method="post" action="/login">
                <label for="username">Usuario</label>
                <input
                    id="username"
                    name="username"
                    type="text"
                    required
                >

                <label for="password">Contraseña</label>
                <input
                    id="password"
                    name="password"
                    type="password"
                    required
                >

                <button id="login-button" type="submit">
                    Ingresar
                </button>
            </form>
        </main>
    </body>
    </html>
    """


@app.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
):
    if (
        username != RPA_USERNAME
        or password != RPA_PASSWORD
    ):
        return HTMLResponse(
            content=(
                "<h1>Credenciales incorrectas</h1>"
                "<a href='/login'>Regresar</a>"
            ),
            status_code=401,
        )

    response = RedirectResponse(
        url="/form",
        status_code=303,
    )

    response.set_cookie(
        key="rpa_session",
        value=SESSION_VALUE,
        httponly=True,
        samesite="strict",
    )

    return response


@app.get(
    "/form",
    response_class=HTMLResponse,
)
def invoice_form(
    request: Request,
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/login",
            status_code=302,
        )

    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Registro de factura</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #eef2f5;
                margin: 0;
            }

            .container {
                width: 700px;
                margin: 30px auto;
                padding: 32px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 6px 20px rgba(0,0,0,.12);
            }

            .grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
            }

            label {
                display: block;
                margin-bottom: 4px;
                font-weight: bold;
            }

            input, button {
                box-sizing: border-box;
                width: 100%;
                padding: 11px;
            }

            button {
                margin-top: 22px;
                color: white;
                background: #263238;
                border: 0;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <main class="container">
            <h1>Registro administrativo de factura</h1>

            <form method="post" action="/submit">
                <div class="grid">
                    <div>
                        <label>Número</label>
                        <input
                            id="invoice_number"
                            name="invoice_number"
                            required
                        >
                    </div>

                    <div>
                        <label>Fecha</label>
                        <input
                            id="invoice_date"
                            name="invoice_date"
                            type="date"
                            required
                        >
                    </div>

                    <div>
                        <label>Proveedor</label>
                        <input
                            id="provider_name"
                            name="provider_name"
                            required
                        >
                    </div>

                    <div>
                        <label>NIT</label>
                        <input
                            id="nit"
                            name="nit"
                            required
                        >
                    </div>

                    <div>
                        <label>Subtotal</label>
                        <input
                            id="subtotal"
                            name="subtotal"
                            required
                        >
                    </div>

                    <div>
                        <label>Impuestos</label>
                        <input
                            id="tax"
                            name="tax"
                            required
                        >
                    </div>

                    <div>
                        <label>Total</label>
                        <input
                            id="total"
                            name="total"
                            required
                        >
                    </div>

                    <div>
                        <label>Moneda</label>
                        <input
                            id="currency"
                            name="currency"
                            required
                        >
                    </div>
                </div>

                <button id="submit-button" type="submit">
                    Registrar factura
                </button>
            </form>
        </main>
    </body>
    </html>
    """


@app.post(
    "/submit",
    response_class=HTMLResponse,
)
def submit_invoice(
    request: Request,
    invoice_number: str = Form(...),
    invoice_date: str = Form(...),
    provider_name: str = Form(...),
    nit: str = Form(...),
    subtotal: str = Form(...),
    tax: str = Form(...),
    total: str = Form(...),
    currency: str = Form(...),
):
    if not is_authenticated(request):
        return RedirectResponse(
            url="/login",
            status_code=302,
        )

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO submissions (
            invoice_number,
            invoice_date,
            provider_name,
            nit,
            subtotal,
            tax,
            total,
            currency,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            invoice_number,
            invoice_date,
            provider_name,
            nit,
            subtotal,
            tax,
            total,
            currency,
            datetime.now(
                timezone.utc
            ).isoformat(),
        ),
    )

    submission_id = cursor.lastrowid

    connection.commit()
    connection.close()

    safe_number = html.escape(
        invoice_number
    )

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Registro completado</title>
    </head>
    <body>
        <main>
            <h1 id="success-message">
                Factura registrada correctamente
            </h1>

            <p>
                ID:
                <strong id="submission-id">
                    {submission_id}
                </strong>
            </p>

            <p>
                Factura:
                <strong>{safe_number}</strong>
            </p>

            <a href="/form">Registrar otra factura</a>
        </main>
    </body>
    </html>
    """


@app.get("/api/submissions")
def list_submissions() -> JSONResponse:
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM submissions
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return JSONResponse(
        content=[
            dict(row)
            for row in rows
        ]
    )
