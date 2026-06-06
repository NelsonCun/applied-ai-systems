import re
from pathlib import Path
from pyswip import Prolog


class PrologRepository:
    def __init__(self):
        self.prolog = Prolog()

        root = Path(__file__).resolve().parents[3]
        prolog_file = root / "prolog" / "rutas.pl"

        self.prolog.consult(str(prolog_file))

    def _normalize_atom(self, value: str) -> str:
        atom = value.strip().lower().replace(" ", "_")

        if not re.fullmatch(r"[a-z][a-z0-9_]*", atom):
            raise ValueError("Nombre de ciudad inválido. Use letras, números o guion bajo.")

        return atom

    def get_cities(self):
        results = list(self.prolog.query("ciudad(C)"))
        cities = sorted({str(item["C"]) for item in results})
        return cities

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
        query = f"agregar_ciudad({city_atom})"
        return bool(list(self.prolog.query(query, maxresult=1)))

    def add_connection(self, origin: str, destination: str, distance: int):
        origin_atom = self._normalize_atom(origin)
        destination_atom = self._normalize_atom(destination)

        query = f"agregar_conexion({origin_atom}, {destination_atom}, {distance})"
        return bool(list(self.prolog.query(query, maxresult=1)))