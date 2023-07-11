import os, dotenv
import json
import psycopg2
import gspread
import pandas as pd
from time import sleep

PG_CONN     = 'PG_CONN'
TZ          = 'TZ'
SHEET_LINK  = 'SHEET_LINK'
SHEET_ACC   = 'SHEET_ACC'
WS_CLIENTS  = 'WS_CLIENTS'
WS_FIRMS    = 'WS_FIRMS'

dotenv.load_dotenv()

print("Started and loaded environment")


connection = psycopg2.connect(os.environ.get(PG_CONN, 'postgresql://postgres:postgres@localhost:5432/postgres'))
connection.autocommit = True

print("Connected to database")

gc = gspread.service_account_from_dict(json.loads(os.environ.get(SHEET_ACC)))
sh = gc.open_by_url(os.environ.get(SHEET_LINK))
ws = sh.worksheet(os.environ.get(WS_CLIENTS))

print('Connected to spreadsheet')


df = pd.DataFrame(ws.get_all_records())
df = df.drop(0, axis='index')
print(df)

print('Loaded clients dataframe')

for idx,row in df.iterrows():
    squad = row['squad']
    name  = row['name']
    uuid  = row['uuid']
    sleep(1)

    with connection.cursor() as cur:
        cur.execute((
           f"SELECT True " 
           f"FROM card_codes "
           f"WHERE uuid = '{uuid}'" 
        ))
        if cur.rowcount == 0:
            print(f"Card code does not exist {uuid=} {name=} {squad=}")
            ws.format(
                f"C{idx+2}", {
                    "backgroundColorStyle": {
                        "rgbColor": {
                            "red":   0.82,
                            "green": 0.03,
                            "blue":  0.036, 
                        }
                    }
                }
            )
            continue

    with connection.cursor() as cur:
        cur.execute((
           f"SELECT True " 
           f"FROM active_clients_card_codes "
           f"WHERE uuid = '{uuid}' and name = '{name}'" 
        ))
        if cur.rowcount == 1 and cur.fetchone()[0] == True:
            print(f"Client already exist {uuid=} {name=} {squad=}")
            ws.format(
                f"A{idx+2}:C{idx+2}", {
                    "backgroundColorStyle": {
                        "rgbColor": {
                            "red":   0.03,
                            "green": 0.82,
                            "blue":  0.319, 
                        }
                    }
                }
            )
            continue
    
    with connection.cursor() as cur:
        cur.execute((
           f"INSERT INTO clients (card_code_id, name, squad) " 
           f"SELECT id as card_code_id, "
           f"'{name}' as name, "
           f"'{squad}'::squad_type as squad "
           f"FROM card_codes "
           f"WHERE uuid = '{uuid}'" 
        ))
        if cur.rowcount == 1:
            print(f"Created client {uuid=} {name=} {squad=}")
            ws.format(
                f"A{idx+2}:C{idx+2}", {
                    "backgroundColorStyle": {
                        "rgbColor": {
                            "red":   0.03,
                            "green": 0.82,
                            "blue":  0.319, 
                        }
                    }
                }
            )
            continue

print("Done! Have a greate day!")