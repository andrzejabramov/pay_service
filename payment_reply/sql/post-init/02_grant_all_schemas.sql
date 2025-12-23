-- Grant privileges on all existing schemas and objects
DO $$
DECLARE
    schemaname TEXT;
BEGIN
    FOR schemaname IN
        SELECT nspname
        FROM pg_namespace
        WHERE nspname NOT LIKE 'pg_%'
          AND nspname <> 'information_schema'
    LOOP
        EXECUTE format('GRANT USAGE ON SCHEMA %I TO app_role', schemaname);
        EXECUTE format('GRANT SELECT ON ALL TABLES IN SCHEMA %I TO app_role', schemaname);
        EXECUTE format('GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA %I TO app_role', schemaname);
    END LOOP;
END $$;

-- Set default privileges for future objects
DO $$
DECLARE
    schemaname TEXT;
BEGIN
    FOR schemaname IN
        SELECT nspname
        FROM pg_namespace
        WHERE nspname NOT LIKE 'pg_%'
          AND nspname <> 'information_schema'
    LOOP
        EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA %I GRANT SELECT ON TABLES TO app_role', schemaname);
        EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA %I GRANT EXECUTE ON FUNCTIONS TO app_role', schemaname);
    END LOOP;
END $$;