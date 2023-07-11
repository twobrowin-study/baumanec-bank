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
WS_CLIENTS  = 'WS_CLIENTS'
WS_FIRMS    = 'WS_FIRMS'

dotenv.load_dotenv()

print("Started and loaded environment")


connection = psycopg2.connect(os.environ.get(PG_CONN, 'postgresql://postgres:postgres@localhost:5432/postgres'))
connection.autocommit = True

print("Connected to database")

gc = gspread.service_account_from_dict(json.loads(os.environ.get(SHEET_ACC)))
sh = gc.open_by_url(os.environ.get(SHEET_LINK))
ws = sh.worksheet(os.environ.get(WS_FIRMS))

print('Connected to spreadsheet')

df = pd.DataFrame(ws.get_all_records())
df = df.drop(0, axis='index')
print(df)

print('Loaded employees dataframe')

for idx,row in df.iterrows():
    sleep(1)
    uuid = row['uuid']
    for colname in [ f"account_{x}" for x in range(1,3) ]:
        with connection.cursor() as cur:
            cur.execute((
                f"UPDATE employees "
                f"SET is_account = True "
                f"WHERE firm_id   = (SELECT id FROM active_firms_card_codes   WHERE uuid = '{uuid}')"
                f"AND   client_id = (SELECT id FROM active_clients_card_codes WHERE uuid = '{row[colname]}')"
            ))
            if cur.rowcount == 1:
                print(f"Seted account for {row[colname]=} for {row['name']=}")
                ws.format(
                    rowcol_to_a1(idx+2, df.columns.get_loc(colname)+1), {
                        "backgroundColorStyle": {
                            "rgbColor": {
                                "red":   0.03,
                                "green": 0.82,
                                "blue":  0.319, 
                            }
                        }
                    }
                )

print('Seted all of accounts')

print("Done! Have a greate day!")