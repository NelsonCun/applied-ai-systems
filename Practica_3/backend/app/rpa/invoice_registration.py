from pathlib import Path
from typing import Any

import psycopg
from playwright.sync_api import (
    TimeoutError as PlaywrightTimeoutError,
)
from playwright.sync_api import sync_playwright
from psycopg.rows import dict_row

from app.core.config import settings
from app.repositories.automation_repository import (
    get_rpa_payload,
    mark_rpa_error,
    mark_rpa_running,
    mark_rpa_success,
)


def display_value(
    value: Any,
) -> str:
    if value is None:
        return ""

    return str(value)


def execute_invoice_registration(
    run_id: int,
) -> dict[str, Any]:
    connection = psycopg.connect(
        settings.database_url,
        row_factory=dict_row,
    )

    evidence_directory = Path(
        settings.rpa_evidence_dir
    )

    evidence_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    evidence_path = (
        evidence_directory
        / f"rpa_run_{run_id}.png"
    )

    browser = None

    try:
        payload = get_rpa_payload(
            connection,
            run_id,
        )

        if payload is None:
            raise ValueError(
                "La automatización no existe"
            )

        if payload["invoice_status"] != "PROCESSED":
            raise ValueError(
                "Solo se pueden registrar facturas procesadas"
            )

        required_fields = {
            "invoice_number": payload["invoice_number"],
            "invoice_date": payload["invoice_date"],
            "provider_name": payload["provider_name"],
            "nit": payload["nit"],
            "subtotal": payload["subtotal"],
            "tax": payload["tax"],
            "total": payload["total"],
            "currency": payload["currency"],
        }

        missing_fields = [
            key
            for key, value in required_fields.items()
            if value is None or str(value).strip() == ""
        ]

        if missing_fields:
            raise ValueError(
                "La factura no contiene todos los datos: "
                + ", ".join(missing_fields)
            )

        mark_rpa_running(
            connection,
            run_id,
        )

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                executable_path="/usr/bin/chromium",
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )

            page = browser.new_page(
                viewport={
                    "width": 1440,
                    "height": 1000,
                }
            )

            login_url = (
                settings.rpa_target_url.rstrip("/")
                + "/login"
            )

            page.goto(
                login_url,
                wait_until="networkidle",
                timeout=30000,
            )

            page.locator("#username").fill(
                settings.rpa_username
            )

            page.locator("#password").fill(
                settings.rpa_password
            )

            page.locator(
                "#login-button"
            ).click()

            page.wait_for_url(
                "**/form",
                timeout=15000,
            )

            page.locator(
                "#invoice_number"
            ).fill(
                display_value(
                    payload["invoice_number"]
                )
            )

            page.locator(
                "#invoice_date"
            ).fill(
                payload["invoice_date"].isoformat()
            )

            page.locator(
                "#provider_name"
            ).fill(
                display_value(
                    payload["provider_name"]
                )
            )

            page.locator("#nit").fill(
                display_value(payload["nit"])
            )

            page.locator("#subtotal").fill(
                display_value(
                    payload["subtotal"]
                )
            )

            page.locator("#tax").fill(
                display_value(payload["tax"])
            )

            page.locator("#total").fill(
                display_value(payload["total"])
            )

            page.locator("#currency").fill(
                display_value(
                    payload["currency"]
                )
            )

            page.locator(
                "#submit-button"
            ).click()

            page.locator(
                "#success-message"
            ).wait_for(
                state="visible",
                timeout=15000,
            )

            submission_id = page.locator(
                "#submission-id"
            ).inner_text().strip()

            page.screenshot(
                path=str(evidence_path),
                full_page=True,
            )

            final_url = page.url

            browser.close()
            browser = None

        result = {
            "submission_id": submission_id,
            "invoice_id": payload["invoice_id"],
            "invoice_number": (
                payload["invoice_number"]
            ),
            "target_url": final_url,
            "message": (
                "Factura registrada en el sistema externo"
            ),
        }

        mark_rpa_success(
            connection=connection,
            run_id=run_id,
            result=result,
            evidence_path=str(evidence_path),
        )

        return {
            "run_id": run_id,
            "status": "SUCCESS",
            **result,
        }

    except PlaywrightTimeoutError as error:
        message = (
            "Tiempo de espera agotado durante "
            "la automatización RPA"
        )

        if browser is not None:
            browser.close()

        mark_rpa_error(
            connection,
            run_id,
            message,
            (
                str(evidence_path)
                if evidence_path.exists()
                else None
            ),
        )

        raise RuntimeError(message) from error

    except Exception as error:
        if browser is not None:
            browser.close()

        mark_rpa_error(
            connection,
            run_id,
            str(error),
            (
                str(evidence_path)
                if evidence_path.exists()
                else None
            ),
        )

        raise

    finally:
        connection.close()
