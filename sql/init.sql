-- Database pgQueue
CREATE DATABASE "pgQueue"
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

\connect pgQueue

-- Table message_queued
CREATE TABLE IF NOT EXISTS public.message_queued
(
    id bigserial NOT NULL,
    channel character varying(10) COLLATE pg_catalog."default" NOT NULL,
    message jsonb NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT message_queued_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.message_queued
    OWNER to postgres;


CREATE INDEX IF NOT EXISTS mq_channel_id
    ON public.message_queued USING btree
    (channel COLLATE pg_catalog."default" ASC NULLS LAST, id ASC NULLS LAST)
    TABLESPACE pg_default;

-- Table message_processed
CREATE TABLE IF NOT EXISTS public.message_processed
(
    id bigint NOT NULL,
    channel character varying(10) COLLATE pg_catalog."default" NOT NULL,
    message jsonb NOT NULL,
    created_at timestamp without time zone NOT NULL, 
    moved_at timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT message_processed_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.message_processed
    OWNER to postgres;


-- Function get_message
CREATE OR REPLACE FUNCTION public.get_message(
	channel_par character varying)
    RETURNS TABLE(var_id bigint, var_channel character varying, var_message jsonb, var_created_at character varying) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE var_created_at_ts timestamp;

BEGIN
	SELECT "id", "channel", "message", "created_at", "created_at"
	  INTO var_id, var_channel, var_message, var_created_at, var_created_at_ts
      FROM message_queued
     WHERE channel = channel_par
     ORDER BY id 
     LIMIT 1
       FOR UPDATE  
      SKIP LOCKED;

	IF FOUND THEN
		INSERT INTO message_processed (id, channel, message, created_at)
	       VALUES (var_id, var_channel, var_message, var_created_at_ts);	

		DELETE FROM message_queued WHERE id = var_id;

	ELSE
		var_id := 0;
		var_channel := channel_par;
		var_message := '{"a":"b"}'::jsonb;
		var_created_at := now()::timestamp::varchar;

	END IF;

	RETURN NEXT;

END
$BODY$;

ALTER FUNCTION public.get_message(character varying)
    OWNER TO postgres;