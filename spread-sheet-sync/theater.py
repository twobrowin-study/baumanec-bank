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
WS_THEATER  = 'WS_THEATER'

dotenv.load_dotenv()

print("Started and loaded environment")


connection = psycopg2.connect(os.environ.get(PG_CONN, 'postgresql://postgres:postgres@localhost:5432/postgres'))
connection.autocommit = True

print("Connected to database")

gc = gspread.service_account_from_dict(json.loads(os.environ.get(SHEET_ACC)))
sh = gc.open_by_url(os.environ.get(SHEET_LINK))
ws = sh.worksheet(os.environ.get(WS_THEATER))

print('Connected to spreadsheet')

df = pd.DataFrame(ws.get_all_records())
df = df.drop(0, axis='index')
df = df.loc[~df.uuid.isin(["", None])]
print(df)

print('Loaded theater employees dataframe')

# for idx,row in df.iterrows():
#     if idx % 30 == 0:
#         print("Sleeping for minute")
#         sleep(60)
#     uuid   = row['uuid']
#     name   = row['name']
#     squad  = row['squad']
#     with connection.cursor() as cur:
#         cur.execute((
#             f"INSERT into employees (firm_id, client_id) "
#             f"SELECT 12, c.id "
#             f"FROM active_clients_card_codes c "
#             f"WHERE c.uuid = '{uuid}' "
#         ))
#         if cur.rowcount == 1:
#             print(f"Created theater employee {uuid=} {name=} {squad=}")
#             ws.format(
#                 f"D{idx+2}", {
#                     "backgroundColorStyle": {
#                         "rgbColor": {
#                             "red":   0.03,
#                             "green": 0.82,
#                             "blue":  0.319, 
#                         }
#                     }
#                 }
#             )

# print('Created all of the theater employees')

for idx,row in df.loc[34:].iterrows():
    if idx % 30 == 0:
        print("Sleeping for minute")
        sleep(60)
    uuid   = row['uuid']
    name   = row['name']
    squad  = row['squad']
    for colname in [ f"salary_{x}" for x in range(3) ]:
        if row[colname] not in ["", None]:
            with connection.cursor() as cur:
                cur.execute((
                    f"INSERT into transactions (source_card_code_id, recipient_card_code_id, amount, type) "
                    f"SELECT 12, c.card_code_id, {row[colname]}, 'salary' "
                    f"FROM active_clients_card_codes c "
                    f"WHERE c.uuid = '{uuid}' "
                ))
                if cur.rowcount == 1:
                    print(f"Created theater salary {uuid=} {name=} {squad=} {colname=}")
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

print('Created all of the theater employees')

print("Done! Have a greate day!")