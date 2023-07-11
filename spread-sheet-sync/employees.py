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
    for colname in [ f"employee_{x}" for x in range(1,21) ]:
        with connection.cursor() as cur:
            cur.execute((
                f"INSERT into employees (firm_id, client_id) "
                f"SELECT f.id, c.id "
                f"FROM active_firms_card_codes f, active_clients_card_codes c "
                f"WHERE f.uuid = '{uuid}' "
                f"AND c.uuid = '{row[colname]}'"
            ))
            if cur.rowcount == 1:
                print(f"Created employee {row[colname]=} for {row['name']=}")
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

print('Created all of the employees')

print("Done! Have a greate day!")