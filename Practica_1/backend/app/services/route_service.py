from app.repositories.prolog_repository import PrologRepository


class RouteService:
    def __init__(self):
        self.repository = PrologRepository()

    def list_cities(self):
        return self.repository.get_cities()

    def shortest_route(self, origin: str, destination: str):
        if origin == destination:
            raise ValueError("La ciudad origen y destino no pueden ser iguales.")

        return self.repository.get_shortest_route(origin, destination)

    def all_routes(self, origin: str, destination: str):
        if origin == destination:
            raise ValueError("La ciudad origen y destino no pueden ser iguales.")

        return self.repository.get_all_routes(origin, destination)

    def add_city(self, city: str):
        return self.repository.add_city(city)

    def add_connection(self, origin: str, destination: str, distance: int):
        return self.repository.add_connection(origin, destination, distance)