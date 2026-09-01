BEGIN;

INSERT INTO invoice_categories (
    name,
    description
)
VALUES
    ('Tecnología', 'Equipo de cómputo, electrónica y accesorios'),
    ('Oficina', 'Papelería, mobiliario y suministros'),
    ('Servicios', 'Servicios profesionales y empresariales'),
    ('Alimentos', 'Productos alimenticios y consumo'),
    ('Transporte', 'Combustible, logística y transporte'),
    ('Otros', 'Facturas sin una categoría específica')
ON CONFLICT (name) DO NOTHING;

INSERT INTO users (
    full_name,
    username,
    email,
    password_hash,
    role,
    is_active
)
SELECT
    'Administrador SmartInvoice',
    'admin',
    'admin@example.com',
    crypt('Admin123*', gen_salt('bf', 12)),
    'ADMIN',
    TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM users
    WHERE username = 'admin'
       OR email = 'admin@example.com'
);

INSERT INTO providers (
    name,
    nit,
    email,
    phone,
    address,
    category_id,
    created_by
)
SELECT
    'Demo Ficticio Tecnologia Alfa',
    '9000001-9',
    'proveedor.alfa@example.com',
    '0000-0001',
    'Ubicacion ficticia Alfa',
    category.id,
    admin_user.id
FROM invoice_categories category
CROSS JOIN users admin_user
WHERE category.name = 'Tecnología'
  AND admin_user.username = 'admin'
  AND NOT EXISTS (
      SELECT 1
      FROM providers
      WHERE nit = '9000001-9'
  );

INSERT INTO providers (
    name,
    nit,
    email,
    phone,
    address,
    category_id,
    created_by
)
SELECT
    'Demo Ficticio Oficina Beta',
    '9000002-9',
    'proveedor.beta@example.com',
    '0000-0002',
    'Ubicacion ficticia Beta',
    category.id,
    admin_user.id
FROM invoice_categories category
CROSS JOIN users admin_user
WHERE category.name = 'Oficina'
  AND admin_user.username = 'admin'
  AND NOT EXISTS (
      SELECT 1
      FROM providers
      WHERE nit = '9000002-9'
  );

INSERT INTO providers (
    name,
    nit,
    email,
    phone,
    address,
    category_id,
    created_by
)
SELECT
    'Demo Ficticio Servicios Gamma',
    '9000003-9',
    'proveedor.gamma@example.com',
    '0000-0003',
    'Ubicacion ficticia Gamma',
    category.id,
    admin_user.id
FROM invoice_categories category
CROSS JOIN users admin_user
WHERE category.name = 'Servicios'
  AND admin_user.username = 'admin'
  AND NOT EXISTS (
      SELECT 1
      FROM providers
      WHERE nit = '9000003-9'
  );

INSERT INTO scheduled_tasks (
    name,
    task_type,
    cron_expression,
    parameters,
    is_active,
    created_by
)
SELECT
    'Reporte administrativo diario',
    'GENERATE_DAILY_REPORT',
    '0 18 * * *',
    '{"formats": ["PDF", "XLSX", "CSV"], "send_email": false}'::JSONB,
    FALSE,
    id
FROM users
WHERE username = 'admin'
ON CONFLICT (name) DO NOTHING;

INSERT INTO system_settings (
    setting_key,
    setting_value,
    description,
    is_public
)
VALUES
    (
        'ocr.configuration',
        '{"language": "spa", "minimum_confidence": 60, "dpi": 300}'::JSONB,
        'Configuración general del procesamiento OCR',
        FALSE
    ),
    (
        'invoice.validation',
        '{"total_tolerance": 0.05, "validate_nit": true, "detect_duplicates": true}'::JSONB,
        'Configuración de validación de facturas',
        FALSE
    )
ON CONFLICT (setting_key) DO NOTHING;

COMMIT;
