from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.schemas import (
    MazeConfiguration,
    PdfReportRequest,
    SearchResponse,
)


COLOR_TEXT = colors.HexColor("#172033")
COLOR_MUTED = colors.HexColor("#657083")
COLOR_ACCENT = colors.HexColor("#0F766E")
COLOR_ACCENT_LIGHT = colors.HexColor("#D8EFEB")
COLOR_BORDER = colors.HexColor("#D7DEE8")
COLOR_SURFACE = colors.HexColor("#F5F7FA")

COLOR_OBSTACLE = colors.HexColor("#29313D")
COLOR_EXPLORED = colors.HexColor("#B9DCE7")
COLOR_PATH = colors.HexColor("#EAC45F")
COLOR_START = colors.HexColor("#23855B")
COLOR_GOAL = colors.HexColor("#B94B4B")
COLOR_FREE = colors.HexColor("#FAFBFC")


class MazeFlowable(Flowable):
    """Dibuja el laberinto directamente dentro del PDF."""

    def __init__(
        self,
        maze: MazeConfiguration,
        result: SearchResponse | None,
        max_width: float = 235 * mm,
        max_height: float = 105 * mm,
    ) -> None:
        super().__init__()

        self.maze = maze
        self.result = result

        self.cell_size = min(
            max_width / maze.columns,
            max_height / maze.rows,
        )

        self.grid_width = self.cell_size * maze.columns
        self.grid_height = self.cell_size * maze.rows
        self.legend_height = 13 * mm

        self.width = max(self.grid_width, 205 * mm)
        self.height = self.grid_height + self.legend_height

    def wrap(
        self,
        available_width: float,
        available_height: float,
    ) -> tuple[float, float]:
        return min(self.width, available_width), self.height

    def draw(self) -> None:
        canvas = self.canv

        obstacles = {
            (coordinate.row, coordinate.column)
            for coordinate in self.maze.obstacles
        }

        explored = set()
        path = set()

        if self.result is not None:
            explored = {
                (coordinate.row, coordinate.column)
                for coordinate in self.result.explored_order
            }

            path = {
                (coordinate.row, coordinate.column)
                for coordinate in self.result.path
            }

        start = (
            self.maze.start.row,
            self.maze.start.column,
        )

        goal = (
            self.maze.goal.row,
            self.maze.goal.column,
        )

        x_offset = (self.width - self.grid_width) / 2
        y_offset = self.legend_height

        canvas.setLineWidth(0.25)
        canvas.setStrokeColor(COLOR_BORDER)

        for row in range(self.maze.rows):
            for column in range(self.maze.columns):
                position = (row, column)

                x = x_offset + column * self.cell_size
                y = (
                    y_offset
                    + (self.maze.rows - row - 1) * self.cell_size
                )

                fill_color = COLOR_FREE

                if position in explored:
                    fill_color = COLOR_EXPLORED

                if position in path:
                    fill_color = COLOR_PATH

                if position in obstacles:
                    fill_color = COLOR_OBSTACLE

                if position == start:
                    fill_color = COLOR_START

                if position == goal:
                    fill_color = COLOR_GOAL

                canvas.setFillColor(fill_color)

                canvas.rect(
                    x,
                    y,
                    self.cell_size,
                    self.cell_size,
                    fill=1,
                    stroke=1,
                )

                if self.cell_size >= 5 * mm:
                    if position == start:
                        self._draw_cell_label(
                            "S",
                            x,
                            y,
                        )

                    if position == goal:
                        self._draw_cell_label(
                            "G",
                            x,
                            y,
                        )

        canvas.setStrokeColor(COLOR_TEXT)
        canvas.setLineWidth(1)

        canvas.rect(
            x_offset,
            y_offset,
            self.grid_width,
            self.grid_height,
            fill=0,
            stroke=1,
        )

        self._draw_legend(canvas)

    def _draw_cell_label(
        self,
        label: str,
        x: float,
        y: float,
    ) -> None:
        canvas = self.canv

        canvas.setFillColor(colors.white)
        canvas.setFont(
            "Helvetica-Bold",
            min(9, self.cell_size * 0.42),
        )

        canvas.drawCentredString(
            x + self.cell_size / 2,
            y + self.cell_size / 2 - 3,
            label,
        )

    def _draw_legend(self, canvas) -> None:
        legend = (
            ("Libre", COLOR_FREE),
            ("Obstáculo", COLOR_OBSTACLE),
            ("Explorado", COLOR_EXPLORED),
            ("Ruta", COLOR_PATH),
            ("Inicio", COLOR_START),
            ("Destino", COLOR_GOAL),
        )

        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(COLOR_MUTED)

        item_width = self.width / len(legend)
        square_size = 3.5 * mm
        y = 3.5 * mm

        for index, (label, color) in enumerate(legend):
            x = index * item_width

            canvas.setFillColor(color)
            canvas.setStrokeColor(COLOR_BORDER)

            canvas.rect(
                x,
                y,
                square_size,
                square_size,
                fill=1,
                stroke=1,
            )

            canvas.setFillColor(COLOR_MUTED)

            canvas.drawString(
                x + square_size + 2 * mm,
                y + 1,
                label,
            )


def create_styles() -> dict:
    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="RoboMazeTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=COLOR_TEXT,
            spaceAfter=3 * mm,
        )
    )

    styles.add(
        ParagraphStyle(
            name="RoboMazeSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=COLOR_MUTED,
            spaceAfter=5 * mm,
        )
    )

    styles.add(
        ParagraphStyle(
            name="RoboMazeHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=COLOR_TEXT,
            spaceBefore=3 * mm,
            spaceAfter=3 * mm,
        )
    )

    styles.add(
        ParagraphStyle(
            name="RoboMazeCentered",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=COLOR_MUTED,
            alignment=TA_CENTER,
        )
    )

    return styles


def create_table_style(
    header: bool = False,
) -> TableStyle:
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, -1), COLOR_TEXT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, COLOR_BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        (
            "ROWBACKGROUNDS",
            (0, 0),
            (-1, -1),
            [colors.white, COLOR_SURFACE],
        ),
    ]

    if header:
        commands.extend(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    COLOR_TEXT,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
            ]
        )

    return TableStyle(commands)


def format_coordinate(row: int, column: int) -> str:
    return f"({row}, {column})"


def result_status(result: SearchResponse) -> str:
    return "Ruta encontrada" if result.found else "Sin solución"


def draw_footer(canvas, document) -> None:
    canvas.saveState()

    page_width, _ = landscape(A4)

    canvas.setStrokeColor(COLOR_BORDER)
    canvas.setLineWidth(0.5)

    canvas.line(
        14 * mm,
        10 * mm,
        page_width - 14 * mm,
        10 * mm,
    )

    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(COLOR_MUTED)

    canvas.drawString(
        14 * mm,
        6 * mm,
        "RoboMaze - Inteligencia Artificial 1",
    )

    canvas.drawRightString(
        page_width - 14 * mm,
        6 * mm,
        f"Página {document.page}",
    )

    canvas.restoreState()


def create_configuration_table(
    request: PdfReportRequest,
) -> Table:
    maze = request.maze

    data = [
        [
            "Dimensiones",
            f"{maze.rows} x {maze.columns}",
            "Inicio",
            format_coordinate(
                maze.start.row,
                maze.start.column,
            ),
            "Destino",
            format_coordinate(
                maze.goal.row,
                maze.goal.column,
            ),
            "Obstáculos",
            str(len(maze.obstacles)),
        ]
    ]

    table = Table(
        data,
        colWidths=[
            25 * mm,
            24 * mm,
            16 * mm,
            25 * mm,
            18 * mm,
            25 * mm,
            22 * mm,
            20 * mm,
        ],
    )

    table.setStyle(create_table_style())

    return table


def create_result_table(
    result: SearchResponse,
) -> Table:
    data = [
        [
            "Algoritmo",
            "Estado",
            "Longitud",
            "Nodos explorados",
            "Tiempo",
        ],
        [
            result.algorithm_name,
            result_status(result),
            f"{result.path_length} movimientos",
            str(result.explored_nodes),
            f"{result.execution_time_ms:.6f} ms",
        ],
    ]

    table = Table(
        data,
        colWidths=[
            55 * mm,
            38 * mm,
            35 * mm,
            38 * mm,
            38 * mm,
        ],
        repeatRows=1,
    )

    table.setStyle(create_table_style(header=True))

    return table


def create_comparison_table(
    request: PdfReportRequest,
) -> Table | None:
    if request.comparison is None:
        return None

    results = (
        request.comparison.bfs,
        request.comparison.dfs,
        request.comparison.astar,
    )

    data = [
        [
            "Algoritmo",
            "Estado",
            "Longitud",
            "Nodos explorados",
            "Tiempo",
        ]
    ]

    for result in results:
        data.append(
            [
                result.algorithm_name,
                result_status(result),
                result.path_length if result.found else "—",
                result.explored_nodes,
                f"{result.execution_time_ms:.6f} ms",
            ]
        )

    table = Table(
        data,
        colWidths=[
            55 * mm,
            37 * mm,
            32 * mm,
            38 * mm,
            40 * mm,
        ],
        repeatRows=1,
    )

    table.setStyle(create_table_style(header=True))

    return table


def create_route_table(
    result: SearchResponse,
) -> Table | Paragraph:
    if not result.path:
        styles = create_styles()

        return Paragraph(
            "El algoritmo no encontró una ruta válida.",
            styles["RoboMazeCentered"],
        )

    data = [["Paso", "Fila", "Columna"]]

    for index, coordinate in enumerate(
        result.path,
        start=1,
    ):
        data.append(
            [
                str(index),
                str(coordinate.row),
                str(coordinate.column),
            ]
        )

    table = Table(
        data,
        colWidths=[
            35 * mm,
            45 * mm,
            45 * mm,
        ],
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(create_table_style(header=True))

    return table


def build_pdf_report(
    request: PdfReportRequest,
) -> tuple[bytes, str]:
    """Construye y devuelve el documento PDF completo."""

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=13 * mm,
        bottomMargin=15 * mm,
        title="Reporte RoboMaze",
        author="RoboMaze",
        subject="Resultados de algoritmos de búsqueda",
    )

    styles = create_styles()

    primary_result = request.result

    if primary_result is None and request.comparison is not None:
        primary_result = request.comparison.bfs

    story = [
        Paragraph(
            "RoboMaze",
            styles["RoboMazeTitle"],
        ),
        Paragraph(
            (
                "Reporte de navegación y comparación de algoritmos "
                "de búsqueda en una cuadrícula bidimensional."
            ),
            styles["RoboMazeSubtitle"],
        ),
        Paragraph(
            "Configuración del laberinto",
            styles["RoboMazeHeading"],
        ),
        create_configuration_table(request),
        Spacer(1, 4 * mm),
    ]

    if primary_result is not None:
        story.extend(
            [
                Paragraph(
                    "Resultado principal",
                    styles["RoboMazeHeading"],
                ),
                create_result_table(primary_result),
                Spacer(1, 4 * mm),
            ]
        )

    story.extend(
        [
            Paragraph(
                "Representación del recorrido",
                styles["RoboMazeHeading"],
            ),
            MazeFlowable(
                request.maze,
                primary_result,
            ),
        ]
    )

    comparison_table = create_comparison_table(request)

    if comparison_table is not None:
        story.extend(
            [
                Spacer(1, 3 * mm),
                Paragraph(
                    "Comparación de algoritmos",
                    styles["RoboMazeHeading"],
                ),
                comparison_table,
            ]
        )

    if primary_result is not None:
        story.extend(
            [
                PageBreak(),
                Paragraph(
                    "Ruta completa",
                    styles["RoboMazeTitle"],
                ),
                Paragraph(
                    (
                        f"Algoritmo: {primary_result.algorithm_name}. "
                        f"Longitud: {primary_result.path_length} movimientos."
                    ),
                    styles["RoboMazeSubtitle"],
                ),
                create_route_table(primary_result),
            ]
        )

    generated_at = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    document.build(
        story,
        onFirstPage=draw_footer,
        onLaterPages=draw_footer,
    )

    pdf_content = buffer.getvalue()
    buffer.close()

    filename = f"robomaze-reporte-{generated_at}.pdf"

    return pdf_content, filename
