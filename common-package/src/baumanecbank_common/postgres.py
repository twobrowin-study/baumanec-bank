import os
from typing import Any
import psycopg2, psycopg2.extras

from baumanecbank_common.abstract import AbstractBbClass
from baumanecbank_common.log import Log

from tenacity import retry, wait_exponential, stop_after_attempt
from typing import Callable

PG_CONN = 'PG_CONN'
TZ      = 'TZ'

PURCHASE = 'purchase'
SALARY   = 'salary'
SERVICE  = 'service'
MANUAL   = 'manual'
DEPOSIT  = 'deposit'
WITHDRAW = 'withdraw'
LOAN     = 'loan'
REPAY    = 'repay'

class PgTelegramTokenManyOrMissing(Exception):
    pass

class PgConAbstract(AbstractBbClass):
    def __init__(self, appname: str) -> None:
        super().__init__(appname)
        self._conn: str  = os.environ.get(PG_CONN, 'postgresql://postgres:postgres@localhost:5432/postgres')
        self._connection = None
    
    def connected(self) -> bool:
        return self._connection is not None and self._connection.closed == 0
    
    def connect(self):
        self.close()
        self._connection = psycopg2.connect(self._conn)
        self._connection.autocommit = True
        with self._connection.cursor() as cursor:
            cursor.execute(f"SET timezone TO '{os.environ.get(TZ, 'Europe/Moscow')}'")

    def close(self):
        if self.connected():
            try:
                self._connection.close()
            except Exception:
                pass
        self._connection = None

def reconnect(f: Callable):
    def wrapper(storage: PgConAbstract, *args, **kwargs):
        if not storage.connected():
            storage.connect()
        try:
            return f(storage, *args, **kwargs)
        except psycopg2.Error:
            storage.close()
            raise
    return wrapper

class PgCon(PgConAbstract):
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def _get_exactly_one_or_none(self, sql: str) -> Any|None:
        with self._connection.cursor() as cursor:
            cursor.execute(sql)
            if cursor.rowcount == 0:
                return None
            return cursor.fetchone()[0]

    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def get_telegram_token(self) -> str:
        with self._connection.cursor() as cursor:
            cursor.execute(f"SELECT token FROM telegram_tokens WHERE app = '{self.appname}'")
            if cursor.rowcount != 1:
                raise PgTelegramTokenManyOrMissing(f"App {self.appname} has none or more than one telegram token")
            return cursor.fetchone()[0]
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def write_event(self, message: str, chat_id: str|int = None) -> None:
        chat_id_val = f"'{chat_id}'" if chat_id is not None else 'NULL'
        with self._connection.cursor() as cursor:
            cursor.execute((
                "INSERT INTO events"
                " (chat_id, message, app)"
                " VALUES"
                f" ({chat_id_val}, '{message}', '{self.appname}')"
            ))
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def get_admin_groups(self) -> list[str]:
        with self._connection.cursor() as cursor:
            cursor.execute(f"SELECT chat_id FROM admin_groups")
            if cursor.rowcount == 0:
                return []
            return [ x[0] for x in cursor.fetchall()]
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def check_if_government_group(self, chat_id: int|str) -> bool:
        repl = self._get_exactly_one_or_none(
            f"SELECT True FROM government_groups WHERE chat_id = '{chat_id}'"
        )
        if repl is None:
            return False
        return repl
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def check_if_market_group(self, chat_id: int|str) -> bool:
        repl = self._get_exactly_one_or_none(
            f"SELECT True FROM market_groups WHERE chat_id = '{chat_id}'"
        )
        if repl is None:
            return False
        return repl
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def check_if_bank_group(self, chat_id: int|str) -> bool:
        repl = self._get_exactly_one_or_none(
            f"SELECT True FROM bank_groups WHERE chat_id = '{chat_id}'"
        )
        if repl is None:
            return False
        return repl

    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def get_card_code_id_or_none_by_uuid(self, uuid: str) -> int|None:
        return self._get_exactly_one_or_none(
            f"SELECT id FROM avaliable_card_codes WHERE uuid = '{uuid}'"
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def check_if_squad_valid(self, squad: str) -> bool:
        repl = self._get_exactly_one_or_none(
            f"SELECT True FROM valid_squads WHERE squad = '{squad}'"
        )
        if repl is None:
            return False
        return repl

    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def create_client(self, card_code_id: int|str, name: str, squad: int|str) -> None|Exception:
        try:
            with self._connection.cursor() as cursor:
                cursor.execute((
                    "INSERT INTO clients"
                    " (card_code_id, name, squad)"
                    " VALUES"
                    f" ({card_code_id}, '{name}', '{squad}')"
                ))
                Log.info(f"Created client {card_code_id=} {name=} {squad=}")
                return None
        except Exception as e:
            return e
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def check_if_client_exists_by_chat_id(self, chat_id: str|int) -> bool:
        repl = self._get_exactly_one_or_none(
            f"select true from active_clients_card_codes_balances where chat_id = '{chat_id}'"
        )
        if repl is None:
            return False
        return repl
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def check_if_client_exists_by_uuid(self, uuid: str|int) -> bool:
        repl = self._get_exactly_one_or_none(
            f"select true from active_clients_card_codes_balances where uuid = '{uuid}'"
        )
        if repl is None:
            return False
        return repl

    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def get_client_by_uuid(self, uuid: str|int) -> Any|None:
        with self._connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            cursor.execute((
                "SELECT * "
                "FROM active_clients_card_codes_balances "
                f"WHERE uuid = '{uuid}'"
            ))
            if cursor.rowcount == 0:
                return None
            return cursor.fetchone()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def get_client_by_chat_id(self, chat_id: str|int) -> Any|None:
        with self._connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            cursor.execute((
                "SELECT * "
                "FROM active_clients_card_codes_balances "
                f"WHERE chat_id = '{chat_id}'"
            ))
            if cursor.rowcount == 0:
                return None
            return cursor.fetchone()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def check_if_account_exists_by_chat_id(self, chat_id: str|int) -> bool:
        repl = self._get_exactly_one_or_none(
            f"select true from active_accounts_card_codes_balances where client_chat_id = '{chat_id}'"
        )
        if repl is None:
            return False
        return repl
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def check_if_account_exists_by_uuid(self, uuid: str|int) -> bool:
        repl = self._get_exactly_one_or_none(
            f"select true from active_accounts_card_codes_balances where uuid = '{uuid}'"
        )
        if repl is None:
            return False
        return repl

    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def get_account_by_uuid(self, uuid: str|int) -> Any|None:
        with self._connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            cursor.execute((
                "SELECT * "
                "FROM active_accounts_card_codes_balances "
                f"WHERE uuid = '{uuid}'"
            ))
            if cursor.rowcount == 0:
                return None
            return cursor.fetchone()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def get_account_by_chat_id(self, chat_id: str|int) -> Any|None:
        with self._connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            cursor.execute((
                "SELECT * "
                "FROM active_accounts_card_codes_balances "
                f"WHERE client_chat_id = '{chat_id}'"
            ))
            if cursor.rowcount == 0:
                return None
            return cursor.fetchone()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def check_if_firm_exists_by_uuid(self, uuid: str|int) -> bool:
        repl = self._get_exactly_one_or_none(
            f"select true from active_firms_card_codes_balances where uuid = '{uuid}'"
        )
        if repl is None:
            return False
        return repl

    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def get_firm_by_uuid(self, uuid: str|int) -> Any|None:
        with self._connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            cursor.execute((
                "SELECT * "
                "FROM active_firms_card_codes_balances "
                f"WHERE uuid = '{uuid}'"
            ))
            if cursor.rowcount == 0:
                return None
            return cursor.fetchone()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def update_client_chat_id_username(self, id: int|str, chat_id: int|str, username: str) -> None|Exception:
        try:
            with self._connection.cursor() as cursor:
                cursor.execute((
                    "UPDATE clients "
                    f"SET chat_id  = '{chat_id}', "
                    f"    username = '{username}' "
                    f"WHERE id = {id}"
                ))
                Log.info(f"UPDATE client {id=} {chat_id=} {username=}")
                return None
        except Exception as e:
            return e
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def get_client_operations_by_chat_id(self, chat_id: int|str) -> list[Any]:
        with self._connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            cursor.execute((
                "SELECT * "
                "FROM client_operations "
                f"WHERE client_chat_id = '{chat_id}'"
            ))
            return cursor.fetchall()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def create_purchase(self, card_code_id: int|str, amount: float) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute((
                "INSERT INTO transactions"
                " (source_card_code_id, amount, type)"
                " VALUES"
                f" ({card_code_id}, {amount}, '{PURCHASE}')"
            ))
            Log.info(f"INSERT transaction {PURCHASE} {card_code_id=} {amount=}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def get_frim_operations_by_account_chat_id(self, chat_id: int|str) -> list[Any]:
        with self._connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            cursor.execute((
                "SELECT * "
                "FROM firm_operations_balance_account "
                f"WHERE client_chat_id = '{chat_id}'"
            ))
            return cursor.fetchall()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def get_employees_by_account_chat_id(self, chat_id: int|str) -> list[Any]:
        with self._connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            cursor.execute((
                "SELECT * "
                "FROM active_employees_accounts "
                f"WHERE account_client_chat_id = '{chat_id}'"
            ))
            return cursor.fetchall()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def create_salary(self, firm_card_code_id: int|str, client_card_code_id: int|str, amount: float) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute((
                "INSERT INTO transactions"
                " (source_card_code_id, recipient_card_code_id, amount, type)"
                " VALUES"
                f" ({firm_card_code_id}, {client_card_code_id}, {amount}, '{SALARY}')"
            ))
            Log.info(f"INSERT transaction {SALARY} {firm_card_code_id=} {client_card_code_id=} {amount=}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def get_client_firm_by_uuid(self, uuid: str|int) -> Any|None:
        with self._connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            cursor.execute((
                "SELECT * "
                "FROM active_clients_firms_card_codes_balances "
                f"WHERE uuid = '{uuid}'"
            ))
            if cursor.rowcount == 0:
                return None
            return cursor.fetchone()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def create_service(self, source_card_code_id: int|str, firm_card_code_id: int|str, amount: float) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute((
                "INSERT INTO transactions"
                " (source_card_code_id, recipient_card_code_id, amount, type)"
                " VALUES"
                f" ({source_card_code_id}, {firm_card_code_id}, {amount}, '{SERVICE}')"
            ))
            Log.info(f"INSERT transaction {SERVICE} {source_card_code_id=} {firm_card_code_id=} {amount=}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def create_manual_transaction(self, firm_card_code_id: int|str, amount: float) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute((
                "INSERT INTO transactions"
                " (recipient_card_code_id, amount, type)"
                " VALUES"
                f" ({firm_card_code_id}, {amount}, '{MANUAL}')"
            ))
            Log.info(f"INSERT transaction {MANUAL} {firm_card_code_id=} {amount=}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def get_client_frim_operations_by_uuid(self, uuid: str|int) -> Any|None:
        with self._connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            cursor.execute((
                "SELECT * "
                "FROM operations_clients_firms_taxes "
                f"WHERE uuid = '{uuid}'"
            ))
            if cursor.rowcount == 0:
                return None
            return cursor.fetchall()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def create_deposit_transaction(self, firm_card_code_id: int|str, amount: float) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute((
                "INSERT INTO transactions"
                " (source_card_code_id, amount, type)"
                " VALUES"
                f" ({firm_card_code_id}, {amount}, '{DEPOSIT}')"
            ))
            Log.info(f"INSERT transaction {DEPOSIT} {firm_card_code_id=} {amount=}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def create_withdraw_transaction(self, firm_card_code_id: int|str, amount: float) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute((
                "INSERT INTO transactions"
                " (recipient_card_code_id, amount, type)"
                " VALUES"
                f" ({firm_card_code_id}, {amount}, '{WITHDRAW}')"
            ))
            Log.info(f"INSERT transaction {WITHDRAW} {firm_card_code_id=} {amount=}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def create_loan_transaction(self, firm_card_code_id: int|str, amount: float) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute((
                "INSERT INTO transactions"
                " (recipient_card_code_id, amount, type)"
                " VALUES"
                f" ({firm_card_code_id}, {amount}, '{LOAN}')"
            ))
            Log.info(f"INSERT transaction {LOAN} {firm_card_code_id=} {amount=}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def create_repay_transaction(self, firm_card_code_id: int|str, amount: float) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute((
                "INSERT INTO transactions"
                " (source_card_code_id, amount, type)"
                " VALUES"
                f" ({firm_card_code_id}, {amount}, '{REPAY}')"
            ))
            Log.info(f"INSERT transaction {REPAY} {firm_card_code_id=} {amount=}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def get_clients_queue_and_answer(self) -> Any|None:
        with self._connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            cursor.execute((
                "SELECT * "
                "FROM queue_client_app "
                f"WHERE NOT answered"
            ))
            if cursor.rowcount == 0:
                return None
            ans = cursor.fetchall()
            cursor.execute((
                "UPDATE queue_client_app "
                "SET answered = True "
                f"WHERE id in ({', '.join([str(x.id) for x in ans])})"
            ))
            return ans
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    @reconnect
    def get_firms_queue_and_answer(self) -> Any|None:
        with self._connection.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
            cursor.execute((
                "SELECT * "
                "FROM queue_firm_app "
                f"WHERE NOT answered"
            ))
            if cursor.rowcount == 0:
                return None
            ans = cursor.fetchall()
            cursor.execute((
                "UPDATE queue_firm_app "
                "SET answered = True "
                f"WHERE id in ({', '.join([str(x.id) for x in ans])})"
            ))
            return ans