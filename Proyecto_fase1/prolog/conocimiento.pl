:- encoding(utf8).

:- dynamic sintoma/3.
:- dynamic falla/3.
:- dynamic recomendacion/3.
:- dynamic regla/3.

% ============================================================
% SÍNTOMAS
% sintoma(Id, NombreVisible, Categoria).
% ============================================================

sintoma(no_enciende, "El equipo no enciende", "Arranque y energía").
sintoma(pantalla_negra, "La pantalla permanece negra", "Arranque y energía").
sintoma(bateria_no_carga, "La batería no carga", "Arranque y energía").
sintoma(pantalla_azul, "Aparece una pantalla azul", "Sistema operativo").
sintoma(lentitud_sistema, "El sistema funciona muy lento", "Sistema operativo").
sintoma(aplicaciones_se_cierran, "Las aplicaciones se cierran solas", "Sistema operativo").
sintoma(ventanas_emergentes, "Aparecen ventanas emergentes inesperadas", "Sistema operativo").
sintoma(reinicio_inesperado, "El equipo se reinicia inesperadamente", "Hardware interno").
sintoma(pitidos_arranque, "El equipo emite pitidos al encender", "Hardware interno").
sintoma(ruido_disco, "El disco duro produce ruidos extraños", "Hardware interno").
sintoma(sobrecalentamiento, "El equipo se sobrecalienta", "Hardware interno").
sintoma(ventilador_ruidoso, "El ventilador produce demasiado ruido", "Hardware interno").
sintoma(sin_internet, "El equipo no tiene conexión a internet", "Conectividad").
sintoma(no_detecta_usb, "El equipo no detecta dispositivos USB", "Conectividad").
sintoma(sin_sonido, "El equipo no reproduce sonido", "Conectividad").
sintoma(teclado_no_responde, "El teclado no responde", "Periféricos").
sintoma(mouse_no_responde, "El mouse no responde", "Periféricos").
sintoma(fecha_hora_reinicia, "La fecha y la hora se reinician", "Periféricos").

% ============================================================
% FALLAS
% falla(Id, NombreVisible, Descripcion).
% ============================================================

falla(fuente_poder, "Falla en la fuente de poder", "El equipo puede presentar problemas en el suministro de energía.").
falla(memoria_ram, "Falla de memoria RAM", "Uno o varios módulos de memoria pueden estar dañados o mal conectados.").
falla(disco_duro, "Falla de disco duro", "La unidad de almacenamiento puede presentar deterioro o errores físicos.").
falla(sobrecalentamiento_cpu, "Sobrecalentamiento del procesador", "La temperatura interna supera los niveles adecuados de funcionamiento.").
falla(sistema_operativo_corrupto, "Sistema operativo corrupto", "Algunos archivos esenciales del sistema pueden estar dañados.").
falla(malware, "Posible infección por malware", "El equipo puede contener software malicioso o programas no deseados.").
falla(tarjeta_red, "Problema de conexión de red", "El adaptador, sus controladores o la configuración de red pueden estar fallando.").
falla(bateria_danada, "Batería dañada", "La batería puede haber perdido su capacidad de almacenar energía.").
falla(puerto_usb_danado, "Problema en puerto USB", "Uno o varios puertos USB pueden estar dañados o mal configurados.").
falla(controladores_audio, "Problema de audio", "Los controladores o la configuración de sonido pueden ser incorrectos.").
falla(bios_bateria_cmos, "Batería CMOS descargada", "La batería que mantiene la configuración del BIOS puede estar agotada.").
falla(periferico_danado, "Periférico dañado o desconectado", "El teclado, mouse, cable, receptor o puerto pueden presentar una falla.").

% ============================================================
% RECOMENDACIONES
% recomendacion(Id, FallaId, Texto).
% ============================================================

recomendacion(rec_fuente_poder, fuente_poder, "Verifique el cable de corriente, pruebe otra fuente de poder y revise las conexiones internas.").
recomendacion(rec_memoria_ram, memoria_ram, "Ejecute una prueba de memoria, limpie los módulos RAM y pruebe cada módulo en ranuras diferentes.").
recomendacion(rec_disco_duro, disco_duro, "Revise el estado SMART del disco, respalde la información y considere reemplazar la unidad.").
recomendacion(rec_sobrecalentamiento, sobrecalentamiento_cpu, "Limpie los ventiladores, cambie la pasta térmica y revise el flujo de aire del equipo.").
recomendacion(rec_sistema_operativo, sistema_operativo_corrupto, "Ejecute las herramientas de reparación, restaure el sistema o reinstale el sistema operativo.").
recomendacion(rec_malware, malware, "Ejecute un análisis antivirus, elimine programas sospechosos y actualice el sistema.").
recomendacion(rec_tarjeta_red, tarjeta_red, "Revise los controladores de red, reinicie el adaptador y pruebe otra conexión.").
recomendacion(rec_bateria, bateria_danada, "Pruebe otro cargador, revise el estado de la batería y considere reemplazarla.").
recomendacion(rec_usb, puerto_usb_danado, "Pruebe otro puerto, actualice los controladores y revise si existe daño físico.").
recomendacion(rec_audio, controladores_audio, "Actualice los controladores de audio y verifique la configuración del dispositivo de salida.").
recomendacion(rec_cmos, bios_bateria_cmos, "Reemplace la batería CMOS y configure nuevamente la fecha y la hora en el BIOS.").
recomendacion(rec_periferico, periferico_danado, "Pruebe el periférico en otro equipo y revise el cable, receptor o puerto de conexión.").

% ============================================================
% REGLAS
% regla(Id, FallaId, ListaSintomas).
% ============================================================

regla(regla_fuente_poder, fuente_poder, [no_enciende, pantalla_negra]).
regla(regla_memoria_ram, memoria_ram, [pantalla_azul, reinicio_inesperado, pitidos_arranque]).
regla(regla_disco_duro, disco_duro, [ruido_disco, lentitud_sistema, aplicaciones_se_cierran]).
regla(regla_sobrecalentamiento, sobrecalentamiento_cpu, [sobrecalentamiento, reinicio_inesperado, ventilador_ruidoso]).
regla(regla_sistema_operativo, sistema_operativo_corrupto, [pantalla_azul, aplicaciones_se_cierran, lentitud_sistema]).
regla(regla_malware, malware, [lentitud_sistema, ventanas_emergentes, aplicaciones_se_cierran]).
regla(regla_tarjeta_red, tarjeta_red, [sin_internet]).
regla(regla_bateria, bateria_danada, [bateria_no_carga]).
regla(regla_usb, puerto_usb_danado, [no_detecta_usb]).
regla(regla_audio, controladores_audio, [sin_sonido]).
regla(regla_cmos, bios_bateria_cmos, [fecha_hora_reinicia]).
regla(regla_periferico, periferico_danado, [teclado_no_responde, mouse_no_responde]).
