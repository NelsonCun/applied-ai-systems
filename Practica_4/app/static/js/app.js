import {
    compareSearches,
    createPdfReport,
    executeSearch,
    generateMaze,
    getHealth,
    getMazeCatalog,
    getPredefinedMaze,
} from "./api.js";


const elements = {
    apiStatus: document.querySelector("#api-status"),
    apiStatusText: document.querySelector("#api-status-text"),

    mazeSelect: document.querySelector("#maze-select"),
    loadMazeButton: document.querySelector("#load-maze-button"),
    mazeDescription: document.querySelector("#maze-description"),

    rowsInput: document.querySelector("#rows-input"),
    columnsInput: document.querySelector("#columns-input"),
    applySizeButton: document.querySelector("#apply-size-button"),

    densityInput: document.querySelector("#density-input"),
    seedInput: document.querySelector("#seed-input"),
    generateMazeButton: document.querySelector("#generate-maze-button"),

    toolButtons: [
        ...document.querySelectorAll("[data-tool]"),
    ],

    clearRouteButton: document.querySelector(
        "#clear-route-button",
    ),
    clearMazeButton: document.querySelector(
        "#clear-maze-button",
    ),

    saveMazeButton: document.querySelector(
        "#save-maze-button",
    ),
    loadMazeFileButton: document.querySelector(
        "#load-maze-file-button",
    ),
    mazeFileInput: document.querySelector(
        "#maze-file-input",
    ),

    exportCsvButton: document.querySelector(
        "#export-csv-button",
    ),
    exportPdfButton: document.querySelector(
        "#export-pdf-button",
    ),

    algorithmButtons: [
        ...document.querySelectorAll("[data-algorithm]"),
    ],
    compareButton: document.querySelector("#compare-button"),
    animationSpeed: document.querySelector("#animation-speed"),

    mazeGrid: document.querySelector("#maze-grid"),
    mazeSize: document.querySelector("#maze-size"),
    workspaceStatus: document.querySelector("#workspace-status"),

    metricAlgorithm: document.querySelector(
        "#metric-algorithm",
    ),
    metricStatus: document.querySelector("#metric-status"),
    metricLength: document.querySelector("#metric-length"),
    metricExplored: document.querySelector(
        "#metric-explored",
    ),
    metricTime: document.querySelector("#metric-time"),
    resultMessage: document.querySelector("#result-message"),

    comparisonSection: document.querySelector(
        "#comparison-section",
    ),
    comparisonBody: document.querySelector(
        "#comparison-body",
    ),
    nodesChart: document.querySelector("#nodes-chart"),
    timeChart: document.querySelector("#time-chart"),

    routeList: document.querySelector("#route-list"),

    idleControls: [
        ...document.querySelectorAll(".requires-idle"),
    ],
};


const state = {
    rows: 10,
    columns: 10,
    start: {
        row: 0,
        column: 0,
    },
    goal: {
        row: 9,
        column: 9,
    },
    obstacles: new Set(),
    explored: new Set(),
    path: new Set(),
    activeTool: "obstacle",
    animationToken: 0,
    busy: false,
    lastResult: null,
    lastComparison: null,
};


function coordinateKey(row, column) {
    return `${row}:${column}`;
}


function coordinateToKey(coordinate) {
    return coordinateKey(
        coordinate.row,
        coordinate.column,
    );
}


function keyToCoordinate(key) {
    const [row, column] = key
        .split(":")
        .map(Number);

    return {
        row,
        column,
    };
}


function coordinatesAreEqual(first, second) {
    return (
        first.row === second.row
        && first.column === second.column
    );
}


function sleep(milliseconds) {
    return new Promise((resolve) => {
        window.setTimeout(resolve, milliseconds);
    });
}


function showWorkspaceStatus(message, type = "neutral") {
    elements.workspaceStatus.textContent = message;

    elements.workspaceStatus.classList.remove(
        "workspace-status--success",
        "workspace-status--warning",
        "workspace-status--error",
    );

    if (type !== "neutral") {
        elements.workspaceStatus.classList.add(
            `workspace-status--${type}`,
        );
    }
}


function setBusy(isBusy) {
    state.busy = isBusy;

    for (const control of elements.idleControls) {
        control.disabled = isBusy;
    }
}


function cancelAnimation() {
    state.animationToken += 1;
}


function clearVisualization({
    resetResults = true,
    render = true,
} = {}) {
    cancelAnimation();

    state.explored.clear();
    state.path.clear();

    if (render) {
        renderGrid();
    }

    if (resetResults) {
        resetResultPanels();
    }
}


function resetResultPanels() {
    state.lastResult = null;
    state.lastComparison = null;

    elements.exportCsvButton.disabled = true;
    elements.exportPdfButton.disabled = true;

    elements.metricAlgorithm.textContent = "—";
    elements.metricStatus.textContent = "—";

    const statusCard = elements.metricStatus.closest(".metric-card");

    statusCard?.classList.remove(
        "metric-card--success",
        "metric-card--danger",
    );

    elements.metricLength.textContent = "—";
    elements.metricExplored.textContent = "—";
    elements.metricTime.textContent = "—";

    elements.resultMessage.textContent = (
        "Ejecute un algoritmo para obtener resultados."
    );

    elements.routeList.textContent = (
        "No existe una ruta calculada."
    );

    elements.comparisonSection.hidden = true;
    elements.comparisonBody.replaceChildren();
    elements.nodesChart.replaceChildren();
    elements.timeChart.replaceChildren();
}


function setActiveTool(tool) {
    state.activeTool = tool;

    for (const button of elements.toolButtons) {
        const isActive = button.dataset.tool === tool;

        button.classList.toggle(
            "tool-button--active",
            isActive,
        );

        button.setAttribute(
            "aria-pressed",
            String(isActive),
        );
    }

    const toolNames = {
        obstacle: "obstáculos",
        start: "la posición inicial",
        goal: "la posición de destino",
        erase: "obstáculos",
    };

    showWorkspaceStatus(
        `Herramienta activa: ${toolNames[tool]}.`,
    );
}


function applyConfiguration(
    configuration,
    description = "",
) {
    cancelAnimation();

    state.rows = configuration.rows;
    state.columns = configuration.columns;

    state.start = {
        row: configuration.start.row,
        column: configuration.start.column,
    };

    state.goal = {
        row: configuration.goal.row,
        column: configuration.goal.column,
    };

    state.obstacles = new Set(
        configuration.obstacles.map(
            (obstacle) => coordinateToKey(obstacle),
        ),
    );

    state.explored.clear();
    state.path.clear();

    elements.rowsInput.value = state.rows;
    elements.columnsInput.value = state.columns;
    elements.mazeSize.textContent = (
        `${state.rows} × ${state.columns}`
    );

    if (description) {
        elements.mazeDescription.textContent = description;
    }

    resetResultPanels();
    renderGrid();
}


function renderGrid() {
    const fragment = document.createDocumentFragment();

    elements.mazeGrid.style.setProperty(
        "--columns",
        state.columns,
    );

    elements.mazeGrid.setAttribute(
        "aria-rowcount",
        String(state.rows),
    );

    elements.mazeGrid.setAttribute(
        "aria-colcount",
        String(state.columns),
    );

    for (let row = 0; row < state.rows; row += 1) {
        for (
            let column = 0;
            column < state.columns;
            column += 1
        ) {
            const key = coordinateKey(row, column);
            const coordinate = {
                row,
                column,
            };

            const cell = document.createElement("button");

            cell.type = "button";
            cell.className = "maze-cell";
            cell.dataset.row = String(row);
            cell.dataset.column = String(column);
            cell.dataset.key = key;
            cell.setAttribute("role", "gridcell");
            cell.setAttribute(
                "aria-label",
                `Fila ${row + 1}, columna ${column + 1}`,
            );

            if (state.obstacles.has(key)) {
                cell.classList.add("maze-cell--obstacle");
                cell.setAttribute("aria-label", "Obstáculo");
            }

            if (state.explored.has(key)) {
                cell.classList.add("maze-cell--explored");
            }

            if (state.path.has(key)) {
                cell.classList.add("maze-cell--path");
            }

            if (
                coordinatesAreEqual(
                    coordinate,
                    state.start,
                )
            ) {
                cell.classList.add("maze-cell--start");
                cell.textContent = "S";
                cell.setAttribute(
                    "aria-label",
                    "Posición inicial",
                );
            }

            if (
                coordinatesAreEqual(
                    coordinate,
                    state.goal,
                )
            ) {
                cell.classList.add("maze-cell--goal");
                cell.textContent = "G";
                cell.setAttribute(
                    "aria-label",
                    "Posición de destino",
                );
            }

            cell.addEventListener("click", () => {
                editCell(row, column);
            });

            fragment.append(cell);
        }
    }

    elements.mazeGrid.replaceChildren(fragment);
}


function editCell(row, column) {
    if (state.busy) {
        return;
    }

    clearVisualization({
        resetResults: true,
        render: false,
    });

    const coordinate = {
        row,
        column,
    };

    const key = coordinateKey(row, column);

    if (state.activeTool === "obstacle") {
        if (
            coordinatesAreEqual(coordinate, state.start)
            || coordinatesAreEqual(coordinate, state.goal)
        ) {
            showWorkspaceStatus(
                "No se puede colocar un obstáculo sobre el inicio o el destino.",
                "warning",
            );

            renderGrid();
            return;
        }

        if (state.obstacles.has(key)) {
            state.obstacles.delete(key);
        } else {
            state.obstacles.add(key);
        }
    }

    if (state.activeTool === "start") {
        if (coordinatesAreEqual(coordinate, state.goal)) {
            showWorkspaceStatus(
                "El inicio y el destino deben estar en posiciones diferentes.",
                "warning",
            );

            renderGrid();
            return;
        }

        state.obstacles.delete(key);
        state.start = coordinate;
    }

    if (state.activeTool === "goal") {
        if (coordinatesAreEqual(coordinate, state.start)) {
            showWorkspaceStatus(
                "El destino y el inicio deben estar en posiciones diferentes.",
                "warning",
            );

            renderGrid();
            return;
        }

        state.obstacles.delete(key);
        state.goal = coordinate;
    }

    if (state.activeTool === "erase") {
        state.obstacles.delete(key);
    }

    renderGrid();
}


function buildMazePayload() {
    const obstacles = [
        ...state.obstacles,
    ]
        .map(keyToCoordinate)
        .sort((first, second) => (
            first.row - second.row
            || first.column - second.column
        ));

    return {
        rows: state.rows,
        columns: state.columns,
        start: {
            ...state.start,
        },
        goal: {
            ...state.goal,
        },
        obstacles,
    };
}


function getCell(coordinate) {
    const key = coordinateToKey(coordinate);

    return elements.mazeGrid.querySelector(
        `[data-key="${key}"]`,
    );
}


function markExplored(coordinate) {
    const key = coordinateToKey(coordinate);

    state.explored.add(key);

    const cell = getCell(coordinate);

    if (
        cell
        && !coordinatesAreEqual(coordinate, state.start)
        && !coordinatesAreEqual(coordinate, state.goal)
    ) {
        cell.classList.add("maze-cell--explored");
    }
}


function markPath(coordinate) {
    const key = coordinateToKey(coordinate);

    state.path.add(key);

    const cell = getCell(coordinate);

    if (cell) {
        cell.classList.remove("maze-cell--explored");
        cell.classList.add("maze-cell--path");
    }
}


async function animateResult(result) {
    const delay = Number(elements.animationSpeed.value);
    const token = state.animationToken + 1;

    state.animationToken = token;
    state.explored.clear();
    state.path.clear();

    renderGrid();

    if (delay === 0) {
        for (const coordinate of result.explored_order) {
            state.explored.add(coordinateToKey(coordinate));
        }

        for (const coordinate of result.path) {
            state.path.add(coordinateToKey(coordinate));
        }

        renderGrid();
        return;
    }

    for (const coordinate of result.explored_order) {
        if (state.animationToken !== token) {
            return;
        }

        markExplored(coordinate);
        await sleep(delay);
    }

    for (const coordinate of result.path) {
        if (state.animationToken !== token) {
            return;
        }

        markPath(coordinate);
        await sleep(Math.max(18, delay));
    }
}


function renderRoute(path) {
    elements.routeList.replaceChildren();

    if (path.length === 0) {
        elements.routeList.textContent = (
            "El algoritmo no encontró una ruta válida."
        );
        return;
    }

    const fragment = document.createDocumentFragment();

    path.forEach((coordinate, index) => {
        const item = document.createElement("span");

        item.className = "route-coordinate";
        item.textContent = (
            `${index + 1}. (${coordinate.row}, ${coordinate.column})`
        );

        fragment.append(item);
    });

    elements.routeList.append(fragment);
}


function renderSingleResult(result) {
    state.lastResult = result;

    elements.exportCsvButton.disabled = false;
    elements.exportPdfButton.disabled = false;

    elements.metricAlgorithm.textContent = (
        result.algorithm_name
    );

    elements.metricStatus.textContent = result.found
        ? "Ruta encontrada"
        : "Sin solución";

    const statusCard = elements.metricStatus.closest(".metric-card");

    statusCard?.classList.toggle(
        "metric-card--success",
        result.found,
    );

    statusCard?.classList.toggle(
        "metric-card--danger",
        !result.found,
    );

    elements.metricLength.textContent = result.found
        ? `${result.path_length} movimientos`
        : "0 movimientos";

    elements.metricExplored.textContent = (
        `${result.explored_nodes} nodos`
    );

    elements.metricTime.textContent = (
        `${result.execution_time_ms.toFixed(6)} ms`
    );

    elements.resultMessage.textContent = result.message;

    renderRoute(result.path);
}


function algorithmShortName(result) {
    const names = {
        bfs: "BFS",
        dfs: "DFS",
        astar: "A*",
    };

    return names[result.algorithm];
}


function minimumFoundValue(results, property) {
    const values = results
        .filter((result) => result.found)
        .map((result) => result[property]);

    return values.length > 0
        ? Math.min(...values)
        : null;
}


function renderBarChart(
    container,
    results,
    property,
    formatter,
) {
    container.replaceChildren();

    const maximum = Math.max(
        ...results.map((result) => result[property]),
        0.000001,
    );

    const fragment = document.createDocumentFragment();

    for (const result of results) {
        const row = document.createElement("div");
        const label = document.createElement("strong");
        const track = document.createElement("div");
        const value = document.createElement("div");
        const amount = document.createElement("small");

        row.className = "bar-row";
        label.textContent = algorithmShortName(result);

        track.className = "bar-track";
        value.className = "bar-value";

        value.style.width = (
            `${(result[property] / maximum) * 100}%`
        );

        amount.textContent = formatter(result[property]);

        track.append(value);
        row.append(label, track, amount);
        fragment.append(row);
    }

    container.append(fragment);
}


function renderComparison(comparison) {
    state.lastComparison = comparison;

    elements.exportCsvButton.disabled = false;
    elements.exportPdfButton.disabled = false;

    const results = [
        comparison.bfs,
        comparison.dfs,
        comparison.astar,
    ];

    const bestLength = minimumFoundValue(
        results,
        "path_length",
    );

    const bestExplored = Math.min(
        ...results.map(
            (result) => result.explored_nodes,
        ),
    );

    const bestTime = Math.min(
        ...results.map(
            (result) => result.execution_time_ms,
        ),
    );

    elements.comparisonBody.replaceChildren();

    const fragment = document.createDocumentFragment();

    for (const result of results) {
        const row = document.createElement("tr");

        const nameCell = document.createElement("td");
        const lengthCell = document.createElement("td");
        const exploredCell = document.createElement("td");
        const timeCell = document.createElement("td");

        nameCell.textContent = algorithmShortName(result);

        nameCell.classList.add(
            "algorithm-label",
            `algorithm-label--${result.algorithm}`,
        );

        lengthCell.textContent = result.found
            ? String(result.path_length)
            : "—";

        exploredCell.textContent = String(
            result.explored_nodes,
        );

        timeCell.textContent = (
            `${result.execution_time_ms.toFixed(4)} ms`
        );

        if (
            result.found
            && result.path_length === bestLength
        ) {
            lengthCell.classList.add("is-best");
        }

        if (result.explored_nodes === bestExplored) {
            exploredCell.classList.add("is-best");
        }

        if (result.execution_time_ms === bestTime) {
            timeCell.classList.add("is-best");
        }

        row.append(
            nameCell,
            lengthCell,
            exploredCell,
            timeCell,
        );

        fragment.append(row);
    }

    elements.comparisonBody.append(fragment);

    renderBarChart(
        elements.nodesChart,
        results,
        "explored_nodes",
        (value) => `${value} nodos`,
    );

    renderBarChart(
        elements.timeChart,
        results,
        "execution_time_ms",
        (value) => `${value.toFixed(4)} ms`,
    );

    elements.comparisonSection.hidden = false;
}


function createTimestamp() {
    return new Date()
        .toISOString()
        .replaceAll(":", "-")
        .replaceAll(".", "-");
}


function downloadTextFile({
    content,
    filename,
    mimeType,
}) {
    const blob = new Blob(
        [content],
        {
            type: `${mimeType};charset=utf-8`,
        },
    );

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = filename;

    document.body.append(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(url);
}


function downloadBlobFile(
    blob,
    filename,
) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = filename;

    document.body.append(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(url);
}


function saveMazeAsJson() {
    const maze = buildMazePayload();

    const documentData = {
        format: "robomaze-maze",
        version: 1,
        saved_at: new Date().toISOString(),
        maze,
    };

    downloadTextFile({
        content: JSON.stringify(documentData, null, 2),
        filename: (
            `robomaze-laberinto-${createTimestamp()}.json`
        ),
        mimeType: "application/json",
    });

    showWorkspaceStatus(
        "El laberinto fue guardado en un archivo JSON.",
        "success",
    );
}


function validateInteger(value, minimum, maximum, name) {
    if (
        !Number.isInteger(value)
        || value < minimum
        || value > maximum
    ) {
        throw new Error(
            `${name} debe ser un número entero entre `
            + `${minimum} y ${maximum}.`,
        );
    }
}


function validateImportedCoordinate(
    coordinate,
    rows,
    columns,
    name,
) {
    if (
        coordinate === null
        || typeof coordinate !== "object"
    ) {
        throw new Error(
            `${name} debe contener una fila y una columna.`,
        );
    }

    validateInteger(
        coordinate.row,
        0,
        rows - 1,
        `La fila de ${name}`,
    );

    validateInteger(
        coordinate.column,
        0,
        columns - 1,
        `La columna de ${name}`,
    );

    return {
        row: coordinate.row,
        column: coordinate.column,
    };
}


function normalizeImportedMaze(fileData) {
    const maze = (
        fileData?.format === "robomaze-maze"
        && fileData?.maze
    )
        ? fileData.maze
        : fileData;

    if (maze === null || typeof maze !== "object") {
        throw new Error(
            "El archivo no contiene un laberinto válido.",
        );
    }

    validateInteger(
        maze.rows,
        5,
        40,
        "La cantidad de filas",
    );

    validateInteger(
        maze.columns,
        5,
        40,
        "La cantidad de columnas",
    );

    const start = validateImportedCoordinate(
        maze.start,
        maze.rows,
        maze.columns,
        "la posición inicial",
    );

    const goal = validateImportedCoordinate(
        maze.goal,
        maze.rows,
        maze.columns,
        "la posición objetivo",
    );

    if (coordinatesAreEqual(start, goal)) {
        throw new Error(
            "La posición inicial y el destino deben ser diferentes.",
        );
    }

    if (!Array.isArray(maze.obstacles)) {
        throw new Error(
            "La propiedad obstacles debe ser una lista.",
        );
    }

    const obstacleKeys = new Set();
    const obstacles = [];

    for (
        let index = 0;
        index < maze.obstacles.length;
        index += 1
    ) {
        const obstacle = validateImportedCoordinate(
            maze.obstacles[index],
            maze.rows,
            maze.columns,
            `el obstáculo ${index + 1}`,
        );

        const key = coordinateToKey(obstacle);

        if (obstacleKeys.has(key)) {
            throw new Error(
                "El archivo contiene obstáculos repetidos.",
            );
        }

        if (
            coordinatesAreEqual(obstacle, start)
            || coordinatesAreEqual(obstacle, goal)
        ) {
            throw new Error(
                "Un obstáculo no puede ocupar el inicio o el destino.",
            );
        }

        obstacleKeys.add(key);
        obstacles.push(obstacle);
    }

    return {
        rows: maze.rows,
        columns: maze.columns,
        start,
        goal,
        obstacles,
    };
}


async function loadMazeFromJson(event) {
    const [file] = event.target.files;

    if (!file) {
        return;
    }

    try {
        const fileContent = await file.text();
        const fileData = JSON.parse(fileContent);
        const maze = normalizeImportedMaze(fileData);

        applyConfiguration(
            maze,
            `Laberinto importado desde ${file.name}.`,
        );

        elements.mazeSelect.value = "";

        showWorkspaceStatus(
            `El archivo "${file.name}" fue cargado correctamente.`,
            "success",
        );
    } catch (error) {
        const message = error instanceof SyntaxError
            ? "El archivo seleccionado no contiene JSON válido."
            : error.message;

        showWorkspaceStatus(message, "error");
    } finally {
        event.target.value = "";
    }
}


function escapeCsvValue(value) {
    const text = String(value ?? "");

    if (
        text.includes(",")
        || text.includes('"')
        || text.includes("\n")
    ) {
        return `"${text.replaceAll('"', '""')}"`;
    }

    return text;
}


function pathToText(path) {
    return path
        .map(
            (coordinate) => (
                `(${coordinate.row},${coordinate.column})`
            ),
        )
        .join(" -> ");
}


function resultToCsvRow(result) {
    return [
        algorithmShortName(result),
        result.found ? "Ruta encontrada" : "Sin solución",
        result.path_length,
        result.explored_nodes,
        result.execution_time_ms,
        pathToText(result.path),
    ];
}


function exportResultsAsCsv() {
    let results = [];

    if (state.lastComparison) {
        results = [
            state.lastComparison.bfs,
            state.lastComparison.dfs,
            state.lastComparison.astar,
        ];
    } else if (state.lastResult) {
        results = [state.lastResult];
    }

    if (results.length === 0) {
        showWorkspaceStatus(
            "Primero debe ejecutar un algoritmo.",
            "warning",
        );
        return;
    }

    const rows = [
        [
            "Algoritmo",
            "Estado",
            "Longitud de ruta",
            "Nodos explorados",
            "Tiempo de ejecución (ms)",
            "Ruta completa",
        ],
        ...results.map(resultToCsvRow),
    ];

    const csv = rows
        .map(
            (row) => row
                .map(escapeCsvValue)
                .join(","),
        )
        .join("\n");

    downloadTextFile({
        content: `\ufeff${csv}`,
        filename: (
            `robomaze-resultados-${createTimestamp()}.csv`
        ),
        mimeType: "text/csv",
    });

    showWorkspaceStatus(
        "Los resultados fueron exportados a CSV.",
        "success",
    );
}


async function exportResultsAsPdf() {
    if (!state.lastResult && !state.lastComparison) {
        showWorkspaceStatus(
            "Primero debe ejecutar un algoritmo.",
            "warning",
        );
        return;
    }

    elements.exportPdfButton.disabled = true;

    showWorkspaceStatus(
        "Generando el reporte PDF en el backend...",
    );

    try {
        const report = await createPdfReport({
            maze: buildMazePayload(),
            result: state.lastResult,
            comparison: state.lastComparison,
        });

        downloadBlobFile(
            report.blob,
            report.filename,
        );

        showWorkspaceStatus(
            "El reporte PDF fue generado y descargado correctamente.",
            "success",
        );
    } catch (error) {
        showWorkspaceStatus(
            `No fue posible generar el PDF: ${error.message}`,
            "error",
        );
    } finally {
        elements.exportPdfButton.disabled = false;
    }
}


async function verifyApiStatus() {
    try {
        const result = await getHealth();

        elements.apiStatus.classList.remove(
            "api-status--checking",
            "api-status--offline",
        );

        elements.apiStatus.classList.add(
            "api-status--online",
        );

        elements.apiStatusText.textContent = result.message;
    } catch (error) {
        elements.apiStatus.classList.remove(
            "api-status--checking",
            "api-status--online",
        );

        elements.apiStatus.classList.add(
            "api-status--offline",
        );

        elements.apiStatusText.textContent = (
            "Servicio no disponible"
        );

        showWorkspaceStatus(error.message, "error");
    }
}


async function loadCatalog() {
    try {
        const catalog = await getMazeCatalog();

        elements.mazeSelect.replaceChildren();

        for (const maze of catalog) {
            const option = document.createElement("option");

            option.value = maze.id;
            option.textContent = (
                `${maze.name} · ${maze.rows} × ${maze.columns}`
            );

            elements.mazeSelect.append(option);
        }

        if (catalog.length > 0) {
            elements.mazeSelect.value = catalog[0].id;
            await loadSelectedMaze();
        }
    } catch (error) {
        showWorkspaceStatus(
            `No fue posible cargar los escenarios: ${error.message}`,
            "error",
        );
    }
}


async function loadSelectedMaze() {
    const mazeId = elements.mazeSelect.value;

    if (!mazeId) {
        return;
    }

    setBusy(true);

    try {
        const maze = await getPredefinedMaze(mazeId);

        applyConfiguration(maze, maze.description);

        showWorkspaceStatus(
            `Escenario "${maze.name}" cargado correctamente.`,
            maze.has_solution ? "success" : "warning",
        );
    } catch (error) {
        showWorkspaceStatus(error.message, "error");
    } finally {
        setBusy(false);
    }
}


function applyNewSize() {
    const rows = Number(elements.rowsInput.value);
    const columns = Number(elements.columnsInput.value);

    if (
        !Number.isInteger(rows)
        || !Number.isInteger(columns)
        || rows < 5
        || columns < 5
        || rows > 40
        || columns > 40
    ) {
        showWorkspaceStatus(
            "El tamaño debe estar entre 5 y 40 filas y columnas.",
            "warning",
        );
        return;
    }

    applyConfiguration(
        {
            rows,
            columns,
            start: {
                row: 0,
                column: 0,
            },
            goal: {
                row: rows - 1,
                column: columns - 1,
            },
            obstacles: [],
        },
        "Laberinto personalizado creado manualmente.",
    );

    elements.mazeSelect.value = "";

    showWorkspaceStatus(
        `Se creó un tablero vacío de ${rows} × ${columns}.`,
        "success",
    );
}


function clearMaze() {
    applyConfiguration(
        {
            rows: state.rows,
            columns: state.columns,
            start: {
                row: 0,
                column: 0,
            },
            goal: {
                row: state.rows - 1,
                column: state.columns - 1,
            },
            obstacles: [],
        },
        "Tablero vacío listo para edición.",
    );

    elements.mazeSelect.value = "";

    showWorkspaceStatus(
        "El tablero fue vaciado.",
        "success",
    );
}


async function generateAutomaticMaze() {
    const rows = Number(elements.rowsInput.value);
    const columns = Number(elements.columnsInput.value);
    const densityPercentage = Number(
        elements.densityInput.value,
    );

    const seedText = elements.seedInput.value.trim();

    if (
        !Number.isInteger(rows)
        || !Number.isInteger(columns)
        || rows < 5
        || columns < 5
        || rows > 40
        || columns > 40
    ) {
        showWorkspaceStatus(
            "La generación admite tamaños entre 5 y 40.",
            "warning",
        );
        return;
    }

    if (
        densityPercentage < 5
        || densityPercentage > 45
    ) {
        showWorkspaceStatus(
            "La densidad debe estar entre 5 % y 45 %.",
            "warning",
        );
        return;
    }

    const payload = {
        rows,
        columns,
        obstacle_density: densityPercentage / 100,
        seed: seedText === ""
            ? null
            : Number(seedText),
    };

    setBusy(true);

    try {
        const maze = await generateMaze(payload);

        applyConfiguration(
            maze,
            "Laberinto generado automáticamente con una ruta garantizada.",
        );

        elements.mazeSelect.value = "";

        showWorkspaceStatus(
            "El laberinto automático fue generado correctamente.",
            "success",
        );
    } catch (error) {
        showWorkspaceStatus(error.message, "error");
    } finally {
        setBusy(false);
    }
}


async function runAlgorithm(algorithm) {
    clearVisualization();

    setBusy(true);

    showWorkspaceStatus(
        `Ejecutando ${algorithm.toUpperCase()} en el backend...`,
    );

    try {
        const result = await executeSearch({
            ...buildMazePayload(),
            algorithm,
        });

        renderSingleResult(result);

        showWorkspaceStatus(
            result.message,
            result.found ? "success" : "warning",
        );

        await animateResult(result);
    } catch (error) {
        showWorkspaceStatus(error.message, "error");
    } finally {
        setBusy(false);
    }
}


async function compareAlgorithms() {
    clearVisualization();

    setBusy(true);

    showWorkspaceStatus(
        "Ejecutando BFS, DFS y A* sobre el mismo laberinto...",
    );

    try {
        const comparison = await compareSearches(
            buildMazePayload(),
        );

        renderComparison(comparison);
        renderSingleResult(comparison.bfs);

        showWorkspaceStatus(
            "La comparación de algoritmos terminó correctamente.",
            "success",
        );

        await animateResult(comparison.bfs);
    } catch (error) {
        showWorkspaceStatus(error.message, "error");
    } finally {
        setBusy(false);
    }
}


function registerEvents() {
    for (const button of elements.toolButtons) {
        button.addEventListener("click", () => {
            setActiveTool(button.dataset.tool);
        });
    }

    for (const button of elements.algorithmButtons) {
        button.addEventListener("click", () => {
            runAlgorithm(button.dataset.algorithm);
        });
    }

    elements.loadMazeButton.addEventListener(
        "click",
        loadSelectedMaze,
    );

    elements.applySizeButton.addEventListener(
        "click",
        applyNewSize,
    );

    elements.generateMazeButton.addEventListener(
        "click",
        generateAutomaticMaze,
    );

    elements.clearRouteButton.addEventListener(
        "click",
        () => {
            clearVisualization();

            showWorkspaceStatus(
                "La visualización del recorrido fue limpiada.",
                "success",
            );
        },
    );

    elements.clearMazeButton.addEventListener(
        "click",
        clearMaze,
    );

    elements.saveMazeButton.addEventListener(
        "click",
        saveMazeAsJson,
    );

    elements.loadMazeFileButton.addEventListener(
        "click",
        () => {
            elements.mazeFileInput.click();
        },
    );

    elements.mazeFileInput.addEventListener(
        "change",
        loadMazeFromJson,
    );

    elements.exportCsvButton.addEventListener(
        "click",
        exportResultsAsCsv,
    );

    elements.exportPdfButton.addEventListener(
        "click",
        exportResultsAsPdf,
    );

    elements.compareButton.addEventListener(
        "click",
        compareAlgorithms,
    );
}


function initializeDefaultMaze() {
    applyConfiguration(
        {
            rows: 10,
            columns: 10,
            start: {
                row: 0,
                column: 0,
            },
            goal: {
                row: 9,
                column: 9,
            },
            obstacles: [],
        },
        "Tablero inicial.",
    );
}


async function initialize() {
    initializeDefaultMaze();
    registerEvents();
    setActiveTool("obstacle");

    await verifyApiStatus();
    await loadCatalog();
}


initialize();
