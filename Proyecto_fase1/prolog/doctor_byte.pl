% ============================================================
% Doctor Byte - Sistema experto para diagnóstico de fallas
% ============================================================

% -------------------------
% Síntomas disponibles
% -------------------------

sintoma(no_enciende).
sintoma(pantalla_negra).
sintoma(reinicio_inesperado).
sintoma(pitidos_arranque).
sintoma(lentitud_sistema).
sintoma(sin_internet).
sintoma(pantalla_azul).
sintoma(sobrecalentamiento).
sintoma(teclado_no_responde).
sintoma(mouse_no_responde).
sintoma(ruido_disco).
sintoma(aplicaciones_se_cierran).
sintoma(no_detecta_usb).
sintoma(sin_sonido).
sintoma(bateria_no_carga).
sintoma(ventilador_ruidoso).
sintoma(fecha_hora_reinicia).
sintoma(ventanas_emergentes).

% -------------------------
% Fallas diagnosticables
% -------------------------

falla(fuente_poder).
falla(memoria_ram).
falla(disco_duro).
falla(sobrecalentamiento_cpu).
falla(sistema_operativo_corrupto).
falla(malware).
falla(tarjeta_red).
falla(bateria_danada).
falla(puerto_usb_danado).
falla(controladores_audio).
falla(bios_bateria_cmos).
falla(periferico_danado).

% -------------------------
% Recomendaciones
% -------------------------

recomendacion(fuente_poder, 'Verificar cable de corriente, probar otra fuente de poder y revisar conexiones internas.').
recomendacion(memoria_ram, 'Ejecutar prueba de memoria, limpiar los modulos RAM y probar ranuras diferentes.').
recomendacion(disco_duro, 'Revisar estado SMART del disco, respaldar informacion y considerar reemplazo.').
recomendacion(sobrecalentamiento_cpu, 'Limpiar ventiladores, cambiar pasta termica y revisar flujo de aire.').
recomendacion(sistema_operativo_corrupto, 'Ejecutar reparacion del sistema, restaurar archivos o reinstalar el sistema operativo.').
recomendacion(malware, 'Ejecutar analisis antivirus, eliminar programas sospechosos y actualizar el sistema.').
recomendacion(tarjeta_red, 'Revisar controladores de red, reiniciar adaptador y probar otra conexion.').
recomendacion(bateria_danada, 'Probar cargador, revisar estado de bateria y considerar reemplazo.').
recomendacion(puerto_usb_danado, 'Probar otro puerto, actualizar controladores y revisar posible dano fisico.').
recomendacion(controladores_audio, 'Actualizar controladores de audio y verificar configuracion de salida.').
recomendacion(bios_bateria_cmos, 'Reemplazar bateria CMOS y configurar nuevamente fecha y hora en BIOS.').
recomendacion(periferico_danado, 'Probar perifericos en otro equipo y revisar cable, receptor o puerto de conexion.').

% -------------------------
% Reglas de inferencia
% regla(Falla, ListaDeSintomas)
% -------------------------

regla(fuente_poder, [no_enciende, pantalla_negra]).
regla(memoria_ram, [pantalla_azul, reinicio_inesperado, pitidos_arranque]).
regla(disco_duro, [ruido_disco, lentitud_sistema, aplicaciones_se_cierran]).
regla(sobrecalentamiento_cpu, [sobrecalentamiento, reinicio_inesperado, ventilador_ruidoso]).
regla(sistema_operativo_corrupto, [pantalla_azul, aplicaciones_se_cierran, lentitud_sistema]).
regla(malware, [lentitud_sistema, ventanas_emergentes, aplicaciones_se_cierran]).
regla(tarjeta_red, [sin_internet]).
regla(bateria_danada, [bateria_no_carga]).
regla(puerto_usb_danado, [no_detecta_usb]).
regla(controladores_audio, [sin_sonido]).
regla(bios_bateria_cmos, [fecha_hora_reinicia]).
regla(periferico_danado, [teclado_no_responde, mouse_no_responde]).

% -------------------------
% Conteo de coincidencias
% -------------------------

coincide(SintomasUsuario, Sintoma) :-
    member(Sintoma, SintomasUsuario).

contar_coincidencias([], _, 0).

contar_coincidencias([Sintoma|Resto], SintomasUsuario, Total) :-
    coincide(SintomasUsuario, Sintoma),
    contar_coincidencias(Resto, SintomasUsuario, Parcial),
    Total is Parcial + 1.

contar_coincidencias([Sintoma|Resto], SintomasUsuario, Total) :-
    \+ coincide(SintomasUsuario, Sintoma),
    contar_coincidencias(Resto, SintomasUsuario, Total).

% -------------------------
% Diagnóstico individual
% -------------------------

diagnosticar(SintomasUsuario, Falla, Recomendacion, Coincidencias) :-
    regla(Falla, SintomasRegla),
    contar_coincidencias(SintomasRegla, SintomasUsuario, Coincidencias),
    Coincidencias > 0,
    recomendacion(Falla, Recomendacion).

% -------------------------
% Mejor diagnóstico
% Usa corte (!) para evitar backtracking después de elegir el mejor.
% -------------------------

mejor_diagnostico(SintomasUsuario, Falla, Recomendacion, Coincidencias) :-
    findall(
        CoincidenciasTemp-FallaTemp-RecomendacionTemp,
        diagnosticar(SintomasUsuario, FallaTemp, RecomendacionTemp, CoincidenciasTemp),
        Resultados
    ),
    Resultados \= [],
    sort(Resultados, Ordenados),
    reverse(Ordenados, [Coincidencias-Falla-Recomendacion|_]),
    !.
