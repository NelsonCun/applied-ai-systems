BEGIN;

-- ============================================================
-- Usuario administrador requerido por el enunciado
-- Usuario: IA1-User
-- Contraseña: IA1-password@_new
--
-- La contraseña se almacena como hash bcrypt mediante pgcrypto.
-- ============================================================

INSERT INTO admin_users (
    username,
    password_hash,
    full_name,
    is_active
)
VALUES (
    'IA1-User',
    crypt('IA1-password@_new', gen_salt('bf', 12)),
    'Administrador SmartBot',
    TRUE
)
ON CONFLICT (username) DO NOTHING;

-- ============================================================
-- Configuración inicial de la institución ficticia
-- ============================================================

INSERT INTO bot_settings (
    id,
    hospital_name,
    telegram_chat_id,
    bot_username,
    welcome_message,
    unknown_question_message,
    is_active
)
VALUES (
    1,
    'Hospital Vida Central',
    NULL,
    NULL,
    'Bienvenido al asistente virtual del Hospital Vida Central. Escriba su consulta para buscar información administrativa del hospital.',
    'No encontré una respuesta registrada para esa consulta. Comuníquese con atención al paciente para recibir ayuda.',
    TRUE
)
ON CONFLICT (id) DO NOTHING;

COMMIT;
