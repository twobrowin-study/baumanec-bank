import os, dotenv
import re
import psycopg2
import urllib.parse, urllib.request
import base64

PG_CONN = 'PG_CONN'
TZ      = 'TZ'

RE_CARD_CODE_SYMBOL = r"(?P<open><text:span.*>)x(?P<close><\/text:span>)"
RE_CARD_CODE_QR     = r"(?P<open><office:binary-data)(?P<open_br>>)[-A-Za-z0-9+/=\n\s]*(?P<close><\/office:binary-data>)"


F_TG_BOT_LINK = "https://t.me/{bot}?start={uuid}"

F_QR_CREATE_LINK = "http://qrcoder.ru/code/?{link}&8&3"

TEMPLATE_FILENAME = os.environ.get('TEMPLATE_FILENAME')
OUTPUT_FILENAME   = os.environ.get('OUTPUT_FILENAME')
TG_BOT_NAME       = os.environ.get('TG_BOT_NAME')
CONDITIONS        = os.environ.get('CONDITIONS')

dotenv.load_dotenv()

print("Started and loaded environment")

connection = psycopg2.connect(os.environ.get(PG_CONN, 'postgresql://postgres:postgres@localhost:5432/postgres'))
connection.autocommit = True
cursor = connection.cursor()

print("Connected to database")

with open(TEMPLATE_FILENAME, 'r') as file :
    filedata = file.read()

print(f"Loaded {TEMPLATE_FILENAME=}")

cursor.execute(f"SELECT uuid FROM card_codes WHERE {CONDITIONS}")
uuids = [
    x[0]
    for x in cursor.fetchall()
]

print("Fetched all firms uuids")

print("Prepeared to template substitute")

for uuid in uuids:
    print(f"Prepared to process {uuid=}")
    for sym in uuid:
        filedata = re.sub(RE_CARD_CODE_SYMBOL, rf"\g<open>{sym}\g<close>", filedata, 1)
    print(f"Wrote symbols of {uuid=}")

    url = F_QR_CREATE_LINK.format(
        link = urllib.parse.quote_plus(
            F_TG_BOT_LINK.format(
                bot  = TG_BOT_NAME,
                uuid =  uuid
            )
        )
    )
    print(f"Prepared to call {url=}")

    response = urllib.request.urlopen(url)
    print(f"Responce code {response.getcode()}")
    
    qr_image = base64.b64encode(response.read()).decode("utf-8")
    filedata = re.sub(RE_CARD_CODE_QR, rf'\g<open> processed="true"\g<open_br>{qr_image}\g<close>', filedata, 1)
    print(f"Changed qr code for {uuid=}")
    print()

with open(OUTPUT_FILENAME, 'w') as file:
    file.write(filedata)

print(f"Wrote {OUTPUT_FILENAME=}")
print("Done! Have a greate day!")