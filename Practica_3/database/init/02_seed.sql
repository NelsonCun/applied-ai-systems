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
    'admin@smartinvoice.com',
    crypt('Admin123*', gen_salt('bf', 12)),
    'ADMIN',
    TRUE
WHERE NOT EXISTS (
    SELECT 1
    FROM users
    WHERE username = 'admin'
       OR email = 'admin@smartinvoice.com'
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
    'Tecnología Maya, S.A.',
    '1234567-8',
    'ventas@tecnologiamaya.com',
    '2222-1001',
    'Ciudad de Guatemala',
    category.id,
    admin_user.id
FROM invoice_categories category
CROSS JOIN users admin_user
WHERE category.name = 'Tecnología'
  AND admin_user.username = 'admin'
  AND NOT EXISTS (
      SELECT 1
      FROM providers
      WHERE nit = '1234567-8'
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
    'Distribuidora Quetzal, S.A.',
    '7654321-0',
    'facturacion@quetzal.com',
    '2222-1002',
    'Mixco, Guatemala',
    category.id,
    admin_user.id
FROM invoice_categories category
CROSS JOIN users admin_user
WHERE category.name = 'Oficina'
  AND admin_user.username = 'admin'
  AND NOT EXISTS (
      SELECT 1
      FROM providers
      WHERE nit = '7654321-0'
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
    'Servicios Chapines',
    '9876543-K',
    'contacto@servicioschapines.com',
    '2222-1003',
    'Antigua Guatemala',
    category.id,
    admin_user.id
FROM invoice_categories category
CROSS JOIN users admin_user
WHERE category.name = 'Servicios'
  AND admin_user.username = 'admin'
  AND NOT EXISTS (
      SELECT 1
      FROM providers
      WHERE nit = '9876543-K'
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
