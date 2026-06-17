BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

DO $$
BEGIN
    CREATE TYPE user_role AS ENUM (
        'ADMIN',
        'OPERATOR'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE invoice_status AS ENUM (
        'PENDING',
        'PROCESSING',
        'PROCESSED',
        'REJECTED',
        'ERROR',
        'DUPLICATE'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE processing_stage AS ENUM (
        'UPLOAD',
        'COMPUTER_VISION',
        'OCR',
        'EXTRACTION',
        'VALIDATION',
        'STORAGE',
        'RPA',
        'REPORT',
        'EMAIL'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE execution_status AS ENUM (
        'PENDING',
        'RUNNING',
        'SUCCESS',
        'WARNING',
        'ERROR'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE report_format AS ENUM (
        'PDF',
        'XLSX',
        'CSV'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE report_type AS ENUM (
        'INVOICE_DETAIL',
        'ADMINISTRATIVE',
        'SUMMARY',
        'ERRORS'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    CREATE TYPE email_status AS ENUM (
        'PENDING',
        'SENT',
        'ERROR'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    username CITEXT NOT NULL UNIQUE,
    email CITEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role user_role NOT NULL DEFAULT 'OPERATOR',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_users_username_length
        CHECK (char_length(username::TEXT) >= 3),

    CONSTRAINT chk_users_email_format
        CHECK (email::TEXT ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$')
);

CREATE TABLE IF NOT EXISTS invoice_categories (
    id BIGSERIAL PRIMARY KEY,
    name CITEXT NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS providers (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(180) NOT NULL,
    nit CITEXT NOT NULL UNIQUE,
    email CITEXT,
    phone VARCHAR(30),
    address TEXT,
    category_id BIGINT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_providers_category
        FOREIGN KEY (category_id)
        REFERENCES invoice_categories(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_providers_created_by
        FOREIGN KEY (created_by)
        REFERENCES users(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_providers_nit
        CHECK (
            upper(nit::TEXT) = 'CF'
            OR nit::TEXT ~ '^[0-9]{9}$'
            OR nit::TEXT ~ '^[0-9]{1,8}-[0-9Kk]$'
        ),

    CONSTRAINT chk_providers_email
        CHECK (
            email IS NULL
            OR email::TEXT ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
        )
);

CREATE TABLE IF NOT EXISTS invoices (
    id BIGSERIAL PRIMARY KEY,
    invoice_number VARCHAR(100),
    invoice_date DATE,

    provider_id BIGINT,
    category_id BIGINT,

    detected_provider_name VARCHAR(180),
    detected_nit VARCHAR(30),

    subtotal NUMERIC(14, 2),
    tax NUMERIC(14, 2),
    total NUMERIC(14, 2),
    currency CHAR(3) NOT NULL DEFAULT 'GTQ',

    original_file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    processed_file_path TEXT,
    file_sha256 CHAR(64) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_size_bytes BIGINT NOT NULL,

    ocr_text TEXT,
    ocr_confidence NUMERIC(5, 2),

    extracted_data JSONB NOT NULL DEFAULT '{}'::JSONB,
    validation_errors JSONB NOT NULL DEFAULT '[]'::JSONB,

    status invoice_status NOT NULL DEFAULT 'PENDING',
    attempt_count SMALLINT NOT NULL DEFAULT 0,
    last_error TEXT,

    duplicate_of_invoice_id BIGINT,

    created_by BIGINT NOT NULL,
    confirmed_by BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMPTZ,
    confirmed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_invoices_provider
        FOREIGN KEY (provider_id)
        REFERENCES providers(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_invoices_category
        FOREIGN KEY (category_id)
        REFERENCES invoice_categories(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_invoices_created_by
        FOREIGN KEY (created_by)
        REFERENCES users(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_invoices_confirmed_by
        FOREIGN KEY (confirmed_by)
        REFERENCES users(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_invoices_duplicate
        FOREIGN KEY (duplicate_of_invoice_id)
        REFERENCES invoices(id)
        ON DELETE RESTRICT,

    CONSTRAINT chk_invoices_subtotal
        CHECK (subtotal IS NULL OR subtotal >= 0),

    CONSTRAINT chk_invoices_tax
        CHECK (tax IS NULL OR tax >= 0),

    CONSTRAINT chk_invoices_total
        CHECK (total IS NULL OR total >= 0),

    CONSTRAINT chk_invoices_file_size
        CHECK (file_size_bytes > 0),

    CONSTRAINT chk_invoices_hash
        CHECK (file_sha256 ~ '^[a-fA-F0-9]{64}$'),

    CONSTRAINT chk_invoices_confidence
        CHECK (
            ocr_confidence IS NULL
            OR ocr_confidence BETWEEN 0 AND 100
        ),

    CONSTRAINT chk_invoices_validation_errors
        CHECK (jsonb_typeof(validation_errors) = 'array'),

    CONSTRAINT chk_invoices_extracted_data
        CHECK (jsonb_typeof(extracted_data) = 'object'),

    CONSTRAINT chk_invoices_duplicate_reference
        CHECK (
            duplicate_of_invoice_id IS NULL
            OR duplicate_of_invoice_id <> id
        )
);

CREATE TABLE IF NOT EXISTS invoice_items (
    id BIGSERIAL PRIMARY KEY,
    invoice_id BIGINT NOT NULL,
    line_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantity NUMERIC(12, 3),
    unit_price NUMERIC(14, 4),
    line_total NUMERIC(14, 2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_invoice_items_invoice
        FOREIGN KEY (invoice_id)
        REFERENCES invoices(id)
        ON DELETE CASCADE,

    CONSTRAINT uq_invoice_items_line
        UNIQUE (invoice_id, line_number),

    CONSTRAINT chk_invoice_items_line_number
        CHECK (line_number > 0),

    CONSTRAINT chk_invoice_items_quantity
        CHECK (quantity IS NULL OR quantity >= 0),

    CONSTRAINT chk_invoice_items_unit_price
        CHECK (unit_price IS NULL OR unit_price >= 0),

    CONSTRAINT chk_invoice_items_total
        CHECK (line_total IS NULL OR line_total >= 0)
);

CREATE TABLE IF NOT EXISTS processing_logs (
    id BIGSERIAL PRIMARY KEY,
    invoice_id BIGINT,
    user_id BIGINT,

    stage processing_stage NOT NULL,
    status execution_status NOT NULL,

    message TEXT NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::JSONB,

    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMPTZ,
    duration_ms INTEGER,

    CONSTRAINT fk_processing_logs_invoice
        FOREIGN KEY (invoice_id)
        REFERENCES invoices(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_processing_logs_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_processing_logs_details
        CHECK (jsonb_typeof(details) = 'object'),

    CONSTRAINT chk_processing_logs_duration
        CHECK (duration_ms IS NULL OR duration_ms >= 0)
);

CREATE TABLE IF NOT EXISTS reports (
    id BIGSERIAL PRIMARY KEY,
    report_type report_type NOT NULL,
    format report_format NOT NULL,
    status execution_status NOT NULL DEFAULT 'PENDING',

    file_name VARCHAR(255),
    file_path TEXT,
    filters JSONB NOT NULL DEFAULT '{}'::JSONB,

    generated_by BIGINT,
    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    generated_at TIMESTAMPTZ,

    CONSTRAINT fk_reports_generated_by
        FOREIGN KEY (generated_by)
        REFERENCES users(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_reports_filters
        CHECK (jsonb_typeof(filters) = 'object')
);

CREATE TABLE IF NOT EXISTS automation_runs (
    id BIGSERIAL PRIMARY KEY,
    invoice_id BIGINT,
    triggered_by BIGINT,

    automation_type VARCHAR(80) NOT NULL,
    status execution_status NOT NULL DEFAULT 'PENDING',

    target_url TEXT,
    result JSONB NOT NULL DEFAULT '{}'::JSONB,
    evidence_path TEXT,
    error_message TEXT,

    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_automation_runs_invoice
        FOREIGN KEY (invoice_id)
        REFERENCES invoices(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_automation_runs_user
        FOREIGN KEY (triggered_by)
        REFERENCES users(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_automation_runs_result
        CHECK (jsonb_typeof(result) = 'object')
);

CREATE TABLE IF NOT EXISTS email_logs (
    id BIGSERIAL PRIMARY KEY,
    report_id BIGINT,
    requested_by BIGINT,

    recipient CITEXT NOT NULL,
    subject VARCHAR(255) NOT NULL,
    status email_status NOT NULL DEFAULT 'PENDING',

    attachment_paths JSONB NOT NULL DEFAULT '[]'::JSONB,
    error_message TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMPTZ,

    CONSTRAINT fk_email_logs_report
        FOREIGN KEY (report_id)
        REFERENCES reports(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_email_logs_user
        FOREIGN KEY (requested_by)
        REFERENCES users(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_email_logs_recipient
        CHECK (
            recipient::TEXT ~*
            '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'
        ),

    CONSTRAINT chk_email_logs_attachments
        CHECK (jsonb_typeof(attachment_paths) = 'array')
);

CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL UNIQUE,
    task_type VARCHAR(80) NOT NULL,
    cron_expression VARCHAR(100) NOT NULL,
    parameters JSONB NOT NULL DEFAULT '{}'::JSONB,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,

    created_by BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_scheduled_tasks_user
        FOREIGN KEY (created_by)
        REFERENCES users(id)
        ON DELETE SET NULL,

    CONSTRAINT chk_scheduled_tasks_parameters
        CHECK (jsonb_typeof(parameters) = 'object')
);

CREATE TABLE IF NOT EXISTS external_api_logs (
    id BIGSERIAL PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    endpoint TEXT NOT NULL,
    request_parameters JSONB NOT NULL DEFAULT '{}'::JSONB,
    response_data JSONB,
    http_status INTEGER,
    duration_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_external_api_request
        CHECK (jsonb_typeof(request_parameters) = 'object'),

    CONSTRAINT chk_external_api_response
        CHECK (
            response_data IS NULL
            OR jsonb_typeof(response_data) IN ('object', 'array')
        ),

    CONSTRAINT chk_external_api_http_status
        CHECK (
            http_status IS NULL
            OR http_status BETWEEN 100 AND 599
        ),

    CONSTRAINT chk_external_api_duration
        CHECK (duration_ms IS NULL OR duration_ms >= 0)
);

CREATE TABLE IF NOT EXISTS system_settings (
    setting_key VARCHAR(120) PRIMARY KEY,
    setting_value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    updated_by BIGINT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_system_settings_user
        FOREIGN KEY (updated_by)
        REFERENCES users(id)
        ON DELETE SET NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_invoices_original_hash
    ON invoices(file_sha256)
    WHERE duplicate_of_invoice_id IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_invoices_provider_number
    ON invoices(provider_id, invoice_number)
    WHERE provider_id IS NOT NULL
      AND invoice_number IS NOT NULL
      AND status <> 'DUPLICATE';

CREATE INDEX IF NOT EXISTS idx_invoices_status
    ON invoices(status);

CREATE INDEX IF NOT EXISTS idx_invoices_invoice_date
    ON invoices(invoice_date);

CREATE INDEX IF NOT EXISTS idx_invoices_provider
    ON invoices(provider_id);

CREATE INDEX IF NOT EXISTS idx_invoices_category
    ON invoices(category_id);

CREATE INDEX IF NOT EXISTS idx_invoices_created_at
    ON invoices(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_processing_logs_invoice
    ON processing_logs(invoice_id);

CREATE INDEX IF NOT EXISTS idx_processing_logs_status
    ON processing_logs(status);

CREATE INDEX IF NOT EXISTS idx_processing_logs_started_at
    ON processing_logs(started_at DESC);

CREATE INDEX IF NOT EXISTS idx_reports_created_at
    ON reports(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_automation_runs_invoice
    ON automation_runs(invoice_id);

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_categories_updated_at ON invoice_categories;
CREATE TRIGGER trg_categories_updated_at
BEFORE UPDATE ON invoice_categories
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_providers_updated_at ON providers;
CREATE TRIGGER trg_providers_updated_at
BEFORE UPDATE ON providers
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_invoices_updated_at ON invoices;
CREATE TRIGGER trg_invoices_updated_at
BEFORE UPDATE ON invoices
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_scheduled_tasks_updated_at ON scheduled_tasks;
CREATE TRIGGER trg_scheduled_tasks_updated_at
BEFORE UPDATE ON scheduled_tasks
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

COMMIT;
