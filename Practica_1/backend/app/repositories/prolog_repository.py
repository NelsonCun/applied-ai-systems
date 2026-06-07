import re
from pathlib import Path
import re
import unicodedata
from pyswip import Prolog


class PrologRepository:
    BASE_PROLOG_FILE = "rutas.pl"          # Cambia a "tienda.pl" si ese es tu archivo original
    USER_DATA_FILE = "datos_usuario.pl"

    def __init__(self):
        self.prolog = Prolog()

        self.root = Path(__file__).resolve().parents[3]
        self.prolog_dir = self.root / "prolog"

        self.base_file = self.prolog_dir / self.BASE_PROLOG_FILE
        self.user_data_file = self.prolog_dir / self.USER_DATA_FILE

        self._ensure_user_data_file()

        self.prolog.consult(str(self.base_file))
        self.prolog.consult(str(self.user_data_file))

    def _ensure_user_data_file(self):
        self.prolog_dir.mkdir(parents=True, exist_ok=True)

        if not self.user_data_file.exists():
            self.user_data_file.write_text(
                ":- dynamic ciudad/1.\n"
                ":- dynamic conexion/3.\n\n"
                ":- multifile ciudad/1.\n"
                ":- multifile conexion/3.\n\n"
                "% Datos agregados desde la aplicación.\n"
                "% Este archivo puede ser sobrescrito automáticamente.\n",
                encoding="utf-8"
            )

    def _normalize_atom(self, value: str) -> str:
        if value is None:
            raise ValueError("El nombre no puede estar vacío.")

        text = value.strip().lower()

        if not text:
            raise ValueError("El nombre no puede estar vacío.")

        # Quita tildes: San José -> san jose
        text = unicodedata.normalize("NFD", text)
        text = "".join(char for char in text if unicodedata.category(char) != "Mn")

        # Convierte espacios, guiones y separadores en guion bajo
        text = re.sub(r"[\s\-]+", "_", text)

        # Elimina caracteres no válidos para átomos Prolog simples
        text = re.sub(r"[^a-z0-9_]", "", text)

        # Evita varios guiones bajos seguidos
        text = re.sub(r"_+", "_", text).strip("_")

        if not text:
            raise ValueError("Nombre de ciudad inválido.")

        # Prolog necesita que el átomo simple no inicie con número
        if not re.fullmatch(r"[a-z][a-z0-9_]*", text):
            raise ValueError(
                "Nombre de ciudad inválido. Debe iniciar con una letra."
            )

        return text

    def _city_exists(self, city: str) -> bool:
        query = f"ciudad({city})"
        return bool(list(self.prolog.query(query, maxresult=1)))

    def _connection_exists(self, origin: str, destination: str) -> bool:
        query = f"conectadas({origin}, {destination}, _)"
        return bool(list(self.prolog.query(query, maxresult=1)))

    def _read_user_facts(self):
        cities = set()
        connections = set()

        if not self.user_data_file.exists():
            return cities, connections

        content = self.user_data_file.read_text(encoding="utf-8")

        city_matches = re.findall(r"ciudad\(([a-z][a-z0-9_]*)\)\.", content)
        connection_matches = re.findall(
            r"conexion\(([a-z][a-z0-9_]*),\s*([a-z][a-z0-9_]*),\s*(\d+)\)\.",
            content
        )

        for city in city_matches:
            cities.add(city)

        for origin, destination, distance in connection_matches:
            connections.add((origin, destination, int(distance)))

        return cities, connections

    def _rewrite_user_data_file(self, cities, connections):
        lines = [
            ":- dynamic ciudad/1.",
            ":- dynamic conexion/3.",
            "",
            ":- multifile ciudad/1.",
            ":- multifile conexion/3.",
            "",
            "% Datos agregados desde la aplicación.",
            "% Este archivo puede ser sobrescrito automáticamente.",
            ""
        ]

        for city in sorted(cities):
            lines.append(f"ciudad({city}).")

        if cities:
            lines.append("")

        for origin, destination, distance in sorted(connections):
            lines.append(f"conexion({origin}, {destination}, {distance}).")

        lines.append("")

        self.user_data_file.write_text("\n".join(lines), encoding="utf-8")

    def get_cities(self):
        results = list(self.prolog.query("ciudad(C)"))
        return sorted({str(item["C"]) for item in results})

    def get_shortest_route(self, origin: str, destination: str):
        origin_atom = self._normalize_atom(origin)
        destination_atom = self._normalize_atom(destination)

        query = f"ruta_mas_corta({origin_atom}, {destination_atom}, Ruta, Distancia)"
        results = list(self.prolog.query(query, maxresult=1))

        if not results:
            return None

        result = results[0]

        return {
            "route": [str(city) for city in result["Ruta"]],
            "distance": int(result["Distancia"])
        }

    def get_all_routes(self, origin: str, destination: str):
        origin_atom = self._normalize_atom(origin)
        destination_atom = self._normalize_atom(destination)

        query = f"ruta_ordenada({origin_atom}, {destination_atom}, Ruta, Distancia)"
        results = list(self.prolog.query(query))

        return [
            {
                "route": [str(city) for city in item["Ruta"]],
                "distance": int(item["Distancia"])
            }
            for item in results
        ]

    def add_city(self, city: str):
        city_atom = self._normalize_atom(city)

        if self._city_exists(city_atom):
            return {
                "created": False,
                "message": "La ciudad ya existe."
            }

        list(self.prolog.query(f"agregar_ciudad({city_atom})", maxresult=1))

        cities, connections = self._read_user_facts()
        cities.add(city_atom)
        self._rewrite_user_data_file(cities, connections)

        return {
            "created": True,
            "message": "Ciudad agregada correctamente."
        }

    def add_connection(self, origin: str, destination: str, distance: int):
        origin_atom = self._normalize_atom(origin)
        destination_atom = self._normalize_atom(destination)

        if origin_atom == destination_atom:
            raise ValueError("El origen y el destino no pueden ser iguales.")

        if distance <= 0:
            raise ValueError("La distancia debe ser mayor a 0.")

        if not self._city_exists(origin_atom):
            raise ValueError("La ciudad origen no existe.")

        if not self._city_exists(destination_atom):
            raise ValueError("La ciudad destino no existe.")

        if self._connection_exists(origin_atom, destination_atom):
            return {
                "created": False,
                "message": "La conexión ya existe."
            }

        list(
            self.prolog.query(
                f"agregar_conexion({origin_atom}, {destination_atom}, {distance})",
                maxresult=1
            )
        )

        cities, connections = self._read_user_facts()
        connections.add((origin_atom, destination_atom, distance))
        self._rewrite_user_data_file(cities, connections)

        return {
            "created": True,
            "message": "Conexión agregada correctamente."
        }