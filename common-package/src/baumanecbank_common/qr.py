import io, re
from pyzbar.pyzbar import decode
from PIL import Image

from telegram import PhotoSize

from baumanecbank_common.log import Log

RE_QR_LINK = r"https:\/\/t.me\/.+Bot\?start=(.+)"

async def RecognizeUuidFromQr(photo: PhotoSize, chat_id: int|str) -> str|None:
    try:
        file = await photo.get_file()
        in_memory = io.BytesIO()
        await file.download_to_memory(in_memory)
        in_memory.seek(0)

        qr_decoded   = decode(Image.open(in_memory))
        qr_data: str = qr_decoded[0].data.decode("utf-8")
        return re.findall(RE_QR_LINK, qr_data)[0]
    except Exception as e:
        Log.info((
            f"Got an error while processing qr code for "
            f"{chat_id=}"
        ))
        return None
        