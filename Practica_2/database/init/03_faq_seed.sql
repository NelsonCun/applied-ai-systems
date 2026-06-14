\set ON_ERROR_STOP on

BEGIN;

-- ============================================================
-- Categorías administrativas del Hospital Vida Central
-- ============================================================

INSERT INTO categories (
    name,
    description,
    is_active
)
VALUES
(
    'Horarios y visitas',
    'Información sobre horarios de atención, emergencias, visitas y laboratorio.',
    TRUE
),
(
    'Citas y admisiones',
    'Procedimientos para solicitar, modificar y asistir a citas hospitalarias.',
    TRUE
),
(
    'Pagos y seguros',
    'Información administrativa sobre pagos, facturación, costos y seguros médicos.',
    TRUE
),
(
    'Documentos y resultados',
    'Requisitos de identificación, expedientes y entrega de resultados.',
    TRUE
),
(
    'Servicios e instalaciones',
    'Información sobre farmacia, cafetería, estacionamiento y accesibilidad.',
    TRUE
)
ON CONFLICT (name)
DO UPDATE SET
    description = EXCLUDED.description,
    is_active = TRUE,
    updated_at = CURRENT_TIMESTAMP;


-- ============================================================
-- Preguntas frecuentes
-- ============================================================

INSERT INTO questions (
    category_id,
    question_text,
    normalized_text,
    is_active
)
SELECT
    category.id,
    faq.question_text,
    faq.normalized_text,
    TRUE
FROM (
    VALUES
    (
        'Horarios y visitas',
        '¿Cuál es el horario de atención general?',
        'cual es el horario de atencion general'
    ),
    (
        'Horarios y visitas',
        '¿Cuál es el horario de emergencias?',
        'cual es el horario de emergencias'
    ),
    (
        'Horarios y visitas',
        '¿Cuál es el horario de visitas?',
        'cual es el horario de visitas'
    ),
    (
        'Horarios y visitas',
        '¿Cuál es el horario del laboratorio?',
        'cual es el horario del laboratorio'
    ),
    (
        'Citas y admisiones',
        '¿Cómo puedo solicitar una cita?',
        'como puedo solicitar una cita'
    ),
    (
        'Citas y admisiones',
        '¿Cómo puedo cancelar o reprogramar una cita?',
        'como puedo cancelar o reprogramar una cita'
    ),
    (
        'Citas y admisiones',
        '¿Qué documentos debo llevar a una cita?',
        'que documentos debo llevar a una cita'
    ),
    (
        'Citas y admisiones',
        '¿Con cuánto tiempo de anticipación debo llegar?',
        'con cuanto tiempo de anticipacion debo llegar'
    ),
    (
        'Pagos y seguros',
        '¿Qué métodos de pago aceptan?',
        'que metodos de pago aceptan'
    ),
    (
        'Pagos y seguros',
        '¿Atienden seguros médicos?',
        'atienden seguros medicos'
    ),
    (
        'Pagos y seguros',
        '¿Cómo solicito una factura?',
        'como solicito una factura'
    ),
    (
        'Pagos y seguros',
        '¿Dónde puedo consultar el costo de un servicio?',
        'donde puedo consultar el costo de un servicio'
    ),
    (
        'Documentos y resultados',
        '¿Cómo puedo obtener mis resultados de laboratorio?',
        'como puedo obtener mis resultados de laboratorio'
    ),
    (
        'Documentos y resultados',
        '¿Cómo solicito una copia de mi expediente clínico?',
        'como solicito una copia de mi expediente clinico'
    ),
    (
        'Documentos y resultados',
        '¿Qué documento necesito para ser atendido?',
        'que documento necesito para ser atendido'
    ),
    (
        'Documentos y resultados',
        '¿Puede otra persona recoger mis resultados?',
        'puede otra persona recoger mis resultados'
    ),
    (
        'Servicios e instalaciones',
        '¿El hospital cuenta con estacionamiento?',
        'el hospital cuenta con estacionamiento'
    ),
    (
        'Servicios e instalaciones',
        '¿El hospital tiene acceso para personas con discapacidad?',
        'el hospital tiene acceso para personas con discapacidad'
    ),
    (
        'Servicios e instalaciones',
        '¿Hay farmacia dentro del hospital?',
        'hay farmacia dentro del hospital'
    ),
    (
        'Servicios e instalaciones',
        '¿El hospital cuenta con cafetería?',
        'el hospital cuenta con cafeteria'
    )
) AS faq (
    category_name,
    question_text,
    normalized_text
)
INNER JOIN categories AS category
    ON category.name = faq.category_name
ON CONFLICT (normalized_text)
DO UPDATE SET
    category_id = EXCLUDED.category_id,
    question_text = EXCLUDED.question_text,
    is_active = TRUE,
    updated_at = CURRENT_TIMESTAMP;


-- ============================================================
-- Respuestas
-- ============================================================

INSERT INTO answers (
    question_id,
    answer_text,
    is_active
)
SELECT
    question.id,
    faq.answer_text,
    TRUE
FROM (
    VALUES
    (
        'cual es el horario de atencion general',
        'La atención general se brinda de lunes a viernes de 7:00 a 18:00 horas y los sábados de 8:00 a 13:00 horas. Los domingos se atienden únicamente emergencias.'
    ),
    (
        'cual es el horario de emergencias',
        'El área de emergencias del Hospital Vida Central funciona las 24 horas, todos los días del año.'
    ),
    (
        'cual es el horario de visitas',
        'El horario general de visitas es de 15:00 a 18:00 horas todos los días. Se permite un visitante por paciente y debe presentar documento de identificación.'
    ),
    (
        'cual es el horario del laboratorio',
        'El laboratorio atiende de lunes a viernes de 6:30 a 17:00 horas y los sábados de 7:00 a 12:00 horas.'
    ),
    (
        'como puedo solicitar una cita',
        'Puede solicitar una cita en el área de recepción o mediante el canal telefónico oficial del hospital. Debe indicar el servicio requerido y proporcionar sus datos personales.'
    ),
    (
        'como puedo cancelar o reprogramar una cita',
        'Puede cancelar o reprogramar su cita comunicándose con recepción. Se recomienda realizar el cambio con al menos 24 horas de anticipación.'
    ),
    (
        'que documentos debo llevar a una cita',
        'Debe presentar DPI o pasaporte, confirmación de la cita y, cuando corresponda, orden médica, referencia o carné del seguro.'
    ),
    (
        'con cuanto tiempo de anticipacion debo llegar',
        'Se recomienda llegar 30 minutos antes de la cita para completar el registro y la verificación de documentos.'
    ),
    (
        'que metodos de pago aceptan',
        'El hospital acepta efectivo, tarjetas de débito, tarjetas de crédito y transferencias bancarias autorizadas.'
    ),
    (
        'atienden seguros medicos',
        'El hospital trabaja con diferentes aseguradoras. Antes de recibir el servicio debe confirmar la cobertura y presentar la autorización correspondiente.'
    ),
    (
        'como solicito una factura',
        'Solicite la factura en caja antes de efectuar el pago y proporcione el nombre de facturación, NIT o la indicación de consumidor final.'
    ),
    (
        'donde puedo consultar el costo de un servicio',
        'Los costos pueden consultarse en admisiones o caja. El monto puede variar según el procedimiento, materiales y cobertura del seguro.'
    ),
    (
        'como puedo obtener mis resultados de laboratorio',
        'Puede solicitar sus resultados en la recepción del laboratorio presentando su documento de identificación y comprobante. Los resultados se entregan después de su validación.'
    ),
    (
        'como solicito una copia de mi expediente clinico',
        'Debe completar una solicitud en el área de archivo clínico y presentar su documento de identificación. La entrega puede requerir varios días hábiles.'
    ),
    (
        'que documento necesito para ser atendido',
        'Las personas adultas deben presentar DPI o pasaporte. Para menores de edad se requiere certificado de nacimiento y documento de identificación del responsable.'
    ),
    (
        'puede otra persona recoger mis resultados',
        'Sí. La persona debe presentar una autorización firmada, copia del documento del paciente, su propio documento de identificación y el comprobante correspondiente.'
    ),
    (
        'el hospital cuenta con estacionamiento',
        'Sí. El hospital dispone de estacionamiento para pacientes y visitantes cerca de la entrada principal, sujeto a disponibilidad.'
    ),
    (
        'el hospital tiene acceso para personas con discapacidad',
        'Sí. Las instalaciones cuentan con rampas, elevadores y servicios sanitarios adaptados para facilitar el acceso.'
    ),
    (
        'hay farmacia dentro del hospital',
        'Sí. La farmacia se encuentra en el primer nivel y atiende todos los días de 7:00 a 21:00 horas.'
    ),
    (
        'el hospital cuenta con cafeteria',
        'Sí. La cafetería se encuentra en el primer nivel y atiende todos los días de 6:00 a 20:00 horas.'
    )
) AS faq (
    normalized_text,
    answer_text
)
INNER JOIN questions AS question
    ON question.normalized_text = faq.normalized_text
ON CONFLICT (question_id)
DO UPDATE SET
    answer_text = EXCLUDED.answer_text,
    is_active = TRUE,
    updated_at = CURRENT_TIMESTAMP;

COMMIT;
