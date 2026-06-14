:- encoding(utf8).

:- use_module(library(http/json)).

:- prolog_load_context(directory, Directorio),
   directory_file_path(Directorio, 'conocimiento.pl', ArchivoConocimiento),
   consult(ArchivoConocimiento).

% ============================================================
% MOTOR DE INFERENCIA
% ============================================================

coincide(SintomasUsuario, Sintoma) :-
    member(Sintoma, SintomasUsuario).

contar_coincidencias([], _, 0).

contar_coincidencias(
    [Sintoma | Resto],
    SintomasUsuario,
    Total
) :-
    coincide(SintomasUsuario, Sintoma),
    contar_coincidencias(
        Resto,
        SintomasUsuario,
        Parcial
    ),
    Total is Parcial + 1.

contar_coincidencias(
    [Sintoma | Resto],
    SintomasUsuario,
    Total
) :-
    \+ coincide(SintomasUsuario, Sintoma),
    contar_coincidencias(
        Resto,
        SintomasUsuario,
        Total
    ).

diagnosticar(
    SintomasUsuario,
    ReglaId,
    FallaId,
    FallaNombre,
    Recomendacion,
    Coincidencias
) :-
    regla(ReglaId, FallaId, SintomasRegla),

    contar_coincidencias(
        SintomasRegla,
        SintomasUsuario,
        Coincidencias
    ),

    Coincidencias > 0,

    falla(
        FallaId,
        FallaNombre,
        _
    ),

    once(
        recomendacion(
            _,
            FallaId,
            Recomendacion
        )
    ).

mejor_diagnostico(
    SintomasUsuario,
    FallaId,
    FallaNombre,
    Recomendacion,
    Coincidencias
) :-
    findall(
        CoincidenciasTemporal-
        FallaIdTemporal-
        FallaNombreTemporal-
        RecomendacionTemporal,

        diagnosticar(
            SintomasUsuario,
            _,
            FallaIdTemporal,
            FallaNombreTemporal,
            RecomendacionTemporal,
            CoincidenciasTemporal
        ),

        Resultados
    ),

    Resultados \= [],

    sort(Resultados, ResultadosOrdenados),

    reverse(
        ResultadosOrdenados,
        [
            Coincidencias-
            FallaId-
            FallaNombre-
            Recomendacion
            | _
        ]
    ),

    !.

% ============================================================
% SALIDAS JSON PARA EL BACKEND
% ============================================================

listar_sintomas_json :-
    findall(
        _{
            id: Id,
            nombre: Nombre,
            categoria: Categoria
        },
        sintoma(Id, Nombre, Categoria),
        Sintomas
    ),

    json_write_dict(
        current_output,
        _{sintomas: Sintomas}
    ).

listar_fallas_json :-
    findall(
        _{
            id: Id,
            nombre: Nombre,
            descripcion: Descripcion
        },
        falla(Id, Nombre, Descripcion),
        Fallas
    ),

    json_write_dict(
        current_output,
        _{fallas: Fallas}
    ).

listar_recomendaciones_json :-
    findall(
        _{
            id: Id,
            falla_id: FallaId,
            falla_nombre: FallaNombre,
            texto: Texto
        },
        (
            recomendacion(Id, FallaId, Texto),
            falla(FallaId, FallaNombre, _)
        ),
        Recomendaciones
    ),

    json_write_dict(
        current_output,
        _{recomendaciones: Recomendaciones}
    ).

listar_reglas_json :-
    findall(
        _{
            id: Id,
            falla_id: FallaId,
            falla_nombre: FallaNombre,
            sintomas: Sintomas
        },
        (
            regla(Id, FallaId, Sintomas),
            falla(FallaId, FallaNombre, _)
        ),
        Reglas
    ),

    json_write_dict(
        current_output,
        _{reglas: Reglas}
    ).

diagnostico_json(SintomasUsuario) :-
    (
        mejor_diagnostico(
            SintomasUsuario,
            FallaId,
            FallaNombre,
            Recomendacion,
            Coincidencias
        )
    ->
        Resultado = _{
            encontrado: true,
            falla: FallaId,
            falla_texto: FallaNombre,
            recomendacion: Recomendacion,
            coincidencias: Coincidencias
        }
    ;
        Resultado = _{
            encontrado: false,
            falla: "sin_diagnostico",
            falla_texto: "Sin diagnóstico",
            recomendacion:
                "No se encontró una falla probable con los síntomas seleccionados.",
            coincidencias: 0
        }
    ),

    json_write_dict(
        current_output,
        Resultado
    ).