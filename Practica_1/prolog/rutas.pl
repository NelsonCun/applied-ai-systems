:- dynamic ciudad/1.
:- dynamic conexion/3.

:- multifile ciudad/1.
:- multifile conexion/3.

% Base de conocimiento

ciudad(guatemala).
ciudad(antigua).
ciudad(escuintla).
ciudad(mazatenango).
ciudad(retalhuleu).
ciudad(quetzaltenango).
ciudad(huehuetenango).
ciudad(salama).
ciudad(coban).
ciudad(zacapa).
ciudad(chiquimula).
ciudad(flores).

conexion(guatemala, antigua, 40).
conexion(guatemala, escuintla, 60).
conexion(antigua, escuintla, 50).
conexion(escuintla, mazatenango, 110).
conexion(mazatenango, retalhuleu, 35).
conexion(retalhuleu, quetzaltenango, 65).
conexion(quetzaltenango, huehuetenango, 90).
conexion(guatemala, salama, 100).
conexion(salama, coban, 110).
conexion(coban, flores, 250).
conexion(guatemala, zacapa, 150).
conexion(zacapa, chiquimula, 40).
conexion(chiquimula, flores, 270).
conexion(zacapa, salama, 120).
conexion(antigua, quetzaltenango, 180).
conexion(escuintla, retalhuleu, 160).

% Conexión bidireccional

conectadas(A, B, D) :-
    conexion(A, B, D).

conectadas(A, B, D) :-
    conexion(B, A, D).


% Listar ciudades

ciudades(Lista) :-
    findall(C, ciudad(C), Ciudades),
    sort(Ciudades, Lista).


% Búsqueda de rutas sin ciclos

ruta(Origen, Destino, Ruta, Distancia) :-
    ciudad(Origen),
    ciudad(Destino),
    camino(Origen, Destino, [Origen], RutaInvertida, 0, Distancia),
    reverse(RutaInvertida, Ruta).

camino(Destino, Destino, Visitados, Visitados, Distancia, Distancia).

camino(Actual, Destino, Visitados, Ruta, Acumulado, DistanciaTotal) :-
    conectadas(Actual, Siguiente, Distancia),
    \+ member(Siguiente, Visitados),
    NuevoAcumulado is Acumulado + Distancia,
    camino(Siguiente, Destino, [Siguiente | Visitados], Ruta, NuevoAcumulado, DistanciaTotal).



% Rutas ordenadas por distancia

ruta_ordenada(Origen, Destino, Ruta, Distancia) :-
    setof(D-R, ruta(Origen, Destino, R, D), ParesOrdenados),
    member(Distancia-Ruta, ParesOrdenados).


% Ruta mas corta

ruta_mas_corta(Origen, Destino, Ruta, Distancia) :-
    setof(D-R, ruta(Origen, Destino, R, D), [Distancia-Ruta | _]).


% Agregar ciudad y conexión

agregar_ciudad(Ciudad) :-
    ciudad(Ciudad),
    !.

agregar_ciudad(Ciudad) :-
    assertz(ciudad(Ciudad)).

agregar_conexion(Origen, Destino, Distancia) :-
    number(Distancia),
    Distancia > 0,
    agregar_ciudad(Origen),
    agregar_ciudad(Destino),
    \+ conectadas(Origen, Destino, _),
    assertz(conexion(Origen, Destino, Distancia)).