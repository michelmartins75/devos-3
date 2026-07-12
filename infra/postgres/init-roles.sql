-- Bootstrap roles matching CT130 (OS-01). Runs once on first Postgres init.

CREATE DATABASE devos_audit;

\c devos_app

CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
BEGIN
      IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'devos_migrator') THEN
        CREATE ROLE devos_migrator LOGIN PASSWORD 'devos_migrator' BYPASSRLS;
      END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'devos_api') THEN
    CREATE ROLE devos_api LOGIN PASSWORD 'devos_api' NOSUPERUSER NOBYPASSRLS;
  END IF;
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'devos_readonly') THEN
    CREATE ROLE devos_readonly LOGIN PASSWORD 'devos_readonly' NOSUPERUSER NOBYPASSRLS;
  END IF;
END
$$;

ALTER ROLE devos_migrator BYPASSRLS;

GRANT CONNECT ON DATABASE devos_app TO devos_migrator, devos_api, devos_readonly;
GRANT CREATE ON SCHEMA public TO devos_migrator;
GRANT USAGE ON SCHEMA public TO devos_api, devos_readonly;

ALTER DEFAULT PRIVILEGES FOR ROLE devos_migrator IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO devos_api;
ALTER DEFAULT PRIVILEGES FOR ROLE devos_migrator IN SCHEMA public
  GRANT SELECT ON TABLES TO devos_readonly;

\c devos_audit

CREATE EXTENSION IF NOT EXISTS pgcrypto;

GRANT CONNECT ON DATABASE devos_audit TO devos_migrator, devos_api, devos_readonly;
GRANT CREATE ON SCHEMA public TO devos_migrator;
GRANT USAGE ON SCHEMA public TO devos_api, devos_readonly;

ALTER DEFAULT PRIVILEGES FOR ROLE devos_migrator IN SCHEMA public
  GRANT SELECT, INSERT ON TABLES TO devos_api;
ALTER DEFAULT PRIVILEGES FOR ROLE devos_migrator IN SCHEMA public
  GRANT SELECT ON TABLES TO devos_readonly;
