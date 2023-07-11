import os, asyncio

from baumanecbank_common import ApplicationBb, Log

from telegram import Bot
from telegram.constants import ParseMode

UPD_TIME = 'UPD_TIME'
UPD_TIME_VAL = int(os.environ.get(UPD_TIME, '15'))

async def update_task(app: ApplicationBb) -> None:
    await asyncio.sleep(UPD_TIME_VAL)
    app.create_update_task()
    bot: Bot = app.bot
    updates = app.pgcon.get_firms_queue_and_answer()
    if updates is None:
        return
    for update in updates:
        if update.client_chat_id is None:
            continue
        name = update.counter_firm_name if update.counter_firm_name is not None else update.counter_client_name
        message = app.i18n.app['updates'][update.type][update.operation].format(
            update = update,
            timestamp = update.timestamp.strftime(
                app.i18n.pure['timestamp']['format']
            ),
            name = name
        )
        try:
            await bot.send_message(
                update.client_chat_id, message,
                reply_markup = app.keyboard_main,
                parse_mode = ParseMode.MARKDOWN
            )
        except Exception:
            Log.info(f"Got an exception while sending message to user {update.client_chat_id=}")
