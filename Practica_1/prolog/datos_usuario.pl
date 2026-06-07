:- dynamic ciudad/1.
:- dynamic conexion/3.

:- multifile ciudad/1.
:- multifile conexion/3.

% Datos agregados desde la aplicación.
% Este archivo puede ser sobrescrito automáticamente.

ciudad(chimaltenango).
ciudad(cuilapa).
ciudad(jalapa).
ciudad(san_lucas).
ciudad(san_marcos).

conexion(antigua, chimaltenango, 20).
conexion(guatemala, jalapa, 167).
conexion(quetzaltenango, san_marcos, 45).
