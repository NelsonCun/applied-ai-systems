#!/usr/bin/env python3
"""
Carga y verifica un lote de facturas contra SmartInvoice usando únicamente
la biblioteca estándar de Python.

Uso:
    python3 scripts/upload_verify_batch_20.py \
        --directory samples/batch_20 \
        --base-url http://localhost:8001 \
        --identifier admin \
        --password 'Admin123*'
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import (
    Request,
    urlopen,
)


TERMINAL_STATUSES = {
    "PROCESSED",
    "REJECTED",
    "ERROR",
    "DUPLICATE",
}


def request_json(
    url: str,
    *,
    method: str = "GET",
    token: str | None = None,
    payload: dict[str, Any] | None = None,
    timeout: int = 60,
) -> Any:
    data = None
    headers = {
        "Accept": "application/json",
    }

    if token:
        headers[
            "Authorization"
        ] = f"Bearer {token}"

    if payload is not None:
        data = json.dumps(
            payload
        ).encode("utf-8")

        headers[
            "Content-Type"
        ] = "application/json"

    request = Request(
        url=url,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(
            request,
            timeout=timeout,
        ) as response:
            raw = response.read()

            if not raw:
                return None

            return json.loads(
                raw.decode("utf-8")
            )

    except HTTPError as error:
        body = error.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            f"HTTP {error.code} en {url}: {body}"
        ) from error

    except URLError as error:
        raise RuntimeError(
            f"No fue posible conectar con {url}: "
            f"{error.reason}"
        ) from error


def resolve_schema(
    openapi: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    reference = schema.get("$ref")

    if not reference:
        return schema

    prefix = "#/components/schemas/"

    if not reference.startswith(prefix):
        return schema

    name = reference.removeprefix(
        prefix
    )

    return (
        openapi
        .get("components", {})
        .get("schemas", {})
        .get(name, schema)
    )


def detect_batch_field(
    base_url: str,
) -> str:
    openapi = request_json(
        f"{base_url}/openapi.json"
    )

    operation = (
        openapi
        .get("paths", {})
        .get(
            "/api/v1/invoices/batch",
            {},
        )
        .get("post", {})
    )

    schema = (
        operation
        .get("requestBody", {})
        .get("content", {})
        .get(
            "multipart/form-data",
            {},
        )
        .get("schema", {})
    )

    schema = resolve_schema(
        openapi,
        schema,
    )

    properties = schema.get(
        "properties",
        {},
    )

    for name, definition in (
        properties.items()
    ):
        definition = resolve_schema(
            openapi,
            definition,
        )

        if (
            definition.get("type")
            == "array"
            and definition
            .get("items", {})
            .get("format")
            == "binary"
        ):
            return name

    return "files"


def build_multipart(
    files: list[Path],
    field_name: str,
) -> tuple[bytes, str]:
    boundary = (
        "----SmartInvoice"
        + uuid.uuid4().hex
    )

    body = bytearray()

    for path in files:
        mime_type = (
            mimetypes.guess_type(
                path.name
            )[0]
            or "application/octet-stream"
        )

        body.extend(
            f"--{boundary}\r\n".encode()
        )

        body.extend(
            (
                "Content-Disposition: "
                "form-data; "
                f'name="{field_name}"; '
                f'filename="{path.name}"'
                "\r\n"
            ).encode("utf-8")
        )

        body.extend(
            (
                f"Content-Type: {mime_type}"
                "\r\n\r\n"
            ).encode("utf-8")
        )

        body.extend(
            path.read_bytes()
        )

        body.extend(b"\r\n")

    body.extend(
        f"--{boundary}--\r\n".encode()
    )

    return (
        bytes(body),
        (
            "multipart/form-data; "
            f"boundary={boundary}"
        ),
    )


def upload_batch(
    *,
    base_url: str,
    token: str,
    files: list[Path],
    field_name: str,
) -> Any:
    body, content_type = build_multipart(
        files,
        field_name,
    )

    request = Request(
        url=(
            f"{base_url}"
            "/api/v1/invoices/batch"
        ),
        data=body,
        headers={
            "Accept": "application/json",
            "Authorization": (
                f"Bearer {token}"
            ),
            "Content-Type": content_type,
        },
        method="POST",
    )

    try:
        with urlopen(
            request,
            timeout=180,
        ) as response:
            raw = response.read()

            return json.loads(
                raw.decode("utf-8")
            )

    except HTTPError as error:
        body_text = error.read().decode(
            "utf-8",
            errors="replace",
        )

        raise RuntimeError(
            "Falló la carga masiva: "
            f"HTTP {error.code}: "
            f"{body_text}"
        ) from error


def list_invoices(
    base_url: str,
    token: str,
) -> list[dict[str, Any]]:
    query = urlencode(
        {
            "page": 1,
            "page_size": 100,
        }
    )

    response = request_json(
        (
            f"{base_url}"
            f"/api/v1/invoices?{query}"
        ),
        token=token,
    )

    if isinstance(response, list):
        return response

    return response.get(
        "items",
        [],
    )


def print_status_table(
    expected_files: set[str],
    invoices: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    found = {
        invoice.get(
            "original_file_name"
        ): invoice
        for invoice in invoices
        if invoice.get(
            "original_file_name"
        ) in expected_files
    }

    print()
    print(
        "ARCHIVO".ljust(34),
        "ID".rjust(5),
        "ESTADO".ljust(13),
        "CONFIANZA".rjust(10),
    )
    print("-" * 68)

    for file_name in sorted(
        expected_files
    ):
        invoice = found.get(file_name)

        if invoice is None:
            print(
                file_name.ljust(34),
                "—".rjust(5),
                "NO ENCONTRADA".ljust(13),
                "—".rjust(10),
            )
            continue

        confidence = invoice.get(
            "ocr_confidence"
        )

        confidence_text = (
            f"{float(confidence):.2f}%"
            if confidence is not None
            else "—"
        )

        print(
            file_name.ljust(34),
            str(invoice.get("id")).rjust(5),
            str(
                invoice.get("status")
            ).ljust(13),
            confidence_text.rjust(10),
        )

    return found


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--directory",
        default="samples/batch_20",
    )

    parser.add_argument(
        "--base-url",
        default="http://localhost:8001",
    )

    parser.add_argument(
        "--identifier",
        default="admin",
    )

    parser.add_argument(
        "--password",
        default="Admin123*",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help=(
            "Tiempo máximo de espera en segundos."
        ),
    )

    parser.add_argument(
        "--poll-interval",
        type=float,
        default=3.0,
    )

    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help=(
            "Solo verifica un lote previamente cargado."
        ),
    )

    args = parser.parse_args()

    directory = Path(
        args.directory
    )

    manifest_path = (
        directory
        / "expected_results.json"
    )

    if not manifest_path.is_file():
        raise SystemExit(
            "No se encontró el manifest: "
            f"{manifest_path}"
        )

    manifest = json.loads(
        manifest_path.read_text(
            encoding="utf-8"
        )
    )

    expected_files = {
        invoice["file"]
        for invoice in manifest[
            "invoices"
        ]
    }

    files = sorted(
        [
            directory / name
            for name in expected_files
        ],
        key=lambda path: path.name,
    )

    missing_files = [
        str(path)
        for path in files
        if not path.is_file()
    ]

    if missing_files:
        raise SystemExit(
            "Faltan archivos:\n"
            + "\n".join(
                missing_files
            )
        )

    if len(files) != 20:
        raise SystemExit(
            "El lote debe contener exactamente "
            f"20 documentos; encontrados: "
            f"{len(files)}"
        )

    base_url = args.base_url.rstrip("/")

    login_response = request_json(
        (
            f"{base_url}"
            "/api/v1/auth/login"
        ),
        method="POST",
        payload={
            "identifier": args.identifier,
            "password": args.password,
        },
    )

    token = login_response.get(
        "access_token"
    )

    if not token:
        raise SystemExit(
            "La autenticación no devolvió "
            "access_token."
        )

    print("Autenticación correcta.")

    if not args.skip_upload:
        field_name = detect_batch_field(
            base_url
        )

        print(
            "Campo multipart detectado:",
            field_name,
        )

        upload_response = upload_batch(
            base_url=base_url,
            token=token,
            files=files,
            field_name=field_name,
        )

        print(
            "Respuesta de carga masiva:"
        )

        print(
            json.dumps(
                upload_response,
                ensure_ascii=False,
                indent=2,
            )
        )

    deadline = (
        time.monotonic()
        + args.timeout
    )

    last_signature = None

    while True:
        invoices = list_invoices(
            base_url,
            token,
        )

        found = {
            invoice.get(
                "original_file_name"
            ): invoice
            for invoice in invoices
            if invoice.get(
                "original_file_name"
            ) in expected_files
        }

        signature = tuple(
            sorted(
                (
                    name,
                    item.get("status"),
                )
                for name, item
                in found.items()
            )
        )

        if signature != last_signature:
            print_status_table(
                expected_files,
                invoices,
            )

            last_signature = signature

        all_found = (
            len(found)
            == len(expected_files)
        )

        all_terminal = (
            all_found
            and all(
                item.get("status")
                in TERMINAL_STATUSES
                for item in found.values()
            )
        )

        if all_terminal:
            break

        if time.monotonic() >= deadline:
            print()
            print(
                "Se agotó el tiempo de espera."
            )

            print_status_table(
                expected_files,
                invoices,
            )

            sys.exit(2)

        time.sleep(
            args.poll_interval
        )

    final_items = print_status_table(
        expected_files,
        invoices,
    )

    status_counts: dict[str, int] = {}

    for item in final_items.values():
        status = str(
            item.get("status")
        )

        status_counts[status] = (
            status_counts.get(
                status,
                0,
            )
            + 1
        )

    print()
    print("Resumen final:")

    for status, count in sorted(
        status_counts.items()
    ):
        print(
            f"- {status}: {count}"
        )

    non_processed = [
        item
        for item in final_items.values()
        if item.get("status")
        != "PROCESSED"
    ]

    if non_processed:
        print()
        print(
            "RESULTADO: FALLÓ. "
            "No todas las facturas terminaron "
            "en PROCESSED."
        )

        for item in non_processed:
            print(
                "-",
                item.get(
                    "original_file_name"
                ),
                item.get("status"),
                item.get("last_error"),
            )

        sys.exit(1)

    print()
    print(
        "RESULTADO: CORRECTO. "
        "Las 20 facturas terminaron "
        "en PROCESSED."
    )


if __name__ == "__main__":
    main()
