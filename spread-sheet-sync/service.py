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
WS_SERVICE  = 'WS_SERVICE'

dotenv.load_dotenv()

print("Started and loaded environment")


connection = psycopg2.connect(os.environ.get(PG_CONN, 'postgresql://postgres:postgres@localhost:5432/postgres'))
connection.autocommit = True

print("Connected to database")

gc = gspread.service_account_from_dict(json.loads(os.environ.get(SHEET_ACC)))
sh = gc.open_by_url(os.environ.get(SHEET_LINK))
ws = sh.worksheet(os.environ.get(WS_SERVICE))

print('Connected to spreadsheet')

df = pd.DataFrame(ws.get_all_records())
df = df.drop(0, axis='index')
print(df)

print('Loaded labor dataframe')

for idx,row in df.iterrows():
    if idx % 30 == 0:
        print("Sleeping for minute")
        sleep(60)
    client_name  = row['client_name']
    client_squad = row['client_squad']
    amount       = row['amount']
    client_uuid  = row['client_uuid']
    firm_uuid    = row['firm_uuid']
    firm_name    = row['firm_name']
    with connection.cursor() as cur:
        cur.execute((
            f"INSERT into transactions (source_card_code_id, recipient_card_code_id, amount, type) "
            f"SELECT c.card_code_id, f.card_code_id, {amount}, 'service' "
            f"FROM active_clients_card_codes c, active_firms_card_codes f "
            f"WHERE c.uuid = '{client_uuid}' "
            f"AND   f.uuid = '{firm_uuid}' "
        ))
        if cur.rowcount == 1:
            print(f"Created service transaction {client_name=} {client_squad=} {amount=} {client_uuid=} {firm_uuid=} {firm_name=}")
            ws.format(
                f"A{idx+2}:H{idx+2}", {
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