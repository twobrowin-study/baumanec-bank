--
-- PostgreSQL database dump
--

-- Dumped from database version 15.3
-- Dumped by pg_dump version 15.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: group_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.group_type AS ENUM (
    'government',
    'admin',
    'bank',
    'market'
);


ALTER TYPE public.group_type OWNER TO postgres;

--
-- Name: operation_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.operation_type AS ENUM (
    'income',
    'outcome'
);


ALTER TYPE public.operation_type OWNER TO postgres;

--
-- Name: squad_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.squad_type AS ENUM (
    '0',
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    '10',
    '11',
    '12',
    '13',
    '14',
    '15'
);


ALTER TYPE public.squad_type OWNER TO postgres;

--
-- Name: transaction_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.transaction_type AS ENUM (
    'salary',
    'purchase',
    'deposit',
    'withdraw',
    'loan',
    'repay',
    'service',
    'manual',
    'labor'
);


ALTER TYPE public.transaction_type OWNER TO postgres;

--
-- Name: bank_card_code_id(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.bank_card_code_id() RETURNS bigint
    LANGUAGE sql
    AS $$
	select card_code_id from bank;
$$;


ALTER FUNCTION public.bank_card_code_id() OWNER TO postgres;

--
-- Name: card_codes_insert_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.card_codes_insert_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF NEW.uuid IS null then
      NEW.uuid = card_uuid();
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.card_codes_insert_trigger() OWNER TO postgres;

--
-- Name: card_uuid(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.card_uuid() RETURNS text
    LANGUAGE sql
    AS $$
    SELECT substring(md5(random()::text || random()::text)::text FROM '.{12}') as card_uid;
$$;


ALTER FUNCTION public.card_uuid() OWNER TO postgres;

--
-- Name: FUNCTION card_uuid(); Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON FUNCTION public.card_uuid() IS 'Creats 12 numbered uid card number';


--
-- Name: check_if_government(bigint); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.check_if_government(inp_card_code_id bigint) RETURNS boolean
    LANGUAGE sql
    AS $$
select is_government from firms where card_code_id = inp_card_code_id
$$;


ALTER FUNCTION public.check_if_government(inp_card_code_id bigint) OWNER TO postgres;

--
-- Name: client_queue_insert_after_transaction(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.client_queue_insert_after_transaction() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
	BEGIN
		insert into queue_client_app
			(operation, amount, balance, firm_name, "type", client_chat_id, uuid, firm_uuid, "timestamp")
		select
			operation, amount, balance, firm_name, "type", client_chat_id, uuid, firm_uuid, "timestamp"
		from client_opreations_balance
		where client_chat_id is not null
		and id = new.id;
		return new;
	END;
$$;


ALTER FUNCTION public.client_queue_insert_after_transaction() OWNER TO postgres;

--
-- Name: deposit_transaction_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.deposit_transaction_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
	BEGIN
	    IF NEW."type" = 'deposit' then
	     	NEW.recipient_card_code_id = bank_card_code_id();
	    END IF;
	    RETURN NEW;
	END;
$$;


ALTER FUNCTION public.deposit_transaction_trigger() OWNER TO postgres;

--
-- Name: firm_queue_insert_after_transaction(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.firm_queue_insert_after_transaction() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
	BEGIN
		insert into queue_firm_app
			(operation, amount, balance, uuid, client_chat_id, firm_name, "type", counter_uuid, counter_firm_name, counter_client_name, counter_client_squad, "timestamp")
		select
			operation, amount, balance, uuid, client_chat_id, firm_name, "type", counter_uuid, counter_firm_name, counter_client_name, counter_client_squad, "timestamp"
		from firm_operations_balance_account
		where client_chat_id is not null
		and id = new.id;
		return new;
	END;
$$;


ALTER FUNCTION public.firm_queue_insert_after_transaction() OWNER TO postgres;

--
-- Name: get_balance(bigint); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.get_balance(card_code_id_inp bigint) RETURNS numeric
    LANGUAGE sql
    AS $$
	select b.balance from balances b where b.card_code_id = card_code_id_inp;
$$;


ALTER FUNCTION public.get_balance(card_code_id_inp bigint) OWNER TO postgres;

--
-- Name: labor_transaction_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.labor_transaction_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
	BEGIN
	    IF NEW."type" = 'labor' then
	     	NEW.source_card_code_id = bank_card_code_id();
	    END IF;
	    RETURN NEW;
	END;
$$;


ALTER FUNCTION public.labor_transaction_trigger() OWNER TO postgres;

--
-- Name: loan_transaction_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.loan_transaction_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
	BEGIN
	    IF NEW."type" = 'loan' then
	     	NEW.source_card_code_id = bank_card_code_id();
	    END IF;
	    RETURN NEW;
	END;
$$;


ALTER FUNCTION public.loan_transaction_trigger() OWNER TO postgres;

--
-- Name: manual_transaction_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.manual_transaction_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
	BEGIN
	    IF NEW."type" = 'manual' then
	     	NEW.source_card_code_id = bank_card_code_id();
	    END IF;
	    RETURN NEW;
	END;
$$;


ALTER FUNCTION public.manual_transaction_trigger() OWNER TO postgres;

--
-- Name: market_card_code_id(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.market_card_code_id() RETURNS bigint
    LANGUAGE sql
    AS $$
	select card_code_id from market;
$$;


ALTER FUNCTION public.market_card_code_id() OWNER TO postgres;

--
-- Name: purchase_transaction_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.purchase_transaction_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
	BEGIN
	    IF NEW."type" = 'purchase' then
	     	NEW.recipient_card_code_id = market_card_code_id();
	    END IF;
	    RETURN NEW;
	END;
$$;


ALTER FUNCTION public.purchase_transaction_trigger() OWNER TO postgres;

--
-- Name: repay_transaction_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.repay_transaction_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
	BEGIN
	    IF NEW."type" = 'repay' then
	     	NEW.recipient_card_code_id = bank_card_code_id();
	    END IF;
	    RETURN NEW;
	END;
$$;


ALTER FUNCTION public.repay_transaction_trigger() OWNER TO postgres;

--
-- Name: transaction_insert_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.transaction_insert_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
	BEGIN
	    IF NEW.amount <= 0 then
			RAISE EXCEPTION 'amount must be positive';
	    END IF;
	    IF new.source_card_code_id = new.recipient_card_code_id then
			RAISE EXCEPTION 'cannot create transaction to yourself';
	    END IF;
	    IF ((get_balance(new.source_card_code_id) < new.amount)
	    	and (not check_if_government(new.source_card_code_id))
	    ) then
			RAISE EXCEPTION 'Balance of source card is less than transaction amount';
	    END IF;
	    RETURN NEW;
	END;
$$;


ALTER FUNCTION public.transaction_insert_trigger() OWNER TO postgres;

--
-- Name: withdraw_transaction_trigger(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.withdraw_transaction_trigger() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
	BEGIN
	    IF NEW."type" = 'withdraw' then
	     	NEW.source_card_code_id = bank_card_code_id();
	    END IF;
	    RETURN NEW;
	END;
$$;


ALTER FUNCTION public.withdraw_transaction_trigger() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: card_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.card_codes (
    id bigint NOT NULL,
    uuid text NOT NULL
);


ALTER TABLE public.card_codes OWNER TO postgres;

--
-- Name: clients; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clients (
    id bigint NOT NULL,
    card_code_id bigint NOT NULL,
    name character varying NOT NULL,
    squad public.squad_type NOT NULL,
    chat_id character varying,
    username character varying,
    is_active boolean DEFAULT true NOT NULL,
    is_master boolean DEFAULT false NOT NULL
);


ALTER TABLE public.clients OWNER TO postgres;

--
-- Name: active_clients_card_codes; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.active_clients_card_codes AS
 SELECT c.id,
    c.card_code_id,
    cc.uuid,
    c.name,
    c.squad,
    c.chat_id,
    c.username,
    c.is_master
   FROM public.clients c,
    public.card_codes cc
  WHERE ((cc.id = c.card_code_id) AND c.is_active);


ALTER TABLE public.active_clients_card_codes OWNER TO postgres;

--
-- Name: firms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.firms (
    id bigint NOT NULL,
    card_code_id bigint NOT NULL,
    name character varying NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    is_bank boolean DEFAULT false NOT NULL,
    is_market boolean DEFAULT false NOT NULL,
    is_government boolean DEFAULT false NOT NULL
);


ALTER TABLE public.firms OWNER TO postgres;

--
-- Name: active_firms_card_codes; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.active_firms_card_codes AS
 SELECT f.id,
    f.card_code_id,
    cc.uuid,
    f.name,
    f.is_bank,
    f.is_market,
    f.is_government
   FROM public.firms f,
    public.card_codes cc
  WHERE ((cc.id = f.card_code_id) AND f.is_active);


ALTER TABLE public.active_firms_card_codes OWNER TO postgres;

--
-- Name: employees; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employees (
    id bigint NOT NULL,
    firm_id bigint NOT NULL,
    client_id bigint NOT NULL,
    is_account boolean DEFAULT false NOT NULL,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.employees OWNER TO postgres;

--
-- Name: active_employees; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.active_employees AS
 SELECT e.id,
    e.firm_id,
    afcc.card_code_id AS firm_card_code_id,
    afcc.uuid AS firm_uuid,
    afcc.name AS firm_name,
    afcc.is_bank,
    afcc.is_market,
    e.client_id,
    accc.card_code_id AS client_card_code_id,
    accc.uuid AS client_uuid,
    accc.name AS client_name,
    accc.squad AS client_squad,
    accc.chat_id AS client_chat_id,
    accc.username AS client_username,
    e.is_account,
    afcc.is_government
   FROM public.employees e,
    public.active_firms_card_codes afcc,
    public.active_clients_card_codes accc
  WHERE ((afcc.id = e.firm_id) AND (accc.id = e.client_id) AND e.is_active);


ALTER TABLE public.active_employees OWNER TO postgres;

--
-- Name: bank; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.bank AS
 SELECT afcc.id,
    afcc.card_code_id,
    afcc.uuid,
    afcc.name
   FROM public.active_firms_card_codes afcc
  WHERE afcc.is_bank
 LIMIT 1;


ALTER TABLE public.bank OWNER TO postgres;

--
-- Name: transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transactions (
    id bigint NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    source_card_code_id bigint NOT NULL,
    recipient_card_code_id bigint NOT NULL,
    amount numeric NOT NULL,
    type public.transaction_type NOT NULL,
    is_active boolean DEFAULT true NOT NULL
);


ALTER TABLE public.transactions OWNER TO postgres;

--
-- Name: deposits; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.deposits AS
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    accc.uuid AS source_uuid,
    NULL::bigint AS source_firm_id,
    NULL::text AS source_firm_name,
    accc.id AS source_client_id,
    accc.name AS source_client_name,
    accc.squad AS source_client_squad,
    accc.chat_id AS source_client_chat_id,
    accc.username AS source_client_username,
    t.recipient_card_code_id,
    b.uuid AS recipient_uuid,
    b.id AS recipient_firm_id,
    b.name AS recipient_firm_name,
    NULL::bigint AS recipient_client_id,
    NULL::text AS recipient_client_name,
    NULL::public.squad_type AS recipient_client_squad,
    NULL::text AS recipient_client_chat_id,
    NULL::text AS recipient_client_username,
    t.amount,
    t.amount AS income,
    0.0 AS govtax
   FROM public.transactions t,
    public.active_clients_card_codes accc,
    public.bank b
  WHERE ((t.type = 'deposit'::public.transaction_type) AND (accc.card_code_id = t.source_card_code_id) AND (b.card_code_id = t.recipient_card_code_id) AND t.is_active)
UNION
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    b.uuid AS source_uuid,
    b.id AS source_firm_id,
    b.name AS source_firm_name,
    NULL::bigint AS source_client_id,
    NULL::text AS source_client_name,
    NULL::public.squad_type AS source_client_squad,
    NULL::text AS source_client_chat_id,
    NULL::text AS source_client_username,
    t.recipient_card_code_id,
    afcc.uuid AS recipient_uuid,
    afcc.id AS recipient_firm_id,
    afcc.name AS recipient_firm_name,
    NULL::bigint AS recipient_client_id,
    NULL::text AS recipient_client_name,
    NULL::public.squad_type AS recipient_client_squad,
    NULL::text AS recipient_client_chat_id,
    NULL::text AS recipient_client_username,
    t.amount,
    t.amount AS income,
    0.0 AS govtax
   FROM public.transactions t,
    public.bank b,
    public.active_firms_card_codes afcc
  WHERE ((t.type = 'deposit'::public.transaction_type) AND (b.card_code_id = t.source_card_code_id) AND (afcc.card_code_id = t.recipient_card_code_id) AND t.is_active);


ALTER TABLE public.deposits OWNER TO postgres;

--
-- Name: labor; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.labor AS
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    b.uuid AS source_uuid,
    b.id AS source_firm_id,
    b.name AS source_firm_name,
    NULL::bigint AS source_client_id,
    NULL::text AS source_client_name,
    NULL::public.squad_type AS source_client_squad,
    NULL::text AS source_client_chat_id,
    NULL::text AS source_client_username,
    t.recipient_card_code_id,
    accc.uuid AS recipient_uuid,
    NULL::bigint AS recipient_firm_id,
    NULL::text AS recipient_firm_name,
    accc.id AS recipient_client_id,
    accc.name AS recipient_client_name,
    accc.squad AS recipient_client_squad,
    accc.chat_id AS recipient_client_chat_id,
    accc.username AS recipient_client_username,
    t.amount,
    (t.amount * 0.87) AS income,
    (t.amount * 0.13) AS govtax
   FROM public.transactions t,
    public.bank b,
    public.active_clients_card_codes accc
  WHERE ((t.type = 'labor'::public.transaction_type) AND (b.card_code_id = t.source_card_code_id) AND (accc.card_code_id = t.recipient_card_code_id) AND t.is_active);


ALTER TABLE public.labor OWNER TO postgres;

--
-- Name: loans; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.loans AS
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    b.uuid AS source_uuid,
    b.id AS source_firm_id,
    b.name AS source_firm_name,
    NULL::bigint AS source_client_id,
    NULL::text AS source_client_name,
    NULL::public.squad_type AS source_client_squad,
    NULL::text AS source_client_chat_id,
    NULL::text AS source_client_username,
    t.recipient_card_code_id,
    accc.uuid AS recipient_uuid,
    NULL::bigint AS recipient_firm_id,
    NULL::text AS recipient_firm_name,
    accc.id AS recipient_client_id,
    accc.name AS recipient_client_name,
    accc.squad AS recipient_client_squad,
    accc.chat_id AS recipient_client_chat_id,
    accc.username AS recipient_client_username,
    t.amount,
    t.amount AS income,
    0.0 AS govtax
   FROM public.transactions t,
    public.bank b,
    public.active_clients_card_codes accc
  WHERE ((t.type = 'loan'::public.transaction_type) AND (b.card_code_id = t.source_card_code_id) AND (accc.card_code_id = t.recipient_card_code_id) AND t.is_active)
UNION
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    b.uuid AS source_uuid,
    b.id AS source_firm_id,
    b.name AS source_firm_name,
    NULL::bigint AS source_client_id,
    NULL::text AS source_client_name,
    NULL::public.squad_type AS source_client_squad,
    NULL::text AS source_client_chat_id,
    NULL::text AS source_client_username,
    t.recipient_card_code_id,
    afcc.uuid AS recipient_uuid,
    afcc.id AS recipient_firm_id,
    afcc.name AS recipient_firm_name,
    NULL::bigint AS recipient_client_id,
    NULL::text AS recipient_client_name,
    NULL::public.squad_type AS recipient_client_squad,
    NULL::text AS recipient_client_chat_id,
    NULL::text AS recipient_client_username,
    t.amount,
    t.amount AS income,
    0.0 AS govtax
   FROM public.transactions t,
    public.bank b,
    public.active_firms_card_codes afcc
  WHERE ((t.type = 'loan'::public.transaction_type) AND (b.card_code_id = t.source_card_code_id) AND (afcc.card_code_id = t.recipient_card_code_id) AND t.is_active);


ALTER TABLE public.loans OWNER TO postgres;

--
-- Name: manual_clients; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.manual_clients AS
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    b.uuid AS source_uuid,
    b.id AS source_firm_id,
    b.name AS source_firm_name,
    NULL::bigint AS source_client_id,
    NULL::text AS source_client_name,
    NULL::public.squad_type AS source_client_squad,
    NULL::text AS source_client_chat_id,
    NULL::text AS source_client_username,
    t.recipient_card_code_id,
    accc.uuid AS recipient_uuid,
    NULL::bigint AS recipient_firm_id,
    NULL::text AS recipient_firm_name,
    accc.id AS recipient_client_id,
    accc.name AS recipient_client_name,
    accc.squad AS recipient_client_squad,
    accc.chat_id AS recipient_client_chat_id,
    accc.username AS recipient_client_username,
    t.amount,
    t.amount AS income,
    0.0 AS govtax
   FROM public.transactions t,
    public.bank b,
    public.active_clients_card_codes accc
  WHERE ((t.type = 'manual'::public.transaction_type) AND (b.card_code_id = t.source_card_code_id) AND (accc.card_code_id = t.recipient_card_code_id) AND t.is_active);


ALTER TABLE public.manual_clients OWNER TO postgres;

--
-- Name: manual_firms; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.manual_firms AS
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    b.uuid AS source_uuid,
    b.id AS source_firm_id,
    b.name AS source_firm_name,
    NULL::bigint AS source_client_id,
    NULL::text AS source_client_name,
    NULL::public.squad_type AS source_client_squad,
    NULL::text AS source_client_chat_id,
    NULL::text AS source_client_username,
    t.recipient_card_code_id,
    afcc.uuid AS recipient_uuid,
    afcc.id AS recipient_firm_id,
    afcc.name AS recipient_firm_name,
    NULL::bigint AS recipient_client_id,
    NULL::text AS recipient_client_name,
    NULL::public.squad_type AS recipient_client_squad,
    NULL::text AS recipient_client_chat_id,
    NULL::text AS recipient_client_username,
    t.amount,
    t.amount AS income,
    0.0 AS govtax
   FROM public.transactions t,
    public.bank b,
    public.active_firms_card_codes afcc
  WHERE ((t.type = 'manual'::public.transaction_type) AND (b.card_code_id = t.source_card_code_id) AND (afcc.card_code_id = t.recipient_card_code_id) AND t.is_active);


ALTER TABLE public.manual_firms OWNER TO postgres;

--
-- Name: market; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.market AS
 SELECT afcc.id,
    afcc.card_code_id,
    afcc.uuid,
    afcc.name
   FROM public.active_firms_card_codes afcc
  WHERE afcc.is_market
 LIMIT 1;


ALTER TABLE public.market OWNER TO postgres;

--
-- Name: purchases; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.purchases AS
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    accc.uuid AS source_uuid,
    NULL::bigint AS source_firm_id,
    NULL::text AS source_firm_name,
    accc.id AS source_client_id,
    accc.name AS source_client_name,
    accc.squad AS source_client_squad,
    accc.chat_id AS source_client_chat_id,
    accc.username AS source_client_username,
    t.recipient_card_code_id,
    m.uuid AS recipient_uuid,
    m.id AS recipient_firm_id,
    m.name AS recipient_firm_name,
    NULL::bigint AS recipient_client_id,
    NULL::text AS recipient_client_name,
    NULL::public.squad_type AS recipient_client_squad,
    NULL::text AS recipient_client_chat_id,
    NULL::text AS recipient_client_username,
    t.amount,
    (t.amount * 0.80) AS income,
    (t.amount * 0.20) AS govtax
   FROM public.transactions t,
    public.active_clients_card_codes accc,
    public.market m
  WHERE ((t.type = 'purchase'::public.transaction_type) AND (accc.card_code_id = t.source_card_code_id) AND (m.card_code_id = t.recipient_card_code_id) AND t.is_active)
UNION
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    afcc.uuid AS source_uuid,
    afcc.id AS source_firm_id,
    afcc.name AS source_firm_name,
    NULL::bigint AS source_client_id,
    NULL::text AS source_client_name,
    NULL::public.squad_type AS source_client_squad,
    NULL::text AS source_client_chat_id,
    NULL::text AS source_client_username,
    t.recipient_card_code_id,
    m.uuid AS recipient_uuid,
    m.id AS recipient_firm_id,
    m.name AS recipient_firm_name,
    NULL::bigint AS recipient_client_id,
    NULL::text AS recipient_client_name,
    NULL::public.squad_type AS recipient_client_squad,
    NULL::text AS recipient_client_chat_id,
    NULL::text AS recipient_client_username,
    t.amount,
    (t.amount * 0.80) AS income,
    (t.amount * 0.20) AS govtax
   FROM public.transactions t,
    public.active_firms_card_codes afcc,
    public.market m
  WHERE ((t.type = 'purchase'::public.transaction_type) AND (afcc.card_code_id = t.source_card_code_id) AND (m.card_code_id = t.recipient_card_code_id) AND t.is_active);


ALTER TABLE public.purchases OWNER TO postgres;

--
-- Name: repays; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.repays AS
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    accc.uuid AS source_uuid,
    NULL::bigint AS source_firm_id,
    NULL::text AS source_firm_name,
    accc.id AS source_client_id,
    accc.name AS source_client_name,
    accc.squad AS source_client_squad,
    accc.chat_id AS source_client_chat_id,
    accc.username AS source_client_username,
    t.recipient_card_code_id,
    b.uuid AS recipient_uuid,
    b.id AS recipient_firm_id,
    b.name AS recipient_firm_name,
    NULL::bigint AS recipient_client_id,
    NULL::text AS recipient_client_name,
    NULL::public.squad_type AS recipient_client_squad,
    NULL::text AS recipient_client_chat_id,
    NULL::text AS recipient_client_username,
    t.amount,
    t.amount AS income,
    0.0 AS govtax
   FROM public.transactions t,
    public.active_clients_card_codes accc,
    public.bank b
  WHERE ((t.type = 'repay'::public.transaction_type) AND (accc.card_code_id = t.source_card_code_id) AND (b.card_code_id = t.recipient_card_code_id) AND t.is_active)
UNION
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    b.uuid AS source_uuid,
    b.id AS source_firm_id,
    b.name AS source_firm_name,
    NULL::bigint AS source_client_id,
    NULL::text AS source_client_name,
    NULL::public.squad_type AS source_client_squad,
    NULL::text AS source_client_chat_id,
    NULL::text AS source_client_username,
    t.recipient_card_code_id,
    afcc.uuid AS recipient_uuid,
    afcc.id AS recipient_firm_id,
    afcc.name AS recipient_firm_name,
    NULL::bigint AS recipient_client_id,
    NULL::text AS recipient_client_name,
    NULL::public.squad_type AS recipient_client_squad,
    NULL::text AS recipient_client_chat_id,
    NULL::text AS recipient_client_username,
    t.amount,
    t.amount AS income,
    0.0 AS govtax
   FROM public.transactions t,
    public.bank b,
    public.active_firms_card_codes afcc
  WHERE ((t.type = 'repay'::public.transaction_type) AND (b.card_code_id = t.source_card_code_id) AND (afcc.card_code_id = t.recipient_card_code_id) AND t.is_active);


ALTER TABLE public.repays OWNER TO postgres;

--
-- Name: salaries; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.salaries AS
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    afcc.uuid AS source_uuid,
    afcc.id AS source_firm_id,
    afcc.name AS source_firm_name,
    NULL::bigint AS source_client_id,
    NULL::text AS source_client_name,
    NULL::public.squad_type AS source_client_squad,
    NULL::text AS source_client_chat_id,
    NULL::text AS source_client_username,
    t.recipient_card_code_id,
    accc.uuid AS recipient_uuid,
    NULL::bigint AS recipient_firm_id,
    NULL::text AS recipient_firm_name,
    accc.id AS recipient_client_id,
    accc.name AS recipient_client_name,
    accc.squad AS recipient_client_squad,
    accc.chat_id AS recipient_client_chat_id,
    accc.username AS recipient_client_username,
    t.amount,
    (t.amount * 0.87) AS income,
    (t.amount * 0.13) AS govtax
   FROM public.transactions t,
    public.active_clients_card_codes accc,
    public.active_firms_card_codes afcc
  WHERE ((t.type = 'salary'::public.transaction_type) AND (afcc.card_code_id = t.source_card_code_id) AND (accc.card_code_id = t.recipient_card_code_id) AND t.is_active);


ALTER TABLE public.salaries OWNER TO postgres;

--
-- Name: services; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.services AS
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    afcc_s.uuid AS source_uuid,
    afcc_s.id AS source_firm_id,
    afcc_s.name AS source_firm_name,
    NULL::bigint AS source_client_id,
    NULL::text AS source_client_name,
    NULL::public.squad_type AS source_client_squad,
    NULL::text AS source_client_chat_id,
    NULL::text AS source_client_username,
    t.recipient_card_code_id,
    afcc_r.uuid AS recipient_uuid,
    afcc_r.id AS recipient_firm_id,
    afcc_r.name AS recipient_firm_name,
    NULL::bigint AS recipient_client_id,
    NULL::text AS recipient_client_name,
    NULL::public.squad_type AS recipient_client_squad,
    NULL::text AS recipient_client_chat_id,
    NULL::text AS recipient_client_username,
    t.amount,
    t.amount AS income,
    0.0 AS govtax
   FROM public.transactions t,
    public.active_firms_card_codes afcc_s,
    public.active_firms_card_codes afcc_r
  WHERE ((t.type = 'service'::public.transaction_type) AND (afcc_s.card_code_id = t.source_card_code_id) AND (afcc_r.card_code_id = t.recipient_card_code_id) AND (t.source_card_code_id <> t.recipient_card_code_id) AND t.is_active)
UNION
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    accc.uuid AS source_uuid,
    NULL::bigint AS source_firm_id,
    NULL::text AS source_firm_name,
    accc.id AS source_client_id,
    accc.name AS source_client_name,
    accc.squad AS source_client_squad,
    accc.chat_id AS source_client_chat_id,
    accc.username AS source_client_username,
    t.recipient_card_code_id,
    afcc_r.uuid AS recipient_uuid,
    afcc_r.id AS recipient_firm_id,
    afcc_r.name AS recipient_firm_name,
    NULL::bigint AS recipient_client_id,
    NULL::text AS recipient_client_name,
    NULL::public.squad_type AS recipient_client_squad,
    NULL::text AS recipient_client_chat_id,
    NULL::text AS recipient_client_username,
    t.amount,
    t.amount AS income,
    0.0 AS govtax
   FROM public.transactions t,
    public.active_clients_card_codes accc,
    public.active_firms_card_codes afcc_r
  WHERE ((t.type = 'service'::public.transaction_type) AND (accc.card_code_id = t.source_card_code_id) AND (afcc_r.card_code_id = t.recipient_card_code_id) AND (t.source_card_code_id <> t.recipient_card_code_id) AND t.is_active);


ALTER TABLE public.services OWNER TO postgres;

--
-- Name: withdraws; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.withdraws AS
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    b.uuid AS source_uuid,
    b.id AS source_firm_id,
    b.name AS source_firm_name,
    NULL::bigint AS source_client_id,
    NULL::text AS source_client_name,
    NULL::public.squad_type AS source_client_squad,
    NULL::text AS source_client_chat_id,
    NULL::text AS source_client_username,
    t.recipient_card_code_id,
    accc.uuid AS recipient_uuid,
    NULL::bigint AS recipient_firm_id,
    NULL::text AS recipient_firm_name,
    accc.id AS recipient_client_id,
    accc.name AS recipient_client_name,
    accc.squad AS recipient_client_squad,
    accc.chat_id AS recipient_client_chat_id,
    accc.username AS recipient_client_username,
    t.amount,
    t.amount AS income,
    0.0 AS govtax
   FROM public.transactions t,
    public.bank b,
    public.active_clients_card_codes accc
  WHERE ((t.type = 'withdraw'::public.transaction_type) AND (b.card_code_id = t.source_card_code_id) AND (accc.card_code_id = t.recipient_card_code_id) AND t.is_active)
UNION
 SELECT t.id,
    t."timestamp",
    t.type,
    t.source_card_code_id,
    b.uuid AS source_uuid,
    b.id AS source_firm_id,
    b.name AS source_firm_name,
    NULL::bigint AS source_client_id,
    NULL::text AS source_client_name,
    NULL::public.squad_type AS source_client_squad,
    NULL::text AS source_client_chat_id,
    NULL::text AS source_client_username,
    t.recipient_card_code_id,
    afcc.uuid AS recipient_uuid,
    afcc.id AS recipient_firm_id,
    afcc.name AS recipient_firm_name,
    NULL::bigint AS recipient_client_id,
    NULL::text AS recipient_client_name,
    NULL::public.squad_type AS recipient_client_squad,
    NULL::text AS recipient_client_chat_id,
    NULL::text AS recipient_client_username,
    t.amount,
    t.amount AS income,
    0.0 AS govtax
   FROM public.transactions t,
    public.bank b,
    public.active_firms_card_codes afcc
  WHERE ((t.type = 'withdraw'::public.transaction_type) AND (b.card_code_id = t.source_card_code_id) AND (afcc.card_code_id = t.recipient_card_code_id) AND t.is_active);


ALTER TABLE public.withdraws OWNER TO postgres;

--
-- Name: transactions_clients_firms_taxes; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.transactions_clients_firms_taxes AS
 SELECT tr.id,
    tr."timestamp",
    tr.type,
    tr.source_card_code_id,
    tr.source_uuid,
    tr.source_firm_id,
    tr.source_firm_name,
    tr.source_client_id,
    tr.source_client_name,
    tr.source_client_squad,
    tr.source_client_chat_id,
    tr.source_client_username,
    tr.recipient_card_code_id,
    tr.recipient_uuid,
    tr.recipient_firm_id,
    tr.recipient_firm_name,
    tr.recipient_client_id,
    tr.recipient_client_name,
    tr.recipient_client_squad,
    tr.recipient_client_chat_id,
    tr.recipient_client_username,
    tr.amount,
    tr.income,
    tr.govtax
   FROM ( SELECT salaries.id,
            salaries."timestamp",
            salaries.type,
            salaries.source_card_code_id,
            salaries.source_uuid,
            salaries.source_firm_id,
            salaries.source_firm_name,
            salaries.source_client_id,
            salaries.source_client_name,
            salaries.source_client_squad,
            salaries.source_client_chat_id,
            salaries.source_client_username,
            salaries.recipient_card_code_id,
            salaries.recipient_uuid,
            salaries.recipient_firm_id,
            salaries.recipient_firm_name,
            salaries.recipient_client_id,
            salaries.recipient_client_name,
            salaries.recipient_client_squad,
            salaries.recipient_client_chat_id,
            salaries.recipient_client_username,
            salaries.amount,
            salaries.income,
            salaries.govtax
           FROM public.salaries
        UNION
         SELECT purchases.id,
            purchases."timestamp",
            purchases.type,
            purchases.source_card_code_id,
            purchases.source_uuid,
            purchases.source_firm_id,
            purchases.source_firm_name,
            purchases.source_client_id,
            purchases.source_client_name,
            purchases.source_client_squad,
            purchases.source_client_chat_id,
            purchases.source_client_username,
            purchases.recipient_card_code_id,
            purchases.recipient_uuid,
            purchases.recipient_firm_id,
            purchases.recipient_firm_name,
            purchases.recipient_client_id,
            purchases.recipient_client_name,
            purchases.recipient_client_squad,
            purchases.recipient_client_chat_id,
            purchases.recipient_client_username,
            purchases.amount,
            purchases.income,
            purchases.govtax
           FROM public.purchases
        UNION
         SELECT deposits.id,
            deposits."timestamp",
            deposits.type,
            deposits.source_card_code_id,
            deposits.source_uuid,
            deposits.source_firm_id,
            deposits.source_firm_name,
            deposits.source_client_id,
            deposits.source_client_name,
            deposits.source_client_squad,
            deposits.source_client_chat_id,
            deposits.source_client_username,
            deposits.recipient_card_code_id,
            deposits.recipient_uuid,
            deposits.recipient_firm_id,
            deposits.recipient_firm_name,
            deposits.recipient_client_id,
            deposits.recipient_client_name,
            deposits.recipient_client_squad,
            deposits.recipient_client_chat_id,
            deposits.recipient_client_username,
            deposits.amount,
            deposits.income,
            deposits.govtax
           FROM public.deposits
        UNION
         SELECT withdraws.id,
            withdraws."timestamp",
            withdraws.type,
            withdraws.source_card_code_id,
            withdraws.source_uuid,
            withdraws.source_firm_id,
            withdraws.source_firm_name,
            withdraws.source_client_id,
            withdraws.source_client_name,
            withdraws.source_client_squad,
            withdraws.source_client_chat_id,
            withdraws.source_client_username,
            withdraws.recipient_card_code_id,
            withdraws.recipient_uuid,
            withdraws.recipient_firm_id,
            withdraws.recipient_firm_name,
            withdraws.recipient_client_id,
            withdraws.recipient_client_name,
            withdraws.recipient_client_squad,
            withdraws.recipient_client_chat_id,
            withdraws.recipient_client_username,
            withdraws.amount,
            withdraws.income,
            withdraws.govtax
           FROM public.withdraws
        UNION
         SELECT loans.id,
            loans."timestamp",
            loans.type,
            loans.source_card_code_id,
            loans.source_uuid,
            loans.source_firm_id,
            loans.source_firm_name,
            loans.source_client_id,
            loans.source_client_name,
            loans.source_client_squad,
            loans.source_client_chat_id,
            loans.source_client_username,
            loans.recipient_card_code_id,
            loans.recipient_uuid,
            loans.recipient_firm_id,
            loans.recipient_firm_name,
            loans.recipient_client_id,
            loans.recipient_client_name,
            loans.recipient_client_squad,
            loans.recipient_client_chat_id,
            loans.recipient_client_username,
            loans.amount,
            loans.income,
            loans.govtax
           FROM public.loans
        UNION
         SELECT repays.id,
            repays."timestamp",
            repays.type,
            repays.source_card_code_id,
            repays.source_uuid,
            repays.source_firm_id,
            repays.source_firm_name,
            repays.source_client_id,
            repays.source_client_name,
            repays.source_client_squad,
            repays.source_client_chat_id,
            repays.source_client_username,
            repays.recipient_card_code_id,
            repays.recipient_uuid,
            repays.recipient_firm_id,
            repays.recipient_firm_name,
            repays.recipient_client_id,
            repays.recipient_client_name,
            repays.recipient_client_squad,
            repays.recipient_client_chat_id,
            repays.recipient_client_username,
            repays.amount,
            repays.income,
            repays.govtax
           FROM public.repays
        UNION
         SELECT services.id,
            services."timestamp",
            services.type,
            services.source_card_code_id,
            services.source_uuid,
            services.source_firm_id,
            services.source_firm_name,
            services.source_client_id,
            services.source_client_name,
            services.source_client_squad,
            services.source_client_chat_id,
            services.source_client_username,
            services.recipient_card_code_id,
            services.recipient_uuid,
            services.recipient_firm_id,
            services.recipient_firm_name,
            services.recipient_client_id,
            services.recipient_client_name,
            services.recipient_client_squad,
            services.recipient_client_chat_id,
            services.recipient_client_username,
            services.amount,
            services.income,
            services.govtax
           FROM public.services
        UNION
         SELECT manual_clients.id,
            manual_clients."timestamp",
            manual_clients.type,
            manual_clients.source_card_code_id,
            manual_clients.source_uuid,
            manual_clients.source_firm_id,
            manual_clients.source_firm_name,
            manual_clients.source_client_id,
            manual_clients.source_client_name,
            manual_clients.source_client_squad,
            manual_clients.source_client_chat_id,
            manual_clients.source_client_username,
            manual_clients.recipient_card_code_id,
            manual_clients.recipient_uuid,
            manual_clients.recipient_firm_id,
            manual_clients.recipient_firm_name,
            manual_clients.recipient_client_id,
            manual_clients.recipient_client_name,
            manual_clients.recipient_client_squad,
            manual_clients.recipient_client_chat_id,
            manual_clients.recipient_client_username,
            manual_clients.amount,
            manual_clients.income,
            manual_clients.govtax
           FROM public.manual_clients
        UNION
         SELECT manual_firms.id,
            manual_firms."timestamp",
            manual_firms.type,
            manual_firms.source_card_code_id,
            manual_firms.source_uuid,
            manual_firms.source_firm_id,
            manual_firms.source_firm_name,
            manual_firms.source_client_id,
            manual_firms.source_client_name,
            manual_firms.source_client_squad,
            manual_firms.source_client_chat_id,
            manual_firms.source_client_username,
            manual_firms.recipient_card_code_id,
            manual_firms.recipient_uuid,
            manual_firms.recipient_firm_id,
            manual_firms.recipient_firm_name,
            manual_firms.recipient_client_id,
            manual_firms.recipient_client_name,
            manual_firms.recipient_client_squad,
            manual_firms.recipient_client_chat_id,
            manual_firms.recipient_client_username,
            manual_firms.amount,
            manual_firms.income,
            manual_firms.govtax
           FROM public.manual_firms
        UNION
         SELECT labor.id,
            labor."timestamp",
            labor.type,
            labor.source_card_code_id,
            labor.source_uuid,
            labor.source_firm_id,
            labor.source_firm_name,
            labor.source_client_id,
            labor.source_client_name,
            labor.source_client_squad,
            labor.source_client_chat_id,
            labor.source_client_username,
            labor.recipient_card_code_id,
            labor.recipient_uuid,
            labor.recipient_firm_id,
            labor.recipient_firm_name,
            labor.recipient_client_id,
            labor.recipient_client_name,
            labor.recipient_client_squad,
            labor.recipient_client_chat_id,
            labor.recipient_client_username,
            labor.amount,
            labor.income,
            labor.govtax
           FROM public.labor) tr
  ORDER BY tr."timestamp";


ALTER TABLE public.transactions_clients_firms_taxes OWNER TO postgres;

--
-- Name: minus_balances; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.minus_balances AS
 SELECT transactions_clients_firms_taxes.source_card_code_id AS card_code_id,
    sum(transactions_clients_firms_taxes.amount) AS outcome
   FROM public.transactions_clients_firms_taxes
  GROUP BY transactions_clients_firms_taxes.source_card_code_id;


ALTER TABLE public.minus_balances OWNER TO postgres;

--
-- Name: plus_balances; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.plus_balances AS
 SELECT transactions_clients_firms_taxes.recipient_card_code_id AS card_code_id,
    sum(transactions_clients_firms_taxes.income) AS income
   FROM public.transactions_clients_firms_taxes
  GROUP BY transactions_clients_firms_taxes.recipient_card_code_id;


ALTER TABLE public.plus_balances OWNER TO postgres;

--
-- Name: balances; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.balances AS
 SELECT plus.card_code_id,
    (plus.income - minus.outcome) AS balance
   FROM ( SELECT plus_balances.card_code_id,
            plus_balances.income
           FROM public.plus_balances
        UNION
         SELECT card_codes.id,
            0.0
           FROM public.card_codes
          WHERE (NOT (card_codes.id IN ( SELECT plus_balances.card_code_id
                   FROM public.plus_balances)))) plus,
    ( SELECT minus_balances.card_code_id,
            minus_balances.outcome
           FROM public.minus_balances
        UNION
         SELECT card_codes.id,
            0.0
           FROM public.card_codes
          WHERE (NOT (card_codes.id IN ( SELECT minus_balances.card_code_id
                   FROM public.minus_balances)))) minus
  WHERE (plus.card_code_id = minus.card_code_id)
  ORDER BY plus.card_code_id;


ALTER TABLE public.balances OWNER TO postgres;

--
-- Name: active_accounts_card_codes_balances; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.active_accounts_card_codes_balances AS
 SELECT ae.id,
    ae.firm_id,
    ae.firm_card_code_id,
    ae.firm_uuid,
    ae.firm_name,
    ae.is_bank,
    ae.is_market,
    ae.client_id,
    ae.client_card_code_id,
    ae.client_uuid,
    ae.client_name,
    ae.client_squad,
    ae.client_chat_id,
    ae.client_username,
    b.balance,
    ae.is_government
   FROM public.active_employees ae,
    public.balances b
  WHERE (ae.is_account AND (ae.firm_card_code_id = b.card_code_id));


ALTER TABLE public.active_accounts_card_codes_balances OWNER TO postgres;

--
-- Name: active_clients_card_codes_balances; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.active_clients_card_codes_balances AS
 SELECT accc.id,
    accc.card_code_id,
    accc.uuid,
    accc.name,
    accc.squad,
    accc.chat_id,
    accc.username,
    b.balance,
    accc.is_master
   FROM public.balances b,
    public.active_clients_card_codes accc
  WHERE (b.card_code_id = accc.card_code_id);


ALTER TABLE public.active_clients_card_codes_balances OWNER TO postgres;

--
-- Name: active_firms_card_codes_balances; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.active_firms_card_codes_balances AS
 SELECT afcc.id,
    afcc.card_code_id,
    afcc.uuid,
    afcc.name,
    b.balance,
    afcc.is_government
   FROM public.balances b,
    public.active_firms_card_codes afcc
  WHERE (b.card_code_id = afcc.card_code_id);


ALTER TABLE public.active_firms_card_codes_balances OWNER TO postgres;

--
-- Name: active_clients_firms_card_codes_balances; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.active_clients_firms_card_codes_balances AS
 SELECT acccb.card_code_id,
    acccb.uuid,
    NULL::bigint AS firm_id,
    NULL::text AS firm_name,
    acccb.id AS client_id,
    acccb.name AS client_name,
    acccb.squad AS client_squad,
    acccb.chat_id AS client_chat_id,
    acccb.username AS client_username,
    acccb.balance,
    false AS is_government
   FROM public.active_clients_card_codes_balances acccb
UNION
 SELECT afccb.card_code_id,
    afccb.uuid,
    afccb.id AS firm_id,
    afccb.name AS firm_name,
    NULL::bigint AS client_id,
    NULL::text AS client_name,
    NULL::public.squad_type AS client_squad,
    NULL::text AS client_chat_id,
    NULL::text AS client_username,
    afccb.balance,
    afccb.is_government
   FROM public.active_firms_card_codes_balances afccb;


ALTER TABLE public.active_clients_firms_card_codes_balances OWNER TO postgres;

--
-- Name: active_employees_accounts; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.active_employees_accounts AS
 SELECT ae.id AS employee_id,
    ae.firm_id,
    ae.firm_card_code_id,
    ae.firm_uuid,
    ae.firm_name,
    ae.client_id AS employee_client_id,
    ae.client_card_code_id AS employeeclient_card_code_id,
    ae.client_uuid AS employee_client_uuid,
    ae.client_name AS employee_client_name,
    ae.client_squad AS employee_client_squad,
    aaccb.client_id AS account_client_id,
    aaccb.client_card_code_id AS account_client_card_code_id,
    aaccb.client_uuid AS account_client_uuid,
    aaccb.client_name AS account_client_name,
    aaccb.client_squad AS account_client_squad,
    aaccb.client_chat_id AS account_client_chat_id,
    aaccb.client_username AS account_client_username
   FROM public.active_employees ae,
    public.active_accounts_card_codes_balances aaccb
  WHERE (ae.firm_id = aaccb.firm_id);


ALTER TABLE public.active_employees_accounts OWNER TO postgres;

--
-- Name: groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.groups (
    id bigint NOT NULL,
    chat_id character varying NOT NULL,
    type public.group_type NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.groups OWNER TO postgres;

--
-- Name: admin_groups; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.admin_groups AS
 SELECT groups.chat_id
   FROM public.groups
  WHERE (groups.type = 'admin'::public.group_type);


ALTER TABLE public.admin_groups OWNER TO postgres;

--
-- Name: avaliable_card_codes; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.avaliable_card_codes AS
 SELECT card_codes.id,
    card_codes.uuid
   FROM public.card_codes
  WHERE ((NOT (card_codes.id IN ( SELECT clients.card_code_id
           FROM public.clients))) AND (NOT (card_codes.id IN ( SELECT firms.card_code_id
           FROM public.firms))));


ALTER TABLE public.avaliable_card_codes OWNER TO postgres;

--
-- Name: bank_groups; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.bank_groups AS
 SELECT groups.chat_id
   FROM public.groups
  WHERE (groups.type = 'bank'::public.group_type);


ALTER TABLE public.bank_groups OWNER TO postgres;

--
-- Name: card_codes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.card_codes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.card_codes_id_seq OWNER TO postgres;

--
-- Name: card_codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.card_codes_id_seq OWNED BY public.card_codes.id;


--
-- Name: client_operations; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.client_operations AS
 SELECT dt.id,
    dt."timestamp",
    dt.card_code_id,
    dt.uuid,
    dt.client_id,
    dt.client_name,
    dt.client_squad,
    dt.client_chat_id,
    dt.client_username,
    dt.firm_card_code_id,
    dt.firm_uuid,
    dt.firm_id,
    dt.firm_name,
    dt.amount,
    dt.operation,
    dt.type,
    dt.govtax
   FROM ( SELECT transactions_clients_firms_taxes.id,
            transactions_clients_firms_taxes."timestamp",
            transactions_clients_firms_taxes.recipient_card_code_id AS card_code_id,
            transactions_clients_firms_taxes.recipient_uuid AS uuid,
            transactions_clients_firms_taxes.recipient_client_id AS client_id,
            transactions_clients_firms_taxes.recipient_client_name AS client_name,
            transactions_clients_firms_taxes.recipient_client_squad AS client_squad,
            transactions_clients_firms_taxes.recipient_client_chat_id AS client_chat_id,
            transactions_clients_firms_taxes.recipient_client_username AS client_username,
            transactions_clients_firms_taxes.source_card_code_id AS firm_card_code_id,
            transactions_clients_firms_taxes.source_uuid AS firm_uuid,
            transactions_clients_firms_taxes.source_firm_id AS firm_id,
            transactions_clients_firms_taxes.source_firm_name AS firm_name,
            transactions_clients_firms_taxes.income AS amount,
            transactions_clients_firms_taxes.govtax,
            'income'::public.operation_type AS operation,
            transactions_clients_firms_taxes.type
           FROM public.transactions_clients_firms_taxes
          WHERE (transactions_clients_firms_taxes.recipient_client_id IS NOT NULL)
        UNION
         SELECT transactions_clients_firms_taxes.id,
            transactions_clients_firms_taxes."timestamp",
            transactions_clients_firms_taxes.source_card_code_id AS card_code_id,
            transactions_clients_firms_taxes.source_uuid AS uuid,
            transactions_clients_firms_taxes.source_client_id AS client_id,
            transactions_clients_firms_taxes.source_client_name AS client_name,
            transactions_clients_firms_taxes.source_client_squad AS client_squad,
            transactions_clients_firms_taxes.source_client_chat_id AS client_chat_id,
            transactions_clients_firms_taxes.source_client_username AS client_username,
            transactions_clients_firms_taxes.recipient_card_code_id AS firm_card_code_id,
            transactions_clients_firms_taxes.recipient_uuid AS firm_uuid,
            transactions_clients_firms_taxes.recipient_firm_id AS firm_id,
            transactions_clients_firms_taxes.recipient_firm_name AS firm_name,
            transactions_clients_firms_taxes.amount,
            transactions_clients_firms_taxes.govtax,
            'outcome'::public.operation_type AS operation,
            transactions_clients_firms_taxes.type
           FROM public.transactions_clients_firms_taxes
          WHERE (transactions_clients_firms_taxes.source_client_id IS NOT NULL)) dt
  ORDER BY dt."timestamp";


ALTER TABLE public.client_operations OWNER TO postgres;

--
-- Name: client_opreations_balance; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.client_opreations_balance AS
 SELECT co.id,
    co."timestamp",
    co.card_code_id,
    co.uuid,
    co.client_id,
    co.client_name,
    co.client_squad,
    co.client_chat_id,
    co.client_username,
    co.firm_card_code_id,
    co.firm_uuid,
    co.firm_id,
    co.firm_name,
    co.amount,
    co.operation,
    co.type,
    b.balance,
    co.govtax
   FROM public.client_operations co,
    public.balances b
  WHERE (co.card_code_id = b.card_code_id)
  ORDER BY co.id;


ALTER TABLE public.client_opreations_balance OWNER TO postgres;

--
-- Name: clients_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.clients_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.clients_id_seq OWNER TO postgres;

--
-- Name: clients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.clients_id_seq OWNED BY public.clients.id;


--
-- Name: employees_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employees_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.employees_id_seq OWNER TO postgres;

--
-- Name: employees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employees_id_seq OWNED BY public.employees.id;


--
-- Name: events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.events (
    id bigint NOT NULL,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    chat_id character varying,
    message text NOT NULL,
    app character varying NOT NULL
);


ALTER TABLE public.events OWNER TO postgres;

--
-- Name: events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.events_id_seq OWNER TO postgres;

--
-- Name: events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.events_id_seq OWNED BY public.events.id;


--
-- Name: firm_operations; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.firm_operations AS
 SELECT dt.id,
    dt."timestamp",
    dt.card_code_id,
    dt.uuid,
    dt.firm_id,
    dt.firm_name,
    dt.counter_card_code_id,
    dt.counter_uuid,
    dt.counter_firm_id,
    dt.counter_firm_name,
    dt.counter_client_id,
    dt.counter_client_name,
    dt.counter_client_squad,
    dt.amount,
    dt.operation,
    dt.type,
    dt.govtax
   FROM ( SELECT transactions_clients_firms_taxes.id,
            transactions_clients_firms_taxes."timestamp",
            transactions_clients_firms_taxes.recipient_card_code_id AS card_code_id,
            transactions_clients_firms_taxes.recipient_uuid AS uuid,
            transactions_clients_firms_taxes.recipient_firm_id AS firm_id,
            transactions_clients_firms_taxes.recipient_firm_name AS firm_name,
            transactions_clients_firms_taxes.source_card_code_id AS counter_card_code_id,
            transactions_clients_firms_taxes.source_uuid AS counter_uuid,
            transactions_clients_firms_taxes.source_firm_id AS counter_firm_id,
            transactions_clients_firms_taxes.source_firm_name AS counter_firm_name,
            transactions_clients_firms_taxes.source_client_id AS counter_client_id,
            transactions_clients_firms_taxes.source_client_name AS counter_client_name,
            transactions_clients_firms_taxes.source_client_squad AS counter_client_squad,
            transactions_clients_firms_taxes.income AS amount,
            transactions_clients_firms_taxes.govtax,
            'income'::public.operation_type AS operation,
            transactions_clients_firms_taxes.type
           FROM public.transactions_clients_firms_taxes
          WHERE (transactions_clients_firms_taxes.recipient_firm_id IS NOT NULL)
        UNION
         SELECT transactions_clients_firms_taxes.id,
            transactions_clients_firms_taxes."timestamp",
            transactions_clients_firms_taxes.source_card_code_id AS card_code_id,
            transactions_clients_firms_taxes.source_uuid AS uuid,
            transactions_clients_firms_taxes.source_firm_id AS firm_id,
            transactions_clients_firms_taxes.source_firm_name AS firm_name,
            transactions_clients_firms_taxes.recipient_card_code_id AS counter_card_code_id,
            transactions_clients_firms_taxes.recipient_uuid AS counter_uuid,
            transactions_clients_firms_taxes.recipient_firm_id AS counter_firm_id,
            transactions_clients_firms_taxes.recipient_firm_name AS counter_firm_name,
            transactions_clients_firms_taxes.recipient_client_id AS counter_client_id,
            transactions_clients_firms_taxes.recipient_client_name AS counter_client_name,
            transactions_clients_firms_taxes.recipient_client_squad AS counter_client_squad,
            transactions_clients_firms_taxes.amount,
            transactions_clients_firms_taxes.govtax,
            'outcome'::public.operation_type AS operation,
            transactions_clients_firms_taxes.type
           FROM public.transactions_clients_firms_taxes
          WHERE (transactions_clients_firms_taxes.source_firm_id IS NOT NULL)) dt
  ORDER BY dt."timestamp";


ALTER TABLE public.firm_operations OWNER TO postgres;

--
-- Name: firm_operations_balance_account; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.firm_operations_balance_account AS
 SELECT fo.id,
    fo."timestamp",
    fo.card_code_id,
    fo.uuid,
    fo.firm_id,
    fo.firm_name,
    fo.counter_card_code_id,
    fo.counter_uuid,
    fo.counter_firm_id,
    fo.counter_firm_name,
    fo.counter_client_id,
    fo.counter_client_name,
    fo.counter_client_squad,
    fo.amount,
    fo.operation,
    fo.type,
    b.balance,
    aefu.client_id,
    aefu.client_chat_id,
    aefu.client_username,
    fo.govtax
   FROM public.firm_operations fo,
    public.balances b,
    public.active_employees aefu
  WHERE ((fo.card_code_id = b.card_code_id) AND (fo.firm_id = aefu.firm_id) AND aefu.is_account)
  ORDER BY fo.id;


ALTER TABLE public.firm_operations_balance_account OWNER TO postgres;

--
-- Name: firms_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.firms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.firms_id_seq OWNER TO postgres;

--
-- Name: firms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.firms_id_seq OWNED BY public.firms.id;


--
-- Name: government_groups; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.government_groups AS
 SELECT groups.chat_id
   FROM public.groups
  WHERE (groups.type = 'government'::public.group_type);


ALTER TABLE public.government_groups OWNER TO postgres;

--
-- Name: groups_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.groups_id_seq OWNER TO postgres;

--
-- Name: groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.groups_id_seq OWNED BY public.groups.id;


--
-- Name: market_groups; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.market_groups AS
 SELECT groups.chat_id
   FROM public.groups
  WHERE (groups.type = 'market'::public.group_type);


ALTER TABLE public.market_groups OWNER TO postgres;

--
-- Name: operations_clients_firms_taxes; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.operations_clients_firms_taxes AS
 SELECT t.id,
    t."timestamp",
    t.type,
    t.operation,
    t.card_code_id,
    t.uuid,
    t.firm_id,
    t.firm_name,
    t.client_id,
    t.client_name,
    t.client_squad,
    t.client_chat_id,
    t.client_username,
    t.amount,
    t.govtax,
    t.counter_card_code_id,
    t.counter_uuid,
    t.counter_firm_id,
    t.counter_firm_name,
    t.counter_client_id,
    t.counter_client_name,
    t.counter_client_squad,
    t.counter_client_chat_id,
    t.counter_client_username
   FROM ( SELECT transactions_clients_firms_taxes.id,
            transactions_clients_firms_taxes."timestamp",
            transactions_clients_firms_taxes.type,
            'outcome'::text AS operation,
            transactions_clients_firms_taxes.source_card_code_id AS card_code_id,
            transactions_clients_firms_taxes.source_uuid AS uuid,
            transactions_clients_firms_taxes.source_firm_id AS firm_id,
            transactions_clients_firms_taxes.source_firm_name AS firm_name,
            transactions_clients_firms_taxes.source_client_id AS client_id,
            transactions_clients_firms_taxes.source_client_name AS client_name,
            transactions_clients_firms_taxes.source_client_squad AS client_squad,
            transactions_clients_firms_taxes.source_client_chat_id AS client_chat_id,
            transactions_clients_firms_taxes.source_client_username AS client_username,
            transactions_clients_firms_taxes.amount,
            transactions_clients_firms_taxes.govtax,
            transactions_clients_firms_taxes.recipient_card_code_id AS counter_card_code_id,
            transactions_clients_firms_taxes.recipient_uuid AS counter_uuid,
            transactions_clients_firms_taxes.recipient_firm_id AS counter_firm_id,
            transactions_clients_firms_taxes.recipient_firm_name AS counter_firm_name,
            transactions_clients_firms_taxes.recipient_client_id AS counter_client_id,
            transactions_clients_firms_taxes.recipient_client_name AS counter_client_name,
            transactions_clients_firms_taxes.recipient_client_squad AS counter_client_squad,
            transactions_clients_firms_taxes.recipient_client_chat_id AS counter_client_chat_id,
            transactions_clients_firms_taxes.recipient_client_username AS counter_client_username
           FROM public.transactions_clients_firms_taxes
        UNION
         SELECT transactions_clients_firms_taxes.id,
            transactions_clients_firms_taxes."timestamp",
            transactions_clients_firms_taxes.type,
            'income'::text AS operation,
            transactions_clients_firms_taxes.recipient_card_code_id AS card_code_id,
            transactions_clients_firms_taxes.recipient_uuid AS uuid,
            transactions_clients_firms_taxes.recipient_firm_id AS firm_id,
            transactions_clients_firms_taxes.recipient_firm_name AS firm_name,
            transactions_clients_firms_taxes.recipient_client_id AS client_id,
            transactions_clients_firms_taxes.recipient_client_name AS client_name,
            transactions_clients_firms_taxes.recipient_client_squad AS client_squad,
            transactions_clients_firms_taxes.recipient_client_chat_id AS client_chat_id,
            transactions_clients_firms_taxes.recipient_client_username AS client_username,
            transactions_clients_firms_taxes.income AS amount,
            transactions_clients_firms_taxes.govtax,
            transactions_clients_firms_taxes.source_card_code_id AS counter_card_code_id,
            transactions_clients_firms_taxes.source_uuid AS counter_uuid,
            transactions_clients_firms_taxes.source_firm_id AS counter_firm_id,
            transactions_clients_firms_taxes.source_firm_name AS counter_firm_name,
            transactions_clients_firms_taxes.source_client_id AS counter_client_id,
            transactions_clients_firms_taxes.source_client_name AS counter_client_name,
            transactions_clients_firms_taxes.source_client_squad AS counter_client_squad,
            transactions_clients_firms_taxes.source_client_chat_id AS counter_client_chat_id,
            transactions_clients_firms_taxes.source_client_username AS counter_client_username
           FROM public.transactions_clients_firms_taxes) t
  ORDER BY t.id;


ALTER TABLE public.operations_clients_firms_taxes OWNER TO postgres;

--
-- Name: queue_client_app; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.queue_client_app (
    id bigint NOT NULL,
    operation public.operation_type NOT NULL,
    amount numeric NOT NULL,
    balance numeric NOT NULL,
    firm_name character varying NOT NULL,
    type public.transaction_type NOT NULL,
    client_chat_id character varying NOT NULL,
    uuid character varying NOT NULL,
    firm_uuid character varying NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    answered boolean DEFAULT false NOT NULL
);


ALTER TABLE public.queue_client_app OWNER TO postgres;

--
-- Name: queue_client_app_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.queue_client_app_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.queue_client_app_id_seq OWNER TO postgres;

--
-- Name: queue_client_app_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.queue_client_app_id_seq OWNED BY public.queue_client_app.id;


--
-- Name: queue_firm_app; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.queue_firm_app (
    id bigint NOT NULL,
    operation public.operation_type NOT NULL,
    amount numeric NOT NULL,
    balance numeric NOT NULL,
    uuid character varying NOT NULL,
    client_chat_id character varying NOT NULL,
    type public.transaction_type NOT NULL,
    counter_uuid character varying NOT NULL,
    counter_firm_name character varying,
    counter_client_name character varying,
    counter_client_squad public.squad_type,
    "timestamp" timestamp without time zone NOT NULL,
    firm_name character varying NOT NULL,
    answered boolean DEFAULT false NOT NULL
);


ALTER TABLE public.queue_firm_app OWNER TO postgres;

--
-- Name: queue_firm_app_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.queue_firm_app_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.queue_firm_app_id_seq OWNER TO postgres;

--
-- Name: queue_firm_app_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.queue_firm_app_id_seq OWNED BY public.queue_firm_app.id;


--
-- Name: telegram_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.telegram_tokens (
    id bigint NOT NULL,
    token character varying NOT NULL,
    app character varying NOT NULL
);


ALTER TABLE public.telegram_tokens OWNER TO postgres;

--
-- Name: telegram_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.telegram_tokens_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.telegram_tokens_id_seq OWNER TO postgres;

--
-- Name: telegram_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.telegram_tokens_id_seq OWNED BY public.telegram_tokens.id;


--
-- Name: transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transactions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.transactions_id_seq OWNER TO postgres;

--
-- Name: transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transactions_id_seq OWNED BY public.transactions.id;


--
-- Name: valid_squads; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.valid_squads AS
 SELECT (unnest.unnest)::text AS squad
   FROM unnest(enum_range(NULL::public.squad_type)) unnest(unnest);


ALTER TABLE public.valid_squads OWNER TO postgres;

--
-- Name: card_codes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.card_codes ALTER COLUMN id SET DEFAULT nextval('public.card_codes_id_seq'::regclass);


--
-- Name: clients id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients ALTER COLUMN id SET DEFAULT nextval('public.clients_id_seq'::regclass);


--
-- Name: employees id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees ALTER COLUMN id SET DEFAULT nextval('public.employees_id_seq'::regclass);


--
-- Name: events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events ALTER COLUMN id SET DEFAULT nextval('public.events_id_seq'::regclass);


--
-- Name: firms id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.firms ALTER COLUMN id SET DEFAULT nextval('public.firms_id_seq'::regclass);


--
-- Name: groups id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups ALTER COLUMN id SET DEFAULT nextval('public.groups_id_seq'::regclass);


--
-- Name: queue_client_app id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queue_client_app ALTER COLUMN id SET DEFAULT nextval('public.queue_client_app_id_seq'::regclass);


--
-- Name: queue_firm_app id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queue_firm_app ALTER COLUMN id SET DEFAULT nextval('public.queue_firm_app_id_seq'::regclass);


--
-- Name: telegram_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.telegram_tokens ALTER COLUMN id SET DEFAULT nextval('public.telegram_tokens_id_seq'::regclass);


--
-- Name: transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions ALTER COLUMN id SET DEFAULT nextval('public.transactions_id_seq'::regclass);


--
-- Name: card_codes card_codes_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.card_codes
    ADD CONSTRAINT card_codes_pk PRIMARY KEY (id);


--
-- Name: clients clients_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pk PRIMARY KEY (id);


--
-- Name: clients clients_un; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_un UNIQUE (card_code_id);


--
-- Name: clients clients_un_1; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_un_1 UNIQUE (chat_id);


--
-- Name: employees employees_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pk PRIMARY KEY (id);


--
-- Name: events events_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pk PRIMARY KEY (id);


--
-- Name: firms firms_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.firms
    ADD CONSTRAINT firms_pk PRIMARY KEY (id);


--
-- Name: firms firms_un; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.firms
    ADD CONSTRAINT firms_un UNIQUE (card_code_id);


--
-- Name: groups groups_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pk PRIMARY KEY (id);


--
-- Name: queue_firm_app newtable_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queue_firm_app
    ADD CONSTRAINT newtable_pk PRIMARY KEY (id);


--
-- Name: queue_client_app queue_client_app_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.queue_client_app
    ADD CONSTRAINT queue_client_app_pk PRIMARY KEY (id);


--
-- Name: telegram_tokens telegram_tokens_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.telegram_tokens
    ADD CONSTRAINT telegram_tokens_pk PRIMARY KEY (id);


--
-- Name: transactions transactions_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pk PRIMARY KEY (id);


--
-- Name: transactions client_queue_insert; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER client_queue_insert AFTER INSERT ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.client_queue_insert_after_transaction();


--
-- Name: transactions deposit_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER deposit_trigger BEFORE INSERT ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.deposit_transaction_trigger();


--
-- Name: transactions firm_queue_insert; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER firm_queue_insert AFTER INSERT ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.firm_queue_insert_after_transaction();


--
-- Name: card_codes insert_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER insert_trigger BEFORE INSERT ON public.card_codes FOR EACH ROW EXECUTE FUNCTION public.card_codes_insert_trigger();


--
-- Name: transactions insert_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER insert_trigger BEFORE INSERT ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.transaction_insert_trigger();


--
-- Name: transactions labor_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER labor_trigger BEFORE INSERT ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.labor_transaction_trigger();


--
-- Name: transactions loan_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER loan_trigger BEFORE INSERT ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.loan_transaction_trigger();


--
-- Name: transactions manual_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER manual_trigger BEFORE INSERT ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.manual_transaction_trigger();


--
-- Name: transactions purchase_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER purchase_trigger BEFORE INSERT ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.purchase_transaction_trigger();


--
-- Name: transactions repay_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER repay_trigger BEFORE INSERT ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.repay_transaction_trigger();


--
-- Name: transactions withdraw_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER withdraw_trigger BEFORE INSERT ON public.transactions FOR EACH ROW EXECUTE FUNCTION public.withdraw_transaction_trigger();


--
-- Name: clients clients_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_fk FOREIGN KEY (card_code_id) REFERENCES public.card_codes(id);


--
-- Name: employees employees_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_fk FOREIGN KEY (firm_id) REFERENCES public.firms(id);


--
-- Name: employees employees_fk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_fk_1 FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- Name: firms firms_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.firms
    ADD CONSTRAINT firms_fk FOREIGN KEY (card_code_id) REFERENCES public.card_codes(id);


--
-- Name: transactions transactions_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_fk FOREIGN KEY (source_card_code_id) REFERENCES public.card_codes(id);


--
-- Name: transactions transactions_fk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_fk_1 FOREIGN KEY (recipient_card_code_id) REFERENCES public.card_codes(id);


--
-- Name: TABLE card_codes; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.card_codes TO government_app;
GRANT SELECT ON TABLE public.card_codes TO card_creator;


--
-- Name: TABLE clients; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,UPDATE ON TABLE public.clients TO client_app;
GRANT INSERT ON TABLE public.clients TO government_app;


--
-- Name: TABLE active_clients_card_codes; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.active_clients_card_codes TO government_app;


--
-- Name: TABLE firms; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.firms TO account_app;
GRANT SELECT ON TABLE public.firms TO government_app;
GRANT SELECT ON TABLE public.firms TO bank_app;


--
-- Name: TABLE active_firms_card_codes; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.active_firms_card_codes TO government_app;


--
-- Name: TABLE employees; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT,INSERT,UPDATE ON TABLE public.employees TO government_app;


--
-- Name: TABLE bank; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.bank TO government_app;
GRANT SELECT ON TABLE public.bank TO bank_app;


--
-- Name: TABLE transactions; Type: ACL; Schema: public; Owner: postgres
--

GRANT INSERT ON TABLE public.transactions TO market_app;
GRANT INSERT ON TABLE public.transactions TO account_app;
GRANT INSERT ON TABLE public.transactions TO government_app;
GRANT INSERT ON TABLE public.transactions TO bank_app;
GRANT INSERT ON TABLE public.transactions TO client_app;


--
-- Name: TABLE market; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.market TO market_app;
GRANT SELECT ON TABLE public.market TO account_app;


--
-- Name: TABLE balances; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.balances TO market_app;
GRANT SELECT ON TABLE public.balances TO account_app;
GRANT SELECT ON TABLE public.balances TO government_app;
GRANT SELECT ON TABLE public.balances TO bank_app;
GRANT SELECT ON TABLE public.balances TO client_app;


--
-- Name: TABLE active_accounts_card_codes_balances; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.active_accounts_card_codes_balances TO account_app;


--
-- Name: TABLE active_clients_card_codes_balances; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.active_clients_card_codes_balances TO client_app;
GRANT SELECT ON TABLE public.active_clients_card_codes_balances TO market_app;
GRANT SELECT ON TABLE public.active_clients_card_codes_balances TO bank_app;
GRANT SELECT ON TABLE public.active_clients_card_codes_balances TO account_app;


--
-- Name: TABLE active_firms_card_codes_balances; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.active_firms_card_codes_balances TO bank_app;
GRANT SELECT ON TABLE public.active_firms_card_codes_balances TO client_app;


--
-- Name: TABLE active_clients_firms_card_codes_balances; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.active_clients_firms_card_codes_balances TO account_app;
GRANT SELECT ON TABLE public.active_clients_firms_card_codes_balances TO government_app;
GRANT SELECT ON TABLE public.active_clients_firms_card_codes_balances TO bank_app;


--
-- Name: TABLE active_employees_accounts; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.active_employees_accounts TO account_app;


--
-- Name: TABLE groups; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.groups TO government_app;


--
-- Name: TABLE admin_groups; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.admin_groups TO government_app;
GRANT SELECT ON TABLE public.admin_groups TO client_app;
GRANT SELECT ON TABLE public.admin_groups TO market_app;
GRANT SELECT ON TABLE public.admin_groups TO bank_app;
GRANT SELECT ON TABLE public.admin_groups TO account_app;


--
-- Name: TABLE bank_groups; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.bank_groups TO bank_app;


--
-- Name: TABLE client_operations; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.client_operations TO client_app;


--
-- Name: TABLE client_opreations_balance; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.client_opreations_balance TO market_app;
GRANT SELECT ON TABLE public.client_opreations_balance TO account_app;
GRANT SELECT ON TABLE public.client_opreations_balance TO government_app;
GRANT SELECT ON TABLE public.client_opreations_balance TO bank_app;
GRANT SELECT ON TABLE public.client_opreations_balance TO client_app;


--
-- Name: SEQUENCE clients_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.clients_id_seq TO government_app;


--
-- Name: SEQUENCE employees_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.employees_id_seq TO government_app;


--
-- Name: TABLE events; Type: ACL; Schema: public; Owner: postgres
--

GRANT INSERT ON TABLE public.events TO government_app;
GRANT INSERT ON TABLE public.events TO client_app;
GRANT INSERT ON TABLE public.events TO market_app;
GRANT INSERT ON TABLE public.events TO bank_app;
GRANT INSERT ON TABLE public.events TO account_app;


--
-- Name: SEQUENCE events_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.events_id_seq TO government_app;
GRANT USAGE ON SEQUENCE public.events_id_seq TO client_app;
GRANT USAGE ON SEQUENCE public.events_id_seq TO market_app;
GRANT USAGE ON SEQUENCE public.events_id_seq TO bank_app;
GRANT USAGE ON SEQUENCE public.events_id_seq TO account_app;


--
-- Name: TABLE firm_operations_balance_account; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.firm_operations_balance_account TO market_app;
GRANT SELECT ON TABLE public.firm_operations_balance_account TO account_app;
GRANT SELECT ON TABLE public.firm_operations_balance_account TO government_app;
GRANT SELECT ON TABLE public.firm_operations_balance_account TO bank_app;
GRANT SELECT ON TABLE public.firm_operations_balance_account TO client_app;


--
-- Name: TABLE government_groups; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.government_groups TO government_app;


--
-- Name: TABLE market_groups; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.market_groups TO market_app;


--
-- Name: TABLE operations_clients_firms_taxes; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.operations_clients_firms_taxes TO bank_app;


--
-- Name: TABLE queue_client_app; Type: ACL; Schema: public; Owner: postgres
--

GRANT INSERT ON TABLE public.queue_client_app TO market_app;
GRANT INSERT ON TABLE public.queue_client_app TO account_app;
GRANT INSERT ON TABLE public.queue_client_app TO government_app;
GRANT INSERT ON TABLE public.queue_client_app TO bank_app;
GRANT SELECT,INSERT,UPDATE ON TABLE public.queue_client_app TO client_app;


--
-- Name: SEQUENCE queue_client_app_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.queue_client_app_id_seq TO market_app;
GRANT USAGE ON SEQUENCE public.queue_client_app_id_seq TO account_app;
GRANT USAGE ON SEQUENCE public.queue_client_app_id_seq TO government_app;
GRANT USAGE ON SEQUENCE public.queue_client_app_id_seq TO bank_app;
GRANT USAGE ON SEQUENCE public.queue_client_app_id_seq TO client_app;


--
-- Name: TABLE queue_firm_app; Type: ACL; Schema: public; Owner: postgres
--

GRANT INSERT ON TABLE public.queue_firm_app TO market_app;
GRANT SELECT,INSERT,UPDATE ON TABLE public.queue_firm_app TO account_app;
GRANT INSERT ON TABLE public.queue_firm_app TO government_app;
GRANT INSERT ON TABLE public.queue_firm_app TO bank_app;
GRANT INSERT ON TABLE public.queue_firm_app TO client_app;


--
-- Name: SEQUENCE queue_firm_app_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.queue_firm_app_id_seq TO account_app;
GRANT USAGE ON SEQUENCE public.queue_firm_app_id_seq TO government_app;
GRANT USAGE ON SEQUENCE public.queue_firm_app_id_seq TO bank_app;
GRANT USAGE ON SEQUENCE public.queue_firm_app_id_seq TO market_app;
GRANT USAGE ON SEQUENCE public.queue_firm_app_id_seq TO client_app;


--
-- Name: TABLE telegram_tokens; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.telegram_tokens TO government_app;
GRANT SELECT ON TABLE public.telegram_tokens TO client_app;
GRANT SELECT ON TABLE public.telegram_tokens TO market_app;
GRANT SELECT ON TABLE public.telegram_tokens TO bank_app;
GRANT SELECT ON TABLE public.telegram_tokens TO account_app;


--
-- Name: SEQUENCE transactions_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT USAGE ON SEQUENCE public.transactions_id_seq TO market_app;
GRANT USAGE ON SEQUENCE public.transactions_id_seq TO account_app;
GRANT USAGE ON SEQUENCE public.transactions_id_seq TO government_app;
GRANT USAGE ON SEQUENCE public.transactions_id_seq TO bank_app;
GRANT USAGE ON SEQUENCE public.transactions_id_seq TO client_app;


--
-- Name: TABLE valid_squads; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.valid_squads TO government_app;


--
-- PostgreSQL database dump complete
--

