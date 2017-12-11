CREATE EXTENSION IF NOT EXISTS dblink;

DO
$do$
BEGIN
    IF NOT EXISTS (
        SELECT
        FROM pg_database
        WHERE datname = 'cloudplayer') THEN
            PERFORM dblink_exec('dbname=' || current_database(), 'CREATE DATABASE cloudplayer');
    END IF;
END
$do$;

DO
$do$
BEGIN
    IF NOT EXISTS (
        SELECT
        FROM pg_catalog.pg_user
        WHERE usename = 'api') THEN
            CREATE ROLE api LOGIN PASSWORD 'password';
            GRANT ALL PRIVILEGES ON DATABASE cloudplayer TO api;
    END IF;
END
$do$;
