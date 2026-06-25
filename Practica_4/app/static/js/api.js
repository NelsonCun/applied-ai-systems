async function getErrorMessage(response) {
    let body = null;

    try {
        body = await response.json();
    } catch {
        body = null;
    }

    if (typeof body?.detail === "string") {
        return body.detail;
    }

    if (Array.isArray(body?.detail)) {
        return body.detail
            .map((item) => item.msg)
            .filter(Boolean)
            .join(" ");
    }

    return `La solicitud falló con estado ${response.status}.`;
}


async function requestJson(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers ?? {}),
        },
        ...options,
    });

    if (!response.ok) {
        throw new Error(
            await getErrorMessage(response),
        );
    }

    return response.json();
}


export function getHealth() {
    return requestJson("/api/v1/health");
}


export function getMazeCatalog() {
    return requestJson("/api/v1/mazes");
}


export function getPredefinedMaze(mazeId) {
    return requestJson(
        `/api/v1/mazes/${encodeURIComponent(mazeId)}`,
    );
}


export function generateMaze(configuration) {
    return requestJson("/api/v1/mazes/generate", {
        method: "POST",
        body: JSON.stringify(configuration),
    });
}


export function executeSearch(configuration) {
    return requestJson("/api/v1/search", {
        method: "POST",
        body: JSON.stringify(configuration),
    });
}


export function compareSearches(configuration) {
    return requestJson("/api/v1/search/compare", {
        method: "POST",
        body: JSON.stringify(configuration),
    });
}


export async function createPdfReport(configuration) {
    const response = await fetch("/api/v1/reports/pdf", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(configuration),
    });

    if (!response.ok) {
        throw new Error(
            await getErrorMessage(response),
        );
    }

    const disposition = response.headers.get(
        "Content-Disposition",
    );

    const filenameMatch = disposition?.match(
        /filename="?([^"]+)"?/i,
    );

    return {
        blob: await response.blob(),
        filename: (
            filenameMatch?.[1]
            ?? "robomaze-reporte.pdf"
        ),
    };
}
