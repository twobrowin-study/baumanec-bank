import os, dotenv
import json
import psycopg2
import gspread
from gspread.utils import rowcol_to_a1
import pandas as pd
from time import sleep

PG_CONN     = 'PG_CONN'
TZ          = 'TZ'
SHEET_LINK  = 'SHEET_LINK'
SHEET_ACC   = 'SHEET_ACC'
WS_LABOR    = 'WS_LABOR'

dotenv.load_dotenv()

print("Started and loaded environment")


connection = psycopg2.connect(os.environ.get(PG_CONN, 'postgresql://postgres:postgres@localhost:5432/postgres'))
connection.autocommit = True

print("Connected to database")

gc = gspread.service_account_from_dict(json.loads(os.environ.get(SHEET_ACC)))
sh = gc.open_by_url(os.environ.get(SHEET_LINK))
ws = sh.worksheet(os.environ.get(WS_LABOR))

print('Connected to spreadsheet')

df = pd.DataFrame(ws.get_all_records())
df = df.drop(0, axis='index')
print(df)

print('Loaded labor dataframe')

for idx,row in df.iterrows():
    if idx % 30 == 0:
        print("Sleeping for minute")
        sleep(60)
    uuid   = row['uuid']
    amount = row['amount']
    name   = row['name']
    squad  = row['squad']
    with connection.cursor() as cur:
        cur.execute((
            f"INSERT into transactions (recipient_card_code_id, amount, type) "
            f"SELECT card_code_id, {amount}, 'labor' "
            f"FROM active_clients_card_codes "
            f"WHERE uuid = '{uuid}' "
        ))
        if cur.rowcount == 1:
            print(f"Created labor transaction {uuid=} {name=} {squad=}")
            ws.format(
                f"A{idx+2}:G{idx+2}", {
                    "backgroundColorStyle": {
                        "rgbColor": {
                            "red":   0.03,
                            "green": 0.82,
                            "blue":  0.319, 
                        }
                    }
                }
            )

print('Created all of the labor')

print("Done! Have a greate day!")