DO 'DECLARE r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = current_schema() AND tablename NOT LIKE $$%yoyo_%$$) LOOP
        EXECUTE $$DROP TABLE IF EXISTS $$ || quote_ident(r.tablename) || $$ CASCADE$$;
    END LOOP;
    FOR r in (SELECT n.nspname AS "schema", t.typname
                FROM pg_catalog.pg_type t
                JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
                JOIN pg_catalog.pg_enum e ON t.oid = e.enumtypid
                WHERE n.nspname = $$public$$
                GROUP BY 1, 2) LOOP
        EXECUTE $$DROP TYPE IF EXISTS $$ || quote_ident(r.typname) || $$ CASCADE$$;
    END LOOP;
END'