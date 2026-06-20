BEGIN;

ALTER TABLE providers
DROP CONSTRAINT IF EXISTS chk_providers_nit;

ALTER TABLE providers
ADD CONSTRAINT chk_providers_nit
CHECK (
    upper(nit::TEXT) = 'CF'
    OR nit::TEXT ~ '^[0-9]{9}$'
    OR nit::TEXT ~ '^[0-9]{1,8}-[0-9Kk]$'
);

COMMIT;
