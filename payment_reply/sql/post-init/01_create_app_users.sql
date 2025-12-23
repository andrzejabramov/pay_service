-- Создаём роль и пользователя для приложения
DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_role') THEN
    CREATE ROLE app_role;
  END IF;
END $$;

DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '') THEN
    CREATE USER  WITH PASSWORD '' IN ROLE app_role;
  END IF;
END $$;

-- Назначаем права на схемы (уточни свои!)
GRANT USAGE ON SCHEMA accounts, auth TO app_role;

GRANT SELECT ON ALL TABLES IN SCHEMA accounts, auth TO app_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA accounts, auth TO app_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA accounts, auth
  GRANT SELECT ON TABLES TO app_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA accounts, auth
  GRANT EXECUTE ON FUNCTIONS TO app_role;