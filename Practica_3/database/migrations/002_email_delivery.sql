BEGIN;

DROP TABLE IF EXISTS email_logs CASCADE;

CREATE TABLE email_logs (
    id BIGSERIAL PRIMARY KEY,

    report_id BIGINT NOT NULL
        REFERENCES reports(id)
        ON DELETE CASCADE,

    requested_by BIGINT
        REFERENCES users(id)
        ON DELETE SET NULL,

    recipient_email CITEXT NOT NULL,
    subject VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,

    attachment_name VARCHAR(255),

    status VARCHAR(20) NOT NULL
        DEFAULT 'PENDING',

    smtp_message_id VARCHAR(255),
    error_message TEXT,

    started_at TIMESTAMPTZ,
    sent_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMPTZ NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_email_logs_status
        CHECK (
            status IN (
                'PENDING',
                'RUNNING',
                'SUCCESS',
                'ERROR'
            )
        )
);

CREATE INDEX idx_email_logs_report
    ON email_logs(report_id);

CREATE INDEX idx_email_logs_status
    ON email_logs(status);

CREATE INDEX idx_email_logs_recipient
    ON email_logs(recipient_email);

CREATE TRIGGER trg_email_logs_updated_at
BEFORE UPDATE ON email_logs
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

COMMIT;
